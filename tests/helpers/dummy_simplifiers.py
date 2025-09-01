from typing import Any

from plugorm import Simplifier


class DummySyncSimplifier(Simplifier):
    def parse(self, low_level_result: Any) -> str:
        return str(low_level_result)


class DummyAsyncSimplifier(Simplifier):
    async def aparse(self, low_level_result: Any) -> str:
        return str(low_level_result)


class DummySyncAsyncSimplifier(Simplifier):
    def parse(self, low_level_result: Any) -> str:
        return str(low_level_result)

    async def aparse(self, low_level_result: Any) -> str:
        return str(low_level_result)
