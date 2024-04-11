------

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/Formartha/pytest-node-dependency/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pytest-node-dependency)](https://pypi.org/project/pytest-node-dependency)
[![Tests](https://img.shields.io/github/actions/workflow/status/Formartha/pytest-node-dependency/test-commit.yml?branch=main&label=tests)](https://github.com/Formartha/pytest-node-dependency/actions/workflows/test-commit.yml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pytest-node-dependency)

What?
------
pytest-node-dependency is a pytest plugin that allows you to define dependencies between tests and reorder their execution based on those dependencies. This plugin ensures that tests with dependencies run after their required prerequisites have completed successfully.

A unique feature of the plugin is that if you set a test to depend on another one, the plugin will check if the test being depended upon failed. If that's the case, it will mark the current test as 'expected to fail' (xfail).

How to install?
----------
```
pip install pytest-node-dependency
```

How to use?
-----------------------------------------------------
To set up a test dependency, decorate the test function with the `depends` mark and provide a list of dependencies via the `on` keyword argument to the decorator. Dependencies can be specified by name only when in the same file as the test being decorated or by the pytest node path for tests in other files/classes.

```
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
```

Xdist adoption:
---------------
The way xdist plugin works is by utilizing multiple cores and spreads the tests among them.
The problem with the plugin is that if you wish to use reordering, you probably want to set some dependency among the tests,
However, the xdist plugin will break it.

For that, you should set the group for the tests. The group means that a gateway worker will collect the tests, and will 
place all the grouped tests in a single gateway worker. 
This will lead creation of serial testing among parallel exectuion.

```
import pytest

@pytest.mark.depends(xdist_group='a')
def test_second(request):
    print("second")
    assert request.session.items[1].name == 'test_second'


@pytest.mark.depends(on=["test_plugin.py::test_second"], xdist_group='a')
def test_last(request):
    print("last")
    assert request.session.items[2].name == 'test_last'


def test_first(request):
    print("first")
    assert request.session.items[0].name == 'test_first'
```


Limitations and known issues:
-----------------------------------------------------
* All the tests without dependency (both dependent-on) will run first, then, all tests with connections will run
(e.g. the list of items will be as described)
* Currently, automated xfail is enabled, it should be configurable.
