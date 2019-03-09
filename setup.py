from setuptools import setup, find_packages

import os

setup(
    name='CardinalVision',
    packages=find_packages(),
    install_requires=[open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'requirements.txt')).read().split('\n')[:-1]],
    package_data={'CardinalVision.test': ['*.mov']},
    include_package_data=True
)
