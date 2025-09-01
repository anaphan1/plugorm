"""Driver interfaces.

This module defines the abstract base driver classes that form the foundation of
the toolchain system:

- Driver: Base class for all drivers, defining input/output typing and sync/async flags.
- ILDriver: Converts internal intermediate representations (IL/IR) into SQL queries.
- ConnectionDriver: Manages database connections and executes SQL statements.
- Simplifier: Transforms low-level execution results into higher-level, simplified forms.

Each driver supports both synchronous and asynchronous methods, with subclasses
required to implement at least one mode of operation.
"""

from abc import ABC, abstractmethod
from typing import Any

from .utils import has_impl


class Driver:
    """Base class for all drivers.

    Defines the required interface and core attributes for drivers, including their input/output domains and
    synchronous/asynchronous capabilities.

    Attributes:
        input_ (set[str]): Set of supported input types for this driver.
        output (set[str]): Set of output types produced by this driver.
        is_sync (bool): Indicates whether the driver supports synchronous execution.
        is_async (bool): Indicates whether the driver supports asynchronous execution.
    """

    input_: set[str]
    output: set[str]

    is_sync: bool
    is_async: bool

    def __repr__(self) -> str:
        """Return a string representation of the driver.

        Returns:
            str: Representation including the class name, input, and output types.
        """
        return (
            f"<{self.__class__.__name__}(input_={self.input_}, output={self.output})>"
        )


class ToolchainDriver(Driver, ABC):
    """Abstract base class for all drivers in the toolchain.

    Automatically detect async and sync support
    """

    def __init__(self):
        self.check_async()

    @abstractmethod
    def check_async(self) -> None:
        """Validate that asynchronous or synchronous behavior is correctly implemented."""

    def __repr__(self) -> str:
        """Return a string representation of the driver.

        Returns:
            str: Representation including the class name, input, and output types.
        """
        return (
            f"<{self.__class__.__name__}(input_={self.input_}, output={self.output})>"
        )


class ILDriver(ToolchainDriver):
    """Abstract base class for internal language (IL) drivers.

    An ``ILDriver`` is responsible for converting the internal language of a dialect into an SQL-specific query.
    Subclasses must support either sync or async implementation
    """

    def check_async(self) -> None:
        """Detect whether sync/async methods are implemented.

        Updates the ``is_sync`` and ``is_async`` flags by checking if the subclass provides ``parse`` and/or ``aparse``.
        """
        self.is_sync = has_impl(ILDriver, self.__class__, "parse")
        self.is_async = has_impl(ILDriver, self.__class__, "aparse")

    def parse(self, internal_language: Any) -> str:
        """Synchronously parse an internal language representation.

        Args:
            internal_language (Any): The internal language object to be parsed.

        Returns:
            str: The SQL-specific query defined by the internal language.
        """
        raise NotImplementedError

    async def aparse(self, internal_language: Any) -> str:
        """Asynchronously parse an internal language representation.

        Args:
            internal_language (Any): The internal language object to be parsed.

        Returns:
            str: The SQL-specific query defined by the internal language.
        """
        raise NotImplementedError


class ConnectionDriver(ToolchainDriver):
    """Abstract base class for database connection drivers.

    A ``ConnectionDriver`` defines the low-level API for connecting to, interacting with, and closing a database
    connection. Subclasses must provide synchronous and/or asynchronous implementations of connection lifecycle methods and SQL
    execution.
    """

    def check_async(self) -> None:
        """Detect whether sync/async methods are implemented.

        Updates the ``is_sync`` and ``is_async`` flags based on whether the subclass provides both
        ``connect``/``close``/``execute`` (sync) and ``aconnect``/``aclose``/``aexecute` (async).
        """
        self.is_sync = (
            has_impl(ConnectionDriver, self.__class__, "execute")
            and has_impl(ConnectionDriver, self.__class__, "connect")
            and has_impl(ConnectionDriver, self.__class__, "close")
        )
        self.is_async = (
            has_impl(ConnectionDriver, self.__class__, "aexecute")
            and has_impl(ConnectionDriver, self.__class__, "aconnect")
            and has_impl(ConnectionDriver, self.__class__, "aclose")
        )

    def connect(self) -> None:
        """Synchronously establish a database connection."""
        raise NotImplementedError

    def close(self) -> None:
        """Synchronously close the database connection."""
        raise NotImplementedError

    def execute(self, statement: str) -> Any:
        """Synchronously execute a SQL statement.

        Args:
            statement (str): The SQL query or command to execute.

        Returns:
            Any: The result returned by the database driver.
        """
        raise NotImplementedError

    async def aconnect(self) -> None:
        """Asynchronously establish a database connection."""
        raise NotImplementedError

    async def aclose(self) -> None:
        """Asynchronously close the database connection."""
        raise NotImplementedError

    async def aexecute(self, statement: str) -> Any:
        """Asynchronously execute a SQL statement.

        Args:
            statement (str): The SQL query or command to execute.

        Returns:
            Any: The result returned by the database driver.
        """
        raise NotImplementedError


class Simplifier(ToolchainDriver):
    """Abstract base class for result simplifiers in the toolchain.

    A Simplifier processes low-level results (e.g., raw database query results) into a higher-level, simplified
    representation. Subclasses must provide synchronous and/or asynchronous parsing methods.
    """

    def check_async(self) -> None:
        """Detect whether sync/async parse methods are implemented.

        Updates the ``is_sync`` and ``is_async`` flags by checking whether
        the subclass provides ``parse`` and/or ``aparse``.
        """
        self.is_sync = has_impl(Simplifier, self.__class__, "parse")
        self.is_async = has_impl(Simplifier, self.__class__, "aparse")

    def parse(self, low_level_result: Any) -> Any:
        """Synchronously simplify a low-level result.

        Args:
            low_level_result (Any): The raw result to be simplified.

        Returns:
            Any: The simplified result.
        """
        raise NotImplementedError

    def aparse(self, low_level_result: Any) -> Any:
        """Asynchronously simplify a low-level result.

        Args:
            low_level_result (Any): The raw result to be simplified.

        Returns:
            Any: The simplified result.
        """
        raise NotImplementedError
