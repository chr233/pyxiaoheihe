import setuptools
from pyxiaoheihe.static import PYXIAOHEIHE_VERSION

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyxiaoheihe",
    version=PYXIAOHEIHE_VERSION,
    author="Chr_",
    author_email="chr@chrxw.com",
    description="用Python实现的小黑盒客户端",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chr233/pyxiaoheihe",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'pyDes',
        'rsa'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
)
