import io
import os
from pathlib import Path
from setuptools import find_packages, setup


# Package meta-data.
NAME = 'model_training'
DESCRIPTION = 'Train classification model for diabetes'
URL = 'https://github.com/doaa-altarawy/ai-deployment-bootcamp'
EMAIL = 'doaa.altarawy@gmail.com'
AUTHOR = 'Doaa Altarawy'
REQUIRES_PYTHON = '>=3.8'


def read_requirements():
    """parses requirements from requirements.txt"""

    with open('requirements.txt') as f:
        req = f.readlines()
    return req

here = os.path.abspath(os.path.dirname(__file__))

# 'README.md' must be in MANIFEST.in
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Load the package's __version__.py module as a dictionary.
ROOT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = ROOT_DIR / NAME
about = {}
with open(PACKAGE_DIR / 'VERSION') as f:
    _version = f.read().strip()
    about['__version__'] = _version


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests', 'notebooks')),
    # package_data={'diabetes_model': []},
    install_requires=read_requirements(),
    extras_require={},
    include_package_data=True,
    license='BSD-3C',
    # entry_points={
    #         "console_scripts": ["qc-time-estimator=qc_time_estimator.cli:main"],
    # },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)