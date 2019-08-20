#!/usr/bin/env python

from setuptools import setup, find_packages

import astrofaker

setup(

    # Project Information
    name="astrofaker",
    version=astrofaker.version(),
    packages=find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['docutils>=0.3'],

    # About us
    description='Gemini Data Processing Python Package',
    author='Gemini Data Processing Software Group',
    author_email='sus_inquiries@gemini.edu',
    url='http://www.gemini.edu',
    maintainer='Science User Support Department',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Gemini Ops',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Linux :: CentOS',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Topic :: Gemini',
        'Topic :: Data Reduction',
        'Topic :: Scientific/Engineering :: Astronomy',
    ]

)
