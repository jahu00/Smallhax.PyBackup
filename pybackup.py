import argparse
import os
from itertools import groupby
from classes import FileDump

def readable_size(size, step = 1000):
    multiplier = 1
    output_size = size
    while output_size > step:
        output_size /= step
        multiplier += 1
        if multiplier == 7:
            break
    suffix = "?"
    match multiplier:
        case 1:
            suffix = "B"
        case 2:
            suffix = "KB"
        case 3:
            suffix = "MB"
        case 4:
            suffix = "GB"
        case 5:
            suffix = "GB"
        case 6:
            suffix = "TB"
        case 7:
            suffix = "TB"
            
    return str(output_size) + " " + suffix

parser = argparse.ArgumentParser(description="Sunchronizes destination path with source")
parser.add_argument("--src", type=str, help="source path/JSON dump", required=True)
parser.add_argument("--dst", type=str, help="destination path/JSON dump", required=True)
parser.add_argument("--move", type=bool, help="allow move operation", default=True)
parser.add_argument("--min", type=int, help="min file size for move operation (in bytes)", default=1048576, required=False)
parser.add_argument("--confirm", type=int, help="automatically confirm", default=False, required=False)

args = parser.parse_args()

print(f"Comparing {args.src} to {args.dst}")

if args.src.endswith(".json"):
    if not os.path.exists(args.src):
        print(f"Source file {args.src} does not exist. Stopping program.")
        exit()
    src_dump = FileDump.from_file(args.src)
    if not os.path.exists(src_dump.path):
        print(f"Source path {src_dump.path} does not exist. Stopping program.")
        exit()
else:
    if not os.path.exists(args.src):
        print(f"Source path {args.src} does not exist. Stopping program.")
        exit()
    src_dump = FileDump.from_path(args.src)

if args.dst.endswith(".json"):
    if not os.path.exists(args.dst):
        print(f"Destination file {args.dst} does not exist. Stopping program.")
        exit()
    dst_dump = FileDump.from_file(args.dst)
    if not os.path.exists(dst_dump.path):
        print(f"Destination path {dst_dump.path} does not exist. Stopping program.")
        exit()
else:
    if not os.path.exists(args.dst):
        print(f"Destination path {args.dst} does not exist. Stopping program.")
        exit()
    dst_dump = FileDump.from_path(args.dst)

operations = src_dump.compare(dst_dump, args.move, args.min)
print(" ")
keys = []
groups = {}
for key, group in groupby(operations.operations, lambda x: x.operation):
    if key not in keys:
        keys.append(key)
        groups[key] = []
    groups[key] += list(group)
   
for key in keys:
   print(f"{len(groups[key])} {key} operations")

operations.operations[:] = [x for x in operations.operations if not x.operation == "match"]
operation_count = len(operations.operations)
print("Total operations: ", operation_count)
print(" ")

if operation_count == 0:
    print("Exiting, nothing to do.")
    exit()

copy_size = sum(operation.size for operation in operations.operations if operation.operation == "copy")
delete_size = sum(operation.size or 0 for operation in operations.operations if operation.operation == "delete")
move_size = sum(operation.size for operation in operations.operations if operation.operation == "move")

print("Copy: ", readable_size(copy_size))
print("Delete: ", readable_size(delete_size))
print("Move: ", readable_size(move_size))
print(" ")

dst_stat = os.statvfs(dst_dump.path)
free_space = dst_stat.f_bavail * dst_stat.f_bsize

print("Free space: ", readable_size(free_space))
print(" ")

if not args.confirm:
    confirm = input("Apply operations? (y/n) ").lower() == "y"

    if not confirm:
        print("Exiting without applying operations.")
        exit()

print(" ")
print("Executing operations")

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
    # TODO: Measure time and report MB/s, possibly average and do it only for copy operations   
    operation.perform()