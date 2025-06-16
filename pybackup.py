import argparse
from itertools import groupby
from classes import FileDump

parser = argparse.ArgumentParser(description="Sunchronizes destination path with source")
parser.add_argument("--src", type=str, help="source path/JSON dump", required=True)
parser.add_argument("--dst", type=str, help="destination path/JSON dump", required=True)
parser.add_argument("--move", type=bool, help="allow move operation", default=True)
parser.add_argument("--min", type=int, help="min file size for move operation (in bytes)", default=1048576, required=False)

args = parser.parse_args()

print(f"Comparing {args.src} to {args.dst}")

if args.src.endswith(".json"):
    src_dump = FileDump.from_file(args.src)
else:
    src_dump = FileDump.from_path(args.src)

if args.dst.endswith(".json"):
    dst_dump = FileDump.from_file(args.dst)
else:
    dst_dump = FileDump.from_path(args.dst)

operations = src_dump.compare(dst_dump, args.move, args.min)
keys = []
groups = {}
for key, group in groupby(operations.operations, lambda x: x.operation):
    if key not in keys:
        keys.append(key)
        groups[key] = []
    groups[key] += list(group)
   
for key in keys:
   print(f"{len(groups[key])} {key} operations")

print("Executing operations")
operation_count = len(operations.operations)
for operation in operations.operations:
    operations.index += 1
    progress = f"{operations.index}/{operation_count}"
    match operation.operation:
        case "match":
            print(f"{progress} - Skipping {operation.src}")
            pass
        case "copy":
            print(f"{progress} - Copying {operation.src} to {operation.dst}")
        case "move":
            print(f"{progress} - Moving {operation.src} to {operation.dst}")
        case "delete":
            print(f"{progress} - Deleting {operation.src}")
        case "create":
            print(f"{progress} - Creating directory {operation.src}")
        case _:
            raise Exception(f"Unsupported operation {operation.operation} on file {operation.src}")
        
    operation.perform()