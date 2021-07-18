

import os
import re
import globals

import debugtrace as DT

# This class holds the values for a field line from a KiCad schematic file
class ComponentField:
	def __init__(self):
		self.name = "" # Field Name, at the end of the line within double-quotes
		self.value = "" # Field Value, at the beginning of the Line after the "F xx " record header
		self._content = "" # text line for the schematic file, including \n at the end. Use getter and setter!
		self.number = 0 # fields in KiCad are numbered, where 0,1,2 and 3 are reserved for reference, value, footprint and datasheet
		self.relativeLine = 0 # relative line within a component, where $COMP is line 0
		self._fieldProperties = "" # is extracted from the content. Starts with 'H' or 'V', and typically ends with 'CNN'.
		self.exists = True # by default, we assume, that this field exists in the Schematic file

		self.orientation = 'H' # horizontal
		self.xPos = 0
		self.yPos = 0
		self.textSize = 50 # mil
		self.visibility = '0001' # invisible
		self.hAdjust = 'C' # center
		self.vAdjustIB = 'CNN' # center, normal, normal

	# parses the content-line and extracts name, value and number
	def setContent(self, content):
		searchResult = re.search('F +(\d+) +"([^"]*)" +([HV] [0-9 A-Z]*[BN])(.*)?', content)
			# group 1: field number
			# group 2: field value (without double quotes)
			# group 3: field properties (without leading or trailing spaces)
			# group 4: optional field name (with leading/trailing spaces and double quotes)

		if searchResult:
			self.number = int(searchResult.group(1))
			self.value = searchResult.group(2)
			self._fieldProperties = searchResult.group(3)
			optFieldName = searchResult.group(4) # this is optional for "F 0" to "F 3"

			if len(optFieldName) > 0:
				searchResult = re.search(' *"([^"]*).*', optFieldName)

				if searchResult:
					self.name = searchResult.group(1)
				else:
					self.name = ""


			searchResult = re.search('([HV]) +([\d]+) +([\d]+) +([\d]+) +([\d]+) ([LRCBT]) ([LRCBT][IN][BN])', self._fieldProperties)
			if searchResult:
				self.orientation = searchResult.group(1)
				self.xPos = int(searchResult.group(2))
				self.yPos = int(searchResult.group(3))
				self.textSize = int(searchResult.group(4))
				self.visibility = searchResult.group(5)
				self.hAdjust = searchResult.group(6)
				self.vAdjustIB = searchResult.group(7)
			else:
				DT.error("Regex missmatch in '" + self._fieldProperties + "'")
		else:
			DT.error("Regex missmatch in ComponentField:setContent(" + content + ")")


	# composes the content line from the existing content and the current values of name, value and number
	def getContent(self):
		fProps = self.orientation + ' ' + \
			str(self.xPos) + ' ' + str(self.yPos) + ' ' +\
			str(self.textSize) + '  ' +\
			self.visibility + ' ' +\
			self.hAdjust + ' ' +\
			self.vAdjustIB

		s = 'F ' + str(self.number) + ' "' + self.value + '" ' + fProps
		if self.name:
			s += ' "' + self.name + '"'
		s += '\n'
		return s


# The Schematic class
# holds its filename and all the subcircuits.
# The components in this schematic are also stored here.
# The main methods are parseSubCircuits (to get the hierarchical schematic tree)
# and the parseComponents, which extracts the components of this single schematic.
class Schematic:
	def __init__(self):
		self.contents = "" # list of all text lines in the schematic
		self.namesOfSubcircuits = [] # List of relative file names (e.g. 'mysubfile.sch')
		self.components = [] # List of Components objects, holding their content and extracted properties/fields
		self.subcircuits = [] # List of Schematic objects
		self.schematicName = "" # file name
		self.path = "" # file system path to this schematic file
		self.fieldList = "" # list of KicadField objects

	def setPath(self, path):
		self.path = path

	def getPath(self):
		return self.path

	def SetContents(self,content):
		#load the contents of the .sch file
		self.contents = content

	def SwapComponents(self, i, j):
		self.components[i] , self.components[j] = self.components[j] , self.components[i]

	def getLastComponent(self):
		last_position = len(self.components)-1
		return self.components[last_position]

	def append_subcircuit(self, subcircuit_instance):
		self.subcircuits.append(subcircuit_instance)

	def appendComponent(self,component):
		self.components.append(component)

	def printprops(self):
		print(len(self.components))
		print(self.components)
		print(self.namesOfSubcircuits)
		print(len(self.namesOfSubcircuits))
		print(self.schematicName)

	def parseSubCircuits(self):
		content = self.contents
		ListOfSubSchematics = []
		for count in range(len(content)):
			if "$Sheet" in content[count]:
				count += 1

				while not "$EndSheet" in content[count]:
					# Example:
					# F1 "ADC-16-Bit.sch" 60
					if content[count][0:3] == "F1 ":
						searchResult = re.search('F1 +"(.*)" +.*', content[count])
						if searchResult:
							ListOfSubSchematics.append(searchResult.group(1))
							break
						else:
							DT.error("cannot find schematic name in F1-record within $Sheet-block "+
								  "in file " + self.schematicName + " in line number " + count)
					count += 1
				#endwhile
			#endif $Sheet
		#endfor all lines

		self.namesOfSubcircuits = ListOfSubSchematics

	def ParseComponents(self):
		if self.namesOfSubcircuits == []:
			self.parseSubCircuits()
		content = self.contents

		# for each line in the whole schematic file
		for count in range(len(content)):
			if "$Comp" in content[count]:

				newComponent = Component()
				self.components.append(newComponent) # copy by reference
				newComponent.setStartPos(count)
				newComponent.schematicName = self.schematicName
				newComponent.fieldList = self.fieldList

				while not "$EndComp" in content[count]:
					count += 1
				# end while(not end of component found)

				newComponent.setEndPos(count)

				# copy raw lines into component including $Comp and $EndComp
				newComponent.contents = content[newComponent.startPosition:count+1]
				newComponent.extractProperties()
			# end if(start of component)
		# end for(all lines)

		for subcircuitCounter in range(len(self.namesOfSubcircuits)):
			global ParsedSchematicFiles;

			subFilePathName = os.path.join(os.path.dirname(self.path), self.namesOfSubcircuits[subcircuitCounter])

			# Open only files, which have not been parsed already! (Deduplication of parts in the CSV)
			if subFilePathName not in globals.ParsedSchematicFiles:
				globals.ParsedSchematicFiles.append(subFilePathName)
				try:
					f = open(subFilePathName)
				except IOError:
					return "error"
				else:
					subSchematic = Schematic()
					self.subcircuits.append(subSchematic)
					subSchematic.setPath(subFilePathName)
					subSchematic.contents=f.readlines()
					f.close()
					subSchematic.schematicName = self.namesOfSubcircuits[subcircuitCounter]
					subSchematic.fieldList = self.fieldList
					subSchematic.ParseComponents()

					#  TODO 2: fix this bad style: each schematic should hold it's own components only.
					# and not all components of all sub and subsubsheets.
					# see also exportCsvFile()
					self.components.extend(subSchematic.components)
			else:
				DT.debug("skip for deduplication: " + subFilePathName)

		# end for(all subcircuits)

		# TODO 2: check for consistent components with multiple units
		# TODO 2: add warnings,	if footprint and/ or value for one components is different between the units

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
			line += "Part"
			line += globals.CsvSeparator
			line += "Reference" # here we use the referenceUnique!!!
			line += globals.CsvSeparator
			line += "Unit"
			line += globals.CsvSeparator
			line += "Value"
			line += globals.CsvSeparator
			line += "Footprint"
			line += globals.CsvSeparator
			line += "Datasheet"
			line += globals.CsvSeparator
			for field in self.fieldList:
				line += field.name
				line += globals.CsvSeparator
			line += ("File")
			f.write(line + "\n")

			for item in range(len(self.components)):
				component = self.components[item]
				# skip export of unlisted components
				if(component.unlisted == False):				
					line = ""
					# TODO 2: add quotation marks for each entry (use csv library)
					#Add Line with component and fields
					line += component.name
					line += globals.CsvSeparator
					line += component.reference
					line += globals.CsvSeparator
					line += component.unit
					line += globals.CsvSeparator
					line += component.value
					line += globals.CsvSeparator
					line += component.footprint
					line += globals.CsvSeparator
					line += component.datasheet
					line += globals.CsvSeparator

					for field in self.fieldList:
					#match fields to component.field
						for property in component.propertyList:
							if field.MatchField(property.name):
								line += property.value
								break
							else:
								line += ""
						
						line += globals.CsvSeparator

					line += component.schematicName
					f.write(line + "\n")
				#endif
			#endfor
			f.close

	def getSubCircuitName(self):
		return self.namesOfSubcircuits

	def getSubCircuits(self):
		return self.subcircuits

	def ModifyNewSCHFile(self, oldSCHFile, csvFile, savepath):
		# TODO 1: don't call this multiple times, if it is referred multiple times in parent sheets!
		# --> more efficient, avoid possible errors

		# TODO 2: improve this messages: SCH and CSV parts should match
		DT.info("Number of Parts in CSV: " + str(len(csvFile.components)))
		DT.info("Number of Parts in this SCH: " + str(len(self.components)))

		if len(csvFile.components) and len(self.components):

			for i in range (len(csvFile.components)):#Loop over csv_components
				for p in range (len(self.components)):#loop over .sch components
					if csvFile.components[i].reference == self.components[p].getReference() and \
							self.schematicName ==  csvFile.components[i].getSchematic() and \
							csvFile.components[i].unit == self.components[p].unit: #if annotation and schematic name match

						comp = self.components[p]

						# assign KiCad's default fields:
						comp.name = csvFile.components[i].name
						comp.value = csvFile.components[i].value
						comp.footprint = csvFile.components[i].footprint
						comp.datasheet = csvFile.components[i].datasheet

						lineTemplate = ""

						for ii in range(comp.startPosition,comp.endPosition):
							line = self.contents[ii]
							helper = ComponentField() # helper for creating 'F x ' records

							if line[0:2] == 'L ':
								self.contents[ii] = 'L ' + comp.name + ' ' + comp.reference + '\n'
							elif line[0:4] == 'F 1 ':  # component value
								helper.setContent(line)
								helper.value = comp.value
								self.contents[ii] = helper.getContent()

								lineTemplate = line # save a template line for newly to be created fields
							elif line[0:4] == 'F 2 ':  # component footprint
								helper.setContent(line)
								helper.value = comp.footprint
								self.contents[ii] = helper.getContent()
							elif line[0:4] == 'F 3 ':  # component datasheet
								helper.setContent(line)
								helper.value = comp.datasheet
								self.contents[ii] = helper.getContent()

						comp.updateAllMatchingFieldValues(csvFile.components[i].propertyList)

						for property in range(len(comp.propertyList)):
							if comp.propertyList[property].exists:
								self.contents[comp.startPosition+comp.propertyList[property].relativeLine] = \
									comp.propertyList[property].getContent()
							else:
								# otherwise we have to append it
								self.contents[comp.startPosition+comp.propertyList[property].relativeLine] += \
									comp.propertyList[property].getContent()
						# end for(all properties)
					# end if components match
				# end for all schematic components
			#end for all csv components

			try:
				f = open(savepath, 'w')
				f.writelines(self.contents)
			except Exception as e:
				print('Error: ' + e)
				return str(e)

			for i in range(len(self.subcircuits)):
				newSavePath = os.path.join(os.path.dirname(savepath), self.namesOfSubcircuits[i])
				DT.info(newSavePath)
				self.subcircuits[i].ModifyNewSCHFile(0, csvFile, newSavePath)
				#mainFile.ModifyNewSCHFile(0, openCSVFile,savePath):
		else:
			DT.error("No components loaded")

	def deleteContents(self):
		for p in range (len(self.subcircuits)):
			# first delete subcircuits
			self.subcircuits[0].deleteContents()

		for i in range (len(self.components)):
			del self.components[0]
		self.contents = ""
		self.namesOfSubcircuits = []
		self.components = []
		self.subcircuits = []
		self.schematicName = ""
		self.path = ""


# The Component Class
# contains all the lines of a Schematic file, which belong to one component.
# it provides two main methods:
#   * extractProperties()
#   * updateAllMatchingFieldValues()
#

class Component:
	def __init__(self):

		# line number within the whole schematic file, set on extraction from schematic:
		self.startPosition = 0 # $Comp
		self.endPosition = 0 # $EndComp

		self.schematicName = "" # relative file name (*.sch)
		self.name = "" # component name in the symbol library eg R
		self.unit = 0 # integer number used for components with multiple units (eg. quad opamp)
			# TODO 2: do not export multiple units for one reference, but update all components with that reference
		self.reference = "" # (common) reference of the component, defined by the annotation eg R501
			# for multiple instances (in subsheets) we have to use the uniqueReference
		self.referenceUnique = ""  # unique reference of the component, defined by the annotation eg R501
			# this holds the true reference name. Different for multiple instances in sub-sheets.
		self.value = "" # value field e.g. 47k
		self.footprint = "" # footprint field e.g. standardSMD:R1608
		self.datasheet = "" # the last special field
		# refactor the field extraction

		# list of 4-tuples: String kicadField.name, String fieldValue, String lineContent, int relative lineNr]
		self.propertyList = [] # list of ComponentField objects
		self.contents = "" # contains all the lines, including $Comp and $EndComp

		self.fieldList = []; # list of KicadField objects.
			# user defined fields with fieldName and aliases, defined by the FieldKeywords.conf

		# relative line number within this component lines; 0 = $Comp
		self.lastContentLine = 0 #
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
		print(self.datasheet)

	def printAll(self):
		print(self.startPosition)
		print(self.endPosition)
		self.printProps()

	def getStartLine(self):
		return self.startPosition

	def getEndLine(self):
		return self.endPosition


	# parse the contents of a component for Fields
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
	def extractProperties(self):

	# temporary dictionay, if we have all fields found
		fieldFound={}
		for anyField in self.fieldList:
			fieldFound[anyField] = False

		fieldTemplate = "" # used for new extra fields
		maxFieldNr = 3 # used for new extra fields; 0 to 3 are default fields
		lastExistingFieldLine = 0 # used for adding new extra fields; relative to $COMP (which is zero)

		for line_nr in range(len(self.contents)):
			line  = self.contents[line_nr]

			# Example for a resistor with component=R and ref=R609
			# L R R609
			# the reference here is a common reference, if it is used in multiple instances of a subsheet
			if line[0] == "L":
				searchResult = re.search('L +(.*) +(.*)', line)

				if searchResult:
					componentName = searchResult.group(1)
					componentRef = searchResult.group(2)

					self.reference = componentRef
					self.name = componentName

					DT.debug("Found Component: "
						  + componentName + " " + componentRef)

					# Special case for power-components: don't parse them
					if componentRef[0] == "#":
						self.unlisted = True
						return # no further parsing for unlisted components

					continue

				else:
					DT.error("Regex Missmatch for L-record in line: " +
						  line + " in file " + self.schematicName)
				# endelse
			# endif L


			# Unit: Example
			# U 1 1 5873950B
			if line[0:2] == "U ":
				searchResult = re.search('U +(\d*) +(\d+) +([0-9A-Fa-f]+) *', line)

				if searchResult:
					componentUnit = searchResult.group(1)
					componentMm = searchResult.group(2) # could not find a proper meaning of this value other than 'mm'
					componentTimestamp = searchResult.group(3) # unused here
					self.unit = componentUnit
					continue
				else:
					DT.error("Regex Missmatch for 'U '-record in line: " +
						  line + " in file " + self.schematicName)
				# end else
			# endif U

			# Example:
			# AR Path="/56647084/5664BC85" Ref="U501"  Part="2"
			# the number for Part= varies e.g. from 1 to 4 for a component with 4 Units (e.g. LM324)
			# NOTE; it is not clear, for what reason we get this record only for some components...
			# we print just a message
			# for now, we don't use the data any further
			if "AR Path=" in line:
				# extract the path, Ref and Part into regex groups:
				searchResult = re.search('AR +Path="(.*)" +Ref="(.*)" +Part="(.*)".*', line)

				if searchResult:
					componentPath = searchResult.group(1)
					componentRef = searchResult.group(2)
					componentUnit = searchResult.group(3)

					# Print some messages
					DT.debug('AR Record: ' + componentPath + ' ' + componentRef + ' ' + componentUnit)

			# Example
			# F 0 "R51" H 5820 2046 50  0000 L CNN
			if line[0:4] == "F 0 ":
				if line_nr > lastExistingFieldLine:
					lastExistingFieldLine = line_nr

				searchResult = re.search('F 0 +"(.*)" +.*', line)

				if searchResult:
					componentRef = searchResult.group(1)

					# TODO 1: handle proper reference name for multiple instances
					# we get the unique references only from the AR-records!!!

					#self.referenceUnique = componentRef

					if not (componentRef == self.reference):
						DT.info("L record value doesn't match 'F 0 ' record: "\
							  + self.reference + " vs. " + componentRef + " in '" +\
						  line + "' in file " + self.schematicName + ". Using 'F 0' records value: " + componentRef)
						self.reference = componentRef
					continue
				else:
					DT.error("Regex Missmatch for 'F 0 '-record in line: " +\
						  line + " in file " + self.schematicName)
				# endelse
			# endif F 0




			# Value, Example:
			# F 1 "LTC2052IS#PBF" H 9750 5550 50  0000 C CNN
			if "F 1 " in line:  # find f1 indicating value field in EEschema file format
				if line_nr > lastExistingFieldLine:
					lastExistingFieldLine = line_nr

				searchResult = re.search('F 1 +"(.*)".*', line)

				if searchResult:
					componentValue = searchResult.group(1)
					self.value = componentValue
					continue
				else:
					DT.error("Regex Mismatch, cannot find value in 'F 1 '-record in '" +
						  line + "' in file " + self.schematicName)
				# end if
			# endif F 1

			# Footprint, Example:
			# F 2 "standardSMD:R0603" V 5680 2000 50  0001 C CNN
			if "F 2 " in line:  # find f2 indicating Footprint field in EEschema file format
				if line_nr > lastExistingFieldLine:
					lastExistingFieldLine = line_nr

				searchResult = re.search('F 2 +"(.*)".*', line)

				if searchResult:
					componentFootprint = searchResult.group(1)
					self.footprint = componentFootprint
					continue
				else:
					DT.error("Regex Mismatch, cannot find value in 'F 2 '-record (footprint) in '" +
						  line + "' in file " + self.schematicName)
				# end if
				# endif F 2

			#
			# Datasheet; Example:
			# F 3 "" H 5750 2000 50  0000 C CNN
			if "F 3 " in line:  # find f3 indicating Datasheet field in EEschema file format
				if line_nr > lastExistingFieldLine:
					lastExistingFieldLine = line_nr

				fieldTemplate = line # use the Datasheet field as a template for new extra fields

				searchResult = re.search('F 3 +"(.*)".*', line)

				if searchResult:
					componentDatasheet = searchResult.group(1)
					self.datasheet = componentDatasheet
					continue
				else:
					DT.error("Regex Mismatch, cannot find value in 'F 3 '-record (datasheet) in '" +
						  line + "' in file " + self.schematicName)
				# end if
				# endif F 3
			else:
				# Custom Fields, Example:
				# F 4 "C3216-100n-50V" H 8450 6050 60  0001 C CNN "InternalName"
			
				searchResult = re.search('F +([0-9]+) +"(.*)" +.*"(.*)".*', line)
				if searchResult:
					if line_nr > lastExistingFieldLine:
						lastExistingFieldLine = line_nr

					fieldNr = int(searchResult.group(1))
					if fieldNr > maxFieldNr:
						maxFieldNr = fieldNr

					fieldValue = searchResult.group(2)
					fieldName = searchResult.group(3)
					print(fieldValue)
					print(fieldName)
					tempFound = False
					for anyField in self.fieldList:
						for Alias in anyField.Aliases:
							if Alias == fieldName:
								if fieldFound[anyField] is True:
									DT.warning("duplicate definition of Field " + fieldName + " with Alias " + Alias
										  + " for Component " + self.getReference()
										  + " in file " + self.schematicName)
								fieldFound[anyField] = True
								tempFound = True
								cf = ComponentField()
								cf.setContent(line)
								cf.relativeLine = line_nr
								self.propertyList.append(cf) 
								print(fieldName + "added to propertylist ")
								
								break
						if tempFound == True:
							break
					if tempFound == True:
						continue
				#endif Regex
			#end for(all lines)

		# set default values for non-found fields:
		
		
		#for anyField in self.fieldList:
		#	if fieldFound[anyField] == False:
		#		print(anyField.name)
		#		cf = ComponentField() # TODO 0: set template line here
		#		cf.setContent(fieldTemplate) #this is broken for empty fields will result in datasheet values being added to fields/keywords which cannot be found
		#		cf.visibility = '0001'
		#		cf.number = maxFieldNr+1
		#		maxFieldNr += 1
		#		cf.relativeLine = lastExistingFieldLine
		#		cf.exists = False
		#		cf.name = anyField.name
		#		self.propertyList.append(cf)

	# Find all matching ComponentFild objects with the properties from the CSV,
	# and update their values.
	def updateAllMatchingFieldValues(self, csvPropertyList):
		for csvProperty in csvPropertyList:
			for schProperty in self.propertyList:
				# TODO 2: strange csvProperty usage, should be fixed
				if csvProperty[0].name == schProperty.name:  # matching property names
					schProperty.value = csvProperty[1]  # copy CSV property data to SCH property


class CsvComponent(object):
	def __init__(self):
		self.name = ""  # component library name, e.g. D_Schottky
		self.reference = "" # Component reference e.g. R517
		self.unit = "" # unit
		self.value = "" # component value, e.g. 4k7
		self.footprint = ""  # footprint incl. library, e.g. standardSMD:R1608
		self.datasheet = ""  #
		self.schematic = ""  # filename of the schematic (sub-) sheet

		# refactor the field extraction
		self.propertyList = []
		self.Contents = ""
		self.fieldList = [];
		self.fieldOrder = [];

	def printprops(self):
		print(self.name)
		print(self.reference)
		print(self.unit)
		print(self.value)
		print(self.footprint)
		print(self.datasheet)
		print(self.schematic)
		print(self.propertyList)

	def setName(self,name):
		self.name = name

	def getName(self):
		return self.name

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


# CsvFile class is used to read a given CSV file and build up the components list.
class CsvFile(object):
	def __init__(self):
			self.contents = []
			self.components = []
			self.fieldList = []

	def setContents(self, to_be_inserted):
		self.contents = to_be_inserted

	def printContents(self):
		print(self.contents)

	def printLine(self, line):
		print(self.contents[line])

	# reads the content of the CSV and extracts the contained components
	def extractCsvComponents(self):
		if globals.CsvSeparator not in self.contents[1]:
			return 'error: no delimiter found in CSV. ' + '"' + globals.CsvSeparator + '" expected. See config.ini'

		# Find the order of the parameters saved in the csv
		header = self.contents[0]
		header = header.strip('\n')
		header = header.strip('\r')
		columnNames = header.split(globals.CsvSeparator)

		if len(columnNames) < 7:
			return 'error: missing delimiter(s) in CSV. ' + 'At least 7 occurrences of "' + globals.CsvSeparator + '" expected. See config.ini'

		for c in columnNames:
			new_csv_field = KicadField()
			new_csv_field.name = c
			self.fieldList.append(new_csv_field)

		#parse date belonging to component
		for i in range(1, len(self.contents)):
			newCsvComponent = CsvComponent()

			dataLine = self.contents[i]
			newCsvComponent.Contents = self.contents[i]

			dataLine = dataLine.strip('\n')
			dataLine = dataLine.strip('\r')
			values = dataLine.split(globals.CsvSeparator)

			column = 0
			for value in values:
				# TODO 3: replace these constants with a common definition in globals
				if columnNames[column] == 'Part':
					newCsvComponent.name = value
				elif columnNames[column] == 'Reference':
					newCsvComponent.reference = value
				elif columnNames[column] == 'Unit':
					newCsvComponent.unit = value
				elif columnNames[column] == 'Value':
					newCsvComponent.value = value
				elif columnNames[column] == 'Footprint':
					newCsvComponent.footprint = value
				elif columnNames[column] == 'Datasheet':
					newCsvComponent.datasheet = value
				elif columnNames[column] == 'File':
					newCsvComponent.schematic = value
				else:
					newCsvComponent.propertyList.append([self.fieldList[column], value])

				column += 1
			# end for all values in dataLine

			self.components.append(newCsvComponent)

		DT.info("finished component extractions")

	def deleteContents(self):
		for i in range (len(self.components)):
			del self.components[0]
		self.contents = []
		self.components = []
		#break









class KicadField(object):
	def __init__(self):
		self.Aliases = []
		self.name = ""
		self.contents = ""

	def appendAlias(self,newAlias):
		self.Aliases.append(newAlias)
	def MatchField(self, stringToMatch):
		if stringToMatch == self.name:
			return True
		else:
			for Alias in self.Aliases:
				if stringToMatch == Alias:
					return True
					break
			else:
				return False

