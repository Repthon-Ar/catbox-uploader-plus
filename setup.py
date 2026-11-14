from setuptools import setup, find_packages
from pathlib import Path

BASE_DIR = Path(__file__).parent

long_description = (BASE_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="catbox-uploader-plus",
    version="2.9.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    install_requires=[
        "requests>=2.28.0",
    ],

    author="Baqir",
    description="An enhanced Python library for uploading files to Catbox and Litterbox.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/Repthon-Ar/catbox-uploader-plus",

    license="MIT",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    python_requires=">=3.8",

    keywords=[
        "catbox",
        "litterbox",
        "uploader",
        "file-upload",
        "python",
    ],
)
