import os
import argparse
import pathlib
import sys

from package import mot
from package import task

def _check_magic(file: str, magic: str):
    with open(file, "rb") as fobj:
        data = fobj.read(len(magic))
    if data == None:
        return False
    elif data.decode("ASCII") != magic:
        return False
    return True


def _dump_json_to_file(file: str, mobj: mot):    
    import jsonpickle # pip install jsonpickle
    import json

    serialized = jsonpickle.encode(mobj)
    with open(file, "w") as f:
        json.dump(json.loads(serialized), fp=f, indent=2)


def dump_mot_as_json(args: argparse, files: list[pathlib.Path], basepath: pathlib.Path):
    for file in files:
        if basepath is not None:
            ofilepath = basepath / f"{file.name}.json"
        else:
            ofilepath = file.parent / f"{file.name}.json"

        mobj = mot.MotFile()
        with open(str(file), "rb") as fobj:
            mobj.fromFile(fobj)

        print(f"+ {file.name}: ")

        _dump_json_to_file(str(ofilepath), mobj)


def apply_and_export(args: argparse, files: list[pathlib.Path], basepath: pathlib.Path):
    if args.task is None:
        raise UserWarning("No task specified ...")

    for file in files:
        if basepath is not None:
            ofilepath = basepath / f"mod_{file.name}"
        else:
            ofilepath = file.parent / f"mod_{file.name}"
    
        mobj = mot.MotFile()
        with open(str(file), "rb") as fobj:
            mobj.fromFile(fobj)

        print(f"+ {file.name}: ")

        if args.debug:
            if basepath is not None:
                debug_json_filepath = basepath / f"{file.name}.json"
            else:
                debug_json_filepath = file.parent / f"{file.name}.json"
            _dump_json_to_file(str(debug_json_filepath), mobj)

        ret = False
        for it in enumerate(mobj.records):
            ret = ret | task.apply(args.task, it)

        # if no modification applied, do not write out mot object
        if not ret:
            continue
        
        with open(ofilepath, "wb") as fobj:
            mobj.writeToFile(fobj)

        if args.debug:
            debug_json_filepath = ofilepath.parent / f"{ofilepath.name}.json"
            _dump_json_to_file(str(debug_json_filepath), mobj)


def match(args: argparse, files: list[pathlib.Path], output_path: pathlib.Path):
    if args.task is None:
        raise UserWarning("No task specified ...")
    
    for file in files:
        mobj = mot.MotFile()
        with open(str(file), "rb") as fobj:
            mobj.fromFile(fobj)

        print(f"+ {file.name}: ")
        ret = False
        for it in enumerate(mobj.records):
            ret = ret | task.match(args.task, it)


action_table = {
    "dump": dump_mot_as_json,
    "apply_and_export": apply_and_export,
    "match": match
}


def main(args: argparse, files: list[pathlib.Path], output_path: pathlib.Path):
    if args.action in action_table:
        action_table[args.action](args, files, output_path)
        return
    raise UserWarning("Not supported action ...")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", "-a", help="specified the action for cli", type=str, choices=[k for k in action_table], required=True)
    parser.add_argument("--output", "-o", help="output directory", type=str)
    parser.add_argument("--task", "-t", help="Task file for modifying the mot file", type=str)
    parser.add_argument("--debug", "-d", help="Generate debug information", action="store_true")
    parser.add_argument('files', help="file .mot or directory includes .mot", nargs='+')
    args = parser.parse_args()

    # check ambiguous arguments here
    file_list = []
    for arg in args.files:
        pth = pathlib.Path(arg)
        if pth.is_file():
            if pth.suffix != ".mot":
                continue
            file_list.append(pth)
        elif pth.is_dir():
            print("> Expand the directory (no nested expand) ...")
            file_list.extend([child for child in pth.glob("*.mot") if child.is_file()])
        else:
            raise UserWarning(f"Unsupported file type ... {pth.absolute()}")
    '''
    for file in file_list:
        if not _check_magic(str(file), "mot"):
            raise UserWarning(f"Not supported mot file ... {file.absolute()}")
    '''
    if len(file_list) == 0:
        parser.print_help()
        raise UserWarning(f"No valid file ...")

    # check output here
    basepath = None
    if args.output is not None:
        basepath = pathlib.Path(args.output)
        if not basepath.exists():
            print("> Create output directory ...")
            basepath.mkdir(parents=True)
        elif not basepath.is_dir():
            raise UserWarning("Argument \"output\" does not target directory")

    main(args, file_list, basepath)