from .helpers.dummy_classes import Parent, ChildImpl, ChildNoImpl, StringObject
from plugorm.utils import has_impl, short_repr


def test_has_impl():
    assert has_impl(Parent, ChildImpl, "a")
    assert not has_impl(Parent, ChildNoImpl, "a")


def test_short_repr():
    max_len = 80

    short_amount = max_len - 10

    short = StringObject("a", short_amount)
    exact = StringObject("a", max_len)
    long = StringObject("a", max_len + 10)

    assert len(short_repr(short, max_len)) == short_amount
    assert len(short_repr(exact, max_len)) == max_len
    assert len(short_repr(long, max_len)) == max_len + 3  # Truncated + ellipsis
