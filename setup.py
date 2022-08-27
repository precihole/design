from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in design/__init__.py
from design import __version__ as version

setup(
	name="design",
	version=version,
	description="for design department",
	author="Rehan Ansari",
	author_email="rehan@preciholesports.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
