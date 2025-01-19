from setuptools import setup, find_packages

setup(
    name="textmap",
    version="0.1.0",
    packages=find_packages(),
       install_requires=[
        "typing-extensions>=4.0.0",
        "chardet>=4.0.0",
    ],
    entry_points={
        'console_scripts': [
            'textmap=textmap.cli:main',
        ],
    },
    author="Your Name",
    description="A utility for secure information mapping within text",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/textmap",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
