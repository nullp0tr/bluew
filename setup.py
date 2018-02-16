"""
setup.py script for bluew.
"""


from setuptools import setup
from bluew import __version__


setup(
    name='bluew',
    version=__version__,
    description='Bluetooth made easy.',
    url='https://github.com/nullp0tr/Bluew',
    author='Ahmed Alsharif (nullp0tr)',
    author_email='ahmeds2000x@gmail.com',
    license='MIT',
    packages=['bluew', 'bluew/dbusted'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='bluetooth bluez BLE',
    install_requires=[]
)
