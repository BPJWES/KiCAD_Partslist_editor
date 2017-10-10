




class Component:
    def __init__(self):
        self.startPosition = 0
        self.endPosition = 0
        self.schematicName = ""
        self.name = ""
        self.annotation = ""
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

    def setAnnotation(self, x):
        self.annotation = x

    def getAnnotation(self):
        return self.annotation

    def setValue(self, x):
        self.value = x

    def getValue(self):
        return self.value

    def printProps(self):
        print(self.name)
        print(self.annotation)
        print(self.value)
        print(self.schematicName)

    def printAll(self):
        print(self.startPosition)
        print(self.endPosition)
        print(self.name)
        print(self.annotation)
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

    def generateProperties(self):
        # parse the contents of a component for Fields
        self.findLastFieldLine()
        for anyField in self.fieldList:
            found = 0
            for Alias in anyField.Aliases:
                for line_nr in range(len(self.contents)):
                    if Alias in self.contents[line_nr]:
                        # find content
                        testvar = 0
                        for i in range(len(self.contents[line_nr])):
                            if self.contents[line_nr][i] == "\"":
                                if testvar == 0:
                                    startOfString = i + 1
                                    testvar = 1
                                else:
                                    endOfString = i
                                    break
                        field_code = self.contents[line_nr][2]  # breaks if more then 10 property fields
                        Data = self.contents[line_nr][startOfString:endOfString]
                        self.propertyList.append(
                            [anyField.name, Data, self.contents[line_nr], line_nr])  # convert to tuple
                        found = 1
                    # break
            if found == 0:
                self.propertyList.append([anyField.name, "", "", 0])  # convert to tuple

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
            lineToBeReturned = lineToBeCleaned[:positions[0] + 1] + lineToBeCleaned[positions[1]:positions[
                                                                                                     2] + 1] + lineToBeCleaned[
                                                                                                               positions[
                                                                                                                   3]:]
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
        self.lastFieldLineNr = self.lastFieldLineNr + 1
        propertyString = cleanLine[:2] + str(self.lastFieldLineNr) + cleanLine[3:5] + self.propertyList[property_nr][
            1] + cleanLine[5:-1] + " \"" + self.propertyList[property_nr][0] + "\"" + "\n"
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

