from setuptools import setup

setup(
    name='gpuplug',
    version='0',
    packages=['gpuplug'],
    license='TBA',
    long_description='Dynamic GPU device binding for containers',
    entry_points = {
        'console_scripts': [
            'gpuplugd=gpuplugd.gpuplug:main',
            'gpuplug=gpuplug.gpuplug:main',
        ]
    }
)
