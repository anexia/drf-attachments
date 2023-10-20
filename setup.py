import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="drf-attachments",
    version=os.getenv("PACKAGE_VERSION", "0.2.1").replace("refs/tags/", ""),
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="A django module to manage any model's file up-/downloads by relating an Attachment model to it.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/anexia/drf-attachments",
    author="Alexandra Bruckner",
    author_email="abruckner@anexia-it.com",
    install_requires=[
        "python-magic>=0.4.18",
        "rest-framework-generic-relations>=2.0.0",
        "content-disposition>=1.1.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
