from setuptools import setup, find_packages
from os.path import join, dirname
import tango_ds

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

import numpy

#Made for using sphinx
#Need to enhance

ext_modules = [Extension("xiApi", ["tango_ds/Detector/xiApi.pyx"], 
	libraries=["tango_ds/Detector/m3apiX64"], include_dirs=[numpy.get_include()])]

setup(
    name='tango-ds',
    version=tango_ds.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    include_package_data=True,
    ext_modules=cythonize(ext_modules)
)
