"""Toolchain step definitions.

This module defines the building blocks of a toolchain, where each step wraps a driver or processor (internal language
driver, connection driver, or simplifier) and provides both synchronous and asynchronous execution methods with
integrated logging for start, success, and error events.

Step:
    Base class for toolchain steps that resolves the underlying driver.

ILStep:
    Wraps an internal language driver for parsing input into SQL dialects.

ConnectionStep:
    Wraps a connection driver for executing SQL statements.

SimplifierStep:
    Wraps a simplifier for post-processing and simplifying results.
"""

import logging
from typing import Any

from .drivers import ILDriver, ConnectionDriver, Simplifier, Driver
from .errors import ExecutionError, SimplifyingError, ILParsingError
from .utils import _LoggerMixin


class Step:
    """Represents a single step in a driver toolchain.

    Each `Step` wraps a driver component (internal language driver, connection driver, or simplifier) and provides
    access to the underlying driver instance for execution.

    Attributes:
        driver (Driver): The driver associated with this step.
    """

    def __init__(self) -> None:
        """Initializes the Step and assigns its driver.

        Automatically selects the appropriate driver from the instance attributes: `il_driver`, `conn_driver`, or
            `simplifier`.
        """
        self.driver = self.get_driver()

    def get_driver(self) -> Driver:
        """Retrieves the associated driver for this step.

        Cycles through possible names for the driver to retrieve the associated driver for this step.

        Returns:
            Driver: The driver instance linked to this step. Selection order is: `il_driver`, then `conn_driver`, then
                `simplifier`.
        """
        return getattr(
            self, "il_driver", getattr(self, "conn_driver", getattr(self, "simplifier"))
        )

    def __repr__(self) -> str:
        """Return a string representation of the Step.

        Includes the class name and indicates whether the underlying driver supports synchronous and asynchronous
        execution.

        Returns:
            str: A string representation of the Step instance.
        """
        return f"<{self.__class__.__name__}(is_sync={self.driver.is_sync}, is_async={self.driver.is_async})>"


class ILStep(Step, _LoggerMixin):
    """Step wrapping an internal language (IL) driver in a toolchain.

    Provides synchronous and asynchronous parsing methods with integrated logging for start, success, and error events.

    Attributes:
        il_driver (ILDriver): The internal language driver wrapped by this step.
        logger (logging.Logger): Logger instance for logging step events.
    """

    def __init__(self, il_driver: ILDriver, logger: logging.Logger):
        """Initializes an ILStep with the given internal language driver.

        Args:
            il_driver (ILDriver): The internal language driver to be wrapped by this step.
            logger (logging.Logger): Logger instance used for debug and info messages within this step.
        """
        super().__init__()
        self.il_driver = il_driver
        self.logger = logger

    def step(self, input_: Any) -> str:
        """Synchronously parses input using the internal language driver.

        Logs the start, success, or failure of the parsing operation.

        Args:
            input_ (Any): The input data to parse.

        Returns:
            str: The parsed internal language representation.

        Raises:
            ILParsingError: If the internal language driver fails to parse the input.
        """
        self._log_start("parse (sync)", input_)
        try:
            parsed_il = self.il_driver.parse(input_)
            self._log_ok("parse (sync)", parsed_il)
            return parsed_il
        except Exception as e:
            self._log_err("parse (sync)", e)
            raise ILParsingError("Failed to parse internal language") from e

    async def astep(self, input_: Any) -> str:
        """Asynchronously parses input using the internal language driver.

        Logs the start, success, or failure of the parsing operation.

        Args:
            input_ (Any): The input data to parse.

        Returns:
            str: The parsed internal language representation.

        Raises:
            ILParsingError: If the internal language driver fails to parse the input asynchronously.
        """
        self._log_start("parse (async)", input_)
        try:
            parsed_dialect = await self.il_driver.aparse(input_)
            self._log_ok("parse (async)", parsed_dialect)
            return parsed_dialect
        except Exception as e:
            self._log_err("parse (async)", e)
            raise ILParsingError("Failed to parse dialect") from e


class ConnectionStep(Step, _LoggerMixin):
    """Step wrapping a connection driver in a toolchain.

    Provides synchronous and asynchronous execution methods, with integrated logging for start, success, and error
    events.

    Attributes:
        connection_driver (ConnectionDriver): The connection driver  wrapped by this step.
        logger (logging.Logger): Logger instance for logging step events.
    """

    def __init__(self, connection_driver: ConnectionDriver, logger: logging.Logger):
        """Initializes a ConnectionStep with the given connection driver.

        Args:
            connection_driver (ConnectionDriver): The connection driver to be wrapped by this step.
            logger (logging.Logger): Logger instance used for debug and info messages within this step.
        """
        super().__init__()
        self.connection_driver = connection_driver
        self.logger = logger

    def step(self, input_: str) -> Any:
        """Synchronously executes a statement using the connection driver.

        Logs the start, success, or failure of the execution.

        Args:
            input_ (str): The SQL statement or command to execute.

        Returns:
            Any: The result of executing the statement.

        Raises:
            ExecutionError: If the connection driver fails to execute the statement.
        """
        self._log_start("execute (sync)", input_)
        try:
            result = self.connection_driver.execute(input_)
            self._log_ok("execute (sync)", result)
            return result
        except Exception as e:
            self._log_err("execute (sync)", e)
            raise ExecutionError("Failed to execute SQL statement") from e

    async def astep(self, input_: str) -> Any:
        """Asynchronously executes a statement using the connection driver.

        Logs the start, success, or failure of the execution.

        Args:
            input_ (str): The SQL statement or command to execute.

        Returns:
            Any: The result of executing the statement.

        Raises:
            ExecutionError: If the connection driver fails to execute the statement asynchronously.
        """
        self._log_start("execute (async)", input_)
        try:
            result = await self.connection_driver.aexecute(input_)
            self._log_ok("execute (async)", result)
            return result
        except Exception as e:
            self._log_err("execute (async)", e)
            raise ExecutionError("Failed to execute SQL statement") from e


class SimplifierStep(Step, _LoggerMixin):
    """Step wrapping a simplifier in a toolchain.

    Provides synchronous and asynchronous simplification methods, with integrated logging for start, success, and error
    events.

    Attributes:
        simplifier (Simplifier): The simplifier wrapped by this step.
        logger (logging.Logger): Logger instance for logging step events.
    """

    def __init__(self, simplifier: Simplifier, logger: logging.Logger):
        """Initializes a SimplifierStep with the given simplifier.

        Args:
            simplifier (Simplifier): The simplifier to be wrapped by this step.
            logger (logging.Logger): Logger instance used for debug and info messages within this step.
        """
        super().__init__()
        self.simplifier = simplifier
        self.logger = logger

    def step(self, input_: Any) -> Any:
        """Synchronously simplifies input using the simplifier.

        Logs the start, success, or failure of the simplification operation.

        Args:
            input_ (Any): The input data to simplify.

        Returns:
            Any: The simplified output.

        Raises:
            SimplifyingError: If the simplifier fails to process the input.
        """
        self._log_start("simplify (sync)", input_)
        try:
            final_result = self.simplifier.parse(input_)
            self._log_ok("simplify (sync)", final_result)
            return final_result
        except Exception as e:
            self._log_err("simplify (sync)", e)
            raise SimplifyingError("Failed to simplify result") from e

    async def astep(self, input_: Any) -> Any:
        """Asynchronously simplifies input using the simplifier.

        Logs the start, success, or failure of the simplification operation.

        Args:
            input_ (Any): The input data to simplify.

        Returns:
            Any: The simplified output.

        Raises:
            SimplifyingError: If the simplifier fails to process the input asynchronously.
        """
        self._log_start("simplify (async)", input_)
        try:
            final_result = await self.simplifier.aparse(input_)
            self._log_ok("simplify (async)", final_result)
            return final_result
        except Exception as e:
            self._log_err("simplify (async)", e)
            raise SimplifyingError("Failed to simplify result") from e
