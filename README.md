# PlugORM

[![PyPI version](https://img.shields.io/pypi/v/plugorm.svg)](https://pypi.org/project/plugorm/)
[![Python versions](https://img.shields.io/pypi/pyversions/plugorm.svg)](https://pypi.org/project/plugorm/)
[![License](https://img.shields.io/pypi/l/plugorm.svg)](https://github.com/yourname/plugorm/blob/main/LICENSE)

PlugORM is a **driver-first ORM framework** built around the concept of a **Surface Driver**.  
It unifies **parsing**, **execution**, and **simplification** into a single pipeline and gives you the tools to define your own ORM “surface.”

---

## ✨ Core Concepts

- **Surface Driver**  
  The main entrypoint. A surface driver wires together:
  - an **ILDriver** (internal language → dialect parser)
  - a **ConnectionDriver** (executes against a database or backend)
  - an optional **Simplifier** (post-processes raw results)

- **Intermediate Language (IL)**  
  Queries and schemas are translated into an **IL**, which is then consumed by the connection driver.

- **Toolchain**  
  Each driver becomes a step in a **sync** or **async** toolchain. Toolchains are validated and executed automatically.

- **Errors with Context**  
  Dedicated exceptions for link validation, parsing failures, execution errors, async/sync mismatches, and more.

---

## 🚀 Installation

```bash
pip install plugorm
```

## 🔧 Quick Example
Here’s how to define and run a surface driver:

```python
import logging
from plugorm import ILDriver, ConnectionDriver, Simplifier, SurfaceDriver

class MyIL(ILDriver):
    input_ = {"il"}
    output = {"sql"}
    def parse(self, il): ...

class MyConn(ConnectionDriver):
    input_ = {"sql"}
    output = {"raw"}
    def connect(self): ...
    def close(self): ...
    def execute(self, statement): ...

class MySimplifier(Simplifier):
    input_ = {"raw"}
    output = {"final"}
    def parse(self, rows): ...

class MySurfaceDriver(SurfaceDriver):
    input_ = {"pythonic"}
    output = {"il"}
    
    @SurfaceDriver.dialect
    def getall(self): ...
    
# Build surface
driver = MySurfaceDriver(
    conn_driver=MyConn(),
    il_driver=MyIL(),
    simplifier=MySimplifier(),
    logger=logging.getLogger("plugorm")
)

with driver as db:
    result = db.getall()
print(result)
```

## 🧩 Architecture

**Surface Driver -?> IL Driver -> Connection Driver -?> Simplifier**

Each driver must declare compatible input_ and output sets.
The surface driver validates these links before building toolchains.

⚡ Sync & Async Support
All drivers can be sync, async, or both.

If a driver only supports async, but you try to use it in a sync toolchain, NotSyncError is raised.

If a driver only supports sync, but you build an async toolchain, you can enable fallback=True to run it in a background thread.

```python
async with driver as db:
    result = await db.getall()
```