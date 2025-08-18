"""Custom exception classes for drivers and toolchains.

This module defines all error types raised during parsing, execution, and toolchain operations. Errors are grouped by
their purpose, including internal language (IL) parsing, SQL dialect translation, execution failures, and result
simplification issues. It also includes validation and synchronous/asynchronous capability errors.

``LinkValidationError``:
    Raised when step input/output sets are incompatible.
``ILParsingError``:
    Raised when parsing the internal language fails.
``DialectParsingError``:
    Raised when converting IL to a SQL dialect fails.
``ExecutionError``:
    Raised when executing a SQL statement fails.
``SimplifyingError``:
    Raised when simplifying low-level results fails.
``NotAsyncError``:
    Raised when async execution is attempted but not supported.
``NotSyncError``:
    Raised when sync execution is attempted but not supported.
"""

class LinkValidationError(ValueError):
    """Exception raised when toolchain step linkage is invalid.

    This error occurs when the output types of one step are not compatible with the expected input types of the
    subsequent step.

    Attributes:
        source (str): The name of the step producing the output.
        target (str): The name of the step expecting compatible input.
        input_ (set[str]): The set of required input types for the target step.
        output (set[str]): The set of output types produced by the source step.
    """
    def __init__(
        self,
        source: str,
        target: str,
        input_: set[str],
        output: set[str],
    ) -> None:
        """Initialize a LinkValidationError.

        Args:
            source (str): The name of the step producing the output.
            target (str): The name of the step expecting compatible input.
            input_ (set[str]): The set of required input types for the target step.
            output (set[str]): The set of output types produced by the source step.
        """
        self.source = source
        self.target = target
        self.input_ = input_
        self.output = output
        super().__init__(
            f"{source} output ({output}) must be compatible with {target} input ({input_})."
        )


class ILParsingError(RuntimeError):
    """Raised when parsing the internal language (IL) fails."""


class DialectParsingError(RuntimeError):
    """Raised when translating dialect into an internal language (IL) dialect fails."""


class ExecutionError(RuntimeError):
    """Raised when execution of a SQL statement fails."""


class SimplifyingError(RuntimeError):
    """Raised when simplification of a low-level result into a higher-level form fails."""


class NotAsyncError(ValueError):
    """Raised when an asynchronous operation is attempted but the driver does not support async execution."""


class NotSyncError(ValueError):
    """Raised when a synchronous operation is attempted but the driver does not support sync execution."""
