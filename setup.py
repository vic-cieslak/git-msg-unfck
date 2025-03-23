from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="git-msg-unfck",
    version="0.1.0",
    author="git-msg-unfck Contributors",
    author_email="your.email@example.com",
    description="A CLI tool to improve Git commit messages using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/git-msg-unfck",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "unfck=src.cli:main",
        ],
    },
)
