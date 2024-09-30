from setuptools import setup, find_packages

VERSION = "1.1.0"

setup(
    name="vidricur-workshop-control",
    version=VERSION,
    license="MIT",
    description="Vidricur Workshop Car Control",
    author="Simon Kaspar, Merima Hotic",
    author_email="simon.kaspar@fhnw.ch",
    url="",
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">=3.7"
)