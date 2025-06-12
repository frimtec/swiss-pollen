""" Set up script """
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here, "README.md"), "rb") as f:
    long_descr = f.read().decode("utf-8")

version = '0.0.0' if '$version'.startswith('$') else '$version'
setup(
    name="swiss-pollen",
    version=version,
    author="Markus Friedli",
    author_email="frimtec@gmx.ch",
    description="API to gather the current pollen load from MeteoSchweiz",
    long_description_content_type="text/markdown",
    long_description=long_descr,
    url="https://github.com/frimtec/swiss-pollen",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'swiss-pollen=swiss_pollen.main:main',
        ],
    },
    install_requires=["requests", "pytz"],
    include_package_data=True,
    python_requires=">=3.9",
    license="Apache-2.0",
    keywords="pollen swiss",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    zip_safe=True
)
