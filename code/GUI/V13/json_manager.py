   
import json

# This function makes the parsing of a nlock of velocities to be send and its corresponding delay per motor

class json_manager():
    def __init__(self):
        self.init_json      = 0
        self.data_string    = ''

    def lookForCompleteMSG(self,data):
        if(data == '{'):
            self.init_json = 1
        if(data == '}'):
            self.init_json = 0

        if(self.init_json == 1):
            self.data_string += data
        if(self.init_json == 0): 
            self.data_string += data
            self.json_data_object = json.loads(self.data_string)
            self.data_string = ''
            return 1
        return 0
    
    def json_loadString(self,msg):
        try:
            self.json_data_object = json.loads(msg)
            return 1
        except:
            return 0

    def json_getValue(self,object_name):
        try:
            data = self.json_data_object[object_name]
            return data
        except:
            return "error_reading_json"
    
    def json_to_string(self):
        return json.dumps(self.json_data_object)