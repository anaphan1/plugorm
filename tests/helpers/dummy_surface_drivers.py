from plugorm import SurfaceDriver


class DummySyncSurfaceDriver(SurfaceDriver):
    is_sync = True
    is_async = False

    @SurfaceDriver.dialect
    def dummy_method(self, arg1):
        return arg1


class DummyAsyncSurfaceDriver(SurfaceDriver):
    input_ = set()  # Input for Surface Driver is unimportant
    output_ = {"metadata1"}

    is_sync = True
    is_async = False

    @SurfaceDriver.dialect
    async def adummy_method(self, arg1):
        return arg1


class DummySyncAsyncSurfaceDriver(SurfaceDriver):
    input_ = set()  # Input for Surface Driver is unimportant
    output_ = {"metadata1"}

    is_sync = True
    is_async = False

    @SurfaceDriver.dialect
    def dummy_method(self, arg1):
        return arg1

    @SurfaceDriver.dialect
    async def adummy_method(self, arg1):
        return arg1
