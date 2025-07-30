import os
import shutil
from .serializable import Serializable

class FileOperation(Serializable):
    def __init__(self, operation, src, dst = None):
        self.src = src
        self.operation = operation
        self.dst = dst

    def __repr__(self):
       return f"FileOperation operation={self.operation}, src='{self.src}', dst='{self.dst}'"
    
    def perform(self):
        match self.operation:
            case "match":
                #nothing to do
                pass
            case "copy":
                #self.ensure_path_exists()
                shutil.copy2(self.src, self.dst)
            case "move":
                #self.ensure_path_exists()
                shutil.move(self.src, self.dst)
            case "delete":
                if os.path.isdir(self.src):
                    os.rmdir(self.src)
                else:
                    os.remove(self.src)
            case "create":
                os.makedirs(self.src)
            case _:
                raise Exception(f"Unsupported operation {self.operation}")
    
    def ensure_path_exists(self):
        directory = os.path.dirname(self.dst)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        