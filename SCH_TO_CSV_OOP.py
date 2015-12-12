import SCH_TO_CSV_OOP_LIB
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

mainFile = SCH_TO_CSV_OOP_LIB.SCH_FILE()
openCSVFile = SCH_TO_CSV_OOP_LIB.CSV_FILE()
def OpenFile():
    #print "click!"
	root.filename = filedialog.askopenfilename(filetypes = (("KiCAD Schematic Files",".sch"),("All Files", ".*")))
	filename = root.filename
	root.SCHFILELAST = filename
	if filename[-4:] == ".sch" or filename[-4:] == ".SCH":
		try:
			f = open(filename)
		except IOError:
			print("Error: can\'t find file or read data")
		else:
			mainFile.setPath(filename)
			data_test_dump = f.readlines()[0]
			f.close()

		if data_test_dump[:-1] == "EESchema Schematic File Version 2":
			#verify it conforms to KiCAD specs
			if mainFile.getComponents():
				#print(mainFile.getComponents())
				#print("am deleting")
				mainFile.deleteContents()

				#print(mainFile.getComponents())
			try:
				f = open(filename)
			except IOError:
				print("Error: can\'t find file or read data")
			else:
				mainFile.SetContents(f.readlines())
				mainFile.setSchematicName("FlowRateControllerV2.sch")
				f.close()
				if mainFile.ParseComponents():
					messagebox.showerror("FileParseError", "This is not a valid KiCAD schematic document.")
		else:
			messagebox.showerror("FileParseError", "This is not a valid KiCAD schematic document.")

	else:
		if filename:
			messagebox.showerror("FileParseError", "This is not a valid KiCAD schematic document.")

	for i in range (len(mainFile.getComponents())):
		if "?" in mainFile.getComponents()[i].GetAnnotation():
			messagebox.showerror("Annotation Incomplete", "The program is unable to process unanotated components")
			mainFile.deleteContents()
			break
	#mainFile.printprops()
def GenerateCSV():
	if mainFile.get_number_of_components() > 0:
		root.path_to_save = filedialog.asksaveasfilename(filetypes = (("Comma seperated values", ".csv"),("All Files",".*")))
		sortParts()
		if mainFile.SaveBOMInCSV(root.path_to_save):
			messagebox.showerror("File IOerror", "The file might still be opened")
	else:
		messagebox.showerror("Cannot generate .CSV", "No SCH File loaded")
def Break():
	root.quit()

def listParts():
	#print("test") this somehow get executed
	#print("hoi")
	if mainFile.get_number_of_components() != 0:
		sub  = Tk()
		height = mainFile.get_number_of_components()

		for i in range(height): #Rows
				b = Entry(sub, text="")
				b.grid(row=i, column=1)
				b.insert(0,mainFile.getComponents()[i].GetAnnotation())

				c = Entry(sub, text="")
				c.grid(row=i, column=2)
				c.insert(0,mainFile.getComponents()[i].GetName())

				d = Entry(sub, text="")
				d.grid(row=i, column=3)
				d.insert(0,mainFile.getComponents()[i].GetFarnellLink())

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
			#print("2hier return hij")
			if lowest_known[i].isdigit() and to_compare[i].isdigit():
				if len(lowest_known) == len(to_compare):
					return 1
				if len(lowest_known) < len(to_compare):
					return 0 #if lowest_known is shorter but digit is higher then lowest known is still lower
			else:
				return 1
	return 0

def sortList(this_list):
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

	sortList = this_list

	return sortedList

def sortParts():
	mainFile.get_number_of_components()
	componentNameList = []
	for i in range (mainFile.get_number_of_components()):
		componentNameList.append(mainFile.getComponents()[i].GetAnnotation())
	sortList(componentNameList)
	for i in range (mainFile.get_number_of_components()):
		for p in range(i, mainFile.get_number_of_components()):
			if componentNameList[i] == mainFile.getComponents()[p].GetAnnotation():
				mainFile.SwapComponents(i,p)

def loadCSV():
	#print("tbg")
	root.filename = filedialog.askopenfilename(filetypes = (("KiCAD Partslist-editor files",".csv"),("All Files", ".*")))
	filename = root.filename
	if filename[-4:] == ".csv" or filename[-4:] == ".CSV":
		try:
			f = open(filename)
		except IOError:
			messagebox.showerror("File IO Error", ".SCH cannot be edited")
		else:
			data_test_dump = f.readlines()[0]
			f.close()
			#print(data_test_dump)

		if "Part\#,PartType,FarnellLink,MouserLink,DigiKeyLink" in data_test_dump:
			#verify it conforms to KiCAD Partslist-editor specs
			if openCSVFile.getComponents():
				openCSVFile.deleteContents()

			f = open(filename)

			openCSVFile.setContents(f.readlines())
			#openCSVFile.printContents()
			#openCSVFile.printLine(1)

			openCSVFile.generateCSVComponents()
			#openCSVFile.printComponents()
			#for i in range (len(mainFile.getComponents())):
			#	print(mainFile.getComponents()[i].GetAnnotation())
			#mainFile.ModifyNewSCHFile(0, openCSVFile)

			f.close()
			#mainFile.ParseComponents()
		else:
			messagebox.showerror("FileParseError", "This is not a valid CSV document.")

	else:
		if filename:
			messagebox.showerror("FileParseError", "This is not a valid CSV document.")
#	for i in openCSVFile.getComponents():
#		i.printprops()
def BuildNewSCH():
	if mainFile.getComponents() and openCSVFile.getComponents():
		print(root.SCHFILELAST)
		savePath = filedialog.asksaveasfilename(initialdir = root.SCHFILELAST, initialfile = root.SCHFILELAST, filetypes = (("KiCAD Schematic File", ".sch"),("All Files",".*")))
		if savePath:
			if mainFile.ModifyNewSCHFile(0, openCSVFile,savePath):
				messagebox.showerror("File IO Error", ".SCH cannot be edited")
	else:
		if mainFile.getComponents():
			messagebox.showerror("Processing Error", "No CSV File Loaded")
		elif openCSVFile.getComponents():
			messagebox.showerror("Processing Error", "No SCH File Loaded")
		else:
			messagebox.showerror("Processing Error", "No Files Loaded")

def CleanMemory():
	mainFile.deleteContents()
	openCSVFile.deleteContents()
root = Tk()

#def mainloop():


root.configure(background='white')
root.title("KiCAD Partslist-editor")
root.bind("<Escape>", lambda e: e.widget.quit())
background_image = PhotoImage(file="KICAD_PLE.png")
background = Label(root, image=background_image, bd=0)
background.pack()

b = ttk.Button(root, text="Open File", command=OpenFile)
b.pack()
c = ttk.Button(root, text="Generate CSV", command=GenerateCSV)
c.pack()
d = ttk.Button(root, text="List Parts", command=listParts)
d.pack()
e = ttk.Button(root, text="Sort Parts", command = sortParts)
e.pack()
f = ttk.Button(root, text="LoadCSV", command=loadCSV)
f.pack()
g = ttk.Button(root, text="SaveNewSCH", command=BuildNewSCH)
g.pack()
h = ttk.Button(root, text="CleanMemory", command=CleanMemory)
h.pack()
i = ttk.Button(root, text="End", command=Break)
i.pack()

#while 1:
#	root.update()
#	print("hoi")
# this is supposed to enable interactive interface (show if
mainloop()
