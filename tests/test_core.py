import logging

import pytest

from plugorm import SurfaceDriver, ILDriver, Simplifier, ConnectionDriver
from plugorm.errors import (
    LinkValidationError,
    NotSyncError,
    NotAsyncError,
    DialectParsingError,
    ILParsingError,
    SimplifyingError,
    ExecutionError,
)
from plugorm.toolchain import SimplifierStep, ILStep, ConnectionStep
from tests.helpers.dummy_conn_drivers import DummySyncConnDriver
from tests.helpers.dummy_sets import SET_1, SET_3
from tests.helpers.dummy_surface_drivers import DummySyncSurfaceDriver


@pytest.mark.parametrize("input_,output", [(SET_1, SET_3), (SET_3, SET_1)])
def test_validation_surface_driver(
    input_, output, sync_il_driver, sync_conn_driver, sync_simplifier
):
    compatible = True

    if sync_il_driver is not None:
        if sorted([output, sync_il_driver.input_]) == sorted(
            [SET_1, SET_3]
        ):  # Non overlapping combination
            compatible = False
        elif sorted([sync_il_driver.output, sync_conn_driver.input_]) == sorted(
            [SET_1, SET_3]
        ):
            compatible = False
    else:
        if sorted([output, sync_conn_driver.input_]) == sorted([SET_1, SET_3]):
            compatible = False

    if sync_simplifier is not None:
        if sorted([sync_conn_driver.output, sync_simplifier.input_]) == sorted(
            [SET_1, SET_3]
        ):
            compatible = False

    if not compatible:
        with pytest.raises(LinkValidationError):
            DriverClass = type(
                "DriverClass",
                (DummySyncSurfaceDriver,),
                {"input_": input_, "output": output},
            )
            DriverClass(
                il_driver=sync_il_driver,
                conn_driver=sync_conn_driver,
                simplifier=sync_simplifier,
            )


def test_sync_surface_driver_runs(sync_surface_driver):
    """This will be run for every compatible combination."""
    # surface_driver is already constructed and validated
    input_ = "input"
    with sync_surface_driver:
        result = sync_surface_driver.run_toolchain(input_)
    assert result == input_


async def test_async_surface_driver_runs(async_surface_driver):
    """This will be run for every compatible combination."""
    input_ = "input"
    async with async_surface_driver:
        result = await async_surface_driver.arun_toolchain(input_)
    assert result == input_


async def test_random_surface_driver_build_toolchain_with_fallback(
    random_surface_driver,
):
    if random_surface_driver.is_async:
        random_surface_driver.build_async_toolchain()
    elif random_surface_driver.is_sync:
        with pytest.raises(NotSyncError):
            random_surface_driver.build_sync_toolchain()


async def test_random_surface_driver_build_toolchain_no_fallback(random_surface_driver):
    random_surface_driver.fallback = False
    if random_surface_driver.is_async:
        with pytest.raises(NotAsyncError):
            random_surface_driver.build_async_toolchain()
    elif random_surface_driver.is_sync:
        with pytest.raises(NotSyncError):
            random_surface_driver.build_sync_toolchain()


def test_both_surface_driver_runs_sync(both_surface_driver):
    input_ = "input"
    with both_surface_driver:
        result = both_surface_driver.run_toolchain(input_)
    assert result == input_


async def test_both_surface_driver_runs_async(both_surface_driver):
    input_ = "input"
    async with both_surface_driver:
        result = both_surface_driver.run_toolchain(input_)
    assert result == input_


def test_dialect_wrapper_success():
    class MyDriver(SurfaceDriver):
        input_ = {"e"}
        output = {"e"}

        @SurfaceDriver.dialect
        def hello(self, x):
            return x.upper()

    driver = DummySyncConnDriver()
    driver.input_ = {"e"}
    driver.output = {"e"}

    d = MyDriver(conn_driver=driver)
    assert d.hello("hi") == "HI"


def test_dialect_wrapper_failure():
    class MyDriver(SurfaceDriver):
        input_ = {"e"}
        output = {"e"}

        @SurfaceDriver.dialect
        def broken(self, x):
            raise ValueError("bad")

    driver = DummySyncConnDriver()
    driver.input_ = {"e"}
    driver.output = {"e"}

    d = MyDriver(conn_driver=driver)
    with pytest.raises(DialectParsingError):
        d.broken("oops")


async def test_adialect_wrapper_failure():
    class MyDriver(SurfaceDriver):
        input_ = {"e"}
        output = {"e"}

        @SurfaceDriver.adialect
        async def broken(self, x):
            raise ValueError("bad")

    driver = DummySyncConnDriver()
    driver.input_ = {"e"}
    driver.output = {"e"}

    d = MyDriver(conn_driver=driver)
    with pytest.raises(DialectParsingError):
        await d.broken("oops")


def test_ildriver_failure():
    class MyDriver(ILDriver):
        input_ = {"e"}
        output = {"e"}

        def parse(self, input_):
            raise ValueError("bad")

    driver = MyDriver()
    step = ILStep(driver, logger=logging.getLogger(__name__))
    with pytest.raises(ILParsingError):
        step.step("oops")


async def test_aildriver_failure():
    class MyDriver(ILDriver):
        input_ = {"e"}
        output = {"e"}

        async def aparse(self, input_):
            raise ValueError("bad")

    driver = MyDriver()
    step = ILStep(driver, logger=logging.getLogger(__name__))
    with pytest.raises(ILParsingError):
        await step.astep("oops")


def test_conndriver_failure():
    class MyDriver(ConnectionDriver):
        input_ = {"e"}
        output = {"e"}

        def connect(self) -> None:
            pass

        def close(self) -> None:
            pass

        def execute(self, input_):
            raise ValueError("bad")

    driver = MyDriver()
    step = ConnectionStep(driver, logger=logging.getLogger(__name__))
    with pytest.raises(ExecutionError):
        step.step("oops")


async def test_aconndriver_failure():
    class MyDriver(ConnectionDriver):
        input_ = {"e"}
        output = {"e"}

        async def aconnect(self):
            pass

        async def aclose(self):
            pass

        async def aexecute(self, input_):
            raise RuntimeError("bad")

    driver = MyDriver()
    step = ConnectionStep(driver, logger=logging.getLogger(__name__))
    with pytest.raises(ExecutionError):
        await step.astep("oops")


def test_simplifier_failure():
    class MyDriver(Simplifier):
        input_ = {"e"}
        output = {"e"}

        def parse(self, input_):
            raise ValueError("bad")

    driver = MyDriver()
    step = SimplifierStep(driver, logger=logging.getLogger(__name__))
    with pytest.raises(SimplifyingError):
        step.step("oops")


async def test_asimplfier_failure():
    class MyDriver(Simplifier):
        input_ = {"e"}
        output = {"e"}

        async def aparse(self, input_):
            raise ValueError("bad")

    driver = MyDriver()
    step = SimplifierStep(driver, logger=logging.getLogger(__name__))
    with pytest.raises(SimplifyingError):
        await step.astep("oops")
