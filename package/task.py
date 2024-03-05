import sys
from collections.abc import Callable

from . import mot

_task_cond_op = {
    "==": lambda a, b: a == b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    "<":  lambda a, b: a < b
}

_record_modifier_op = {
    "+":  lambda a, b: a + b,
    '-':  lambda a, b: a - b,
    "*":  lambda a, b: a * b,
    "/":  lambda a, b: a / b,
    "//": lambda a, b: a // b,
    "=":  lambda a, b: b
}

def _TypeConst(op: Callable, rec: mot.MotRecord, rhs):
    op(rec.interpolation.value, rhs)
    op(rec.value, rhs)

def _TypeValues(op: Callable, rec: mot.MotRecord, rhs):
    new_values = [op(val, rhs) for val in rec.interpolation.values]
    rec.interpolation.values = new_values

_record_modifier = {
    # limited support interpolation type
    0: _TypeConst,
    1: _TypeValues
}

def _task_op_conditon(t, it: tuple[int, mot.MotRecord], callback: Callable = None) -> bool:
    cond_expected = True
    for cond in t['conditions']:
        if cond['operator'] not in _task_cond_op:
            raise UserWarning(f"Unsupported condition operator: {cond['operator']}")
        if cond['field'] not in it[1].__dict__:
            raise UserWarning(f"Unsupported condition field: {cond['field']}")

        cond_op = _task_cond_op[cond['operator']]
        a = it[1].__dict__[cond['field']]
        b = cond['value']
        if cond_expected != cond_op(a, b):
            return False
    
    # call callable when full matching only
    if callback != None:
        condition_strings = []
        for cond in t['conditions']:
            condition_strings.append(f"\tfield:[{cond['field']}] operator:[{cond['operator']}] value:[{cond['value']}]")
        callback("\n".join(condition_strings))

    return True


def _task_op_modifier(t, it: tuple[int, mot.MotRecord]) -> None:
    for m in t['modifications']:
        if it[1].interpolationType not in _record_modifier:
            print(f"Unsupported interpolation type for modifying: {it[1].interpolationType}", file=sys.stderr)
            continue
        if m['operator'] not in _record_modifier_op:
            print(f"Unsupported operator for modifying: {m['operator']}", file=sys.stderr)
            continue
        modifier = _record_modifier[it[1].interpolationType]
        modifier_op = _record_modifier_op[m['operator']]
        modifier(modifier_op, it[1], m['value'])


def apply(path: str, it: tuple[int, mot.MotRecord]):
    import json

    jobj = None
    with open(path, "r") as f:
        jobj = json.load(f)
    if jobj is None:
        raise RuntimeError("Task file")

    for t in jobj:
        # check conditions
        if not _task_op_conditon(t, it):
            continue
        print(f"Record[{it[0]}] matches condition, do task modifier ...")

        # apply modifications
        _task_op_modifier(t, it)


def match(path: str, it: tuple[int, mot.MotRecord]):
    import json

    jobj = None
    with open(path, "r") as f:
        jobj = json.load(f)
    if jobj is None:
        raise RuntimeError("Task file")
    
    for t in jobj:
        # check conditions
        _task_op_conditon(
            t, 
            it, 
            callback=lambda cond_str: print(f"Record[{it[0]}] matches conditions ...\n{cond_str}")
        )