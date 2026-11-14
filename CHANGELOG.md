Changelog

All notable changes to Catbox Uploader Plus are documented in this file.

[2.9.1] - Unreleased

Added

- Added support for "BytesIO" objects in file uploads.
- Added support for "pathlib.Path" objects.
- Added configurable request timeouts for file and album management operations.
- Added support for the "1w" Litterbox expiration period.
- Added public exports for library exception classes.
- Added improved input and upload-response validation.

Improved

- Improved Catbox upload handling.
- Improved Litterbox upload handling and file lifecycle management.
- Improved in-memory file stream-position management.
- Centralized HTTP request handling.
- Improved error handling for connection failures, timeouts, and HTTP errors.
- Improved documentation and usage examples.

Fixed

- Fixed argument mapping in "CatboxUploader.upload_to_litterbox()".
- Fixed file-handle lifecycle handling during Litterbox uploads.
- Improved handling of empty upload responses.
- Fixed file stream handling in upload operations.

Compatibility

- Preserved the original "catbox" package import path.
- Preserved the "CatboxUploader" class.
- Preserved the original main method names and positional argument order.

---

Original Project

Catbox Uploader Plus is based on the original Catbox Uploader project.

Original licensing notices are retained where applicable.

Enhanced and maintained by Repthon Contributors.
