class Component(object):
	def __init__(self):
		self.startposition = 0
		self.endposition = 0
		self.FarnellLink = ""
		self.SchematicName = ""
		self.name = ""
		self.annotation = ""
		self.value = ""
		self.MouserLink = ""
		self.DigiKeyLink = ""
	def startpos(self, x):
		self.startposition = x
	def endpos(self,x):
		self.endposition = x
	def SetFarnellLink(self,x):
		self.FarnellLink = x
	def GetFarnellLink(self):
		return self.FarnellLink
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
	def printprops(self):
		print(self.name)
		print(self.annotation)
		print(self.FarnellLink)
		print(self.MouserLink)
		print(self.DigiKeyLink)
		print(self.value)
		print(self.SchematicName)
	def printall(self):
		print(self.startposition)
		print(self.endposition)
		print(self.name)
		print(self.annotation)
		print(self.FarnellLink)
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
	def setMouserLink(self,MouserLink):
		self.MouserLink = MouserLink
	def getMouserLink(self):
		return self.MouserLink
	def setDigiKeyLink(self,DigiKeyLink):
		self.DigiKeyLink = DigiKeyLink
	def getDigiKeyLink(self):
		return self.DigiKeyLink
	def addNewInfo(self, FarnellLink, MouserLink, DigiKeyLink):
		if FarnellLink != self.FarnellLink:
			self.FarnellLink = FarnellLink
		if MouserLink != self.MouserLink:
			self.setMouserLink(MouserLink)
		if DigiKeyLink != self.DigiKeyLink:
			self.setDigiKeyLink(DigiKeyLink)
	#pass

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
		#print(self.contents)
		print(self.numb_of_comps)
		print(self.components)
		#print(self.components[0].GetAnnotation())
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
						#print(count)
						#LastComponent.
					if content[count][0] == "L":
							i = 0
							for i in range(len(content[count])):
								if content[count][len(content[count])-(i+1)] == " ":
									LastComponent.SetAnnotation(content[count][-(i):-1])
									LastComponent.SetName(content[count][2:-(i+1)])
									break
					if "FarnellLink" in content[count] or "farnelllink" in content[count] or "Farnelllink" in content[count] or "farnellLink" in content[count] : 
						testvar = 0
						
						for i in range(len(content[count])):
							if content[count][i] == "\"":
								if testvar == 0:
									startOfString = i+1
									testvar = 1
								else:
									endOfString = i
									break
						LastComponent.SetFarnellLink(content[count][startOfString:endOfString])
					if "MouserLink" in content[count] : 
						testvar = 0
						
						for i in range(len(content[count])):
							if content[count][i] == "\"":
								if testvar == 0:
									startOfString = i+1
									testvar = 1
								else:
									endOfString = i
									break
						LastComponent.setMouserLink(content[count][startOfString:endOfString])
					if "DigiKeyLink" in content[count] : 
						testvar = 0
						
						for i in range(len(content[count])):
							if content[count][i] == "\"":
								if testvar == 0:
									startOfString = i+1
									testvar = 1
								else:
									endOfString = i
									break
						LastComponent.setDigiKeyLink(content[count][startOfString:endOfString])
					
						#ListOfFarnellLinks.append(content[count][startOfString:endOfString])
					count = count + 1
				if not "#" in content[test_var+1]:
					LastComponent.SetFarnellLink = ""
					#ListOfFarnellLinks.append("")
					LastComponent.endpos(count)
				if test_var > 100000: # prevents fails
					break
		
		for subcircuitcounter in range(len(self.subcircuits_names)):
			
			
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
				self.get_subcircuit(subcircuitcounter).ParseComponents()			
				self.AppendComponents(self.get_subcircuit(subcircuitcounter).getComponents())
	def get_subcircuit(self, x):
		return self.subcircuits[x]
	
	def AppendComponents(self, componentList):
		for item in range(len(componentList)):
			self.components.append(componentList[item])
			self.numb_of_comps = self.get_number_of_components() + 1
	def SaveBOMInCSV(self,savepath):
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
			f.write("FarnellLink")
			f.write(",")
			f.write("MouserLink")
			f.write(",")
			f.write("DigiKeyLink")
			f.write(",")
			f.write("Found in: ")
			f.write("\n")
			for item in range(self.get_number_of_components()):#er stond -1
				#print(str(item))
				f.write(self.getComponents()[item].GetAnnotation())
				f.write(",")
				f.write(self.getComponents()[item].GetName())
				f.write(",")
				f.write(self.getComponents()[item].GetFarnellLink())
				f.write(",")
				f.write(self.getComponents()[item].getMouserLink())
				f.write(",")
				f.write(self.getComponents()[item].getDigiKeyLink())
				f.write(",")
				f.write(self.getComponents()[item].GetSchematicName())
				f.write(",")#make conditional
				f.write(str(self.getComponents()[item].getStartLine()))#make conditional
				f.write(",")#make conditional
				f.write(str(self.getComponents()[item].getEndLine()))#make conditional
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
			for i in range (CSV_FILE.getNumberOfComponents()):
				for p in range (self.get_number_of_components()):
					if CSV_FILE.getComponents()[i].getAnnotation() == self.getComponents()[p].GetAnnotation() and self.SchematicName ==  CSV_FILE.getComponents()[i].getSchematic(): 
						toAddFarnellLink = " "
						toAddMouserLink = " "
						toAddDigikeyLink = " "
						if len(CSV_FILE.getComponents()[i].getFarnellLink()) > 1:

							toAddFarnellLink = CSV_FILE.getComponents()[i].getFarnellLink()

						if len(CSV_FILE.getComponents()[i].getMouserLink())>1:
							toAddMouserLink = CSV_FILE.getComponents()[i].getMouserLink()

						if len(CSV_FILE.getComponents()[i].getDigiKeyLink())>1:
							toAddDigikeyLink = CSV_FILE.getComponents()[i].getDigiKeyLink()

						self.getComponents()[p].addNewInfo(toAddFarnellLink,toAddMouserLink,toAddDigikeyLink)

						q = 0

						while self.contents[q+self.getComponents()[p].getStartLine()][0] != "F":

							q = q + 1
						while self.contents[q+self.getComponents()[p].getStartLine()][0] == "F":

							q = q + 1

						q= q -1
						if "FarnellLink" in self.contents[q+self.getComponents()[p].getStartLine()]:
							positions = []
						
							for r in range(len(self.contents[q+self.getComponents()[p].getStartLine()])):
								
								if self.contents[q+self.getComponents()[p].getStartLine()][r] == "\"":
									positions.append(r)
							
									
							self.contents[q+self.getComponents()[p].getStartLine()] = self.contents[q+self.getComponents()[p].getStartLine()][:positions[-4]+1]+self.getComponents()[p].GetFarnellLink() + self.contents[q+self.getComponents()[p].getStartLine()][positions[-3]:]
							
							#place both DigiKeyLink and  MouserLink on same line:
							FarnellLine = self.contents[q+self.getComponents()[p].getStartLine()]
							bufferstring = getCleanLine(self.contents[q-1+self.getComponents()[p].getStartLine()])
							self.contents[q+self.getComponents()[p].getStartLine()] = FarnellLine +  bufferstring[:2] + str(int(bufferstring[2])+2)+ bufferstring[3:5]+ self.getComponents()[p].getMouserLink() + bufferstring[5:-1] + " \"MouserLink\"" + "\n"
							FarnellLine = self.contents[q+self.getComponents()[p].getStartLine()]
							self.contents[q+self.getComponents()[p].getStartLine()] = FarnellLine +  bufferstring[:2] + str(int(bufferstring[2])+3)+ bufferstring[3:5]+ self.getComponents()[p].getDigiKeyLink() + bufferstring[5:-1] + " \"DigiKeyLink\"" + "\n"
							
							#print("HOIHOIHOIHOI")
						elif "MouserLink" in self.contents[q+self.getComponents()[p].getStartLine()]:	
							#PLACE FarnellLink before, DigiKey After
							if "FarnellLink" in self.contents[q-1 + self.getComponents()[p].getStartLine()]: #is FarnellLink in Previous Line
								positions = []
						
								for r in range(len(self.contents[q-1 + self.getComponents()[p].getStartLine()])):
								
									if self.contents[q-1+self.getComponents()[p].getStartLine()][r] == "\"":
										positions.append(r)
																
								self.contents[q-1+self.getComponents()[p].getStartLine()] = self.contents[q-1+self.getComponents()[p].getStartLine()][:positions[-4]+1]+self.getComponents()[p].GetFarnellLink() + self.contents[q-1+self.getComponents()[p].getStartLine()][positions[-3]:]
							#Reparse MouserString
							
							positions = []
						
							for r in range(len(self.contents[q+self.getComponents()[p].getStartLine()])):
								
								if self.contents[q+self.getComponents()[p].getStartLine()][r] == "\"":
									positions.append(r)
							
									
							self.contents[q+self.getComponents()[p].getStartLine()] = self.contents[q+self.getComponents()[p].getStartLine()][:positions[-4]+1]+self.getComponents()[p].getMouserLink() + self.contents[q+self.getComponents()[p].getStartLine()][positions[-3]:]
							
							# add DigiKeyLink onto MouserLink Line
							if "FarnellLink" in self.contents[q-1 + self.getComponents()[p].getStartLine()]:
								bufferstring = getCleanLine(self.contents[q-2+self.getComponents()[p].getStartLine()])
							else:
								bufferstring = getCleanLine(self.contents[q-1+self.getComponents()[p].getStartLine()])
								# PUT FarnellLink in place:
								q = q -1
								bufferstring = self.contents[q+self.getComponents()[p].getStartLine()]
								self.contents[q+self.getComponents()[p].getStartLine()] = self.contents[q+self.getComponents()[p].getStartLine()] +  bufferstring[:2] + str(int(bufferstring[2])+1)+ bufferstring[3:5]+ self.getComponents()[p].GetFarnellLink() + bufferstring[5:-1] + " \"FarnellLink\"" + "\n"
								q = q + 1
								
							MouserLine = self.contents[q+self.getComponents()[p].getStartLine()]
							self.contents[q+self.getComponents()[p].getStartLine()] = MouserLine +  bufferstring[:2] + str(int(bufferstring[2])+1)+ bufferstring[3:5]+ self.getComponents()[p].getDigiKeyLink() + bufferstring[5:-1] + " \"DigiKeyLink\"" + "\n"
						
						
						elif "DigiKeyLink" in self.contents[q+self.getComponents()[p].getStartLine()]:
							orignalBufferLine = ""
							if "FarnellLink" in self.contents[q-2 + self.getComponents()[p].getStartLine()]: #is FarnellLink in the line before previous Line
								orignalBufferLine = getCleanLine(self.contents[q-3 + self.getComponents()[p].getStartLine()])
								positions = []
						
								for r in range(len(self.contents[q-2 + self.getComponents()[p].getStartLine()])):
									if self.contents[q-2+self.getComponents()[p].getStartLine()][r] == "\"":
										positions.append(r)
																
								self.contents[q-2+self.getComponents()[p].getStartLine()] = self.contents[q-2+self.getComponents()[p].getStartLine()][:positions[-4]+1]+self.getComponents()[p].GetFarnellLink() + self.contents[q-2+self.getComponents()[p].getStartLine()][positions[-3]:]
								
								if "MouserLink" in self.contents[q - 1 + self.getComponents()[p].getStartLine()]:
									positions = []
						
									for r in range(len(self.contents[q-1 + self.getComponents()[p].getStartLine()])):
										if self.contents[q-1+self.getComponents()[p].getStartLine()][r] == "\"":
											positions.append(r)
																
									self.contents[q-1+self.getComponents()[p].getStartLine()] = self.contents[q-1+self.getComponents()[p].getStartLine()][:positions[-4]+1]+self.getComponents()[p].getMouserLink() + self.contents[q-1+self.getComponents()[p].getStartLine()][positions[-3]:]
									#controleer
								if "DigiKeyLink" in self.contents[q + self.getComponents()[p].getStartLine()]:
									positions = []
						
									for r in range(len(self.contents[q + self.getComponents()[p].getStartLine()])):
										if self.contents[q+self.getComponents()[p].getStartLine()][r] == "\"":
											positions.append(r)
																
									self.contents[q+self.getComponents()[p].getStartLine()] = self.contents[q+self.getComponents()[p].getStartLine()][:positions[-4]+1]+self.getComponents()[p].getDigiKeyLink() + self.contents[q+self.getComponents()[p].getStartLine()][positions[-3]:]
								
								
								
							elif "FarnellLink" in self.contents[q-1 + self.getComponents()[p].getStartLine()]: #is FarnellLink in Previous Line
								orignalBufferLine = getCleanLine(self.contents[q-2 + self.getComponents()[p].getStartLine()])
								positions = []
						
								for r in range(len(self.contents[q-1 + self.getComponents()[p].getStartLine()])):
									if self.contents[q-1+self.getComponents()[p].getStartLine()][r] == "\"":
										positions.append(r)
																
								self.contents[q-1+self.getComponents()[p].getStartLine()] = self.contents[q-1+self.getComponents()[p].getStartLine()][:positions[-4]+1]+self.getComponents()[p].GetFarnellLink() + self.contents[q-1+self.getComponents()[p].getStartLine()][positions[-3]:]
								#add MouserLink to Previous line
								FarnellLine = self.contents[q-1+self.getComponents()[p].getStartLine()]
								
								self.contents[q+self.getComponents()[p].getStartLine()] = FarnellLine +  orignalBufferLine[:2] + str(int(orignalBufferLine[2])+2)+ orignalBufferLine[3:5]+ self.getComponents()[p].getMouserLink() + orignalBufferLine[5:-1] + " \"MouserLink\"" + "\n"
								
								#Missing DigiKeyLink Operation
								positions = []
						
								for r in range(len(self.contents[q + self.getComponents()[p].getStartLine()])):
									if self.contents[q+self.getComponents()[p].getStartLine()][r] == "\"":
										positions.append(r)
										
								#print(self.contents[q+self.getComponents()[p].getStartLine()][:positions[-4]+1])
								
								self.contents[q+self.getComponents()[p].getStartLine()] = self.contents[q+self.getComponents()[p].getStartLine()][:positions[-4]+1]+self.getComponents()[p].GetFarnellLink() + self.contents[q-1+self.getComponents()[p].getStartLine()][positions[-3]:]
							elif "MouserLink" in self.contents[q-1 + self.getComponents()[p].getStartLine()]:
								#mouserlink in previous line
								bufferstring = getCleanLine(self.contents[q - 2 + self.getComponents()[p].getStartLine()])
								self.contents[q-1 + self.getComponents()[p].getStartLine()] = self.contents[q-1 + self.getComponents()[p].getStartLine()] + bufferstring[:2] + str(int(bufferstring[2])+1)+ bufferstring[3:5]+ self.getComponents()[p].GetFarnellLink() + bufferstring[5:-1] + " \"FarnellLink\"" + "\n"
								
								positions = []
						
								for r in range(len(self.contents[q - 1 + self.getComponents()[p].getStartLine()])):
									if self.contents[q-1+self.getComponents()[p].getStartLine()][r] == "\"":
										positions.append(r)
								self.contents[q -1 +self.getComponents()[p].getStartLine()] = self.contents[q -1 +self.getComponents()[p].getStartLine()][:2] + str(int(bufferstring[2])+2) + self.contents[q -1 +self.getComponents()[p].getStartLine()][3:positions[-4]+1]+self.getComponents()[p].getDigiKeyLink() + self.contents[q - 1 +self.getComponents()[p].getStartLine()][positions[-3]:]
								#print(self.contents[q -1 +self.getComponents()[p].getStartLine()])
								positions = []
						
								for r in range(len(self.contents[q + self.getComponents()[p].getStartLine()])):
									if self.contents[q+self.getComponents()[p].getStartLine()][r] == "\"":
										positions.append(r)
								self.contents[q +self.getComponents()[p].getStartLine()] = self.contents[q +self.getComponents()[p].getStartLine()][:2] + str(int(bufferstring[2])+3) + self.contents[q +self.getComponents()[p].getStartLine()][3:positions[-4]+1]+self.getComponents()[p].getDigiKeyLink() + self.contents[q +self.getComponents()[p].getStartLine()][positions[-3]:]
								
							else:
								#No Links other than DigiKeyLink found
								positions = []
						
								for r in range(len(self.contents[q + self.getComponents()[p].getStartLine()])):
									if self.contents[q+self.getComponents()[p].getStartLine()][r] == "\"":
										positions.append(r)
								
								#print(positions)
								#print(self.contents[q+self.getComponents()[p].getStartLine()])
								bufferstring = getCleanLine(self.contents[q - 1 +self.getComponents()[p].getStartLine()]) #could be wrong if value exist in last line
								self.contents[q+self.getComponents()[p].getStartLine()] = self.contents[q +self.getComponents()[p].getStartLine()][:2] + str(int(bufferstring[2])+3) + self.contents[q+self.getComponents()[p].getStartLine()][3:positions[-4]+1]+self.getComponents()[p].getDigiKeyLink() + self.contents[q+self.getComponents()[p].getStartLine()][positions[-3]:]
								
								
								#bufferstring = getCleanLine(self.contents[q - 1 +self.getComponents()[p].getStartLine()]) #could be wrong if value exist in last line
								self.contents[q-1+self.getComponents()[p].getStartLine()] = self.contents[q-1+self.getComponents()[p].getStartLine()] +  bufferstring[:2] + str(int(bufferstring[2])+1)+ bufferstring[3:5]+ self.getComponents()[p].GetFarnellLink() + bufferstring[5:-1] + " \"FarnellLink\"" + "\n"
								FarnellLine = self.contents[q -1 +self.getComponents()[p].getStartLine()]
								self.contents[q -1 +self.getComponents()[p].getStartLine()] = FarnellLine +  bufferstring[:2] + str(int(bufferstring[2])+2)+ bufferstring[3:5]+ self.getComponents()[p].getMouserLink() + bufferstring[5:-1] + " \"MouserLink\"" + "\n"
						else:
						#No links have been found
							bufferstring = getCleanLine(self.contents[q+self.getComponents()[p].getStartLine()])
														
							self.contents[q+self.getComponents()[p].getStartLine()] = self.contents[q+self.getComponents()[p].getStartLine()] +  bufferstring[:2] + str(int(bufferstring[2])+1)+ bufferstring[3:5]+ self.getComponents()[p].GetFarnellLink() + bufferstring[5:-1] + " \"FarnellLink\"" + "\n"
							FarnellLine = self.contents[q+self.getComponents()[p].getStartLine()]
							self.contents[q+self.getComponents()[p].getStartLine()] = FarnellLine +  bufferstring[:2] + str(int(bufferstring[2])+2)+ bufferstring[3:5]+ self.getComponents()[p].getMouserLink() + bufferstring[5:-1] + " \"MouserLink\"" + "\n"
							MouserLine = self.contents[q+self.getComponents()[p].getStartLine()]
							self.contents[q+self.getComponents()[p].getStartLine()] = MouserLine +  bufferstring[:2] + str(int(bufferstring[2])+3)+ bufferstring[3:5]+ self.getComponents()[p].getDigiKeyLink() + bufferstring[5:-1] + " \"DigiKeyLink\"" + "\n"
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
			self.FarnellLink = ""
			self.SchematicName = ""
			self.name = ""
			self.annotation = ""
			self.value = ""
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
			for i in range(1, len(self.contents)):
				self.components.append(CSV_COMPONENT())
				self.number_of_components = self.number_of_components + 1
				counter = 0
				for p in range(len(self.contents[i])):
					if self.contents[i][p] == ",":
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
		self.FarnellLink = ""
		self.MouserLink = ""
		self.DigiKeyLink = ""
		self.name = ""
		self.schematic = ""
		self.startLine = ""
		self.endLine = ""
	def printprops(self):
		print(self.annotation)
		print(self.FarnellLink)
		#print(self.MouserLink)
		#print(self.DigiKeyLink)
		#print(self.DigiKeyLink)
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
	def setFarnellLink(self, FarnellLink):
		self.FarnellLink = FarnellLink
	def getFarnellLink(self):
		return self.FarnellLink
	def setMouserLink(self, MouserLink):
		self.MouserLink = MouserLink
	def getMouserLink(self):
		return self.MouserLink
	def setDigiKeyLink(self, DigiKeyLink):
		self.DigiKeyLink = DigiKeyLink
	def getDigiKeyLink(self):
		return self.DigiKeyLink
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
