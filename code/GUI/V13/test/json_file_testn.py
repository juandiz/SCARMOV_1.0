import sys
data = [0,1,2]

sys.path.append('C:/Users/JMAD/Documents/TFG/GitHub/GUI/V13')

from file_manager import FileManager

file = FileManager()

file.updateAttrValue("name",88)

u = data[-1]

file.writeFile()

