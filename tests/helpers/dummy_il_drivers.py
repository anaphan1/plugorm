from typing import Any

from plugorm import ILDriver


class DummySyncILDriver(ILDriver):
    def parse(self, internal_language: Any) -> str:
        return str(internal_language)


class DummyAsyncILDriver(ILDriver):
    async def aparse(self, internal_language: Any) -> str:
        return str(internal_language)


class DummySyncAsyncILDriver(ILDriver):
    def parse(self, internal_language: Any) -> str:
        return str(internal_language)

    async def aparse(self, internal_language: Any) -> str:
        return str(internal_language)
