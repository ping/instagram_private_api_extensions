try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__author__ = 'ping <lastmodified@gmail.com>'
__version__ = '0.1.1'

packages = [
    'instagram_private_api_extensions'
]

setup(
    name='instagram_private_api_extensions',
    version=__version__,
    author='ping',
    author_email='lastmodified@gmail.com>',
    license='MIT',
    url='https://github.com/ping/instagram_private_api_extensions/tree/master',
    keywords='instagram private api extensions',
    description='An extension module for https://github.com/ping/instagram_private_api',
    packages=packages,
    install_requires=['moviepy==0', 'Pillow>=4.0.0'],
    dependency_links=['https://github.com/Zulko/moviepy/tarball/d4c9c37#egg=moviepy-0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
