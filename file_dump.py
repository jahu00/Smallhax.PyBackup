import os
import copy
from serializable import Serializable
from file_entry import FileEntry
from file_operation import FileOperation
class FileDump(Serializable):
    def __init__(self, path, files: list[FileEntry]):
        self.path = path
        self.files: list[FileEntry] = files

    def get_index(self) -> dict[str,FileEntry]:
        index = {}
        for file in self.files:
            index[file.relative_path] = file
        return index
    
    def get_name_index(self) -> dict[str,FileEntry]:
        index = {}
        for file in self.files:
            entry = index.get(file.name)
            if entry is None:
                entry = []
                index[file.name] = entry
            entry.append(file)
        return index
    
    def compare(self, dst_dump, allow_move=False) -> list[FileOperation]:
        return FileDump.__compare(self, dst_dump, allow_move)

    @staticmethod
    def from_path(path, index = None, name_index = None):
        if not os.path.isdir(path):
            raise ValueError(f"The provided path '{path}' is not a valid directory.")

        file_entries = []

        for root, _, files in os.walk(path):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(full_path, start=path)
                file_size = os.path.getsize(full_path)

                file_entry = FileEntry(
                    relative_path=relative_path,
                    name=file_name,
                    size=file_size
                )

                file_entries.append(file_entry)
                if index is not None:
                    index[file_entry.relative_path] = file_entry

                if name_index is not None:
                    index_entry = name_index.get(file_entry.name)
                    if index_entry is None:
                        index_entry = []
                        name_index[file_entry.name] = index_entry
                    index_entry.append(file_entry)

        return FileDump(path, file_entries)
    
    @staticmethod
    def __compare(src_dump, dst_dump, allow_move=False) -> list[FileOperation]:
        src_dump = copy.deepcopy(src_dump)
        dst_dump = copy.deepcopy(dst_dump)
        dst_index = dst_dump.get_index()
        dst_name_index = dst_dump.get_name_index()
        operations = []

        for src_file in src_dump.files:
            #print(file)
            dst_file = dst_index.get(src_file.relative_path)
            src_path = os.path.join(src_dump.path, src_file.relative_path)
            dst_path = os.path.join(dst_dump.path, src_file.relative_path)
            dst_name_entry = dst_name_index.get(src_file.name)
            if dst_file is not None:
                dst_dump.files.remove(dst_file)
                dst_name_entry.remove(dst_file)
                if len(dst_name_entry) == 0:
                    del dst_index[src_file.relative_path]

                if dst_file.size == src_file.size:
                    operations.append(FileOperation('match', src_path, dst_path))
                else:
                    operations.append(FileOperation('copy', src_path, dst_path))
                continue

            if allow_move and dst_name_entry is not None:
                dst_file = next((x for x in dst_name_entry if x.size == src_file.size), None)
                if dst_file is not None:
                    dst_dump.files.remove(dst_file)
                    dst_name_entry.remove(dst_file)
                    if len(dst_name_entry) == 0:
                        del dst_index[src_file.relative_path]

                    operations.append(FileOperation('move', os.path.join(dst_dump.path, dst_file.relative_path), dst_path))
                    continue

            operations.append(FileOperation('copy', src_path, dst_path))

        for dst_file in dst_dump.files:
            dst_path = os.path.join(dst_dump.path, dst_file.relative_path)
            operations.append(FileOperation('delete', dst_path))

        return operations
    
    @classmethod
    def from_dict(cls, dict):
        files = []
        for file in dict["files"]:
            files.append(FileEntry.from_dict(file))
        return cls(path=dict["path"], files=files)