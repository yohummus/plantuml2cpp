#!/usr/bin/env python3

"""
Installer script for plantuml2cpp
"""

import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='plantuml2cpp',
    version='0.0.1',
    author='Johannes Bergmann',
    author_email='j-bergmann@outlook.com',
    description='C++ code generator for finite state machines from PlantUML state diagrams',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yohummus/plantuml2cpp',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'plantuml2cpp = plantuml2cpp.__main__:main'
        ]
    },
)
