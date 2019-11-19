from setuptools import setup
import subprocess

setup(
    name='gpuplug',
    version='0',
    packages=['gpuplug'],
    license='MIT',
    author="Aapo Vienamo",
    author_email="aapo.vienamo@aalto.fi",
    long_description='Dynamic GPU device binding for containers',
    entry_points = {
        'console_scripts': [
            'gpuplugd=gpuplug.gpuplugd:main',
            'gpuplug=gpuplug.gpuplug:main',
        ]
    },
)
