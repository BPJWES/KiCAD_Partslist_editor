from cx_Freeze import setup, Executable

setup(name = 'KiCAD_PLE',
		version = '18.0.1',
		description = 'Partslist Editor',
		executables = [Executable("PartsListEditor.py")])
