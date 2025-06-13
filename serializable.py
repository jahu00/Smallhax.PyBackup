import json
from enum import Enum

class Serializable:
    def to_serializable(self):
        result = {}
        for key, value in self.__dict__.items():
                result[key] = Serializable.__to_serializable(value)
        
        return result
    
    def to_json(self):
        serializable = self.to_serializable()
        return json.dumps(serializable)
    
    def save_to_file(self, file_name):
        _json = self.to_json()
        with open(file_name, "w") as file:
            file.write(_json)

    @staticmethod
    def __to_serializable(value):
        if isinstance(value, list):
            result = []
            for item in value:
                result.append(Serializable.__to_serializable(item))
            return result
        
        if isinstance(value, Serializable):
            return value.to_serializable()
        
        if isinstance(value, Enum):
            return value.value
        
        return value
    
    @classmethod
    def from_dict(cls, dict):
        return cls(**dict)
    
    @classmethod
    def from_json(cls, _json):
        dict = json.loads(_json)
        return cls.from_dict(dict)
    
    @classmethod
    def from_file(cls, file_name):
        with open(file_name, "r") as file:
            _json = file.read()
        return cls.from_json(_json)
    

