import pytest


@pytest.mark.depends(xdist_group="group_a")
def test_second(request):
    if getattr(request.config, "workerinput", None):  # if no workerinput, so no x-dist
        request.config.cache.set('worker_group', request.session.config.workerinput["workerid"])
    assert request.session.items[1].name == 'test_second'


@pytest.mark.depends(on=["test_plugin.py::test_second"], xdist_group="group_a")
def test_last(request):
    if getattr(request.config, "workerinput", None): # if no workerinput, so no x-dist
        assert request.config.cache.get('worker_group', request.session.config.workerinput["workerid"]) is not None
    assert request.session.items[2].name == 'test_last'


def test_first(request):
    assert request.session.items[0].name == 'test_first'

