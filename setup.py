# fix building inside a virtualbox VM
# http://bugs.python.org/issue8876#msg208792
import os
del os.link

from setuptools import setup, Extension

# import the README
with open('README.rst') as f:
    long_description = f.read()

setup(
    name="amazon_scraper",
    version='0.1.8',
    description="Provides content not accessible through the standard Amazon API",
    long_description=long_description,
    license = 'BSD',
    author="Adam Griffiths",
    author_email="adam.lw.griffiths@gmail.com",
    url='https://github.com/adamlwgriffiths/amazon_scraper',
    test_suite='tests',
    packages=['amazon_scraper'],
    requires=[
        'pythonamazonsimpleproductapi',
        'xmltodict',
        'pythondateutil',
        'beautifulsoup4',
        'requests',
    ],
    platforms=['any'],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ),
)
