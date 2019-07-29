from setuptools import setup

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
            'gpuplugd=gpuplugd.gpuplug:main',
            'gpuplug=gpuplug.gpuplug:main',
        ]
    }
)
