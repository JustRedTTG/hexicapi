from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.730'
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
    install_requires=['bottle','cryptography','colorama'],
    package_data={'hexicapi': ['authpage/*.html',

                  'authpage/css/*.css',

                  'authpage/fonts/font-awesome-4.7.0/css/*.css',
                  'authpage/fonts/font-awesome-4.7.0/fonts/*.ttf',
                  'authpage/fonts/font-awesome-4.7.0/fonts/*.otf',
                  'authpage/fonts/font-awesome-4.7.0/fonts/*.eot',
                  'authpage/fonts/font-awesome-4.7.0/fonts/*.woff',
                  'authpage/fonts/font-awesome-4.7.0/fonts/*.woff2',
                  'authpage/fonts/font-awesome-4.7.0/fonts/*.svg',
                  'authpage/fonts/font-awesome-4.7.0/less/*.less',
                  'authpage/fonts/font-awesome-4.7.0/scss/*.scss',

                  'authpage/fonts/iconic/css/*.css',
                  'authpage/fonts/iconic/fonts/*.ttf',
                  'authpage/fonts/iconic/fonts/*.eot',
                  'authpage/fonts/iconic/fonts/*.woff',
                  'authpage/fonts/iconic/fonts/*.woff2',
                  'authpage/fonts/iconic/fonts/*.svg',

                  'authpage/fonts/poppins/*.ttf',

                  'authpage/images/icons/favicon.ico',

                  'authpage/js/*.js',

                  'authpage/vendor/animate/animate.css',
                  'authpage/vendor/animsition/css/*.css',
                  'authpage/vendor/animsition/js/*.js',
                  'authpage/vendor/bootstrap/css/*.css',
                  'authpage/vendor/bootstrap/css/*.map',
                  'authpage/vendor/bootstrap/js/*.js',
                  'authpage/vendor/countdowntime/*.js',
                  'authpage/vendor/css-hamburgers/*.css',
                  'authpage/vendor/daterangepicker/*.css',
                  'authpage/vendor/daterangepicker/*.js',
                  'authpage/vendor/jquery/*.js',
                  'authpage/vendor/perfect-scrollbar/*.css',
                  'authpage/vendor/perfect-scrollbar/*.js',
                  'authpage/vendor/select2/*.css',
                  'authpage/vendor/select2/*.js'
                ]
    },
    keywords=['python']#,
#    classifiers=[
#        "Development Status :: 1 - Planning",
#        "Intended Audience :: Developers",
#        "Programming Language :: Python :: 3",
#        "Operating System :: Unix",
#        "Operating System :: MacOS :: MacOS X",
#        "Operating System :: Microsoft :: Windows",
#    ]
)
