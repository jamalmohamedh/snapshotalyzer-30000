from setuptools import setup

setup(
    name='jammy',
    version='0.1',
    author='Jamal Mohamed H',
    author_email='jamalmohamed.95@gmail.com',
    description='AWS Snapshot Program',
    License='GPLv3+',
    packages=['jammy'],
    url="https://github.com/jamalmohamedh/snapshotalyzer-30000",
    install_requires=[
    'click',
    'boto3'
    ],
    entry_points='''
        [console_scripts]
        jammy=jammy.shotty:cli
        ''',
)
