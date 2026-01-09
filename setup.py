import os
from setuptools import setup, find_packages

long_description = ""
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="mapborn",
    version="0.1.0",
    author="Your Name",
    author_email="your_email@example.com",
    description="A lightweight geographical plotting framework based on Matplotlib and GDAL.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # 自动寻找包
    packages=find_packages(),

    python_requires=">=3.8",

    # 依赖列表
    install_requires=[
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
    ],

    include_package_data=True,

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)