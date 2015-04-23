import os
from setuptools import setup
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "p_framework",
    version = "0.0.1",
    author = "Yohann Gabory",
    author_email = "yohann@gabory.fr",
    description = ("Performance based web framework written in python"),
    license = "BSD",
    keywords = "framework web performances",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['p_framework'],
    long_description=read('README.rst'),
    install_requires = ["werkzeug", "jinja2"],
    tests_require = ["pytest-cov", "pytest", "pytest-codecheckers"],
    test_suite = "test",
    test_loader = "runtests:PyTest",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
