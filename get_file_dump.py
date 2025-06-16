import argparse
from classes import FileDump

parser = argparse.ArgumentParser(description="Dumps file/directory structure to JSON file")
parser.add_argument("--path", type=str, help="source path")
parser.add_argument("--output", type=str, help="output JSON")

args = parser.parse_args()

print(f"Scanning {args.path}")
dump = FileDump.from_path(args.path)
count = len(dump.files)
print(f"Found {count} files and directories")
print(f"Saving output to {args.output}")
dump.save_to_file(args.output)
