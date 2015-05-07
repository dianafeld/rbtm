from setuptools import setup, find_packages
from os.path import join, dirname
import tango_ds

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


ext_modules=[
    Extension("ximc",
              sources=["ximc.pyx"],
              libraries=["libximc"] # Unix-like specific
    ),
    Extension("xiApi",
              sources=["xiApi.pyx"],
              libraries=["m3apiX64"], # Unix-like specific
              include_dirs=[numpy.get_include()]
    )
]


setup(
    name='tango-ds',
    version=tango_ds.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    include_package_data=True,
    ext_modules=cythonize(ext_modules)
)