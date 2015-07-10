import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Elefant",
    version = "0.0.5",
    author = "Will Drevo",
    author_email = "will.drevo@gmail.com",
    description = ("Backing up and restoring Postgres databases "
                                   "using S3 for automation"),
    license = "MIT",
    keywords = "python heroku postgres backup s3",
    url = "http://packages.python.org/elefant",
    packages=['elefant'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)