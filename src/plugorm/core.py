"""Core module containing the ``SurfaceDriver`` class.

This module contains the ``SurfaceDriver`` class, an abstract base class responsible for being the base class developers
subclass to create a dialect driver while also providing core functionality of the package.

SurfaceDriver:
    Abstract base class for managing and running driver toolchains.
"""

import asyncio
import logging
from collections.abc import Callable, Awaitable
from functools import wraps
from typing import Any

from .drivers import Driver, ConnectionDriver, ILDriver, Simplifier
from .errors import (
    LinkValidationError,
    DialectParsingError,
    NotAsyncError,
    NotSyncError,
)
from .toolchain import ILStep, ConnectionStep, SimplifierStep, Step
from .utils import short_repr


class SurfaceDriver(Driver):
    """Abstract base class for a surface driver managing multiple components.

    A ``SurfaceDriver`` orchestrates the execution of connected drivers, including a mandatory connection driver, an
    optional internal language driver, and an optional simplifier. It supports building and running both synchronous and
    asynchronous toolchains, with optional fallback mechanisms for handling async/sync mismatches.

    Attributes:
        conn_driver (ConnectionDriver): The primary connection driver.
        il_driver (ILDriver | None): Optional internal language driver.
        simplifier (Simplifier | None): Optional simplifier for post-processing.
        logger (logging.Logger): Logger instance for debugging and info messages.
        sync_toolchain (list[SyncStep]): Ordered list of synchronous steps.
        async_toolchain (list[AsyncStep]): Ordered list of asynchronous steps.
        fallback (bool): Enables fallback between sync and async execution when a step does not natively support the
            requested mode.
    """

    conn_driver: ConnectionDriver
    il_driver: ILDriver | None
    simplifier: Simplifier | None
    logger: logging.Logger
    sync_toolchain: list[Callable[[Any], Any]]
    async_toolchain: list[Callable[[Any], Awaitable[Any]]]
    fallback: bool

    def __init__(
        self,
        conn_driver: ConnectionDriver,
        il_driver: ILDriver | None = None,
        simplifier: Simplifier | None = None,
        logger: logging.Logger | None = None,
        fallback: bool = False,
    ) -> None:
        """Initializes a SurfaceDriver with its component drivers.

        Sets up the connection driver, optional internal language driver, optional simplifier, and logger. Performs
        initial validation of driver linkages.

        Args:
            conn_driver (ConnectionDriver): The primary connection driver.
            il_driver (ILDriver | None, optional): Optional internal language driver. Defaults to None.
            simplifier (Simplifier | None, optional): Optional simplifier for post-processing. Defaults to None.
            logger (logging.Logger | None, optional): Logger instance to use. Defaults to a logger named after the class.
            fallback (bool, optional): If True, allows sync steps to be wrapped in threaded async fallbacks when
                executing toolchains. Defaults to False.
        """
        self.fallback = fallback
        self.conn_driver = conn_driver
        self.il_driver = il_driver
        self.simplifier = simplifier
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        self.sync_toolchain = []
        self.async_toolchain = []

        self._validate()

    # -------------------------
    # Validation
    # -------------------------

    def _validate(self):
        """Validates the linkages between the surface, internal language, connection, and simplifier drivers.

        This method checks the compatibility between the input/output interfaces of the configured drivers. If an
        internal language driver ``il_driver`` is present, the validation ensures the surface driver connects to it, and
        it connects to the connection driver. Otherwise, the surface driver connects directly to the connection driver.
        If a simplifier is present, the connection driver is also validated against it.
        """
        if self.il_driver is not None:
            self.validate_link(
                repr(self),
                repr(self.il_driver),
                self.output,
                self.il_driver.input_,
            )

            self.validate_link(
                repr(self.il_driver),
                repr(self.conn_driver),
                self.il_driver.output,
                self.conn_driver.input_,
            )

        else:
            self.validate_link(
                repr(self),
                repr(self.conn_driver),
                self.output,
                self.conn_driver.input_,
            )

        if self.simplifier is not None:
            self.validate_link(
                repr(self.conn_driver),
                repr(self.simplifier),
                self.conn_driver.output,
                self.simplifier.input_,
            )

    def validate_link(
        self,
        source_name: str,
        target_name: str,
        source_output: set[str],
        target_input: set[str],
    ) -> None:
        """Validates compatibility between two driver components.

        This method ensures that the output types of a source driver overlap with the input types of a target driver. If
        no overlap exists, the validation fails and a ``LinkValidationError`` is raised.

        Args:
            source_name (str): Human-readable name of the source driver.
            target_name (str): Human-readable name of the target driver.
            source_output (set[str]): The possible output types of the source driver.
            target_input (set[str]): The expected input types of the target driver.

        Raises:
            LinkValidationError: If the source and target driver types are incompatible (no overlapping elements).
        """
        self.logger.debug(f"Detected link between {source_name} and {target_name}")
        if source_output.isdisjoint(target_input):
            self.logger.error(
                f"No overlap found between {source_name} output possibilities ({source_output}) "
                f"and {target_name} input ({target_input})"
            )
            raise LinkValidationError(
                source=source_name,
                target=target_name,
                output=source_output,
                input_=target_input,
            )
        self.logger.debug(
            f"Link between {source_name} and {target_name} passed validation"
        )

    # -------------------------
    # Toolchain operations
    # -------------------------

    def reset_toolchains(self):
        """Resets both sync and async toolchains.

        Clears the internal lists that store the synchronous and asynchronous toolchains. This effectively removes any
        previously built steps.
        """
        self.sync_toolchain = []
        self.logger.debug("Reset sync toolchain")
        self.async_toolchain = []
        self.logger.debug("Reset async toolchain")

    def build_toolchains(self):
        """Builds both sync and async toolchains.

        Calls the internal builder methods to populate the synchronous and asynchronous toolchains with their respective
        steps.
        """
        self.logger.debug("Building both toolchains")
        self.build_sync_toolchain()
        self.build_async_toolchain()

    def build_sync_toolchain(self):
        """Builds the synchronous toolchain.

        Invokes the internal ``_build_toolchain`` with ``allow_async=False`` to construct the sync-only sequence of
        steps and stores it in ``self.sync_toolchain``.
        """
        self.logger.debug("Building sync toolchain")
        self.sync_toolchain = self._build_toolchain(allow_async=False)
        self.logger.debug(short_repr(f"Built sync toolchain: {self.sync_toolchain}"))

    def build_async_toolchain(self):
        """Builds the asynchronous toolchain.

        Invokes the internal ``_build_toolchain`` with ``allow_async=True`` to construct the async-capable sequence of
        steps and stores it in ``self.async_toolchain``.
        """
        self.logger.debug("Building async toolchain")
        self.async_toolchain = self._build_toolchain(allow_async=True)
        self.logger.debug(short_repr(f"Built async toolchain: {self.async_toolchain}"))

    def _build_toolchain(self, allow_async: bool):
        """Constructs and configures the execution toolchain.

        Builds an ordered sequence of steps (internal language, connection, and optional simplifier) based on the
        configured drivers. Each step is returned as either a synchronous or asynchronous callable, depending on
        ``allow_async`` and the capabilities of the underlying driver.

        Args:
            allow_async (bool): If ``True``, build an async-capable toolchain. Steps must be async-native or, if
                ``self.fallback`` is enabled, will be wrapped into a threaded async fallback. If ``False``, only
                sync-capable steps are allowed.

        Returns:
            list[Callable]: The ordered list of step callables forming the toolchain.

        Raises:
            NotAsyncError: If ``allow_async=True`` and a step is not async-capable while fallback is disabled.
            NotSyncError: If ``allow_async=False`` and a step is async-only.
        """
        steps: list[Step] = [ConnectionStep(self.conn_driver, self.logger)]

        if self.il_driver is not None:
            self.logger.debug(
                short_repr(f"Detected and adding IL Driver {self.il_driver}")
            )
            steps.insert(0, ILStep(self.il_driver, self.logger))

        if self.simplifier is not None:
            self.logger.debug(
                short_repr(f"Detected and adding Simplifier {self.simplifier}")
            )
            steps.append(SimplifierStep(self.simplifier, self.logger))

        def pick(step):
            if allow_async:
                if step.driver.is_async:
                    return step.astep
                elif self.fallback:

                    async def func(input_):
                        self.logger.warning(
                            short_repr(
                                f"Modifying {step} execution to threaded async fallback."
                            )
                        )
                        return await asyncio.to_thread(step.step, input_)

                    return func
                else:
                    self.logger.error(
                        short_repr(f"{step} is not async and fallback is disabled")
                    )
                    raise NotAsyncError(
                        f"{step} is not async-capable and fallback is disabled"
                    )
            else:
                if step.driver.is_sync:
                    return step.step
                else:
                    self.logger.error(short_repr(f"{step} is async-only"))
                    raise NotSyncError(f"{step} is async-only")

        return [pick(step) for step in steps]

    # -------------------------
    # Sync lifecycle
    # -------------------------

    def __enter__(self) -> "SurfaceDriver":
        """Enter the context manager (synchronous mode).

        Ensures that the synchronous toolchain is available and connects the driver before returning itself. If the sync
        toolchain has not yet been built, it will be constructed lazily at this point.

        Returns:
            SurfaceDriver: The current instance, ready for use inside a ``with`` block.
        """
        self.logger.debug("Entering context manager (sync)")
        if (
            len(self.sync_toolchain) == 0
        ):  # Lazy build: construct sync toolchain only when needed
            self.logger.debug("No sync toolchain detected")
            self.build_sync_toolchain()
        self.connect()
        return self

    def connect(self) -> None:
        """Establishes a synchronous connection.

        Calls ``connect()`` on the connection driver if it supports synchronous operation. Raises an error if the driver
        is async-only.

        Raises:
            NotSyncError: If the connection driver is async-only.
        """
        self.logger.debug("Connecting (sync)")
        if self.conn_driver.is_sync:
            self.conn_driver.connect()
        else:
            self.logger.error(short_repr(f"{self.conn_driver} is async-only"))
            raise NotSyncError(f"{self.conn_driver} is async-only")

    def run_toolchain(self, value: Any) -> Any:
        """Executes the synchronous toolchain.

        Runs the configured sync toolchain steps sequentially, passing the output of each step as the input to the next.

        Args:
            value (Any): The initial input passed to the first step.

        Returns:
            Any: The final result after all steps have been executed.
        """
        self.logger.info("Running sync toolchain")
        result = value
        for i, step in enumerate(self.sync_toolchain, start=1):
            self.logger.debug(short_repr(f"[sync step {i}] {step}"))
            result = step(result)
        self.logger.info("Sync toolchain finished")
        return result

    def close(self) -> None:
        """Closes the synchronous connection.

        Calls ``close()`` on the connection driver if it supports synchronous operation. Raises an error if the driver
        is async-only.

        Raises:
            NotSyncError: If the connection driver is async-only.
        """
        self.logger.debug("Closing (sync)")
        if self.conn_driver.is_sync:
            self.conn_driver.close()
        else:
            self.logger.error(short_repr(f"{self.conn_driver} is async-only"))
            raise NotSyncError(f"{self.conn_driver} is async-only")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit the context manager (synchronous mode).

        Closes the connection driver when leaving a ``with`` block, regardless of whether an exception occurred.

        Args:
            exc_type (type[BaseException] | None): The type of the exception raised within the block, if any.
            exc_val (BaseException | None): The exception instance raised within the block, if any.
            exc_tb (object | None): The traceback associated with the exception, if any.
        """
        self.logger.debug("Exiting context manager (sync)")
        self.close()

    # -------------------------
    # Async lifecycle
    # -------------------------

    async def __aenter__(self) -> "SurfaceDriver":
        """Enter the context manager (asynchronous mode).

        Ensures that the asynchronous toolchain is available and connects the driver before returning itself. If the
        async toolchain has not yet been built, it will be constructed lazily at this point.

        Returns:
            SurfaceDriver: The current instance, ready for use inside an ``async with`` block.
        """
        self.logger.debug("Entered context manager (async)")
        if (
            len(self.async_toolchain) == 0
        ):  # Lazy build: construct async toolchain only when needed
            self.logger.debug("No async toolchain detected")
            self.build_async_toolchain()
        await self.aconnect()
        return self

    async def aconnect(self) -> None:
        """Establishes an asynchronous connection.

        Calls ``aconnect()`` on the connection driver if it supports  asynchronous operation. If not, falls back to
        threaded sync execution if enabled.

        Raises:
            NotAsyncError: If the connection driver is not async-capable and fallback is disabled.
        """
        self.logger.debug("Connecting (async)")
        if self.conn_driver.is_async:
            await self.conn_driver.aconnect()
        elif self.fallback:
            self.logger.warning("Falling back to threaded async connection")
            await asyncio.to_thread(self.connect)
        else:
            self.logger.error(
                short_repr(f"Cannot asynchronously connect with {self.conn_driver}")
            )
            raise NotAsyncError(
                f"{self.conn_driver} is not async-capable and fallback is disabled"
            )

    async def arun_toolchain(self, value: Any) -> Any:
        """Executes the asynchronous toolchain.

        Runs the configured async toolchain steps sequentially, awaiting the result of each step before passing it to
        the next.

        Args:
            value (Any): The initial input passed to the first step.

        Returns:
            Any: The final result after all steps have been executed.
        """
        self.logger.debug("Running async toolchain")
        result = value
        for i, step in enumerate(self.async_toolchain, start=1):
            self.logger.debug(short_repr(f"[async step {i}] {step}"))
            result = await step(result)
        self.logger.info("Async toolchain finished")
        return result

    async def aclose(self) -> None:
        """Closes the asynchronous connection.

        Calls ``aclose()`` on the connection driver if it supports asynchronous operation. If not, falls back to
        threaded sync execution if enabled.

        Raises:
            NotAsyncError: If the connection driver is not async-capable and fallback is disabled.
        """
        self.logger.debug("Closing (async)")
        if self.conn_driver.is_async:
            await self.conn_driver.aclose()
        elif self.fallback:
            self.logger.warning("Falling back to threaded async connection")
            await asyncio.to_thread(self.close)
        else:
            self.logger.error(short_repr(f"Cannot close async {self.conn_driver}"))
            raise NotAsyncError(
                f"Cannot asynchronously close connection with {self.conn_driver}"
            )

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit the context manager (asynchronous mode).

        Closes the connection driver when leaving an ``async with`` block, regardless of whether an exception occurred.

        Args:
            exc_type (type[BaseException] | None): The type of the exception raised within the block, if any.
            exc_val (BaseException | None): The exception instance raised within the block, if any.
            exc_tb (object | None): The traceback associated with the exception, if any.
        """

        self.logger.debug("Exiting context manager (async)")
        await self.aclose()

    # -------------------------
    # Toolchain starter methods
    # -------------------------

    @staticmethod
    def dialect(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator for synchronous dialect parsing.

        Wraps a function that produces a dialect representation, ensuring that any exceptions raised during parsing are
        caught and re-raised as ``DialectParsingError``. After parsing, the result is executed through the synchronous
        toolchain.

        Args:
            func (Callable[..., Any]): A function that parses and returns a dialect representation.

        Returns:
            Callable[..., Any]: A wrapped function that validates parsing and runs the result through the sync
                toolchain.

        Raises:
            DialectParsingError: If the wrapped function fails to parse.
        """

        @wraps(func)
        def wrapper(self: SurfaceDriver, *args: Any, **kwargs: Any) -> Any:
            self.logger.debug("Parsing dialect synchronously")
            try:
                parsed_dialect = func(self, *args, **kwargs)
            except Exception as e:
                self.logger.error("Failed to parse dialect")
                raise DialectParsingError("Failed to parse dialect") from e
            return self.run_toolchain(parsed_dialect)

        return wrapper

    @staticmethod
    def adialect(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        """Decorator for asynchronous dialect parsing.

        Wraps a coroutine function that produces a dialect representation, ensuring that any exceptions raised during
        parsing are caught and re-raised as ``DialectParsingError``. After parsing, the result is executed through the
        asynchronous toolchain.

        Args:
            func (Callable[..., Awaitable[Any]]): An async function that parses and returns a dialect representation.

        Returns:
            Callable[..., Awaitable[Any]]: A wrapped coroutine function that validates parsing and runs the result
                through the async toolchain.

        Raises:
            DialectParsingError: If the wrapped function fails to parse.
        """

        @wraps(func)
        async def wrapper(self: SurfaceDriver, *args: Any, **kwargs: Any) -> Any:
            self.logger.debug("Parsing dialect asynchronously")
            try:
                parsed_dialect = await func(self, *args, **kwargs)
            except Exception as e:
                self.logger.error("Failed to parse dialect")
                raise DialectParsingError("Failed to parse dialect") from e
            return await self.arun_toolchain(parsed_dialect)

        return wrapper
