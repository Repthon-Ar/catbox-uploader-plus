import mimetypes
import os
from contextlib import ExitStack
from io import BytesIO
from pathlib import Path

import requests

from .exceptions import (
    CatboxError,
    TimeoutError,
    ConnectionError,
    HTTPError,
    FileNotFoundError,
)

CATBOX_API_URL = "https://catbox.moe/user/api.php"
LITTERBOX_API_URL = "https://litterbox.catbox.moe/resources/internals/api.php"
LITTERBOX_EXPIRATION_TIMES = {"1h", "12h", "24h", "72h", "1w"}

def _prepare_upload(file_path_or_bytes, stack, file_name=None):
    """Prepare a multipart upload value without closing caller-owned streams."""
    if isinstance(file_path_or_bytes, (str, os.PathLike, Path)):
        path = os.fspath(file_path_or_bytes)

        if not os.path.isfile(path):
            raise FileNotFoundError(f"File does not exist: {path}")

        file_obj = stack.enter_context(open(path, "rb"))
        upload_name = file_name or os.path.basename(path)
    elif isinstance(file_path_or_bytes, BytesIO):
        file_obj = file_path_or_bytes
        upload_name = (
            file_name
            or getattr(file_path_or_bytes, "name", None)
            or "file"
        )
    else:
        raise CatboxError(
            "Unsupported file input. Provide a file path or io.BytesIO object."
        )

    content_type = (
        mimetypes.guess_type(upload_name)[0]
        or "application/octet-stream"
    )
    return (upload_name, file_obj, content_type)


def _post(url, *, data=None, files=None, timeout=30, operation="Request"):
    """Send a POST request and translate Requests exceptions to library errors."""
    try:
        response = requests.post(
            url,
            data=data,
            files=files,
            timeout=timeout,
        )
        response.raise_for_status()
        return response

    except requests.exceptions.Timeout as exc:
        raise TimeoutError(
            f"{operation} timed out after {timeout} seconds."
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise ConnectionError(
            f"{operation} could not connect to the server."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        body = ""
        if exc.response is not None:
            body = (exc.response.text or "").strip()
        detail = f": {body}" if body else ""
        raise HTTPError(
            f"{operation} failed with HTTP status {status}{detail}"
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise CatboxError(f"{operation} failed: {exc}") from exc


def _response_text(response, operation, *, expect_url=False):
    """Return a non-empty response body and optionally check that it is a URL."""
    result = (response.text or "").strip()

    if not result:
        raise CatboxError(
            f"{operation} returned an empty response "
            f"(HTTP {response.status_code})."
        )

    if expect_url and not result.startswith(("https://", "http://")):
        raise CatboxError(
            f"{operation} returned an unexpected response: {result!r}"
        )

    return result


def _restore_stream_position(file_obj, position):
    """Restore a BytesIO object's cursor after a request, when possible."""
    try:
        file_obj.seek(position)
    except (AttributeError, OSError, ValueError):
        pass


def upload_file(file_path_or_bytes, timeout=30, userhash=None):
    """
    Upload a file to Catbox.

    Args:
        file_path_or_bytes: A filesystem path or BytesIO object.
        timeout: Request timeout in seconds.
        userhash: Optional Catbox userhash.

    Returns:
        The uploaded file URL.
    """
    data = {"reqtype": "fileupload"}
    if userhash:
        data["userhash"] = userhash

    stream_position = None
    if isinstance(file_path_or_bytes, BytesIO):
        try:
            stream_position = file_path_or_bytes.tell()
            file_path_or_bytes.seek(0)
        except (OSError, ValueError):
            pass

    try:
        with ExitStack() as stack:
            upload_file_data = _prepare_upload(file_path_or_bytes, stack)
            response = _post(
                CATBOX_API_URL,
                data=data,
                files={"fileToUpload": upload_file_data},
                timeout=timeout,
                operation="Catbox upload",
            )
            return _response_text(
                response, "Catbox upload", expect_url=True
            )
    finally:
        if stream_position is not None:
            _restore_stream_position(file_path_or_bytes, stream_position)


def upload_to_litterbox(
    file_path_or_bytes,
    file_name="file.png",
    time="1h",
    timeout=30,
):
    """
    Upload a file to Litterbox temporary storage.

    Args:
        file_path_or_bytes: A filesystem path or BytesIO object.
        file_name: Multipart filename for BytesIO uploads. For path uploads,
            the actual path basename is used unless this value is explicitly
            changed from its default.
        time: Expiration period: 1h, 12h, 24h, 72h, or 1w.
        timeout: Request timeout in seconds.

    Returns:
        The temporary file URL.
    """
    if time not in LITTERBOX_EXPIRATION_TIMES:
        raise CatboxError(
            "Invalid Litterbox expiration time. "
            f"Choose one of: {', '.join(sorted(LITTERBOX_EXPIRATION_TIMES))}."
        )

    stream_position = None
    if isinstance(file_path_or_bytes, BytesIO):
        try:
            stream_position = file_path_or_bytes.tell()
            file_path_or_bytes.seek(0)
        except (OSError, ValueError):
            pass

    try:
        with ExitStack() as stack:
            # Keep the original default filename for BytesIO compatibility;
            # filesystem paths use their real basename.
            selected_name = None if file_name == "file.png" else file_name
            upload_file_data = _prepare_upload(
                file_path_or_bytes,
                stack,
                file_name=selected_name,
            )
            response = _post(
                LITTERBOX_API_URL,
                data={"reqtype": "fileupload", "time": time},
                files={"fileToUpload": upload_file_data},
                timeout=timeout,
                operation="Litterbox upload",
            )
            return _response_text(
                response, "Litterbox upload", expect_url=True
            )
    finally:
        if stream_position is not None:
            _restore_stream_position(file_path_or_bytes, stream_position)


def upload_album(file_paths_or_bytes_list, timeout=30, userhash=None):
    """
    Upload multiple files to Catbox and return their URLs.

    This preserves the original library behavior: files are uploaded one by
    one, and the returned list contains the individual file URLs.
    """
    uploaded_links = []

    for file_item in file_paths_or_bytes_list:
        uploaded_links.append(
            upload_file(file_item, timeout=timeout, userhash=userhash)
        )

    return uploaded_links


def delete_files(files, userhash, timeout=30):
    """Delete uploaded Catbox files using a userhash."""
    if not userhash:
        raise CatboxError("Userhash is required to delete files.")

    if isinstance(files, str):
        files = [files]

    file_ids = list(files)
    if not file_ids:
        raise CatboxError("At least one file ID must be provided.")

    _post(
        CATBOX_API_URL,
        data={
            "reqtype": "deletefiles",
            "userhash": userhash,
            "files": " ".join(file_ids),
        },
        timeout=timeout,
        operation="Delete Catbox files",
    )


def create_album(files, title, description, userhash, timeout=30):
    """Create a Catbox album and return its shortcode."""
    if not userhash:
        raise CatboxError("Userhash is required to create an album.")

    file_ids = [files] if isinstance(files, str) else list(files)
    if not file_ids:
        raise CatboxError("At least one file ID must be provided.")

    response = _post(
        CATBOX_API_URL,
        data={
            "reqtype": "createalbum",
            "userhash": userhash,
            "title": title,
            "desc": description,
            "files": " ".join(file_ids),
        },
        timeout=timeout,
        operation="Create Catbox album",
    )
    return _response_text(response, "Create Catbox album")


def edit_album(shortcode, files, title, description, userhash, timeout=30):
    """Edit an existing Catbox album."""
    if not userhash:
        raise CatboxError("Userhash is required to edit an album.")

    file_ids = [files] if isinstance(files, str) else list(files)

    response = _post(
        CATBOX_API_URL,
        data={
            "reqtype": "editalbum",
            "userhash": userhash,
            "short": shortcode,
            "title": title,
            "desc": description,
            "files": " ".join(file_ids),
        },
        timeout=timeout,
        operation="Edit Catbox album",
    )
    return _response_text(response, "Edit Catbox album")


def delete_album(shortcode, userhash, timeout=30):
    """Delete a Catbox album."""
    if not userhash:
        raise CatboxError("Userhash is required to delete an album.")

    _post(
        CATBOX_API_URL,
        data={
            "reqtype": "deletealbum",
            "userhash": userhash,
            "short": shortcode,
        },
        timeout=timeout,
        operation="Delete Catbox album",
    )
