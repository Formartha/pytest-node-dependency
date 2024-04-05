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

```python
import pytest

@pytest.mark.depends(on=['test_dependency'])
def test_my_test():
    # Test code here
    pass

def test_dependency():
    # Code for the dependency test
    pass