from setuptools import setup

setup(
    name='fomod-validator',
    version='1.2.0',
    license='Apache 2.0',
    description='',
    long_description='',
    author='Daniel Nunes',
    author_email='gandaganza@gmail.com',
    url='https://github.com/GandaG/fomod-validator',
    packages=['validator'],
    package_dir={'validator': 'fomod/validator'},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    keywords=[
        'fomod', 'valid', 'validator',
    ],
    install_requires=[
        'lxml',
    ],
)
