





class CsvComponent(object):
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
