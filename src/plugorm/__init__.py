"""
Package initialization.

This module exposes the main components, including the core SurfaceDriver, driver interfaces, and the package version.

``SurfaceDriver``:
    High-level interface for building and running driver toolchains.
``ILDriver``:
    Abstract base class for internal language (IL) drivers.
``ConnectionDriver``:
    Abstract base class for database connection drivers.
``Simplifier``:
    Abstract base class for simplifying low-level results.

``__version__``:
    The current version of the package.
"""

from .core import SurfaceDriver
from .drivers import ILDriver, ConnectionDriver, Simplifier
from ._version import version as __version__

__all__ = ["SurfaceDriver", "ILDriver", "ConnectionDriver", "Simplifier", "__version__"]
