from cx_Freeze import setup, Executable
import os

os.environ['TCL_LIBRARY'] = r'C:\Users\berjan\AppData\Local\Programs\Python\Python36-32\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\berjan\AppData\Local\Programs\Python\Python36-32\tcl\tk8.6'

setup(name = 'KiCAD_PLE',
		version = '18.0.2',
		description = 'Partslist Editor',
		executables = [Executable("PartsListEditor.py")])
	