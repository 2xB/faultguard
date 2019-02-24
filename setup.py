# encoding: utf-8
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='faultguard',
    version='1.0.0',
    py_modules=['faultguard'],
    url='https://github.com/2xB/faultguard',
    license='BSD 3-Clause License',
    author='Benedikt Bieringer',
    author_email='2xB.coding@wwu.de',
    description='Rescuing data from abrubt process termination in python.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
    ],
)
