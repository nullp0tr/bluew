"""
setup.py script for bluew.
"""


from setuptools import setup


setup(
    name='bluew',
    version='0.3.2',
    description='Python Wrapper for Bluetoothctl',
    url='https://github.com/nullp0tr/Bluew',
    author='Ahmed Alsharif (nullp0tr)',
    author_email='ahmed@shnaboo.com',
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

    keywords='bluetooth bluez bluetoothctl wrapper',
    install_requires=[]
)
