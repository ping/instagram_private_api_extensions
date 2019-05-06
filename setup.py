from os import path
from io import open
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__author__ = 'ping <lastmodified@gmail.com>'
__version__ = '0.3.8'

packages = [
    'instagram_private_api_extensions'
]

test_reqs = ['responses>=0.5.1']

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='instagram_private_api_extensions',
    version=__version__,
    author='ping',
    author_email='lastmodified@gmail.com',
    license='MIT',
    url='https://github.com/ping/instagram_private_api_extensions/tree/master',
    keywords='instagram private api extensions',
    description='An extension module for https://github.com/ping/instagram_private_api',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=packages,
    install_requires=['moviepy==0.2.3.2', 'Pillow>=4.0.0', 'requests>=2.9.1'],
    test_requires=test_reqs,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ]
)
