#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='GFAnalytics',
    version='0.1.0',
    author='GFAnalytics Team',
    author_email='your.email@example.com',
    description='A machine learning framework for predicting stock market using Bazi attributes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/GFAnalytics',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'gfanalytics=GFAnalytics.main:main',
        ],
    },
) 