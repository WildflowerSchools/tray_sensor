from setuptools import setup, find_packages

setup(
    name='tray_sensor',
    packages=find_packages(),
    version='0.0.1',
    include_package_data=True,
    description='Python package for communicating with Wildflower tray sensors through BLE interface',
    long_description=open('README.md').read(),
    url='https://github.com/WildflowerSchools/tray_sensor',
    author='Ted Quinn',
    author_email='ted.quinn@wildflowerschools.org',
    install_requires=[
        'bluepy==1.3.0',
        'tenacity==5.0.3',
        'bitstruct==6.0.0'
    ],
    keywords=['bluetooth'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Linux',
        'Programming Language :: Python',
    ]
)
