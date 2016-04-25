from setuptools import setup

setup(
    name='fomod-validator',
    version='1.1.1',
    packages=['validator'],
    package_dir={'validator': 'fomod/validator'},
    url='https://github.com/GandaG/fomod-validator',
    license='Apache 2.0',
    author='Daniel Nunes',
    author_email='gandaganza@gmail.com',
    description='Validate your FOMOD installers.',
    install_requires=['lxml'],
)
