from setuptools import setup, find_packages

setup(
    name="find404crawler",
    version="0.1.0",
    packages=find_packages(include="find404crawler*"),
    install_requires=[
        "playwright==1.50.0",
    ],
    author="Calle Rydén",
    author_email="charliegen@hotmail.se",
    description="A web crawler for finding 404 errors your page might link to",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/404finder-crawler",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
