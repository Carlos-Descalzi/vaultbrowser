import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.readlines()

setuptools.setup(
    name="vaultbrowser",
    version="0.0.1",
    author="Carlos Descalzi",
    author_email="carlos.descalzi@gmail.com",
    description="A terminal-based HashiCorp's Vault client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Carlos-Descalzi/vaultbrowser",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["vaultbrowser = vaultbrowser.main:main"]},
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
