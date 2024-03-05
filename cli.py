import os
import argparse
import pathlib
import sys

from package import mot
from package import task

def check_magic(file, magic):
    with open(file, "rb") as f:
        data = f.read(len(magic))
    if data == None:
        return False
    elif data.decode("ASCII") != magic:
        return False
    return True

def _dump_json_to_file(file, mobj: mot):    
    import jsonpickle # pip install jsonpickle
    import json

    serialized = jsonpickle.encode(mobj)
    with open(file, "w") as f:
        json.dump(json.loads(serialized), fp=f, indent=2)


def dump_mot_as_json(args):
    if args.output is None:
        args.output = args.file + ".json"

    mobj = mot.MotFile()
    with open(args.file, "rb") as f:
        mobj.fromFile(f)

    _dump_json_to_file(args.output, mobj)


def apply_and_export(args):
    import pathlib

    if args.task is None:
        print("No task specified, only export ...", file=sys.stderr)
    if args.output is None:
        pth = pathlib.Path(args.file)
        args.output = str(pth.parent) + "\\" + str(pth.name) + "_mod" + str(pth.suffix)
    elif pathlib.Path(args.output).suffix == ".bxm":
        if pathlib.Path(args.output).samefile(args.file):
            raise UserWarning("file and output have target to same file ...")
    
    mobj = mot.MotFile()
    with open(args.file, "rb") as f:
        mobj.fromFile(f)

    for it in enumerate(mobj.records):
        task.apply(args.task, it)

    _dump_json_to_file(args.output + ".json", mobj)

    with open(args.output, "wb") as f:
        mobj.writeToFile(f)


def match(args):
    import pathlib

    if args.task is None:
        raise UserWarning("No task specified ...")
    
    mobj = mot.MotFile()
    with open(args.file, "rb") as f:
        mobj.fromFile(f)

    print(f"{args.file}:")
    for it in enumerate(mobj.records):
        task.match(args.task, it)


action_table = {
    "dump": dump_mot_as_json,
    "apply_and_export": apply_and_export,
    "match": match
}


def main(args):
    if args.action in action_table:
        action_table[args.action](args)
        return
    raise UserWarning("Not supported action ...")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", "-f", help="file .mot", type=str, required=True)
    parser.add_argument("--action", "-a", help="specified the action for cli", type=str, choices=[k for k in action_table], required=True)
    parser.add_argument("--output", "-o", help="output file path", type=str)
    # For action "apply_and_export" / "match"
    parser.add_argument("--task", "-t", help="Task file for modifying the mot file", type=str)
    args = parser.parse_args()

    # check unify argument "file" here
    if not os.path.exists(args.file):
        parser.print_help()
        raise UserWarning("File is not existing: {} ...".format(args.file))
    elif not check_magic(args.file, "mot"):
        # "mot" at the head 3 bytes
        raise UserWarning("Not supported mot file ...")

    main(args)