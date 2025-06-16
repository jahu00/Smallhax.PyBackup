import argparse
from classes import FileDump

parser = argparse.ArgumentParser(description="Dumps file/directory structure to JSON file")
parser.add_argument("--path", type=str, help="source path")
parser.add_argument("--output", type=str, help="output JSON")

args = parser.parse_args()

dump = FileDump.from_path(args.path)
dump.save_to_file(args.output)
