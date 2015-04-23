import pytest

class PyTest(object):

    def run(self):
        errno = pytest.main(
            "-v p_framework --cov-report term-missing --cov p_framework")
        raise SystemExit(errno)

    def loadTestsFromNames(self, *args):
        return self.run()
