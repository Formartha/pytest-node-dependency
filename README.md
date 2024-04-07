------

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/license/mit)

What?
------
pytest-node-dependency is a pytest plugin that allows you to define dependencies between tests and reorder their execution based on those dependencies. This plugin ensures that tests with dependencies run after their required prerequisites have completed successfully.

How to install?
----------
```
pip install pytest-node-dependency
```

how to use?
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

Limitations and known issues:
-----------------------------------------------------
* The plugin logic makes tests run one after the other in a serial way, as a result, x-dist isn't supported (currently).
* All the tests without depednecy (both dependent on and depends on) will run first, afterwards all tests with connections will run (e.g. the list of items will be as described)
