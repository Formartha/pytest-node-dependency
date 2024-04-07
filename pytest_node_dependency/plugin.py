import os
import platform

import networkx as nx
import pytest


class TestDependencyHandler:

    with_deps = []
    without_deps = []

    @staticmethod
    def clean_nodeid(nodeid):
        """Clean node ids for class-based tests."""
        return nodeid.replace('::()::', '::')

    @staticmethod
    def check_skip_marker(nodeid, nodeid_to_item_map):
        """Check if the given node has a 'skip' marker."""
        if platform.system() == "Windows":
            nodeid = nodeid.replace("\\", "/")
        return bool(nodeid_to_item_map[nodeid].get_closest_marker('skip'))

    @staticmethod
    def get_dependency_nodeid(item, dependency):
        """
        Construct the node id for the given dependency.

        Note: The dependent test must be in the same folder as the main test.
        If the dependency starts with '/', it is treated as a path relative to
        the test start location.
        """
        base_item_nodeid = TestDependencyHandler.clean_nodeid(item.nodeid).rsplit('::', 1)[0]
        dependency = '{}::{}'.format(base_item_nodeid, dependency) if '::' not in dependency else dependency

        if dependency.startswith('/'):
            dependency = dependency[1:]
            prefix_path = ''
        else:
            prefix_path = os.path.dirname(str(item.nodeid).split('::')[0])

        depend_array = str(dependency).split('::')
        dependency = os.path.join(prefix_path, depend_array[0]) + '::' + depend_array[1]

        return dependency

    @staticmethod
    def with_deps_parser(item, dag, nodeid_to_item_map):
        dependency_nodeid = list(dag.pred[TestDependencyHandler.clean_nodeid(item.nodeid)].keys())[0]

        if TestDependencyHandler.check_skip_marker(dependency_nodeid, nodeid_to_item_map):
            current_nodeid = dependency_nodeid
            while dag.succ[current_nodeid]:
                nodeid = list(dag.succ[current_nodeid].keys())[0]
                if not TestDependencyHandler.check_skip_marker(nodeid, nodeid_to_item_map):
                    nodeid_to_item_map[nodeid].add_marker('skip')
                    vars(nodeid_to_item_map[nodeid].get_closest_marker('skip'))['kwargs'] = {
                        'reason': f'depends on skipped test: {current_nodeid.split("::")[1]}'
                    }
                current_nodeid = nodeid

        depends_on = [nodeid_to_item_map[dependency_nodeid], item]
        if nodeid_to_item_map[dependency_nodeid] in TestDependencyHandler.without_deps:
            TestDependencyHandler.without_deps.remove(nodeid_to_item_map[dependency_nodeid])

        TestDependencyHandler.with_deps.extend(dep for dep in depends_on if str(dep) not in str(TestDependencyHandler.with_deps))

    @staticmethod
    def without_deps_parser(item):
        if item not in TestDependencyHandler.with_deps:
            TestDependencyHandler.without_deps.append(item)

    @staticmethod
    def reorder_tests(items):
        """
        Reorder the execution of tests based on the dependency marks.

        To set up a test dependency, decorate the test function with the "depends"
        mark and give a list of dependencies via the "on" keyword argument to the
        decorator. Dependencies can be specified by name only when in the same
        file as the test being decorated, or by pytest node path for tests in
        other files/classes.

        Tests without dependencies will run in arbitrary order.
        """
        dag = nx.DiGraph()
        nodeid_to_item_map = {TestDependencyHandler.clean_nodeid(item.nodeid): item for item in items}

        for item in items:
            dag.add_node(TestDependencyHandler.clean_nodeid(item.nodeid))

            marker = item.get_closest_marker('depends')
            if marker is not None:
                for dependency in marker.kwargs['on']:
                    dependency_nodeid = TestDependencyHandler.get_dependency_nodeid(item, dependency)
                    dag.add_edge(dependency_nodeid, TestDependencyHandler.clean_nodeid(item.nodeid))

        for item in items:
            if not dag.pred[TestDependencyHandler.clean_nodeid(item.nodeid)]:
                TestDependencyHandler.without_deps_parser(item)
            else:
                TestDependencyHandler.with_deps_parser(item, dag, nodeid_to_item_map)

        return TestDependencyHandler.without_deps + TestDependencyHandler.with_deps

    @staticmethod
    def handle_failed_dependency(item):
        """
        Check if the current test has a dependency. If so, check if the dependency
        is in the list of failed tests. If it is, mark the current test as skipped
        and add a reason with pytest.skip.
        """
        name = ''
        test_index = item.session.items.index(item)

        # Initialize the failed list if this is the first test
        if test_index == 0:
            item.config.cache.set('failed_test_list', dict())

        # Check if the test has a dependency
        marker = item.get_closest_marker('depends')
        if marker is not None:
            depends = marker.kwargs.get('on', [])
            for dependency in depends:
                name = dependency.split('::')[1]

                test_list = item.config.cache.get('failed_test_list', dict())
                if name in test_list:
                    item.add_marker('failed_dependency')
                    test_list[item.name] = 'Failed'
                    item.config.cache.set('failed_test_list', test_list)

        if item.get_closest_marker('failed_dependency'):
            pytest.xfail(f'failed due to dependency on test: {name} which is in status: {test_list[name]}')

        # Save the number of failed tests before running the current test
        tests_failed_before = item.session.testsfailed
        item.config.cache.set('tests_failed_before', tests_failed_before)

    @staticmethod
    def handle_failed_test(item):
        """
        Check if the current test failed. If so, save its name in the failed
        test list in the cache.
        """
        tests_failed_before = item.config.cache.get('tests_failed_before', 0)
        tests_failed_after = item.session.testsfailed

        item.config.cache.set('tests_failed_before', tests_failed_after)

        if tests_failed_after - tests_failed_before > 0:
            test_list = item.config.cache.get('failed_test_list', dict())
            test_list[item.name] = 'Failed'
            item.config.cache.set('failed_test_list', test_list)


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items):
    items[:] = TestDependencyHandler.reorder_tests(items)


@pytest.hookimpl(trylast=True)
def pytest_runtest_setup(item):
    TestDependencyHandler.handle_failed_dependency(item)


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    TestDependencyHandler.handle_failed_test(item)
