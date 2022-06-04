import os

from scripts import compile


def test_constants():
    assert compile.SRC_PATH == '/home/algo/workspace/src/', 'SRC_PATH is wrong'
    assert compile.TESTS_PATH == '/home/algo/workspace/tests/', 'TESTS_PATH is wrong'


def test_gettealroot():
    assert compile.get_tealroot() == '/home/algo/workspace/src/teal', 'tealroot is wrong'


def test_list_targets():
    assert compile.list_targets(os.path.join(os.path.dirname(__file__), 'test_glob')) == [
        '/home/algo/workspace/tests/scripts/test_glob/aaa.py',
        '/home/algo/workspace/tests/scripts/test_glob/hoge/bbb.py']
