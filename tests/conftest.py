import pytest

from tests.helpers.dummy_surface_drivers import (
    DummySyncSurfaceDriver,
    DummyAsyncSurfaceDriver,
    DummySyncAsyncSurfaceDriver,
)
from tests.helpers.dummy_il_drivers import (
    DummySyncILDriver,
    DummyAsyncILDriver,
    DummySyncAsyncILDriver,
)
from tests.helpers.dummy_conn_drivers import (
    DummySyncConnDriver,
    DummyAsyncConnDriver,
    DummySyncAsyncConnDriver,
)
from tests.helpers.dummy_simplifiers import (
    DummySyncSimplifier,
    DummyAsyncSimplifier,
    DummySyncAsyncSimplifier,
)
from tests.helpers.dummy_sets import (
    combinations,
    combinations_with_flag,
    combinations_with_flag_syncasync,
)

# -----------------
# Sync Tests
# -----------------


@pytest.fixture(params=combinations_with_flag)
def sync_il_driver(request):
    use, (input_, output) = request.param
    if use:
        DriverClass = type(
            "DriverClass", (DummySyncILDriver,), {"input_": input_, "output": output}
        )
        driver = DriverClass()
        return driver
    else:
        return None


@pytest.fixture(params=combinations)
def sync_conn_driver(request):
    input_, output = request.param
    DriverClass = type(
        "DriverClass", (DummySyncConnDriver,), {"input_": input_, "output": output}
    )
    driver = DriverClass()
    return driver


@pytest.fixture(params=combinations_with_flag)
def sync_simplifier(request):
    use, (input_, output) = request.param
    if use:
        DriverClass = type(
            "DriverClass", (DummySyncSimplifier,), {"input_": input_, "output": output}
        )
        driver = DriverClass()
        return driver
    else:
        return None


@pytest.fixture(params=combinations)
def sync_surface_driver(request, sync_il_driver, sync_conn_driver, sync_simplifier):
    input_, output = request.param
    compatible = True

    if sync_il_driver is not None:
        if output.isdisjoint(sync_il_driver.input_):
            compatible = False
        elif sync_il_driver.output.isdisjoint(sync_conn_driver.input_):
            compatible = False
    else:
        if output.isdisjoint(sync_conn_driver.input_):
            compatible = False

    if sync_simplifier is not None:
        if sync_conn_driver.output.isdisjoint(sync_simplifier.input_):
            compatible = False

    if not compatible:
        pytest.skip("Incompatible driver combination")

    DriverClass = type(
        "DriverClass", (DummySyncSurfaceDriver,), {"input_": input_, "output": output}
    )
    driver = DriverClass(
        il_driver=sync_il_driver,
        conn_driver=sync_conn_driver,
        simplifier=sync_simplifier,
    )
    return driver


# -----------------
# Async Tests
# -----------------
@pytest.fixture(params=combinations_with_flag)
def async_il_driver(request):
    use, (input_, output) = request.param
    if use:
        DriverClass = type(
            "DriverClass", (DummyAsyncILDriver,), {"input_": input_, "output": output}
        )
        driver = DriverClass()
        return driver
    else:
        return None


@pytest.fixture(params=combinations)
def async_conn_driver(request):
    input_, output = request.param
    DriverClass = type(
        "DriverClass", (DummyAsyncConnDriver,), {"input_": input_, "output": output}
    )
    driver = DriverClass()
    return driver


@pytest.fixture(params=combinations_with_flag)
def async_simplifier(request):
    use, (input_, output) = request.param
    if use:
        DriverClass = type(
            "DriverClass", (DummyAsyncSimplifier,), {"input_": input_, "output": output}
        )
        driver = DriverClass()
        return driver
    else:
        return None


@pytest.fixture(params=combinations)
def async_surface_driver(request, async_il_driver, async_conn_driver, async_simplifier):
    input_, output = request.param
    compatible = True

    if async_il_driver is not None:
        if output.isdisjoint(async_il_driver.input_):
            compatible = False
        elif async_il_driver.output.isdisjoint(async_conn_driver.input_):
            compatible = False
    else:
        if output.isdisjoint(async_conn_driver.input_):
            compatible = False

    if async_simplifier is not None:
        if async_conn_driver.output.isdisjoint(async_simplifier.input_):
            compatible = False

    if not compatible:
        pytest.skip("Incompatible driver combination")

    DriverClass = type(
        "DriverClass", (DummyAsyncSurfaceDriver,), {"input_": input_, "output": output}
    )
    driver = DriverClass(
        il_driver=async_il_driver,
        conn_driver=async_conn_driver,
        simplifier=async_simplifier,
    )
    return driver


# --------------
# Random Tests
# -------------
@pytest.fixture(params=combinations_with_flag_syncasync)
def random_il_driver(request):
    is_async, use, (input_, output) = request.param
    if use:
        if is_async:
            DriverClass = type(
                "DriverClass",
                (DummyAsyncILDriver,),
                {"input_": input_, "output": output},
            )
        else:
            DriverClass = type(
                "DriverClass",
                (DummySyncILDriver,),
                {"input_": input_, "output": output},
            )
        driver = DriverClass()
        return driver
    else:
        return None


@pytest.fixture(params=combinations_with_flag)
def random_conn_driver(request):
    is_async, (input_, output) = request.param
    if is_async:
        DriverClass = type(
            "DriverClass", (DummyAsyncConnDriver,), {"input_": input_, "output": output}
        )
    else:
        DriverClass = type(
            "DriverClass", (DummySyncConnDriver,), {"input_": input_, "output": output}
        )
    driver = DriverClass()
    return driver


@pytest.fixture(params=combinations_with_flag_syncasync)
def random_simplifier(request):
    is_async, use, (input_, output) = request.param
    if use:
        if is_async:
            DriverClass = type(
                "DriverClass",
                (DummyAsyncSimplifier,),
                {"input_": input_, "output": output},
            )
        else:
            DriverClass = type(
                "DriverClass",
                (DummySyncSimplifier,),
                {"input_": input_, "output": output},
            )
        driver = DriverClass()
        return driver
    else:
        return None


@pytest.fixture(params=combinations_with_flag)
def random_surface_driver(
    request, random_il_driver, random_conn_driver, random_simplifier
):
    is_async, (input_, output) = request.param
    compatible = True

    if random_il_driver is not None:
        if output.isdisjoint(random_il_driver.input_):
            compatible = False
        elif random_il_driver.output.isdisjoint(random_conn_driver.input_):
            compatible = False
    else:
        if output.isdisjoint(random_conn_driver.input_):
            compatible = False

    if random_simplifier is not None:
        if random_conn_driver.output.isdisjoint(random_simplifier.input_):
            compatible = False

    if not compatible:
        pytest.skip("Incompatible driver combination")
    if is_async and not any(
        driver.is_sync
        for driver in [random_il_driver, random_conn_driver, random_simplifier]
        if driver is not None
    ):
        pytest.skip("At least one driver should be sync")
    elif not any(
        driver.is_async
        for driver in [random_il_driver, random_conn_driver, random_simplifier]
        if driver is not None
    ):
        pytest.skip("At least one driver should be async")

    if is_async:
        DriverClass = type(
            "DriverClass",
            (DummyAsyncSurfaceDriver,),
            {"input_": input_, "output": output},
        )
    else:
        DriverClass = type(
            "DriverClass",
            (DummySyncSurfaceDriver,),
            {"input_": input_, "output": output},
        )
    driver = DriverClass(
        il_driver=random_il_driver,
        conn_driver=random_conn_driver,
        simplifier=random_simplifier,
        fallback=True,
    )
    return driver


# -----------------
# Both Tests
# -----------------
@pytest.fixture(params=combinations_with_flag)
def both_il_driver(request):
    use, (input_, output) = request.param
    if use:
        DriverClass = type(
            "DriverClass",
            (DummySyncAsyncILDriver,),
            {"input_": input_, "output": output},
        )
        driver = DriverClass()
        return driver
    else:
        return None


@pytest.fixture(params=combinations)
def both_conn_driver(request):
    input_, output = request.param
    DriverClass = type(
        "DriverClass", (DummySyncAsyncConnDriver,), {"input_": input_, "output": output}
    )
    driver = DriverClass()
    return driver


@pytest.fixture(params=combinations_with_flag)
def both_simplifier(request):
    use, (input_, output) = request.param
    if use:
        DriverClass = type(
            "DriverClass",
            (DummySyncAsyncSimplifier,),
            {"input_": input_, "output": output},
        )
        driver = DriverClass()
        return driver
    else:
        return None


@pytest.fixture(params=combinations)
def both_surface_driver(request, both_il_driver, both_conn_driver, both_simplifier):
    input_, output = request.param
    compatible = True

    if both_il_driver is not None:
        if output.isdisjoint(both_il_driver.input_):
            compatible = False
        elif both_il_driver.output.isdisjoint(both_conn_driver.input_):
            compatible = False
    else:
        if output.isdisjoint(both_conn_driver.input_):
            compatible = False

    if both_simplifier is not None:
        if both_conn_driver.output.isdisjoint(both_simplifier.input_):
            compatible = False

    if not compatible:
        pytest.skip("Incompatible driver combination")

    DriverClass = type(
        "DriverClass",
        (DummySyncAsyncSurfaceDriver,),
        {"input_": input_, "output": output},
    )
    driver = DriverClass(
        il_driver=both_il_driver,
        conn_driver=both_conn_driver,
        simplifier=both_simplifier,
    )
    return driver
