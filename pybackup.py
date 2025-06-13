import json
from classes import FileDump, FileOperations

src_dump = FileDump.from_path("../temp")
dst_dump = FileDump.from_path("../temp2")
src_dump.save_to_file("temp.json")
temp = FileDump.from_file("temp.json")
print("test")

#operations = FileOperations(src_dump.compare(dst_dump))
#operations.save_to_file("temp.json")
