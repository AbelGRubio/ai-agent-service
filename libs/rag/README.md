# Pygenai Files

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![Package](https://img.shields.io/badge/package-pygenai--files-8A2BE2)
![Status](https://img.shields.io/badge/status-experimental-orange)
![License](https://img.shields.io/badge/license-repository%20license-blue)

`pygenai-files` is a lightweight storage abstraction for the Pygenai ecosystem. It provides a consistent file API across different backends so AI agents and services can read, write, move, and list files without coupling their logic to a specific storage implementation.

## Features

- Local filesystem adapter for dev and testing workflows
- S3 and S3-compatible object storage adapter
- Optional MongoDB/GridFS adapter for document/blob persistence
- Shared abstract interface for common file operations
- Safe, route-scoped storage prefixes for multi-tenant or app-specific usage

## Supported backends

- `LocalFileSystemUnitOfWork`
- `S3FileSystemUnitOfWork`
- `MongoFileSystemUnitOfWork` (available in `pygenai.files.db` when `pymongo` is installed)

## Installation

Install the package with uv:

```bash
uv add pygenai-files
```

If you are working inside this monorepo, install the local package in editable mode:

```bash
uv pip install -e ./libs/files
```

## Usage

### Local filesystem

```python
from pygenai.rag.files import LocalFileSystemUnitOfWork

storage = LocalFileSystemUnitOfWork("./tmp/data")

storage.create_text_file("hello from pygenai", "notes/hello.txt")
content = storage.get_file("notes/hello.txt")
print(content.decode("utf-8"))

print(storage.list_folder("notes"))
```

### S3-compatible storage

```python
from pygenai.rag.files import S3FileSystemUnitOfWork

storage = S3FileSystemUnitOfWork(
    route="my-app/uploads",
    bucket="my-bucket",
    aws_endpoint_url="http://localhost:9000",
    aws_region_name="us-east-1",
)

storage.create_text_file("hello from s3", "sample.txt")
print(storage.get_file("sample.txt"))
```

### Common operations

```python
storage.create_text_file("A simple file", "folder/example.txt")
storage.move_file("folder/example.txt", "renamed.txt")
storage.delete_file("renamed.txt")
```

The core abstraction exposes the following methods:

- `create_text_file(text, file, encoding="utf-8")`
- `get_file(file)`
- `delete_file(file)`
- `list_folder(prefix)`
- `move_file(old_file, new_file, new_route=None)`
- `move_route(route)`
- `upload_file(file_route, name=None)`

## Project structure

```text
libs/files/
├── pyproject.toml
├── README.md
├── src/
│   └── pygenai/
│       └── files/
│           ├── __init__.py
│           ├── _base.py
│           ├── local.py
│           ├── s3.py
│           └── db.py
└── tests/
```

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository and create a feature branch.
2. Add or update tests for behavior changes.
3. Keep the scope small and focused.
4. Run the relevant validation checks before submitting a pull request.
5. Open a PR with a clear summary of the change and why it matters.

Please keep code documentation clear and consistent with the repository style.

## License

This package is distributed under the repository's licensing terms for the Pygenai project. See the repository root for the full license text and any applicable notices.
