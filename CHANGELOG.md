# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-09-22
### Fixed
- Attachment files are stored and looked up in the `AttachmentMeta.storage_location` of their own content
  object instead of a single storage instance shared by the whole process. Previously every upload
  overwrote the location of that shared instance, so the content type that uploaded last in a worker
  process decided where all subsequent file operations looked. Applications using more than one
  `storage_location` saw intermittent 404s on download, "File not found" in the admin, files left behind
  on disk on delete/replace and `FileNotFoundError` when re-saving an attachment.

### Removed
- `AttachmentViewSet.get_storage_path()`, which became obsolete because `attachment.file.path` now
  resolves the correct storage location on its own.

[Unreleased]: https://github.com/anexia/drf-attachments/compare/0.5.0...HEAD
[0.5.0]: https://github.com/anexia/drf-attachments/compare/0.4.2...0.5.0
