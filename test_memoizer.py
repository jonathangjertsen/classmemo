from frozendict import frozendict
import pytest

from . import Memoizer


@pytest.fixture
def cls():
    class SomeClass:
        def __init__(self, a, b, *, c=3):
            self.a = a
            self.b = b
            self.c = c

    return SomeClass


@pytest.fixture
def memoizer(cls):
    return Memoizer(cls)


def test_empty(cls, memoizer):
    """Check that the class behaves correctly after initialization"""
    assert memoizer.instances == {}
    assert memoizer.cls is cls


def test_get_one_instance(memoizer):
    """Check that we can make one instance"""
    instance = memoizer.get(1, 2, c=3)

    assert instance.a == 1
    assert instance.b == 2
    assert instance.c == 3

    assert memoizer.instances == {((1, 2), frozendict(c=3)): instance}


def test_get_same_instance_twice(memoizer):
    """Check that we can make one instance and retrieve the same instance when calling with the same arguments"""
    instance_1 = memoizer.get(1, 2, c=3)
    instance_2 = memoizer.get(1, 2, c=3)

    assert instance_1.a == 1
    assert instance_1.b == 2
    assert instance_1.c == 3
    assert instance_1 is instance_2

    assert memoizer.instances == {((1, 2), frozendict(c=3)): instance_1}


def test_get_one_instance_and_change_it(memoizer):
    """Check that changing an instance property after creation doesn't change the memoizer's key"""
    instance = memoizer.get(1, 2, c=3)

    instance.a = 2

    assert memoizer.instances == {((1, 2), frozendict(c=3)): instance}
    assert memoizer.get(1, 2, c=3) is instance


def test_get_different_instances(memoizer):
    """Here, instance_2 and instance_3 are the same but instance_1 differs."""
    instance_1 = memoizer.get(1, 2, c=3)
    instance_2 = memoizer.get(1, 2, c=4)
    instance_3 = memoizer.get(1, 2, c=4)

    assert instance_1.a == 1
    assert instance_1.b == 2
    assert instance_1.c == 3
    assert instance_2.a == 1
    assert instance_2.b == 2
    assert instance_2.c == 4
    assert instance_2 is instance_3

    assert memoizer.instances == {
        ((1, 2), frozendict(c=3)): instance_1,
        ((1, 2), frozendict(c=4)): instance_2,
    }


def test_forget_empty(memoizer):
    """Check that we can forget without throwing errors"""
    assert memoizer.forget(1, 2, c=2) is None
    assert memoizer.forget(1, 2, 3, a=2) is None


def test_forget_removes_instance_from_memoizer(memoizer):
    """See function name."""
    memoizer.get(1, 2, c=3)
    memoizer.forget(1, 2, c=3)
    assert memoizer.instances == {}


def test_forget_results_in_different_objects_with_same_arguments(memoizer):
    """See function name."""
    instance_1 = memoizer.get(1, 2, c=3)
    memoizer.forget(1, 2, c=3)
    instance_2 = memoizer.get(1, 2, c=3)
    assert instance_1 is not instance_2
