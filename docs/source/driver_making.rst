Making Your Own Drivers
======================

PlugORM (Coatl) is designed to be fully extensible. You can create your own drivers
for user interface, internal language (IL) parsing, database connections, or result simplification.
This guide explains how to implement custom drivers and integrate them with ``SurfaceDriver``.

Driver Types
------------

PlugORM supports four main types of drivers:

1. **ILDriver**: Converts your internal language into a dialect or SQL statement.
2. **ConnectionDriver**: Executes statements against a backend (database, API, etc.).
3. **Simplifier**: Processes raw results from a connection into a simplified form.

All drivers inherit from the base ``Driver`` class. Toolchain drivers (IL drivers and up) inherit from
``ToolchainDriver``, which provides automatic async detection.

Common Concepts
---------------

Each driver has:

- ``input_``: A set of strings representing the accepted input types.
- ``output``: A set of strings representing the produced output types.
- ``is_sync`` / ``is_async``: Booleans indicating synchronous or asynchronous support.

Async Support
~~~~~~~~~~~~~

Drivers can optionally support asynchronous execution. Methods for async toolchain drivers
are prefixed with ``a`` (e.g., ``aparse`` for ILDriver and Simplifier, ``aconnect``, ``aexecute``, ``aclose`` for ConnectionDriver).

If async is not implemented, drivers can optionally fall back to running sync
methods in a thread when ``fallback=True``.

Creating a Surface Driver
-------------------------

A ``SurfaceDriver`` converts the dialect either to raw SQL or to an internal language. User-facing methods are decorated with ``SurfaceDriver.dialect`` or ``SurfaceDriver.adialect`` for sync and async versions respectively.

.. code-block:: python

    from plugorm import SurfaceDriver

    class MySurfaceDriver(SurfaceDriver):

        input_ = {"input_example_1", "input_example_2"}
        output = {"output_example_1"}

        @SurfaceDriver.dialect
        def get_all(self):
            return [i for i in self.db.tables.select()] # Example implementation

        @SurfaceDriver.adialect
        async def aget_all(self):
            return [i for i in await self.db.tables.aselect()]

Creating an IL Driver
--------------------

An ``ILDriver`` converts your internal language into SQL or another backend dialect.

.. code-block:: python

    from plugorm import ILDriver

    class MyILDriver(ILDriver):

        input_ = {"input_example_1", "input_example_2"}
        output = {"sqlite"}

        def parse(self, internal_language: str) -> str:
            # Convert internal representation to SQL
            return f"SELECT * FROM {internal_language}"

        async def aparse(self, internal_language: str) -> str:
            # Optional async implementation
            return self.parse(internal_language)

Creating a Connection Driver
----------------------------

A ``ConnectionDriver`` manages database connections to your database and executes queries

.. code-block:: python

    from plugorm import ConnectionDriver

    class MyConnDriver(ConnectionDriver):

        input_ = {"sqlite"}
        output = {"sqlite_cursor"}

        def connect(self): ... # Connect to database instance
        def execute(self, statement: str): ... # Execute a statement
        def close(self): ... # Close database instance

        # Optional async versions of above 3 methods
        async def aconnect(self): ...
        async def aexecute(self, statement): ...
        async def aclose(self): ...

Creating a Simplifier
--------------------

A ``Simplifier`` converts your cursor or some low-level form of data to a high-level one

.. code-block:: python

    from plugorm import Simplifier

    class MySimplifier(Simplifier):

        input_ = {"sqlite_cursor", "pg_cursor"}
        output = {"pythonic"}

        def parse(self, cursor: Any) -> Any:
            # Convert cursor to a python object
            return cursor.fetchall()

        async def aparse(self, cursor: Any) -> Any:
            # Optional async implementation
            return self.parse(cursor)