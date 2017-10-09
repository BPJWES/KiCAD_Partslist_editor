
import KicadField
import CsvComponent


class CsvFile(object):
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
				new_csv_component = CsvComponent()
				new_csv_component.Contents = self.contents[i]
				self.components.append(new_csv_component)
				self.number_of_components = self.number_of_components + 1
				counter = 0
				positionLast = 0
				for p in range(len(self.contents[i])):
					if self.contents[i][p] == delimiter:
							if counter == 0:
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
