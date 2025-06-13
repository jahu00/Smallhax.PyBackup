from .serializable import Serializable
from .file_type import FileType

class FileEntry(Serializable):
    def __init__(self, relative_path, name, size, type: FileType):
        self.relative_path = relative_path
        self.name = name
        self.size = size
        self.type = type

    def __repr__(self):
        return f"FileEntry(path='{self.relative_path}', name='{self.name}', size={self.size})"
    
    @classmethod
    def from_dict(cls, dict):
        dict["type"] = FileType(dict["type"])
        return cls(**dict)
   
