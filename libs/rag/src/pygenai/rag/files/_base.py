"""Abstract definitions for a filesystem Unit of Work.

Contains an abstract base class that declares a standard API for filesystem-like
services. Concrete adapters should implement methods to read, upload, create,
move, list, and remove files, and to manage base routes or folder prefixes.
"""

import abc


class AbstractFileSystemUnitOfWork(abc.ABC):
    """Contract for a filesystem Unit of Work.

    Lists the methods storage adapters must supply, providing a consistent
    interface for file and directory operations across local, cloud, or
    virtual storage backends.
    """

    def __init__(self, route: str) -> None:
        """Set up the Unit of Work with a base route.

        Args:
            route (str): Path or prefix that scopes all filesystem operations.
                Implementations can use this to build absolute paths, bucket
                prefixes, or folder contexts.
        """
        self._route = route

    @abc.abstractmethod
    def create_text_file(self, text: str, file: str, encoding: str = "utf-8") -> bool:
        """Write text content to a file.

        Args:
            text (str): The text to store in the file.
            file (str): Target file path.
            encoding (str, optional): Encoding to use (default: "utf-8").

        Returns:
            bool: True when the file was successfully created, False otherwise.

        Raises:
            NotImplementedError: Implementations must override this method.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_file(self, file: str) -> bool:
        """Remove a file from storage.

        Args:
            file (str): Path or identifier of the file to remove.

        Returns:
            bool: True if deletion succeeded, False otherwise.

        Raises:
            NotImplementedError: Implementing classes must provide this.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_file(self, file: str) -> bytes:
        """Fetch a file's raw byte contents.

        Args:
            file (str): Path or identifier of the file to fetch.

        Returns:
            bytes: Binary contents of the file.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_folder(self, prefix: str) -> list:
        """Return the entries under a given folder or prefix.

        Args:
            prefix (str): Folder path or prefix to inspect.

        Returns:
            list: Names of files and/or subfolders found under the prefix.

        Raises:
            NotImplementedError: Subclasses must implement this.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def move_file(self, old_file: str, new_file: str, new_route: str | None = None) -> bool:
        """Rename or relocate a file.

        Args:
            old_file (str): Source file path.
            new_file (str): Destination filename or path.
            new_route (str | None): Optional new route/folder to place the file.
                If omitted, the current route is used.

        Returns:
            bool: True on success, False on failure.

        Raises:
            NotImplementedError: Must be provided by concrete implementations.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def move_route(self, route: str) -> str:
        """Update the base route that scopes operations.

        Args:
            route (str): New base path or prefix.

        Returns:
            str: The route value after applying the change.

        Raises:
            NotImplementedError: To be implemented by subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, file_route: str, name: str | None = None) -> bool:
        """Transfer a local file into the storage backend.

        Args:
            file_route (str): Path to the source file on the local filesystem.
            name (str | None): Desired name for the file in storage. If None,
                the source filename may be used.

        Returns:
            bool: True when the upload completes successfully, otherwise False.

        Raises:
            NotImplementedError: Concrete adapters must implement this.
        """
        raise NotImplementedError
