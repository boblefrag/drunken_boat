import pytest


class PyTest(object):

    def run(self):
        errno = pytest.main(
            "-v drunken_boat --cov-report term-missing --cov drunken_boat")
        raise SystemExit(errno)

    def loadTestsFromNames(self, *args):
        return self.run()
