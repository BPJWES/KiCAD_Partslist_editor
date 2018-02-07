

import component
import os
import re


# The Schematic class
# holds its filename and all the subcircuits.
# The components in this schematic are also stored here.
# The main methods are parseSubCircuits (to get the hierarchical schematic tree)
# and the parseComponents, which extracts the components of this single schematic.
class Schematic:
	def __init__(self):
		self.contents = "" # list of all text lines in the schematic
		self.nrOfComponents = 0
		self.namesOfSubcircuits = []
		self.nrOfSubcircuits = 0
		self.components = []
		self.subcircuits = []
		self.schematicName = ""
		self.path = ""
		self.fieldList = "" # list of KicadField objects
		self.delimiter = ";" # TODO 1: make this configurable

	def setPath(self, path):
		self.path = path

	def getPath(self):
		return self.path

	def setSchematicName(self, x):
		self.schematicName = x

	def getSchematicName(self):
		return self.schematicName

	def SetContents(self,content):
		#load the contents of the .sch file
		self.contents = content

	def SwapComponents(self, i, j):
		self.components[i] , self.components[j] = self.components[j] , self.components[i]

	def set_number_of_components(self, x):
		self.nrOfComponents = x

	def get_number_of_components(self):
		return self.nrOfComponents

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
		print(self.nrOfComponents)
		print(self.components)
		print(self.namesOfSubcircuits)
		print(self.nrOfSubcircuits)
		print(self.schematicName)

	def parseSubCircuits(self):
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
						endOfString = 0
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
		self.namesOfSubcircuits = ListOfSubSchematics
		self.nrOfSubcircuits = len(ListOfSubSchematics)

	def ParseComponents(self):
		if self.namesOfSubcircuits == []:
			self.parseSubCircuits()
		content = self.contents
		for count in range(len(content)):
			if "$Comp" in content[count]:
				lineStartOfComponent = count

				while not "$EndComp" in content[count]:
					if "#" in content[lineStartOfComponent+1]: # skip any comment lines
						break
					if count == lineStartOfComponent:
						self.components.append(Component())
						self.set_number_of_components(self.get_number_of_components() + 1)
						lastComponent = self.getLastComponent()
						lastComponent.setStartPos(count)
						lastComponent.setSchematicName(self.getSchematicName())
						lastComponent.fieldList = self.fieldList

					if content[count][0] == "L":
							i = 0
							for i in range(len(content[count])):
								if content[count][len(content[count])-(i+1)] == " ":
									lastComponent.setReference(content[count][-(i):-1])
									lastComponent.setName(content[count][2:-(i + 1)])
									break

					# Example:
					# AR Path="/56647084/5664BC85" Ref="U501"  Part="2"
					# the number for Part= varies e.g. from 1 to 4 for a component with 4 Units (e.g. LM324)
					# NOTE; it is not clear, for what reason we get this record only for some components...
					# we print just a message
					# we don't use the data any further
					if "AR Path=" in content[count] :
						# extract the path, Ref and Part into regex groups:
						searchResult = re.search('AR +Path="(.*)" +Ref="(.*)" +Part="(.*)".*', content[count])

						if searchResult:
							componentPath = searchResult.group(1)
							componentRef = searchResult.group(2)
							componentUnit = searchResult.group(3)

							# Print some messages
							print('Info: AR Record: ' + componentPath + ' ' + componentRef + ' ' + componentUnit)



					# Example:
					# F 1 "LTC2052IS#PBF" H 9750 5550 50  0000 C CNN
					if "F 1 " in content[count] : #find f1 indicating value field in EEschema file format
						searchResult = re.search('F 1 +"(.*)".*', content[count])

						if searchResult:
							componentValue = searchResult.group(1)
							lastComponent.setValue(componentValue)
						else:
							print("Error: Regex Mismatch, cannot find value in 'F 1' field in line: " + content[count])

					count = count + 1
				# end while(not end of component found)

				lastComponent.setEndPos(count)
				lastComponent.contents = content[lastComponent.startPosition:lastComponent.endPosition]
				lastComponent.extractProperties()

				if lineStartOfComponent > 100000: # prevents fails
					break
		# end for(all lines)

		for subcircuitCounter in range(len(self.namesOfSubcircuits)):


			#print("subcircuit")
			#for p in range (len(self.path)):
			#	if self.path[-p] == "/":
			#		break
			#to_open = self.path[:-p+1] + self.subcircuits_names[subcircuitCounter]
			to_open = os.path.join(os.path.dirname(self.path), self.namesOfSubcircuits[subcircuitCounter])
			try:
				f = open(to_open)
			except IOError:
				return "error"
			else:
				self.append_subcircuit(Schematic())
				self.get_subcircuit(subcircuitCounter).setPath(to_open)
				self.subcircuits[subcircuitCounter].contents=f.readlines()
				f.close()
				self.get_subcircuit(subcircuitCounter).setSchematicName(self.namesOfSubcircuits[subcircuitCounter])
				self.get_subcircuit(subcircuitCounter).fieldList = self.fieldList
				self.get_subcircuit(subcircuitCounter).ParseComponents()
				self.AppendComponents(self.get_subcircuit(subcircuitCounter).getComponents())


	def get_subcircuit(self, x):
		return self.subcircuits[x]

	def AppendComponents(self, componentList):
		for item in range(len(componentList)):
			self.components.append(componentList[item])
			self.nrOfComponents = self.get_number_of_components() + 1

	def exportCsvFile(self, savepath):
	#New variant which allows for user configurable field names
		if not '.csv' in savepath:
			savepath = savepath + '.csv'
		try:
			f = open(savepath, 'w')
		except IOError:
			if savepath:
				return "error"
		else:
			line = ""
			line += "Part\#"
			line += self.delimiter
			line += ("PartType")
			line += (self.delimiter)
			for field in self.fieldList:
				line += (field.name)
				line += (self.delimiter)
			line += ("Found in: ")
			f.write(line + "\n")

			for item in range(self.get_number_of_components()):
				line = ""
				#Add Line with component and fields
				line += (self.getComponents()[item].getReference())
				line += (self.delimiter)
				line += (self.getComponents()[item].getName())
				line += (self.delimiter)
				for field in self.fieldList:
				#match fields to component.field
					for counter in range(len(self.getComponents()[item].propertyList)):
						if self.getComponents()[item].propertyList[counter][0] == field.name:
							line += (self.getComponents()[item].propertyList[counter][1])
							line += (self.delimiter)
							break
						else:
							line += ("")

				line += (self.getComponents()[item].GetSchematicName())
				f.write(line + "\n")
			f.close

	def getSubCircuitName(self):
		return self.subcircuits_names

	def getSubCircuits(self):
		return self.subcircuits

	def ModifyNewSCHFile(self, oldSCHFile, csvFile, savepath):
		# this did break if the order is not FarnellLink; MouserLink; DigiKeyLink
		# should be fixed now but am not sure

		print("Number of Parts in CSV: " + str(csvFile.getNumberOfComponents()))
		print("Number of Parts in this SCH: " + str(self.get_number_of_components()))

		if csvFile.getNumberOfComponents() and self.get_number_of_components():

			for i in range (csvFile.getNumberOfComponents()):#Loop over csv_components
				for p in range (self.get_number_of_components()):#loop over .sch components
					if csvFile.getComponents()[i].getReference() == self.getComponents()[p].getReference() and \
									self.schematicName ==  csvFile.getComponents()[i].getSchematic(): #if annotation and schematic name match

						selectedComponent = self.getComponents()[p]
						selectedComponent.addNewInfo(csvFile.components[i].propertyList)

						for property in range(len(selectedComponent.propertyList)):

							if not selectedComponent.propertyList[property][3] == 0: #Not exists for adding fields through .csv
							#Datafield existed in original file

								self.contents[selectedComponent.startPosition+selectedComponent.propertyList[property][3]] = \
									selectedComponent.propertyList[property][2]
							else:
								self.contents[selectedComponent.startPosition+selectedComponent.lastContentLine] = \
									self.contents[selectedComponent.startPosition+selectedComponent.lastContentLine] + \
									selectedComponent.generatePropertyLine(property)
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
				newSavePath = os.path.join(os.path.dirname(savepath), self.namesOfSubcircuits[i])
				print(newSavePath)
				self.subcircuits[i].ModifyNewSCHFile(0, csvFile, newSavePath)
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
		self.nrOfComponents = 0
		self.namesOfSubcircuits = []
		self.nrOfSubcircuits = 0
		self.components = []
		self.subcircuits = []
		self.schematicName = ""
		self.path = ""






# The Component Class
# contains all the lines of a Schematic file, which belong to one component.
# it provides two main methods:
#

class Component:
	def __init__(self):
		self.startPosition = 0
		self.endPosition = 0
		self.schematicName = ""
		self.name = ""
		self.reference = ""
		self.value = ""
		# refactor the field extraction
		self.propertyList = []
		self.contents = ""
		self.fieldList = [];
		self.lastContentLine = 0
		self.lastFieldLineNr = 0

	def setStartPos(self, x):
		self.startPosition = x

	def setEndPos(self, x):
		self.endPosition = x

	def setName(self, x):
		self.name = x

	def getName(self):
		return self.name

	def setReference(self, x):
		self.reference = x

	def getReference(self):
		return self.reference

	def setValue(self, x):
		self.value = x

	def getValue(self):
		return self.value

	def printProps(self):
		print(self.name)
		print(self.reference)
		print(self.value)
		print(self.schematicName)

	def printAll(self):
		print(self.startPosition)
		print(self.endPosition)
		print(self.name)
		print(self.reference)
		print(self.value)
		print(self.schematicName)

	def setSchematicName(self, schematic_name):
		self.schematicName = schematic_name

	def GetSchematicName(self):
		return self.schematicName

	def getStartLine(self):
		return self.startPosition

	def getEndLine(self):
		return self.endPosition

	def extractProperties(self):
		# parse the contents of a component for Fields
		self.findLastFieldLine()

		# temporary dictionay, if we have all fields found
		fieldFound={}
		for anyField in self.fieldList:
			fieldFound[anyField] = False

		for line_nr in range(len(self.contents)):
			found = 0  # example:
			# F 4 "C3216-100n-50V" H 8450 6050 60  0001 C CNN "InternalName"
			searchResult = re.search('F +([0-9]+) +"(.*)" +.*"(.*)".*', self.contents[line_nr])

			if searchResult:
				fieldNr = searchResult.group(1)  # not used in this code
				fieldValue = searchResult.group(2)
				fieldName = searchResult.group(3)

				for anyField in self.fieldList:
					for Alias in anyField.Aliases:

						if Alias == fieldName:
							if fieldFound[anyField] == True:
								print("Warning: duplicate definition of Field " + fieldName + " with Alias " + Alias
									  + " for Component " + self.getReference())
							fieldFound[anyField] = True
							self.propertyList.append(
								[anyField.name, fieldValue, self.contents[line_nr], line_nr])  # convert to tuple
		#end for(all lines)

		# set default values for non-found fields:
		for anyField in self.fieldList:
			if fieldFound[anyField] == False:
				self.propertyList.append([anyField.name, "", "", 0])

	def findLastFieldLine(self):
		line_counter = 0
		for line_nr in range(len(self.contents)):
			if self.contents[line_nr][:2] == "F ":
				line_counter = line_nr
				break
		for line_nr in range(line_counter, len(self.contents)):
			if not self.contents[line_nr][:2] == "F ":
				self.lastContentLine = line_nr - 1
				self.lastFieldLineNr = int(self.contents[line_nr - 1][2])
				break

	def getCleanLine(self, lineToBeCleaned):
		# function to create a clean string to generate new entries
		positions = []
		for r in range(len(lineToBeCleaned)):
			if lineToBeCleaned[r] == "\"":
				positions.append(r)
		if (len(positions) > 2):
			# this line has been contaminated
			lineToBeReturned = lineToBeCleaned[:positions[0] + 1] + \
							   lineToBeCleaned[positions[1]:positions[2] + 1] + \
							   lineToBeCleaned[positions[3]:]
		else:
			# this line was clean or there was a tilde sign in there
			if "\"~\"" in lineToBeCleaned:
				# tilde is found in in kicad schematics with rescued symbols
				lineToBeReturned = lineToBeCleaned[:positions[0] + 1] + lineToBeCleaned[positions[1]:]
			else:
				lineToBeReturned = lineToBeCleaned
		if "0000" in lineToBeReturned:
			i = 0
			for i in range(len(lineToBeReturned) - 4):

				if lineToBeReturned[i:i + 4] == "0000":
					break

			lineToBeReturned = lineToBeReturned[:i] + "0001" + lineToBeReturned[i + 4 - len(lineToBeReturned):]
		# print(lineToBeReturned)
		return lineToBeReturned

	def generatePropertyLine(self, property_nr):
		cleanLine = self.getCleanLine(self.contents[self.lastContentLine])
		self.lastFieldLineNr += 1
		propertyString = cleanLine[:2] + str(self.lastFieldLineNr) + cleanLine[3:5] + \
						 self.propertyList[property_nr][1] + cleanLine[5:-1] + \
						 " \"" + self.propertyList[property_nr][0] + "\"" + "\n"

		if "CNN \"\"" in propertyString :
			a = 5

		return propertyString

	def addNewInfo(self, csvPropertyList):
		for csvProperty in csvPropertyList:
			for schProperty in self.propertyList:
				if csvProperty[0].name == schProperty[0]:  # matching property names
					if not (schProperty[1] == csvProperty[1]):
						schProperty[1] = csvProperty[1]  # copy CSV property data to SCH property
						positions = []
						for r in range(len(schProperty[2])):
							if schProperty[2][r] == "\"":
								positions.append(r)
						if not schProperty[3] == 0:  # if existing fieldname line nr of field != 0
							schProperty[2] = schProperty[2][:positions[0] + 1] + schProperty[1] + schProperty[2][
																								  positions[1]:]
						else:
							schProperty[2] = schProperty[1]
							schProperty[3] = 0  # 0 IS FLAG FOR NEW FIELDNAME









class CsvComponent(object):
	def __init__(self):
		self.reference = ""
		self.value = ""
		self.name = ""
		self.schematic = ""
		self.startLine = ""
		self.endLine = ""
		# refactor the field extraction
		self.propertyList = []
		self.Contents = ""
		self.fieldList = [];
		self.fieldOrder = [];
	def printprops(self):
		print(self.reference)

	def setName(self,name):
		self.name = name

	def getName(self):
		return self.name

	def setReference(self, reference):
		self.reference = reference

	def getReference(self):
		return self.reference

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

						self.propertyList.append([anyField.name,Data])#convert to tuple



class CsvFile(object):
	def __init__(self):
			self.contents = []
			self.components = []
			self.nrOfComponents = 0
			self.startPosition = 0
			self.endPosition = 0
			self.schematicName = ""
			self.name = ""
			self.reference = ""
			self.value = ""
			self.fieldList = []

	def setContents(self, to_be_inserted):
		self.contents = to_be_inserted

	def printContents(self):
		print(self.contents)

	def printLine(self, line):
		print(self.contents[line])

	def printComponents(self):
		for i in range (self.nrOfComponents):
			print(self.components[i].getFarnellLink())

	def getNumberOfComponents(self):
			return self.nrOfComponents

	def getComponents(self):
			return self.components

	# reads the content of the CSV and extracts the contained components
	def extractCsvComponents(self):
			if "," in self.contents[1]:
				delimiter = ","
			elif ";":
				delimiter = ";"
			else:
				return 'error: no delimiter found in CSV'

			# Find the order of the parameters saved in the csv
			positionLast = 0
			for p in range(len(self.contents[0])):
				if self.contents[0][p] == delimiter:
					new_csv_field = KicadField()
					new_csv_field.name = self.contents[0][positionLast:p]
					self.fieldList.append(new_csv_field)
					positionLast = p + 1
			#parse date belonging to component
			for i in range(1, len(self.contents)):
				newCsvComponent = CsvComponent()
				newCsvComponent.Contents = self.contents[i]
				self.components.append(newCsvComponent)
				self.nrOfComponents = self.nrOfComponents + 1
				counter = 0
				positionLast = 0
				for p in range(len(self.contents[i])):
					if self.contents[i][p] == delimiter:
							if counter == 0:
								self.components[i-1].setReference(self.contents[i][positionLast:p])
							field_content = self.contents[i][positionLast:p]
							newCsvComponent.propertyList.append([self.fieldList[counter],field_content])

							positionLast = p + 1
							counter = counter + 1
				else:
					newCsvComponent.schematic = self.contents[i][positionLast:-1]

	def deleteContents(self):
		for i in range (len(self.components)):
			del self.components[0]
		self.contents = []
		self.components = []
		self.nrOfComponents = 0
		self.startPosition = 0
		self.endPosition = 0
		self.FarnellLink = ""
		self.schematicName = ""
		self.name = ""
		self.reference = ""
		self.value = ""
		#break









class KicadField(object):
	def __init__(self):
		self.Aliases = []
		self.name = ""
		self.contents = ""

	def appendAlias(self,newAlias):
		self.Aliases.append(newAlias)



