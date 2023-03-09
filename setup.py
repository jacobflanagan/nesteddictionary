import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nesteddictionary",
    version="1.2.2",
    author="Jacob Flanagan",
    author_email="flanagan.jacob@gmail.com",
    description="Wrapper for the dict class that extends the functionality for nested dicts including navigating using keypaths and nested key searching. This includes mixed dicts and lists.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jacobflanagan/nesteddictionary",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)