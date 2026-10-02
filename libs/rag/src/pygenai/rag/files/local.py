"""Local filesystem adapter for the AbstractFileSystemUnitOfWork.

Implements the Unit of Work API using the host machine's filesystem. It
supports creating, deleting, reading, moving, copying (uploading), and
listing files, all confined under a configured base directory.
"""

import logging
import shutil
from pathlib import Path

from ._base import AbstractFileSystemUnitOfWork

logger = logging.getLogger(__name__)


class LocalFileSystemUnitOfWork(AbstractFileSystemUnitOfWork):
    """Concrete local implementation of the filesystem Unit of Work.

    Provides methods to interact with the OS filesystem, with every operation
    limited to the base route supplied at construction time.
    """

    def __init__(self, route: str) -> None:
        """Set up the local Unit of Work.

        Args:
            route (str): Base directory that scopes filesystem operations. The
                directory is created if it doesn't already exist.
        """
        super().__init__(route)
        self._route = Path(route).resolve()
        self._route.mkdir(parents=True, exist_ok=True)

    def _full_path(self, relative_path: str) -> Path:
        """Resolve a relative path into an absolute path under the base route.

        Args:
            relative_path (str): Path relative to the configured route.

        Returns:
            Path: The absolute, resolved filesystem Path.
        """
        return (Path(self._route) / relative_path).resolve()

    def create_text_file(self, text: str, file: str, encoding: str = "utf-8") -> bool:
        """Write a text file at the given relative path.

        Args:
            text (str): Content to write.
            file (str): Path relative to the base route.
            encoding (str): Text encoding (default: "utf-8").

        Returns:
            bool: True on success, False on failure.

        Raises:
            UnicodeEncodeError: If encoding fails for the provided text.
        """
        try:
            full_path = self._full_path(file)
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with full_path.open(mode="w", encoding=encoding) as f:
                f.write(text)

            return True
        except (OSError, PermissionError, UnicodeEncodeError):
            logger.exception(f"Create text file '{file}' failed with an exception.")
            return False

    def delete_file(self, file: str) -> bool:
        """Remove a file from the local filesystem.

        Args:
            file (str): Path to the file relative to the base route.

        Returns:
            bool: True when the file was removed, False otherwise.
        """
        try:
            full_path = self._full_path(file)
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
            return False
        except (FileNotFoundError, OSError, PermissionError):
            logger.exception(f"Delete file '{file}' failed with an exception.")
            return False

    def get_file(self, file: str) -> bytes:
        """Read and return a file's bytes.

        Args:
            file (str): Relative path to the file under the base route.

        Returns:
            bytes: The file's binary contents.

        Raises:
            FileNotFoundError: When the file does not exist.
            OSError: For unexpected filesystem errors.
            PermissionError: If the file can't be opened.
        """
        full_path = self._full_path(file)
        with full_path.open("rb") as f:
            return f.read()

    def list_folder(self, prefix: str) -> list[str]:
        """Return names of entries inside a directory.

        Args:
            prefix (str): Relative directory path.

        Returns:
            List[str]: Names of files and subdirectories found, or an empty
                list if the directory does not exist.

        Raises:
            OSError: If listing the directory fails.
        """
        full_path = self._full_path(prefix)
        if not full_path.exists():
            return []
        return [item.name for item in full_path.iterdir()]

    def move_file(self, old_file: str, new_file: str, new_route: str | None = None) -> bool:
        """Move or rename a file within the base route.

        Args:
            old_file (str): Source path relative to the base route.
            new_file (str): Destination filename or relative path.
            new_route (str | None): Optional new directory relative to base route.

        Returns:
            bool: True if the operation succeeds, False otherwise.
        """
        try:
            src = self._full_path(old_file)

            target_dir = self._full_path(new_route) if new_route else src.parent

            target_dir.mkdir(parents=True, exist_ok=True)
            dst = (target_dir / new_file).resolve()

            shutil.move(str(src), str(dst))
            return True
        except (FileNotFoundError, PermissionError, OSError):
            logger.exception(f"Move file '{old_file}' to '{new_file}' failed with an exception.")
            return False

    def move_route(self, route: str) -> str:
        """Switch the Unit of Work to a different base directory.

        Args:
            route (str): New base directory to use.

        Returns:
            str: The resolved path of the new base directory.

        Raises:
            OSError: If the directory cannot be created.
        """
        new_route = Path(route).resolve()
        new_route.mkdir(parents=True, exist_ok=True)
        self._route = new_route
        return str(self._route)

    def upload_file(self, file_route: str, name: str | None = None) -> bool:
        """Copy a local file into the Unit of Work's base directory.

        Args:
            file_route (str): Source file path on the local system.
            name (str | None): Desired filename inside the base route; if None,
                the source file's name is used.

        Returns:
            bool: True when the file was copied successfully, False otherwise.
        """
        try:
            source = Path(file_route).resolve()
            if not source.exists():
                return False

            target_name = name or source.name
            destination = self._full_path(target_name)
            destination.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(source, destination)
            return True
        except (FileNotFoundError, PermissionError, OSError):
            logger.exception(f"Upload file '{file_route}' failed with an exception.")
            return False
