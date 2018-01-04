import os

import setuptools

module_path = os.path.join(os.path.dirname(__file__), 'pytest_tornadis', '__init__.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version__')][0]

__version__ = version_line.split('__version__ = ')[-1][1:][:-2]

setuptools.setup(
    name="pytest_tornadis",
    version=__version__,
    url="https://github.com/Woobo/woobo-backend/pytest_tornadis/",

    author="Chuong Ngo",
    author_email="chuong@woobo.io",

    description="Pre-defined functions, utilities, and objects that defines the Mongo database.",
    long_description=open('README.rst').read(),
    packages=setuptools.find_packages(),

    zip_safe=False,
    platforms='any',

    install_requires=['mongoengine==0.14.3', 'pymongo==3.5.1', 'six==1.11.0',
                      'validation_utils==1.0.1', 'passlib==1.7.1', 'python-dateutil==2.6.1'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
