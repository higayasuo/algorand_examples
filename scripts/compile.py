import os


def gettealroot():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src/teal')


print(gettealroot())
