from serializable import Serializable

class FileEntry(Serializable):
    def __init__(self, relative_path, name, size):
        self.relative_path = relative_path
        self.name = name
        self.size = size

    def __repr__(self):
        return f"FileEntry(path='{self.relative_path}', name='{self.name}', size={self.size})"
   
