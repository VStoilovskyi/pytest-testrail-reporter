"""Config for setup package pytest plugin."""

import os

from setuptools import setup, find_packages

__version__ = '0.0.7'


def read_file(filename):
    """
    Read the given file.

    Args:
        filename: Filename to be read

    Returns:
        File content

    """
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(
    name='pytest-testrail-integrator',
    version=__version__,
    description='Pytest plugin for sending report to testrail system.',
    long_description_content_type="text/markdown",
    long_description=read_file('README.md'),
    url='https://github.com/VStoilovskyi/pytest-testrail-reporter',
    packages=find_packages(),
    install_requires=['pytest>=6.2.5', 'testrail-api', 'pydash'],
    license='MIT',
    keywords=['report', 'pytest', 'testrail'],
    classifiers=[
        'Framework :: Pytest',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    entry_points={
        'pytest11': [
            'pytest_testrail_integrator = pytest_testrail_integrator.plugin',
        ]
    }
)
