import argparse
from classes import FileDump

parser = argparse.ArgumentParser(description="Compares file dumps and prepares an operation list for syncing destination to source")
parser.add_argument("--src", type=str, help="source path/JSON")
parser.add_argument("--dst", type=str, help="destination path/JSON")
parser.add_argument("--move", type=bool, help="allow move operation", default=False)
parser.add_argument("--min", type=int, help="min file size for move operation (in bytes)", default=1048576)
parser.add_argument("--output", type=str, help="output JSON")

args = parser.parse_args()

if args.src.endswith(".json"):
    src_dump = FileDump.from_file(args.src)
else:
    src_dump = FileDump.from_path(args.src)

if args.dst.endswith(".json"):
    dst_dump = FileDump.from_file(args.dst)
else:
    dst_dump = FileDump.from_path(args.dst)

operations = src_dump.compare(dst_dump, args.move, args.min)
operations.save_to_file(args.output)