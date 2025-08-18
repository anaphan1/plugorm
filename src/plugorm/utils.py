"""Utility helpers for drivers and toolchains.

Provides reusable mixins and helper functions to streamline logging and
implementation checks across steps and drivers.

has_impl:
    Check whether a subclass provides its own implementation of a method.

short_repr:
    Produce a short, human-readable string representation of an object.

LoggerMixin:
    Mixin providing standardized logging for start, success, and error events.
"""

import logging
from abc import ABC
from typing import Any


def has_impl(subclass: type[ABC], method_name: str) -> bool:
    """Checks whether a subclass implements a given abstract method.

    Determines if the provided method name has been implemented by inspecting the subclass's ``__abstractmethods__``
    attribute.

    Args:
        subclass (type[ABC]): The subclass to check.
        method_name (str): The abstract method name to verify.

    Returns:
        bool: ``True`` if the method is implemented, ``False`` otherwise.
    """
    return method_name not in getattr(subclass, "__abstractmethods__", set())


def short_repr(value: Any, max_len: int = 120) -> str:
    """Generates a shortened string representation of a value.

    Produces a truncated ``repr(value)`` if it exceeds the specified maximum length, appending ``...`` to indicate
    truncation. Useful for logging and debugging large or verbose objects.

    Args:
        value (Any): The object to represent as a string.
        max_len (int, optional): The maximum allowed length of the representation. Defaults to 120.

    Returns:
        str: The shortened string representation of the value.
    """
    text = repr(value)
    return text if len(text) <= max_len else text[:max_len] + "..."


class _LoggerMixin:
    """Mixin providing standardized logging helpers for actions.

    Adds methods to log the start, successful completion, and errors of operations, including automatic class name
    tagging and truncated representations of inputs and outputs.

    Attributes:
        logger (logging.Logger): Logger instance used for all logging methods.
    """

    logger: logging.Logger

    def _log_start(self, action: str, input_: Any) -> None:
        """Logs the start of an action.

        Args:
            action (str): Name or description of the action.
            input_ (Any): Input value associated with the action.
        """
        self.logger.debug(
            f"{self.__class__.__name__}: {action} | input={short_repr(input_)}"
        )

    def _log_ok(self, action: str, output: Any) -> None:
        """Logs the successful completion of an action.

        Args:
            action (str): Name or description of the action.
            output (Any): Output value produced by the action.
        """
        self.logger.debug(
            f"{self.__class__.__name__}: {action} succeeded | output={short_repr(output)}"
        )

    def _log_err(self, action: str, error: Exception) -> None:
        """Logs an error raised during an action.

        Args:
            action (str): Name or description of the action.
            error (Exception): Exception instance that was raised.
        """
        self.logger.error(
            f"{self.__class__.__name__}: {action} failed: {error}", exc_info=True
        )
