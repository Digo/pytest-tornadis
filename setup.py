import os

import setuptools

module_path = os.path.join(os.path.dirname(__file__), 'pytest_tornadis', '__init__.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version__')][0]

__version__ = version_line.split('__version__ = ')[-1][1:][:-2]

setuptools.setup(
    name="pytest-tornadis",
    version=__version__,
    url="https://github.com/cngo-github/pytest-tornadis",

    author="Chuong Ngo",
    author_email="chuong@woobo.io",

    description="Pre-defined functions, utilities, and objects that defines the Mongo database.",
    long_description=open('README.rst').read(),
    packages=setuptools.find_packages(),

    zip_safe=False,
    platforms='any',

    install_requires=['tornadis>=0.8.0', 'tornado>=4.5.2'],
    tests_require=['pytest>=3.3.1', 'pytest-cov==2.5.1', 'pytest-tornado>=0.4.5'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
