"""
YANK is a testbed for experimenting with algorithms for the efficient computation of small molecule binding free energies to biomolecular targets using alchemical methods.
YANK is built on OpenMM, the API for molecular simulation, and uses its GPU-accelerated library implementation for hardware acceleration.
"""
from __future__ import print_function
import os
import sys
import distutils.extension
from setuptools import setup, Extension, find_packages
import glob
import os
from os.path import relpath, join
import subprocess
from Cython.Build import cythonize
DOCLINES = __doc__.split("\n")

########################
VERSION = "0.20.0"  # Primary base version of the build
DEVBUILD = None  # Dev build status, Either None or Integer as string
ISRELEASED = True  # Are we releasing this as a full cut?
__version__ = VERSION
########################
CLASSIFIERS = """\
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: The MIT License (MIT)
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Scientific/Engineering :: Bio-Informatics
Topic :: Scientific/Engineering :: Chemistry
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

################################################################################
# Writing version control information to the module
################################################################################


def git_version():
    # Return the git revision as a string
    # copied from numpy setup.py
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = 'Unknown'

    return GIT_REVISION


def write_version_py(filename='Yank/version.py'):
    cnt = """
# This file is automatically generated by setup.py
short_version = '{base_version:s}'
version = '{version:s}'
full_version = '{full_version:s}'
git_revision = '{git_revision:s}'
release = {isrelease:s}
"""
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of numpy.version messes up the build under Python 3.
    base_version = VERSION
    if DEVBUILD is not None and DEVBUILD != "None":
        local_version = base_version + ".dev" + DEVBUILD
    else:
        local_version = base_version
    full_version = local_version

    if os.path.exists('.git'):
        git_revision = git_version()
    else:
        git_revision = 'Unknown'

    if not ISRELEASED:
        full_version += '-' + git_revision[:7]

    a = open(filename, 'w')
    try:
        a.write(cnt.format(base_version=base_version,   # Base version e.g. X.Y.Z
                           version=local_version,       # Flushed out version, usually just base, but can be X.Y.Z.devN
                           full_version=full_version,   # Full version + git short hash, unless released
                           git_revision=git_revision,   # Matched full github hash
                           isrelease=str(ISRELEASED)))  # Released flag
    finally:
        a.close()

################################################################################
# USEFUL SUBROUTINES
################################################################################


def find_package_data(data_root, package_root):
    files = []
    for root, dirnames, filenames in os.walk(data_root):
        for fn in filenames:
            files.append(relpath(join(root, fn), package_root))
    return files


################################################################################
# SETUP
################################################################################

mixing_ext = distutils.extension.Extension("yank.mixing._mix_replicas", ['./Yank/mixing/_mix_replicas.pyx'])

write_version_py()
setup(
    name='yank',
    author='John Chodera',
    author_email='john.chodera@choderalab.org',
    description=DOCLINES[0],
    long_description="\n".join(DOCLINES[2:]),
    version=__version__,
    license='MIT',
    url='https://github.com/choderalab/yank',
    platforms=['Linux', 'Mac OS-X', 'Unix', 'Windows'],
    classifiers=CLASSIFIERS.splitlines(),
    package_dir={'yank': 'Yank'},
    packages=['yank', "yank.tests", "yank.tests.data", "yank.commands", "yank.mixing", "yank.reports", "yank.schema"], #+ ['yank.{}'.format(package) for package in find_packages('yank')],
    package_data={'yank': find_package_data('Yank/tests/data', 'yank') + ['reports/*.ipynb'],
                  },
    zip_safe=False,
    python_requires=">=3.5",
    install_requires=[
        'numpy',
        'scipy',
        'cython',
        'openmm>=7.1',
        'pymbar',
        'openmmtools>=0.13.4',
        'docopt>=0.6.1',
        'netcdf4',
        'cerberus',
        'openmoltools>=0.7.5',
        'mdtraj',
        'pyyaml',
        'pdbfixer'
        ],
    ext_modules=cythonize(mixing_ext),
    entry_points={'console_scripts': ['yank = yank.cli:main']})
