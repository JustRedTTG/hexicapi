from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.734'
short = 'Tool for making quick servers.'
long = '''API for making servers and clients to connect to those servers. 

Includes end to end encryption!

github: https://github.com/JustRedTTG/hexicapi'''

# Setting up
setup(
    name="hexicapi",
    version=VERSION,
    author="Red",
    author_email="redtonehair@gmail.com",
    description=short,
    long_description_content_type="text/markdown",
    long_description=long,
    packages=['hexicapi'],
    install_requires=['cryptography >= 3.1', 'colorama', 'websocket-client'],
    keywords=['python']
)
