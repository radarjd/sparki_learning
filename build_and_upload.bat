echo "This should be run from inside the Thonny shell"
timeout /T 2 /NOBREAK

del /Q dist\*
python setup.py sdist bdist_wheel
python -m twine upload dist/*

