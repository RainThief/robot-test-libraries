#!/usr/bin/env python
"""package setup"""

from setuptools import setup, find_packages

setup(
    name='robot-support',
    packages=find_packages(),
    version='0.0.1',
    description='common functionality used in system testing',
    license="OGL-UK-3.0",
    install_requires=[
        'robotframework==3.2.2',
        'docker==4.3.1',
        'Faker==4.1.2',
        'SQLAlchemy==1.3.19',
        'psycopg2==2.8.5',
        'alembic==1.4.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OGL-UK-3.0",
        "Operating System :: OS Independent"
    ],
)
