class Parent:
    def a(self):
        print("Parent.a")


class ChildImpl(Parent):
    def a(self):
        print("ChildImpl.a")


class ChildNoImpl(Parent):
    pass


class StringObject:
    string: str

    def __init__(self, letter: str, value: int) -> None:
        self.string = letter * value

    def __repr__(self) -> str:
        return self.string
