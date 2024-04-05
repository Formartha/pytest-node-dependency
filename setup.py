from setuptools import setup

VERSION_NUMBER = "1.1.0"

# Load the README file as the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="pytest-node-dependency",
      version=VERSION_NUMBER,
      description="pytest plugin for controlling execution flow",
      long_description=long_description,  # Add the long_description field here
      long_description_content_type="text/markdown",  # Specify the content type
      include_package_data=True,
      author="Mor Dabastany",
      url="https://github.com/Formartha/pytest-node-dependency",
      packages=["pytest_node_dependency"],
      package_data={"pytest_node_dependency": ["*"]},
      entry_points={"pytest11": ["dependency = pytest_node_dependency.plugin"]},
      install_requires=["networkx"],
      license="MIT",
      keywords="pyest-node-dependency",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Pytest",
          "Intended Audience :: Developers",
          "Operating System :: POSIX",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: MacOS :: MacOS X",
          "Topic :: Software Development :: Quality Assurance",
          "Topic :: Software Development :: Testing",
          "Programming Language :: Python :: 3.11",
      ])
