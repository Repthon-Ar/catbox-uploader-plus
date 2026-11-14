"""High-level Catbox Uploader Plus client.

The public method names and their original positional argument order are
kept compatible with the original catbox-uploader package.
"""

from .helpers import (
    upload_file,
    upload_to_litterbox,
    upload_album,
    delete_files,
    create_album,
    edit_album,
    delete_album,
)
from .exceptions import CatboxError


class CatboxUploader:
    """Client for uploading and managing files on Catbox and Litterbox."""

    def __init__(self, userhash=None):
        """Create a client.

        Args:
            userhash (str, optional): Catbox userhash for authenticated
                uploads and file/album management.
        """
        self.userhash = userhash

    def upload_file(self, file_path, timeout=30):
        """Upload one file to Catbox and return its URL."""
        return upload_file(file_path, timeout=timeout, userhash=self.userhash)

    def upload_to_litterbox(self, file_path, time="1h", timeout=30):
        """Upload a temporary file to Litterbox and return its URL."""
        # Use keywords: the second helper argument is file_name, not time.
        return upload_to_litterbox(file_path, time=time, timeout=timeout)

    def upload_album(self, file_paths, timeout=30):
        """Upload multiple files individually and return their URLs."""
        return upload_album(
            file_paths,
            timeout=timeout,
            userhash=self.userhash,
        )

    def delete_files(self, files, timeout=30):
        """Delete one or more Catbox files using the configured userhash."""
        if not self.userhash:
            raise CatboxError("Userhash is required to delete files.")
        return delete_files(files, self.userhash, timeout=timeout)

    def create_album(self, files, title, description, timeout=30):
        """Create a Catbox album using the configured userhash."""
        if not self.userhash:
            raise CatboxError("Userhash is required to create an album.")
        return create_album(
            files,
            title,
            description,
            self.userhash,
            timeout=timeout,
        )

    def edit_album(self, shortcode, files, title, description, timeout=30):
        """Edit an existing Catbox album."""
        if not self.userhash:
            raise CatboxError("Userhash is required to edit an album.")
        return edit_album(
            shortcode,
            files,
            title,
            description,
            self.userhash,
            timeout=timeout,
        )

    def delete_album(self, shortcode, timeout=30):
        """Delete a Catbox album using the configured userhash."""
        if not self.userhash:
            raise CatboxError("Userhash is required to delete an album.")
        return delete_album(shortcode, self.userhash, timeout=timeout)


__all__ = ["CatboxUploader", "CatboxError"]
