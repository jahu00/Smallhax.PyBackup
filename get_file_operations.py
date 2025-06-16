import argparse
from itertools import groupby
from classes import FileDump

parser = argparse.ArgumentParser(description="Compares file dumps and prepares an operation list for syncing destination to source")
parser.add_argument("--src", type=str, help="source path/JSON", required=True)
parser.add_argument("--dst", type=str, help="destination path/JSON", required=True)
parser.add_argument("--output", type=str, help="output JSON", required=False)
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

if args.output is not None:
    print(f"Saving output to {args.output}")
    operations.save_to_file(args.output)