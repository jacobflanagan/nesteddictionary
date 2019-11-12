import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nesteddictionary-jacobflanagan", # Replace with your own username
    version="1.2.0",
    author="Jacob Flanagan",
    author_email="flanagan.jacob@gmail.com",
    description="Wrapper for the dict class that extends the functionality of nested dicts, includes mixed dicts and lists.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)