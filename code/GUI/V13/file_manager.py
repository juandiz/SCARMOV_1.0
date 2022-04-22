    
############################################################################################################################################
# Data File management 
############################################################################################################################################

import json
from Defines_global import *

class FileManager():

    def __init__(self,json_base = None, file_path = "DataFiles/data_saved.json"):
        self.save_file_flag = 0
        self.file_path = file_path
        self.file_pointer = open(file = file_path ,mode= "r+")
        if json_base is None:
            self.readFileToJSON()
        else:
            self.save_file_flag = 1
            self.json_file  = json_base
    
    def writeFile(self):
        if self.save_file_flag:
            self.file_pointer.seek(0)
            msg = json.dumps(self.json_file)
            bytes_in_file = self.file_pointer.write(msg)
            self.file_pointer.truncate()
            self.save_file_flag = 0
            return bytes_in_file
        else:
            return 0

    def readFileToJSON(self):
        msg = self.file_pointer.read()
        if len(msg) == 0:
            print("file: " + self.file_path +" is empty, load json struct or load file ")
        else:
            self.json_file  = json.loads(msg)

    def updateAttrValue(self, attr_id , value):
        try:
            if (self.json_file[attr_id] != value):
                self.json_file[attr_id] = value
                self.save_file_flag = 1
                return 1
            else:
                return 0
        except:
            return 0
    
    def getAttrValue(self,attr_id):
        return self.json_file[attr_id]