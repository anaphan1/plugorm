from typing import Any

from plugorm import ConnectionDriver


class DummySyncConnDriver(ConnectionDriver):
    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def execute(self, statement: str) -> Any:
        return statement


class DummyAsyncConnDriver(ConnectionDriver):
    async def aconnect(self) -> None:
        pass

    async def aclose(self) -> None:
        pass

    async def aexecute(self, statement: str) -> Any:
        return statement


class DummySyncAsyncConnDriver(ConnectionDriver):
    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def execute(self, statement: str) -> Any:
        return statement

    async def aconnect(self) -> None:
        pass

    async def aclose(self) -> None:
        pass

    async def aexecute(self, statement: str) -> Any:
        return statement
