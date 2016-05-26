@echo off

set PATH=C:\Miniconda-x64;C:\Miniconda-x64\Scripts;%PATH%

conda create -y -n fomod-validator^
 -c https://conda.anaconda.org/mmcauliffe^
 -c https://conda.anaconda.org/anaconda^
 pyqt5=5.5.1 python=3.5.1 lxml=3.5.0
call activate fomod-validator
echo "Done activating."
python -m pip install pip -U
echo "Upgraded pip."
pip install setuptools -U --ignore-installed
echo "Upgraded setuptools."
pip install -r dev\reqs.txt
echo "Installed reqs."
