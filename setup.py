from cx_Freeze import setup, Executable

setup(name = 'KiCAD_PLE',
		version = '0.2',
		description = 'Partslist Editor',
		executables = [Executable("SCH_TO_CSV_OOP.py")])