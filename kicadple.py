

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

		# for each line in the whole schematic file
		for count in range(len(content)):
			if "$Comp" in content[count]:

				newComponent = Component()
				self.components.append(newComponent)
				self.nrOfComponents += 1
				newComponent.setStartPos(count)
				newComponent.setSchematicName(self.getSchematicName())
				newComponent.fieldList = self.fieldList

				while not "$EndComp" in content[count]:
					count += 1
				# end while(not end of component found)

				newComponent.setEndPos(count)
				newComponent.contents = content[newComponent.startPosition:count] # copy raw lines into component
				newComponent.extractProperties()
			# end if(start of component)
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
				# skip export of unlisted components
				if(self.getComponents()[item].unlisted == False):
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
				#endif
			#endfor
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
#   * extractProperties()
#   * generatePropertyLine()
#

class Component:
	def __init__(self):

		# line number within the whole schematic file, set on extraction from schematic:
		self.startPosition = 0 # $Comp
		self.endPosition = 0 # $EndComp

		self.schematicName = "" # relative file name (*.sch)
		self.name = "" # component name in the symbol library eg R
		self.reference = "" # reference of the component, defined by the annotation eg R501
		self.value = "" # value field e.g. 47k
		self.footprint = "" # footprint field e.g. standardSMD:R1608 TODO 0
		self.datasheet = "" # the last special field TODO 0
		# refactor the field extraction

		# list of 4-tuples: String kicadField.name, String fieldValue, String lineContent, int relative lineNr]
		self.propertyList = []
		self.contents = "" # contains all the lines, including $Comp and $EndComp

		self.fieldList = []; # list of KicadField objects.
			# user defined fields with fieldName and aliases, defined by the FieldKeywords.conf

		# relative line number within this component lines; 0 = $Comp
		self.lastContentLine = 0 #
		self.lastFieldLineNr = 0
		self.unlisted = False # used for power components, e.g. GND #PWR123; they get not exported to CSV

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


	# parse the contents of a component for Fields
	def extractProperties(self):

	# Example Component Instance:
	#
	# $Comp
	# L R R51
	# U 1 1 5873950B
	# P 5750 2000
	# F 0 "R51" H 5820 2046 50  0000 L CNN
	# F 1 "3k9" H 5820 1955 50  0000 L CNN
	# F 2 "standardSMD:R0603" V 5680 2000 50  0001 C CNN
	# F 3 "" H 5750 2000 50  0000 C CNN
	# F 4 "R1608-3k9" H 5750 2000 60  0001 C CNN "InternalName"
	# 	1    5750 2000
	# 	1    0    0    -1
	# $EndComp

		self.findLastFieldLine()

	# temporary dictionay, if we have all fields found
		fieldFound={}
		for anyField in self.fieldList:
			fieldFound[anyField] = False

		for line_nr in range(len(self.contents)):
			line  = self.contents[line_nr]

			if line[0] == "L":
				# Example for a resistor with component=R and ref=R609
				# L R R609
				searchResult = re.search('L +(.*) +(.*)', line)

				if searchResult:
					componentName = searchResult.group(1)
					componentRef = searchResult.group(2)

					self.reference = componentRef
					self.name = componentName

					print("Trace: Found Component: "
						  + componentName + " " + componentRef)

					# Special case for power-components: don't parse them
					if componentRef[0] == "#":
						self.unlisted = True

					continue

				else:
					print("Error: Regex Missmatch for L-record in line: " +
						  line + " in file " + self.schematicName)
				# endelse
			# endif L

			# Example:
			# AR Path="/56647084/5664BC85" Ref="U501"  Part="2"
			# the number for Part= varies e.g. from 1 to 4 for a component with 4 Units (e.g. LM324)
			# NOTE; it is not clear, for what reason we get this record only for some components...
			# we print just a message
			# we don't use the data any further
			if "AR Path=" in line:
				# extract the path, Ref and Part into regex groups:
				searchResult = re.search('AR +Path="(.*)" +Ref="(.*)" +Part="(.*)".*', content[count])

				if searchResult:
					componentPath = searchResult.group(1)
					componentRef = searchResult.group(2)
					componentUnit = searchResult.group(3)

					# Print some messages
					print('Info: AR Record: ' + componentPath + ' ' + componentRef + ' ' + componentUnit)


			# Example
			# F 0 "R51" H 5820 2046 50  0000 L CNN
			if line[0:4] == "F 0 ":
				searchResult = re.search('F 0 +"(.*)" +.*', line)

				if searchResult:
					componentRef = searchResult.group(1)

					if not (componentRef == self.reference):
						print("Warning: L record value doesn't match 'F 0 ' record: "
							  + self.reference + " vs. " + componentRef + " in '" +
						  line + "' in file " + self.schematicName)

					continue
				else:
					print("Error: Regex Missmatch for 'F 0 '-record in line: " +
						  line + " in file " + self.schematicName)
				# endelse
			# endif F 0




			# Example:
			# F 1 "LTC2052IS#PBF" H 9750 5550 50  0000 C CNN
			if "F 1 " in line:  # find f1 indicating value field in EEschema file format
				searchResult = re.search('F 1 +"(.*)".*', line)

				if searchResult:
					componentValue = searchResult.group(1)
					self.value = componentValue
				else:
					print("Error: Regex Mismatch, cannot find value in 'F 1 '-record in '" +
						  line + "' in file " + self.schematicName)
				# end if
			# endif F 1

			# TODO 0: footprint!

			# TODO 0: datasheet


			# example:
			# F 4 "C3216-100n-50V" H 8450 6050 60  0001 C CNN "InternalName"
			searchResult = re.search('F +([0-9]+) +"(.*)" +.*"(.*)".*', line)

			if searchResult:
				fieldNr = searchResult.group(1)  # not used in this code
				fieldValue = searchResult.group(2)
				fieldName = searchResult.group(3)

				tempFound = False
				for anyField in self.fieldList:
					for Alias in anyField.Aliases:
						if Alias == fieldName:
							if fieldFound[anyField] is True:
								print("Warning: duplicate definition of Field " + fieldName + " with Alias " + Alias
									  + " for Component " + self.getReference()
									  + " in file " + self.schematicName)
							fieldFound[anyField] = True
							tempFound = True
							self.propertyList.append(
								[anyField.name, fieldValue, line, line_nr])  # convert to tuple
							break
					if tempFound == True:
						break

		#end for(all lines)

		# set default values for non-found fields:
		for anyField in self.fieldList:
			if fieldFound[anyField] == False:
				self.propertyList.append([anyField.name, "", "", 0]) # add tuple to list

	def findLastFieldLine(self):
		line_counter = 0
		# find first field line (F 0 ):
		for line_nr in range(len(self.contents)):
			if self.contents[line_nr][:2] == "F ":
				line_counter = line_nr
				break
		# and then search for the last field line:
		for line_nr in range(line_counter, len(self.contents)):
			if not self.contents[line_nr][:2] == "F ":
				self.lastContentLine = line_nr - 1

				searchResult = re.search('F +([0-9]+) +"(.*)" .*', self.contents[self.lastContentLine])

				if searchResult:
					fieldNr = searchResult.group(1)

				# self.lastFieldLineNr = int(self.contents[line_nr - 1][2]) # <<= here is the BUG! breaks for numbers with more than 1 digit!
					self.lastFieldLineNr = fieldNr
					break
				else:
					print("Error: Regex mismatch on extraction of field number in this line: " +
						  self.contents[self.lastContentLine])

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



