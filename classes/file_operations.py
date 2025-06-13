from serializable import Serializable
from file_operation import FileOperation
class FileOperations(Serializable):
    def __init__(self, operations: list[FileOperation], index = 0):
        self.operations = operations
        self.index = index

    @classmethod
    def from_dict(cls, dict):
        operations = []
        for operation in dict["operations"]:
            operations.append(FileOperation.from_dict(operation))
        return cls(operations=operations, index=dict["index"])