import glob
import os

from pyteal import compileTeal

WORKSPACE_PATH = '/home/algo/workspace/'
SRC_PATH = os.path.join(WORKSPACE_PATH, 'src/')
TESTS_PATH = os.path.join(WORKSPACE_PATH, 'tests/')

SRC_PREFIX_LEN = len(SRC_PATH)
TESTS_PREFIX_LEN = len(TESTS_PATH)


def get_tealroot():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'teal')


def list_targets(base):
    return glob.glob('{０}/**/*.py'.format(base), recursive=True)
