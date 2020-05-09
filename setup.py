import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymindiff", 
    version="1.0",
    author="Clément Lombard",
    author_email="clementlombard@orange.fr",
    description="A Python-package to create fair groups having minimal differences",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Simbamoureux/pymindiff",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)