from setuptools import setup, find_packages
from os.path import join, dirname
import tango_ds

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


#Made for using sphinx
#Need to enhance


setup(
    name='tango-ds',
    version=tango_ds.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    include_package_data=True,
    ext_modules=cythonize([Extension("ximc", ["tango_ds/Motor/ximc.pyx"], libraries=["ximc"])])
)