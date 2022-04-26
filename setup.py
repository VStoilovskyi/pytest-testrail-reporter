"""Config for setup package pytest plugin."""

import os

from setuptools import setup, find_packages

__version__ = '0.0.1b'


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
    name='pytest-testrail-reporter',
    version=__version__,
    description='Pytest plugin for sending report to testrail system.',
    long_description_content_type="text/markdown",
    long_description=read_file('README.md'),
    author_email='vadym.stoilovskyi@gmail.com',
    url='https://github.com/VStoilovskyi/pytest-testrail-reporter',
    packages=find_packages(),
    install_requires=['pytest>=6.2.5', 'testrail-api'],
    license='Apache 2.0',
    keywords=['report', 'pytest', 'testrail'],
    classifiers=[
        'Framework :: Pytest',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    entry_points={
        'pytest11': [
            'pytest_message = pytest_testrail_client.plugin',
        ]
    }
)
