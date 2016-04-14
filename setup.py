################## Sparki Learning Library ##################
#
# This is the setup file for the Sparki Learning library
#
# Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
# remain property of their respective owners
#
# written by Jeremy Eglen
# Created: February 24, 2016
# Last Modified: April 14, 2016
# written targeting Python 3.4, but likely works with other versions, and has been lightly tested with Python 2.7

from setuptools import setup, find_packages
setup(
    name = "sparki_learning",
    version = "1.2.2",
    packages = find_packages(),

    # Project uses pyserial for bluetooth, so ensure that package gets
    # installed or upgraded on the target machine
    install_requires = ['pyserial>=2.7'],

    package_data = {
    },

#    zip_safe = False,

    # metadata for upload to PyPI
    author = "Jeremy Eglen",
    author_email = "jeglen@butler.edu",
    description = "library to implement the Myro API with the Sparki robot",
    license = "Apache License Version 2.0",
    keywords = "sparki learning myro robot",
    url = "https://github.com/radarjd/sparki_learning",   # project home page
    download_url = "https://github.com/radarjd/sparki_learning/tarball/v1.1.4",
    classifiers = [
                   'Development Status :: 4 - Beta',
                   'Intended Audience :: Education',
                   'License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python',
                   'Topic :: Education',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
)
