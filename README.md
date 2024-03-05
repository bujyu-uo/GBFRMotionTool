# \# GBFRMotionTools

This tool is inspired by [NieR2Blender2NieR](https://github.com/WoefulWolf/NieR2Blender2NieR) and [GBFR2Blender2GBFR](https://github.com/WistfulHopes/GBFR2Blender2GBFR),
and simplify the dependencies of module / package, focus on dump / batch processing mot-file in CLI.

# \# Setup

You can use your python environment.

OR, download the python embeddable package and rename the ```python<python_ver>._pth``` under the folder.

## How to install pip and install pacakge for python embbedable pacakage on windows

- Get get-pip-py 
```
https://pip.pypa.io/en/stable/installation/#get-pip-py
```

- Install pip tool
```
python.exe get-pip-py
```

- Install package by pip
```
python.exe Scripts\pip.exe install <package_name>
```

# \# Package dependency

  - jsonpickle (pip)

# \# Usage

```
usage: cli.py [-h] --file FILE --action {dump,apply_and_export,match} [--output OUTPUT] [--task TASK]

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  file .mot
  --action {dump,apply_and_export,match}, -a {dump,apply_and_export,match}
                        specified the action for cli
  --output OUTPUT, -o OUTPUT
                        output file path
  --task TASK, -t TASK  Task file for modifying the mot file
```

# \# Limitaions

1. Only support to batch modify which record field ```interpolationType``` is 0 / 1 now.


# \# File \<task-file\>

## sample_task.json
```
[
    {
        "description": "transform bone _000 with subtracting 0.026782 on y-axis",
        "//conditions": "all conditions will test IN ORDER, and stop when any condition test is false",
        "//conditions.field": "please check the dump content of .mot",
        "//conditions.field.propertyIndex.0": "0, 1, 2: location; 3, 4, 5: rotation_euler; 6, 7, 8: scale",
        "//conditions.field.propertyIndex.1": "0, 3, 6: x-axis;   1, 4, 7: y-axis;         2, 5, 8: z-axis",
        "//conditions.operator": [ "==", ">=", "<=", ">", "<" ],
        "conditions": [
            {
                "field": "boneIndex",
                "operator": "==",
                "value": 0
            },
            {
                "field": "propertyIndex",
                "operator": "==",
                "value": 1
            },
            {
                "field": "interpolationType",
                "operator": "==",
                "value": 1
            }
        ],
        "//modifications": "all operators will apply IN ORDER, and apply to record.value / record.interpolation.value / record.interpolation.values according to record.interpolationType",
        "//modifications.operator": [ "+", "-", "*", "/", "//", "=" ],
        "//modifications.operator.//": "(PYTOHN) floored quotient",
        "//modifications.operator.=": "overwrite",
        "modifications": [
            {
                "operator": "-",
                "value": 0.026782
            }
        ]
    }
]
```