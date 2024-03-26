
import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent.resolve()

PACKAGE_NAME = "eevee"
AUTHOR = "Shaked Zychlinski"
AUTHOR_EMAIL = "shakedzy@gmail.com"
URL = "http://shakedzy.xyz/eevee-chat"
DOWNLOAD_URL = "https://pypi.org/project/eevee-chat/"

LICENSE = "CC BY-NC 4.0"
VERSION = (HERE / "VERSION").read_text(encoding="utf8").strip()
DESCRIPTION = "A single chat interface for multiple LLMs"
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf8")
LONG_DESC_TYPE = "text/markdown"

requirements = (HERE / "requirements.txt").read_text(encoding="utf8")
INSTALL_REQUIRES = [s.strip() for s in requirements.split("\n")]

CLASSIFIERS = [
    f"Programming Language :: Python :: 3.{str(v)}" for v in range(11, 13)
]
PYTHON_REQUIRES = ">=3.11"

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    classifiers=CLASSIFIERS,
    package_data={
        PACKAGE_NAME: ['resources/*'],  
    }
)
