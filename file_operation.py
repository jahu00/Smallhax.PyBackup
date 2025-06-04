from serializable import Serializable
class FileOperation(Serializable):
    def __init__(self, operation, src, dst = None):
        self.src = src
        self.operation = operation
        self.dst = dst

    def __repr__(self):
       return f"FileOperation operation={self.operation}, src='{self.src}', dst='{self.dst}'"