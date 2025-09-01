Introduction
============

Welcome to the PlugORM documentation! 🎉
This guide will help you get started with **using PlugORM** and show you how to **create custom drivers**.

What is PlugORM?
----------------
PlugORM is an **ORM base framework**. Unlike traditional ORMs, it does not ship with built-in syntax or database drivers.
Instead, it gives developers the freedom to **fully customize their ORM experience**:

- **Choose your own syntax** – define how queries should look.
- **Choose your SQL output** – generate queries for multiple SQL dialects from the same syntax.
- **Plug in drivers** – surface, internal language (IL), connection, and simplifier drivers.

This design allows you to write **one consistent syntax** while supporting **multiple SQL dialects**.

PlugORM Architecture
--------------------
PlugORM works in **four layers of drivers**:

1. **Surface Driver**
   - Defines the query syntax you interact with.
   - Can be traditional (like SQLAlchemy style) or entirely custom.

2. **Internal Language (IL) Driver**
   - Translates surface syntax into an intermediate representation.
   - Can then be compiled into one or more SQL dialects.
   - (Optional: surface drivers can output SQL directly without an IL driver.)

3. **Connection Driver**
   - Executes SQL queries against the database.
   - Manages opening and closing connections.

4. **Simplifier**
   - Converts raw results (e.g. SQLite cursors) into more convenient Python objects.

Getting Started
---------------
To use PlugORM, you’ll need to provide drivers. A typical setup looks like this:

.. code-block:: python

    driver = MySurfaceDriver(
        il_driver=MyIlDriver(),      # optional
        conn_driver=MyConnDriver(),  # required
        simplifier=MySimplifier()    # optional
    )

Running Queries
---------------
Once you’ve set up a driver, you can execute statements:

.. code-block:: python

    with driver as db:  # optional context alias
        result = db.select(  # example dialect
            c1 for c1, c2 in db.tables["c1", "c2"] if c1 + c2 == 10
        )

And that’s it—you’re running queries with PlugORM!

Next Steps
----------
- To learn how to **write your own custom drivers**, check out :doc:`driver_making`.

Future Plans
------------
- Add a metadata parameter to ``ToolchainDriver``'s methods to pass metadata through the toolchain
- Add migration support