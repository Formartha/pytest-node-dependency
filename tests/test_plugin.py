import pytest


def test_second(request):
    print("second")
    assert request.session.items[1].name == 'test_second'


@pytest.mark.depends(on=["test_plugin.py::test_second"])
def test_last(request):
    print("last")
    assert request.session.items[2].name == 'test_last'


def test_first(request):
    print("first")
    assert request.session.items[0].name == 'test_first'
