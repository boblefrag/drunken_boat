import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="drunken_boat",
    version='0.0.3',
    author="Yohann Gabory",
    author_email="yohann@gabory.fr",
    description=("Performance based web framework written in python"),
    license = "BSD",
    keywords = "framework web performances",
    url = "https://github.com/boblefrag/drunken_boat",
    packages=['drunken_boat'],
    long_description=read('README.rst'),
    install_requires = ["werkzeug", "jinja2", "psycopg2"],
    tests_require = ["pytest-codecheckers", "pytest-cov",
                     "pytest", "sphinx-pypi-upload"],
    test_suite = "test",
    test_loader = "runtests:PyTest",
    scripts=['drunken_boat/bin/drunken_run.py'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
