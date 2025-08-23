import os
import copy
from .serializable import Serializable
from .file_entry import FileEntry
from .file_type import FileType
from .file_operation import FileOperation
from .file_operations import FileOperations

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
    
    def compare(self, dst_dump, allow_move=False, move_min_size=0) -> FileOperations:
        return FileDump.__compare(self, dst_dump, allow_move, move_min_size)

    @staticmethod
    def from_path(path, index = None, name_index = None):
        if not os.path.isdir(path):
            raise ValueError(f"The provided path '{path}' is not a valid directory.")

        file_entries = []
        for root, directories, files in os.walk(path):
            for directory_name in directories:
                dir_full_path = os.path.join(root, directory_name)
                dir_relative_path = os.path.relpath(dir_full_path, start=path)
                file_entries.append(FileEntry(dir_relative_path, directory_name, None, FileType.Directory))

            for file_name in files:
                full_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(full_path, start=path)
                file_size = os.path.getsize(full_path)

                file_entry = FileEntry(
                    relative_path=relative_path,
                    name=file_name,
                    size=file_size,
                    type=FileType.File
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
    def __compare(src_dump, dst_dump, allow_move=False, move_min_size=0) -> FileOperations:
        src_dump: FileDump = copy.deepcopy(src_dump)
        dst_dump: FileDump = copy.deepcopy(dst_dump)
        dst_index = dst_dump.get_index()
        dst_name_index = dst_dump.get_name_index()
        operations = []

        for src_file in src_dump.files:
            #print(file)
            dst_file: FileEntry | None = dst_index.get(src_file.relative_path)
            src_path = os.path.join(src_dump.path, src_file.relative_path)
            dst_path = os.path.join(dst_dump.path, src_file.relative_path)
            dst_name_entry: list[FileEntry] | None = dst_name_index.get(src_file.name)
            if dst_file is not None:
                dst_dump.files.remove(dst_file)
                dst_name_entry.remove(dst_file)
                if len(dst_name_entry) == 0:
                    del dst_name_index[dst_file.name]

                del dst_index[dst_file.relative_path]

                if (
                        (src_file.type == FileType.Directory and dst_file.type == FileType.Directory)
                        or (src_file.type == FileType.File and dst_file.type == FileType.File and dst_file.size == src_file.size)
                    ):
                    operations.append(FileOperation('match', src_path, dst_path))
                    continue
                
                operations.append(FileOperation('delete', dst_path, size=dst_file.size))
                
                if src_file.type == FileType.File:
                    operations.append(FileOperation('copy', src_path, dst_path, size=src_file.size))
                    continue
                else:
                    operations.append(FileOperation('create', dst_path))
                    continue
                

            if allow_move and src_file.type == FileType.File and src_file.size > move_min_size and dst_name_entry is not None:
                dst_file = next((x for x in dst_name_entry if x.size == src_file.size and x.type == FileType.File), None)
                if dst_file is not None:
                    dst_dump.files.remove(dst_file)
                    dst_name_entry.remove(dst_file)
                    if len(dst_name_entry) == 0:
                        del dst_name_index[src_file.name]

                    del dst_index[dst_file.relative_path]

                    operations.append(FileOperation('move', os.path.join(dst_dump.path, dst_file.relative_path), dst_path, size=dst_file.size))
                    continue

            if src_file.type == FileType.File:
                operations.append(FileOperation('copy', src_path, dst_path, size=src_file.size))
                continue
            else:
                operations.append(FileOperation('create', dst_path))
                continue

        for dst_file in reversed(dst_dump.files):
            dst_path = os.path.join(dst_dump.path, dst_file.relative_path)
            operations.append(FileOperation('delete', dst_path, size=dst_file.size))

        return FileOperations(operations)
    
    @classmethod
    def from_dict(cls, dict):
        files = []
        for file in dict["files"]:
            files.append(FileEntry.from_dict(file))
        return cls(path=dict["path"], files=files)