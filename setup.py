################## Sparki Learning Library ##################
#
# This is the setup file for the Sparki Learning library
#
# Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
# remain property of their respective owners
#
# written by Jeremy Eglen
# Created: February 24, 2016
# Last Modified: November 18, 2019
# originally written targeting Python 3.4 and 3.5
# working with Python 3.7 & 3.8

from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the version number from the constants file
with open(path.join(this_directory, "sparki_learning", "constants.py"), encoding='utf-8') as fc:
    exec(fc.read())
print("sparki_learning version is {}".format(SPARKI_MYRO_VERSION))

setup(
    name = "sparki_learning",
    version = SPARKI_MYRO_VERSION,
    packages = find_packages(),

    # Project uses pyserial for bluetooth, so ensure that package gets
    # installed or upgraded on the target machine
    install_requires = ['pyserial>=2.7', 'pysimplegui>=4.0.0'],

    python_requires='>=2.7, <4',

    project_urls={
        'Documentation': 'https://sparki-learning.readthedocs.io/en/latest/',
        'Source': 'https://github.com/radarjd/sparki_learning/',
    },

    package_data = {
    },

    zip_safe = True,

    # metadata for upload to PyPI
    author = "Jeremy Eglen",
    author_email = "jeglen@butler.edu",
    description = "library to implement the Myro API with the Sparki robot",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license = "Apache License Version 2.0",
    keywords = "sparki learning myro robot",
    url = "https://github.com/radarjd/sparki_learning",   # project home page
    download_url = "https://github.com/radarjd/sparki_learning/tarball/v1.5.2.0",
    classifiers = [
                   'Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Education',
                   'License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python',
                   'Topic :: Education',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
)
