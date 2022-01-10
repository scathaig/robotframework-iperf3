from setuptools import setup, find_packages


with open('README.md') as f:
    README = f.read()


setup(
    name='robotframework_iperf3',
    version='1.1.0',
    description='Robot Framework Iperf3 library',
    long_description=README,
    author='Alexander Klose',
    author_email='alexander.klose@devzero.io',
    url='https://github.com/scathaig/robotframework-iperf3',
    python_requires=">=3.8",
    license='Apache License 2.0',
    install_requires=[
        'robotremoteserver>=1.1'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.8',
        'Framework :: Robot Framework :: Library',
    ],
    keywords='testing testautomation robotframework iperf iperf3',
    packages=find_packages(),
    include_package_data=True,
)
