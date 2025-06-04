import json
from file_dump import FileDump
from file_operations import FileOperations

src_dump = FileDump.from_path("../temp")
dst_dump = FileDump.from_path("../temp2")
operations = FileOperations(src_dump.compare(dst_dump))
operations.save_to_file("temp.json")
