"""setup script"""
from setuptools import setup, find_packages
import os
import glob

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md")) as f:
    long_description = f.read()

with open(os.path.join(this_directory, "requirements.txt")) as f:
    requirements = f.readlines()

setup(
    name="owid-data-utils",
    version="0.0.1.dev0",
    description="Data utils library by the Data Team at Our World in Data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/owid/data-utils-py",
    author="Lucas Rodés-Guirao",
    license="GPL-v3",
    install_requires=requirements,
    # extras_require={"gpu": ["tensorflow-gpu==1.3.0"]},
    packages=find_packages('.'),
    package_dir={'': '.'},
    # namespace_packages=['koalarization'],
    # py_modules=[
    #     os.path.splitext(os.path.basename(path))[0] for path in glob.glob("owid/datautils/*.py")
    # ],
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob.glob('./*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="our world in data, data cleaning, data processing, data processing, data utils",
    project_urls={
        "Github": "http://github.com/owid/data-utils-py",
        'Bug Tracker': 'https://github.com/owid/data-utils-py/issues',
    },
    python_requires=">=3.10",
)
