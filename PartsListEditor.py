
# TODO 3: make suggested filenames
# TODO 4: autogenerate filename for KiCAD_PLE_BOM.csv
# TODO 2: Build Windows Executable

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from configparser import ConfigParser
import os

import debugtrace as DT

import kicadple
import globals

DT.setLevel(4)

version = "21.0.1"

mainSchematicFile = kicadple.Schematic()
csvFile = kicadple.CsvFile()
initialDirectory = "" 
fieldsConfigFile = "FieldKeywords.conf"
fieldList = [];


def read_settings():
	try:
		f = open(fieldsConfigFile)
		
	except IOError:
		DT.error("can\'t find file or read data")
	configfile = f.readlines()
	if "KiCAD PLE Config file v1.1" in configfile[0]:
		
		for line in range(1, len(configfile)-1):
			initPos =1
			newField = kicadple.KicadField()
			if configfile[line][0] == "<" and configfile[line][-2] == ">":
				endPos = configfile[line].find("|");
				
				newField.name = configfile[line][initPos:endPos]
				newField.appendAlias(newField.name)
				initPos = endPos
				endPos = configfile[line].find("|",initPos+1);
				while not endPos == -1:
				
					newField.appendAlias(configfile[line][initPos+1:endPos])
					initPos = endPos
					endPos = configfile[line].find("|",initPos+1);
					
				newField.appendAlias(configfile[line][initPos+1:-2])
				
			global fieldList
			fieldList.append(newField)
			
		
	else:
		DT.error("incorrect config file")

def load_schematic():
	DT.clear()
	globals.ParsedSchematicFiles = [] # clear this list.

	config = ConfigParser()
	config.read('config.ini')
    
	initialDirectory = config.get('main', 'lastDirectory', fallback="")

	if initialDirectory == "": 
		root.filename = filedialog.askopenfilename(filetypes = (("KiCAD Schematic Files",".sch"),("All Files", ".*")))
	else:
		root.filename = filedialog.askopenfilename(initialdir = initialDirectory, filetypes = (("KiCAD Schematic Files",".sch"),("All Files", ".*")))
	filename = root.filename
	root.lastSchematicFileName = filename


	config.read('config.ini')
	if config.has_section('main') == FALSE:
		config.add_section('main')
	config.set('main', 'lastDirectory', os.path.dirname(filename))

	globals.CsvSeparator = config.get('main', 'csvSeparator', fallback=",")
	if globals.CsvSeparator is ",":
		config.set('main', 'csvSeparator', globals.CsvSeparator)

	with open('config.ini', 'w') as f:
		config.write(f)

	
	if filename[-4:] == ".sch" or filename[-4:] == ".SCH":
		try:
			f = open(filename)
		except IOError:
			DT.error("can\'t find file or read data")
		else:
			mainSchematicFile.setPath(filename)
			dataTestDump = f.readlines()[0]
			f.close()

		if dataTestDump[:-1] == "EESchema Schematic File Version 2" or dataTestDump[:-1] == "EESchema Schematic File Version 4": # support for KiCad4 and KiCad5
			# TODO 2: move the laoding of a schematic file into the Schematic class!
			# --> make use of recursive loading of schematics

			#verify it conforms to KiCAD specs
			if mainSchematicFile.components:
				mainSchematicFile.deleteContents()
			try:
				f = open(filename)
			except IOError:
				DT.error("can\'t find file or read data")
			else:
				mainSchematicFile.SetContents(f.readlines())
				mainSchematicFile.fieldList = fieldList;

				mainSchematicFile.schematicName = os.path.basename(filename)

				f.close()
				if mainSchematicFile.ParseComponents():
					if(len(mainSchematicFile.getSubCircuits()) != len(mainSchematicFile.getSubCircuitName())):
						messagebox.showerror("FileParseError", "Hierarchical schematics could not be found")
					else:
						messagebox.showerror("FileParseError", "This is not a valid KiCAD schematic document.")

		else:
			messagebox.showerror("FileParseError", "This is not a valid KiCAD schematic document.")

	else:
		if filename:
			messagebox.showerror("FileParseError", "This is not a valid KiCAD schematic document (*.sch or *.SCH)")


	for i in range (len(mainSchematicFile.components)):
		if "?" in mainSchematicFile.components[i].getReference():
			if messagebox.askyesno("Annotation Incomplete",
                    "The program is unable to process unanotated components. Do you want to clear imported data?"):
				mainSchematicFile.deleteContents()
			break
	root.initialDirectory = set_initial_directory(filename)

	if mainSchematicFile.schematicName:
		unlistedCount = 0
		for c in mainSchematicFile.components:
			if c.unlisted:
				unlistedCount += 1


		statusLabel['text'] = "Loaded schematic: " + mainSchematicFile.schematicName + "\n" +\
							  str(len(mainSchematicFile.components) - unlistedCount ) +\
							  " + " + str(unlistedCount) + " hidden components were found"
	else:
		statusLabel['text'] = "Start by loading a KiCad schematic file..."

	print("Summary of loading schematic: ")
	DT.summary()

	
	
def set_initial_directory(filename):
	mainSchematicFile.schematicName = os.path.basename(filename)
	return os.path.dirname(filename)


def generate_csv():
	DT.clear()
	initialDirectory = root.initialDirectory
	if len(mainSchematicFile.components) > 0:
		root.path_to_save = filedialog.asksaveasfilename(initialdir = initialDirectory, filetypes = (("Comma seperated values", ".csv"),("All Files",".*")))
		root.initialDirectory = set_initial_directory(root.path_to_save)
		sort_parts()
		if mainSchematicFile.exportCsvFile(root.path_to_save):
			messagebox.showerror("File IOerror", "The file might still be opened")
		else:
			statusLabel['text'] = "Saved: " + str(root.path_to_save)
	else:
		messagebox.showerror("Cannot generate .CSV", "No SCH File loaded")
	DT.summary()


def my_break():
	root.quit()

def list_parts():
	if len(mainSchematicFile.components) != 0:
		sub  = Tk()
		height = len(mainSchematicFile.components)

		for i in range(height): #Rows
				b = Entry(sub, text="")
				b.grid(row=i, column=1)
				b.insert(0, mainSchematicFile.components[i].getReference())

				c = Entry(sub, text="")
				c.grid(row=i, column=2)
				c.insert(0, mainSchematicFile.components[i].getName())

				d = Entry(sub, text="")
				d.grid(row=i, column=3)
				#d.insert(0,mainFile.components[i].GetFarnellLink())
				d.insert(0,"deprecated")

def checklower(lowest_known, to_compare):
	#returns 1 if lower
	for i in range(len(lowest_known)):
		if i  == len(to_compare):
			return 1 #to compare is shorter i.e. lower

		if lowest_known[i] < to_compare[i]:
			if lowest_known[i].isdigit() and to_compare[i].isdigit():
				if len(to_compare) < len(lowest_known):
					return 1 #if to_compare is shorter but a digit in the string is higher than it is still lower
			return 0
		if lowest_known[i] > to_compare[i]:
			
			if lowest_known[i].isdigit() and to_compare[i].isdigit():
				if len(lowest_known) == len(to_compare):
					return 1
				if len(lowest_known) < len(to_compare):
					return 0 #if lowest_known is shorter but digit is higher then lowest known is still lower
			else:
				return 1
	return 0

def sort_list(this_list):
	sortedList = []
	lowest_known = "zzzzzzz"
	position = 0

	for i in range(len(this_list)):

		for p in range(i,len(this_list)):

			if checklower(lowest_known,this_list[p]):
				lowest_known = this_list[p]
				position = p

		this_list[i] , this_list[position] = this_list[position] , this_list[i]
		lowest_known = "zzzzzzz"

	sortedList = this_list

	return sortedList

def sort_parts():
	componentNameList = []
	for i in range (len(mainSchematicFile.components)):
		componentNameList.append(mainSchematicFile.components[i].getReference())
	sort_list(componentNameList)
	for i in range (len(mainSchematicFile.components)):
		for p in range(i, len(mainSchematicFile.components)):
			if componentNameList[i] == mainSchematicFile.components[p].getReference():
				mainSchematicFile.SwapComponents(i, p)


def load_csv():
	DT.clear()

	config = ConfigParser()
	config.read('config.ini')

	initialDirectory = config.get('main', 'lastDirectory', fallback="")

	#mainSchematicFile.printprops()
	if initialDirectory == "":
		root.filename = filedialog.askopenfilename(
			filetypes=(("KiCAD Partslist-editor files", ".csv"), ("All Files", ".*")))
	else:
		root.filename = filedialog.askopenfilename(initialdir=initialDirectory, filetypes=(
		("KiCAD Partslist-editor files", ".csv"), ("All Files", ".*")))

	filename = root.filename

	config.read('config.ini')
	if config.has_section('main') == FALSE:
		config.add_section('main')
	config.set('main', 'lastDirectory', os.path.dirname(filename))

	globals.CsvSeparator = config.get('main', 'csvSeparator', fallback=",")
	if globals.CsvSeparator is ",":
		config.set('main', 'csvSeparator', globals.CsvSeparator)

	with open('config.ini', 'w') as f:
		config.write(f)

	
	if filename[-4:] == ".csv" or filename[-4:] == ".CSV":
		try:
			f = open(filename)
		except IOError:
			messagebox.showerror("File IO Error", "Cannot open CSV File " + filename)
		else:
			f.close()


		if csvFile.components:
			csvFile.deleteContents()

		f = open(filename)

		csvFile.setContents(f.readlines())

		error = csvFile.extractCsvComponents()
		if error:
			messagebox.showerror("Incorrect Fileformat", error)
		else:
			statusLabel['text'] = "Import: " + str(root.filename) + " complete" + "\n" +  str(len(csvFile.components)) + " components were imported"

		f.close()

	else:
		if filename:
			messagebox.showerror("FileParseError", "This is not a valid CSV document (*.csv or *.CSV)")

	print("Summary for importing from CSV: ")
	DT.summary()

	DT.info(str(len(csvFile.components)) + ' components were imported from CSV')

	
def build_new_schematic():
	DT.clear()

	initialDirectory = root.initialDirectory
	if mainSchematicFile.components and csvFile.components:
		print(root.lastSchematicFileName)
		savePath = filedialog.asksaveasfilename(initialfile = root.lastSchematicFileName, filetypes = (("KiCAD Schematic File", ".sch"),("All Files",".*")))
		
		if savePath:
			if mainSchematicFile.ModifyNewSCHFile(0, csvFile, savePath):
				messagebox.showerror("File IO Error", ".SCH cannot be edited")
			else:
				statusLabel['text'] = str(savePath) + " updated with new field values"
	else:
		if mainSchematicFile.components:
			messagebox.showerror("Processing Error", "No CSV File Loaded")
		elif csvFile.components:
			messagebox.showerror("Processing Error", "No SCH File Loaded")
		else:
			messagebox.showerror("Processing Error", "No Files Loaded")

	print("Summary for writing to schematic files: ")
	DT.summary()
			
			
def clean_memory():
	mainSchematicFile.deleteContents()
	csvFile.deleteContents()
	statusLabel['text'] = "Memory cleared \n All stored components deleted!"

def show_about_dialog():
	messagebox.showinfo("KiCad Partslist Editor V"+version, "Use this tool to comfortably modify many parts fields in your favourite spreadsheet programm (e.g. LibreOffice Calc)\n" +
						"Written by BPJWES, 2016\n" +
						"and Karl Zeilhofer, 2017-2018\n" +
						"https://github.com/BPJWES/KiCAD_Partslist_editor")

root = Tk()

root.initialDirectory = ""
root.configure(background='white')
root.title("KiCad Partslist Editor V" + version)
root.bind("<Escape>", lambda e: e.widget.quit())
background_image = PhotoImage(file="KICAD_PLE.png")
background = Label(root, image=background_image, bd=0)
background.grid(row = 0, column = 0, columnspan = 3, rowspan = 1, padx = 5, pady = 5)
read_settings()


b = ttk.Button(root, text="Load Schematic", command=load_schematic)
b.grid(row = 1, column = 0, columnspan = 1, rowspan = 1, padx = 5, pady = 5, )

g = ttk.Button(root, text="Save Schematic", command=build_new_schematic)
g.grid(row = 2, column = 0, columnspan = 1, rowspan = 1, padx = 5, pady = 5)


c = ttk.Button(root, text="Export CSV", command=generate_csv)
c.grid(row = 1, column = 1, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

f = ttk.Button(root, text="Import CSV", command=load_csv)
f.grid(row = 2, column = 1, columnspan = 1, rowspan = 1, padx = 5, pady = 5)


d = ttk.Button(root, text="List Parts", command=list_parts)
d.grid(row = 1, column = 2, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

e = ttk.Button(root, text="Sort Parts", command=sort_parts)
e.grid(row = 2, column = 2, columnspan = 1, rowspan = 1, padx = 5, pady = 5)


b = ttk.Button(root, text="About", command=show_about_dialog)
b.grid(row = 3, column = 2, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

h = ttk.Button(root, text="Clear Component Memory", command=clean_memory)
h.grid(row = 3, column = 1, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

#i = ttk.Button(root, text="Exit", command=Break)
#i.grid(row = 5, column = 2, columnspan = 1, rowspan = 1, padx = 5, pady = 5)

statusLabel = ttk.Label(root, text="Start by loading a KiCad schematic file...")
statusLabel['background'] = "white"
statusLabel.grid(row = 4, column = 0, columnspan = 3, rowspan = 1, padx = 5, pady = 5)


mainloop()
