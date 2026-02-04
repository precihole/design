from setuptools import setup, find_packages

try:
    with open("requirements.txt") as f:
        install_requires = [
            req.strip() for req in f.read().splitlines() if req.strip()
        ]
except FileNotFoundError:
    install_requires = []

# fallback-safe version handling
try:
    from design import __version__ as version
except ImportError:
    version = "0.0.1"

setup(
    name="design",
    version=version,
    description="for design department",
    author="Precihole",
    author_email="erpadmin@preciholesports.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
