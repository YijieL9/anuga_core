#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

# Reference: https://github.com/kangwonlee/travis-yml-conda-posix-nt

set -e

# set env variables
export MINICONDA_PATH=$HOME/miniconda;
export MINICONDA_PATH_WIN=`cygpath --windows $MINICONDA_PATH`;
export MINICONDA_SUB_PATH=$MINICONDA_PATH/Scripts;
export MINICONDA_LIB_BIN_PATH=$MINICONDA_PATH/Library/bin;

# obtain miniconda installer
mkdir -p $HOME/download;

# Install openssl for Windows
choco install openssl.light -y;

# install miniconda
echo "checking if folder $MINICONDA_SUB_PATH does not exist"
echo "installing miniconda for windows";
choco install miniconda3 --params="'/JustMe /AddToPath:1 /D:$MINICONDA_PATH_WIN'";

# validate installation
echo "checking if folder $MINICONDA_SUB_PATH exists"
if [[ -d $MINICONDA_SUB_PATH ]]; then
    echo "folder $MINICONDA_SUB_PATH exists"
else
    echo "folder $MINICONDA_SUB_PATH does not exist"
fi;

source $MINICONDA_PATH/etc/profile.d/conda.sh;
hash -r;
conda config --set always_yes yes --set changeps1 no
conda update -q conda -y;


# Configure the conda environment and put it in the path using the
# provided versions
echo "###########################################################"
echo "create virtual env & installing packages"
conda create -n anuga -c conda-forge python=2.7 pip numpy scipy gdal dill cython future openmp gitpython -y
conda activate anuga
conda info --env

echo "###########################################################"
echo "start installing mpi4py"
pip install mpi4py



#########################################################
# Build and install anuga
echo "###########################################################"
echo "start Building!!!!!"
echo "###########################################################"
python setup.py build

echo "###########################################################"
echo "start Building!!!!!"
echo "###########################################################"
python setup.py install
