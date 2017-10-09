

import component


class SchematicFile(object):
	def __init__(self):
		self.contents = ""
		self.numb_of_comps = 0
		self.subcircuits_names = []
		self.number_of_subcircuits = 0
		self.components = []
		self.subcircuits = []
		self.SchematicName = ""
		self.path = ""
		self.fieldList = ""

	def setPath(self, path):
		self.path = path

	def getPath(self):
		return self.path

	def setSchematicName(self, x):
		self.SchematicName = x

	def getSchematicName(self):
		return self.SchematicName

	def SetContents(self,content):
		#load the contents of the .sch file
		self.contents = content

	def SwapComponents(self, i, j):
		self.components[i] , self.components[j] = self.components[j] , self.components[i]

	def number_of_components(self , x):
		self.numb_of_comps = x

	def get_number_of_components(self):
		return self.numb_of_comps

	def getComponents(self):
		return self.components

	def getLastComponent(self):
		last_position = len(self.getComponents())-1
		return self.components[last_position]

	def append_subcircuit(self, subcircuit_instance):
		self.subcircuits.append(subcircuit_instance)

	def appendComponent(self,component):
		self.components.append(component)
		self.numb_of_comps = self.numb_of_comps + 1

	def printprops(self):
		print(self.numb_of_comps)
		print(self.components)
		print(self.subcircuits_names)
		print(self.number_of_subcircuits)
		print(self.SchematicName)

	def ParseSubCircuits(self):
		content = self.contents
		ListOfSubSchematics = []
		for count in range(len(content)):
			if "$Sheet" in content[count]:
				for subcounter in range(10):
					# TODO 1: this is very bad style of parsing the lines. Fix this!
					# it leads to an "out of range" if $EndSheet comes before count+subcounter
					if count+subcounter < len(content) and "F1 " in content[count+subcounter]: # added a quick-fix to the problem described above!
						#print(content[count+subcounter])
						test_var = 0
						for p in range(len(content[count+subcounter])):
							if content[count+subcounter][p] == "\"":
								if test_var == 0:
									startOfString = p+1
									test_var = 1
									#print(p)
								else:
									endOfString = p
									break
						if startOfString != 0:
							ListOfSubSchematics.append(content[count+subcounter][startOfString:endOfString])
		self.subcircuits_names = ListOfSubSchematics
		self.number_of_subcircuits = len(ListOfSubSchematics)

	def ParseComponents(self):
		if self.subcircuits_names == []:
			self.ParseSubCircuits()
		content = self.contents
		for count in range(len(content)):
			if "$Comp" in content[count]:
				test_var = count

				while not "$EndComp" in content[count]:
					if "#" in content[test_var+1]:
						break
					if count == test_var:
						self.components.append(Component())
						self.number_of_components(self.get_number_of_components() + 1)
						LastComponent = self.getLastComponent()
						LastComponent.startpos(count)
						LastComponent.SetSchematicName(self.getSchematicName())
						LastComponent.fieldList = self.fieldList

					if content[count][0] == "L":
							i = 0
							for i in range(len(content[count])):
								if content[count][len(content[count])-(i+1)] == " ":
									LastComponent.setAnnotation(content[count][-(i):-1])
									LastComponent.SetName(content[count][2:-(i+1)])
									break

					if "F 1 " in content[count] : #find f1 indicating value field in EEschema file format
						testvar = 0

						for i in range(len(content[count])):
							if content[count][i] == "\"":
								if testvar == 0:
									startOfString = i+1
									testvar = 1
								else:
									endOfString = i

									break
						LastComponent.setValue(content[count][startOfString:endOfString])

					count = count + 1
				if not "#" in content[test_var+1]:
					#ListOfFarnellLinks.append("")

					LastComponent.endpos(count)
					LastComponent.Contents = content[LastComponent.startposition:LastComponent.endposition]
					LastComponent.generateProperties()
			#		print("parsed")
				if test_var > 100000: # prevents fails
					break

		for subcircuitcounter in range(len(self.subcircuits_names)):


			#print("subcircuit")
			#for p in range (len(self.path)):
			#	if self.path[-p] == "/":
			#		break
			#to_open = self.path[:-p+1] + self.subcircuits_names[subcircuitcounter]
			to_open = os.path.join(os.path.dirname(self.path), self.subcircuits_names[subcircuitcounter])
			try:
				f = open(to_open)
			except IOError:
				return "error"
			else:
				self.append_subcircuit(SchematicFile())
				self.get_subcircuit(subcircuitcounter).setPath(to_open)
				self.get_subcircuit(subcircuitcounter).SetContents(f.readlines())
				f.close()
				self.get_subcircuit(subcircuitcounter).setSchematicName(self.subcircuits_names[subcircuitcounter])
				self.get_subcircuit(subcircuitcounter).fieldList = self.fieldList
				self.get_subcircuit(subcircuitcounter).ParseComponents()
				self.AppendComponents(self.get_subcircuit(subcircuitcounter).getComponents())
	def get_subcircuit(self, x):
		return self.subcircuits[x]

	def AppendComponents(self, componentList):
		for item in range(len(componentList)):
			self.components.append(componentList[item])
			self.numb_of_comps = self.get_number_of_components() + 1

	def SaveBOMInCSV(self,savepath):
	#New variant which allows for user configurable field names
		if not '.csv' in savepath:
			savepath = savepath + '.csv'
		try:
			f = open(savepath, 'w')
		except IOError:
			if savepath:
				return "error"
		else:
			f.write("Part\#")
			f.write(",")
			f.write("PartType")
			f.write(",")
			for field in self.fieldList:
				f.write(field.name)
				f.write(",")
			f.write("Found in: ")
			f.write("\n")
			for item in range(self.get_number_of_components()):
				#Add Line with component and fields
				f.write(self.getComponents()[item].GetAnnotation())
				f.write(",")
				f.write(self.getComponents()[item].GetName())
				f.write(",")
				for field in self.fieldList:
				#match fields to component.field
					for counter in range(len(self.getComponents()[item].PropertyList)):
						if self.getComponents()[item].PropertyList[counter][0] == field.name:
							f.write(self.getComponents()[item].PropertyList[counter][1])
							f.write(",")
							break
					else:
						f.write("")
						f.write(",")
				f.write(self.getComponents()[item].GetSchematicName())
				f.write("\n")
			f.close

	def getSubCircuitName(self):
		return self.subcircuits_names

	def getSubCircuits(self):
		return self.subcircuits

	def ModifyNewSCHFile(self, oldSCHFile, CSV_FILE, savepath):
		# this did break if the order is not FarnellLink; MouserLink; DigiKeyLink
		# should be fixed now but am not sure

		print("Number of Parts in CSV: " + str(CSV_FILE.getNumberOfComponents()))
		print("Number of Parts in this SCH: " + str(self.get_number_of_components()))

		if CSV_FILE.getNumberOfComponents() and self.get_number_of_components():

			for i in range (CSV_FILE.getNumberOfComponents()):#Loop over csv_components
				for p in range (self.get_number_of_components()):#loop over .sch components
					if CSV_FILE.getComponents()[i].getAnnotation() == self.getComponents()[p].GetAnnotation() and self.SchematicName ==  CSV_FILE.getComponents()[i].getSchematic(): #if annotation and schematic name match

						selected_component = self.getComponents()[p]
						selected_component.addNewInfo(CSV_FILE.getComponents()[i].PropertyList)

						for property in range(len(selected_component.PropertyList)):

							if not selected_component.PropertyList[property][3] == 0: #Not exists for adding fields through .csv
							#Datafield existed in original file

								self.contents[selected_component.startposition+selected_component.PropertyList[property][3]] = selected_component.PropertyList[property][2]
							else:
								self.contents[selected_component.startposition+selected_component.lastContentLine] = self.contents[selected_component.startposition+selected_component.lastContentLine] + selected_component.generatePropertyLine(property)
							#datafield not in original file
			try:
				f = open(savepath, 'w')
			except IOError:
				return "error"
			else:
				for i in range (len(self.contents)):
					f.write(self.contents[i])
				f.close

			for i in range(len(self.subcircuits)):
				new_savepath = os.path.join(os.path.dirname(savepath), self.subcircuits_names[i])
				print(new_savepath)
				self.subcircuits[i].ModifyNewSCHFile(0, CSV_FILE, new_savepath)
				#mainFile.ModifyNewSCHFile(0, openCSVFile,savePath):
		else:
			print("No components loaded")

	def deleteContents(self):
		for p in range (len(self.subcircuits)):
			# first delete subcircuits
			self.subcircuits[0].deleteContents()

		for i in range (len(self.components)):
			del self.components[0]
		self.contents = ""
		self.numb_of_comps = 0
		self.subcircuits_names = []
		self.number_of_subcircuits = 0
		self.components = []
		self.subcircuits = []
		self.SchematicName = ""
		self.path = ""

