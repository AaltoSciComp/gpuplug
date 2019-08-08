from setuptools import setup
import subprocess

systemd_service_path = subprocess.check_output(
    ['pkg-config', '--variable=systemdsystemunitdir', 'systemd']
).decode('utf-8').rstrip()

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
    },
    data_files = [
        ('/etc/', ['gpuplugd.conf']),
        (systemd_service_path, ['gpuplugd.service']),
    ],
)
