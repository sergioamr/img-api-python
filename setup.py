from imgapi.version import __version__
from setuptools import setup

setup(name='imgapi',
      version=__version__,
      description='Img-api.com installed',
      url='https://github.com/sergioamr/img-api-python',
      author='Sergio A. Martinez',
      author_email='contact@img-api.com',
      license='MIT',
      packages=['imgapi'],
      zip_safe=False)