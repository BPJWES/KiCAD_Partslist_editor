class Component(object):
	def __init__(self):
		self.startposition = 0
		self.endposition = 0
		self.SchematicName = ""
		self.name = ""
		self.annotation = ""
		self.value = ""
		# refactor the field extraction
		self.PropertyList = []
		self.Contents = ""
		self.fieldList = [];
		self.lastContentLine = 0
		self.lastFieldLineNr = 0
	def startpos(self, x):
		self.startposition = x
	def endpos(self,x):
		self.endposition = x
	def SetName(self,x):
		self.name = x
	def GetName(self):
		return self.name
	def SetAnnotation(self ,x):
		self.annotation = x
	def GetAnnotation(self):
		return self.annotation
	def Value(self,x):
		self.value = x
	def GetValue(self):
		return self.value	
	def printprops(self):
		print(self.name)
		print(self.annotation)
		print(self.value)
		print(self.SchematicName)
	def printall(self):
		print(self.startposition)
		print(self.endposition)
		print(self.name)
		print(self.annotation)
		print(self.value)
		print(self.SchematicName)
	def SetSchematicName(self, schematic_name):
		self.SchematicName = schematic_name
	def GetSchematicName(self):
		return self.SchematicName
	def getStartLine(self):
		return self.startposition
	def getEndLine(self):
		return self.endposition
	def generateProperties(self):
		#parse the contents of a component for Fields
		self.findLastFieldLine()
		for anyField in self.fieldList:
			found = 0
			for Alias in anyField.Aliases:
				for line_nr in range(len(self.Contents)):
					if Alias in self.Contents[line_nr]:
						#find content
						testvar = 0
						for i in range(len(self.Contents[line_nr])):
							if self.Contents[line_nr][i] == "\"":
								if testvar == 0:
									startOfString = i+1
									testvar = 1
								else:
									endOfString = i
									break
						field_code = self.Contents[line_nr][2] # breaks if more then 10 property fields
						Data = self.Contents[line_nr][startOfString:endOfString]
						self.PropertyList.append([anyField.name,Data,self.Contents[line_nr],line_nr])#convert to tuple
						found = 1
						#break
			if found == 0:
				self.PropertyList.append([anyField.name,"","",0])#convert to tuple
					
	def findLastFieldLine(self):
		line_counter = 0
		for line_nr in range(len(self.Contents)):
			if self.Contents[line_nr][:2] == "F ":
				line_counter = line_nr
				break
		for line_nr in range(line_counter,len(self.Contents)):
			if not self.Contents[line_nr][:2] == "F ":
				self.lastContentLine = line_nr-1
				self.lastFieldLineNr = int(self.Contents[line_nr-1][2])
				break
	def generatePropertyLine(self, property_nr):
		cleanLine = getCleanLine(self.Contents[self.lastContentLine])
		self.lastFieldLineNr = self.lastFieldLineNr+1
		propertyString = cleanLine[:2] + str(self.lastFieldLineNr)+ cleanLine[3:5]+ self.PropertyList[property_nr][1] + cleanLine[5:-2] + self.PropertyList[property_nr][0] +"\""+ "\n"
		return propertyString
	def addNewInfo(self, CSV_propertylist):
		for CSV_property in CSV_propertylist:	
			for SCH_property in self.PropertyList:
				if CSV_property[0].name == SCH_property[0]: #matching property names
					if not (SCH_property[1] == CSV_property[1]):
						SCH_property[1] = CSV_property[1] #copy CSV property data to SCH property
						positions = []
						for r in range(len(SCH_property[2])):
							if SCH_property[2][r] == "\"":
								positions.append(r)
						if not SCH_property[3] == 0:#if existing fieldname line nr of field != 0
							SCH_property[2] = SCH_property[2][:positions[0]+1] + SCH_property[1] + SCH_property[2][positions[1]:]						
						else:
							SCH_property[2] = SCH_property[1]
							SCH_property[3] = 0 #0 IS FLAG FOR NEW FIELDNAME
						
class KiCAD_Field(object):
	def __init__(self):
		self.Aliases = []
		self.name = ""
		self.contents = ""
	def appendAlias(self,newAlias):
		self.Aliases.append(newAlias)

def getCleanLine(line_to_be_cleaned):
	#function to create a clean string to generate new entries
	positions = []
	for r in range(len(line_to_be_cleaned)):
				
		if line_to_be_cleaned[r] == "\"":
			positions.append(r)
	if(len(positions) > 2):
		#this line has been contaminated
		line_to_be_returned = line_to_be_cleaned[:positions[0]+1] + line_to_be_cleaned[positions[1]:positions[2]+1] + line_to_be_cleaned[positions[3]:]
	else :
		#this line was clean
		line_to_be_returned = line_to_be_cleaned
	if "0000" in line_to_be_returned:
		i = 0
		for i in range (len(line_to_be_returned)-4):

			if line_to_be_returned[i:i+4] == "0000":
				break
		
		line_to_be_returned = line_to_be_returned[:i] + "0001" + line_to_be_returned[i+4 - len(line_to_be_returned):]
	return line_to_be_returned

class SCH_FILE(object):
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
					if "F1 " in content[count+subcounter]:
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
									LastComponent.SetAnnotation(content[count][-(i):-1])
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
						LastComponent.Value(content[count][startOfString:endOfString])			
					
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
			for p in range (len(self.path)):
				if self.path[-p] == "/":
					break
			to_open = self.path[:-p+1] + self.subcircuits_names[subcircuitcounter]
			try:
				f = open(to_open)
			except IOError:
				return "error"
			else:
				self.append_subcircuit(SCH_FILE())
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
		#this will break if the order is not FarnellLink; MouserLink; DigiKeyLink
		print(str(CSV_FILE.getNumberOfComponents()))
		print(str(self.get_number_of_components()))
		
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
				for p in range (len(savepath)):
					if savepath[-p] == "/":
						break #find first forwardslash to add other file name
				
				new_savepath = savepath[:-p+1]+self.subcircuits_names[i]
				print("new_savepath")
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
		
class CSV_FILE(object):
	def __init__(self):
			self.contents = []
			self.components = []
			self.number_of_components = 0
			self.startposition = 0
			self.endposition = 0
			self.SchematicName = ""
			self.name = ""
			self.annotation = ""
			self.value = ""
			self.fieldList = []
	def setContents(self, to_be_inserted):
		self.contents = to_be_inserted
	def printContents(self):
		print(self.contents)
	def printLine(self, line):
		print(self.contents[line])
	def printComponents(self):
		for i in range (self.number_of_components):
			print(self.components[i].getFarnellLink())
	def getNumberOfComponents(self):
			return self.number_of_components
	def getComponents(self):
			return self.components
	def generateCSVComponents(self):
			if "," in self.contents[1]:
				delimiter = ","
			elif ";":
				delimiter = ","
			else:
				return 'error'
			
			for i in range(1, len(self.contents)):
				new_csv_component = CSV_COMPONENT()
				new_csv_component.Contents = self.contents[i] 
				self.components.append(new_csv_component)
				self.number_of_components = self.number_of_components + 1
				counter = 0
				for p in range(len(self.contents[i])):
					if self.contents[i][p] == delimiter:
						#print("hoi")
						position = p
						if counter == 0:
							self.components[i-1].setAnnotation(self.contents[i][0:p])
							counter = counter + 1
						elif counter == 1:
							self.components[i-1].setName(self.contents[i][positionLast:position])
							counter = counter + 1
						elif counter == 2:
							self.components[i-1].setFarnellLink(self.contents[i][positionLast:position])
							counter = counter + 1
						elif counter == 3:
							self.components[i-1].setMouserLink(self.contents[i][positionLast:position])
							counter = counter + 1
						elif counter == 4:
							self.components[i-1].setDigiKeyLink(self.contents[i][positionLast:position])
							counter = counter + 1
						elif counter == 5:
							self.components[i-1].setSchematic(self.contents[i][positionLast:position])
							counter = counter + 1
						elif counter == 6:
							self.components[i-1].setStartLine(self.contents[i][positionLast:position])
							counter = counter + 1
						elif counter == 7:
							self.components[i-1].setEndLine(self.contents[i][positionLast:position])
							counter = counter + 1
						
							#print(self.contents[i][positionLast:position])
						#	print("test")
						#print(counter)
						positionLast = p + 1
	def generateCSVComponentsNew(self):
			if "," in self.contents[1]:
				delimiter = ","
			elif ";":
				delimiter = ","
			else:
				return 'error'
				
			# Find the order of the parameters saved in the csv	
			positionLast = 0
			for p in range(len(self.contents[0])):
				if self.contents[0][p] == delimiter:
					new_csv_field = KiCAD_Field()
					new_csv_field.name = self.contents[0][positionLast:p]
					self.fieldList.append(new_csv_field)
					positionLast = p + 1
			#parse date belonging to component
			for i in range(1, len(self.contents)):
				new_csv_component = CSV_COMPONENT()
				new_csv_component.Contents = self.contents[i] 
				self.components.append(new_csv_component)
				self.number_of_components = self.number_of_components + 1
				counter = 0
				positionLast = 0	
				for p in range(len(self.contents[i])):
					if self.contents[i][p] == delimiter:
							
							if counter == 0:
								#self.components[i-1] == new_csv_component
								self.components[i-1].setAnnotation(self.contents[i][positionLast:p])
							field_content = self.contents[i][positionLast:p]
							new_csv_component.appendToPropertyList([self.fieldList[counter],field_content])
							
							positionLast = p + 1
							counter = counter + 1
				else:
					new_csv_component.schematic = self.contents[i][positionLast:-1]
					
	def deleteContents(self):
		for i in range (len(self.components)):
			del self.components[0]
		self.contents = []
		self.components = []
		self.number_of_components = 0
		self.startposition = 0
		self.endposition = 0
		self.FarnellLink = ""
		self.SchematicName = ""
		self.name = ""
		self.annotation = ""
		self.value = ""
		#break
class CSV_COMPONENT(object):
	def __init__(self):
		self.annotation = ""
		self.value = ""
		self.name = ""
		self.schematic = ""
		self.startLine = ""
		self.endLine = ""
		# refactor the field extraction
		self.PropertyList = []
		self.Contents = ""
		self.fieldList = [];
		self.fieldOrder = [];
	def printprops(self):
		print(self.annotation)
	def setName(self,name):
		self.name = name
	def getName(self):
		return self.name
	def setAnnotation(self, annotation):
		self.annotation = annotation
	def getAnnotation(self):
		return self.annotation
	def setValue(self,value):
		self.value = value
	def getValue(self):
		return self.value
	def setSchematic(self, schematic):
		self.schematic = schematic
	def getSchematic(self):
		return self.schematic
	def setStartLine(self,startLine):
		self.startLine = startLine
	def getStartLine(self):
		return self.startLine
	def setEndLine(self, endLine):
		self.endLine = endLine
	def getEndLine(self):
		return self.endLine
	def generateProperties(self):
		#Check the contents of a component for Fields
		for line_nr in range(len(self.Contents)):
			for anyField in self.fieldList:
				for Alias in anyField.Aliases:
					if Alias in self.Contents[line_nr]:
						#find content
						testvar = 0
						for i in range(len(self.Contents[line_nr])):
							if self.Contents[line_nr][i] == "\"":
								if testvar == 0:
									startOfString = i+1
									testvar = 1
								else:
									endOfString = i
									break
						Data = self.Contents[line_nr][startOfString:endOfString]
						
						self.PropertyList.append([anyField.name,Data])#convert to tuple
	def appendToPropertyList(self,data):
		self.PropertyList.append(data)#convert to tuple
