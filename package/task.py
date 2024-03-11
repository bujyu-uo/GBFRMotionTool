import sys
from collections.abc import Callable

from . import mot

_task_cond_op = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    "<":  lambda a, b: a < b,
    "&":  lambda a, b: bool(a & b),
    "|":  lambda a, b: bool(a | b),
    "BMSK": lambda a, b: (a & b) == b 
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
    rec.interpolation.value = op(rec.interpolation.value, rhs)
    rec.value = op(rec.value, rhs)

def _TypeValues(op: Callable, rec: mot.MotRecord, rhs):
    new_values = [op(val, rhs) for val in rec.interpolation.values]
    rec.interpolation.values = new_values

def _TypeInterpol2(op: Callable, rec: mot.MotRecord, rhs):
    rec.interpolation.p = op(rec.interpolation.p, rhs)
    new_values = [op(val, rhs) for val in rec.interpolation.values]
    rec.interpolation.values = new_values

def _TypeInterpol3(op: Callable, rec: mot.MotRecord, rhs):
    rec.interpolation.p = op(rec.interpolation.p, rhs)
    new_values = [op(val, rhs) for val in rec.interpolation.values]
    rec.interpolation.values = new_values

def _TypeInterpolSpline(op: Callable, rec: mot.MotRecord, rhs):
    for spline in rec.interpolation.splines:
        spline.value = op(spline.value, rhs)

def _TypeInterpol5(op: Callable, rec: mot.MotRecord, rhs):
    rec.interpolation.p = op(rec.interpolation.p, rhs)
    for spline in rec.interpolation.splines:
        spline.value = op(spline.value, rhs)

def _TypeInterpol6(op: Callable, rec: mot.MotRecord, rhs):
    rec.interpolation.p = op(rec.interpolation.p, rhs)
    for spline in rec.interpolation.splines:
        spline.value = op(spline.value, rhs)

def _TypeInterpol7(op: Callable, rec: mot.MotRecord, rhs):
    rec.interpolation.p = op(rec.interpolation.p, rhs)
    for spline in rec.interpolation.splines:
        spline.value = op(spline.value, rhs)

def _TypeInterpol8(op: Callable, rec: mot.MotRecord, rhs):
    rec.interpolation.p = op(rec.interpolation.p, rhs)
    for spline in rec.interpolation.splines:
        spline.value = op(spline.value, rhs)

_record_modifier = {
    # limited support interpolation type
    0: _TypeConst,
    1: _TypeValues,
    2: _TypeInterpol2,
    3: _TypeInterpol3,
    4: _TypeInterpolSpline,
    5: _TypeInterpol5,
    6: _TypeInterpol6,
    7: _TypeInterpol7,
    8: _TypeInterpol8
}

def _util_conv_int(v: int|str) -> int:
    if type(v) == int:
        return v

    _numeric_map = {
        'b': lambda v: int(v, 2),
        'x': lambda v: int(v, 16)
    }
    if v[0] == '0': # special numeric form
        if v[1] in _numeric_map:
            return _numeric_map[v[1]](v)
        return int(v, 8)
    return int(v) # guess is decimal


def _task_op_conditon(t, it: tuple[int, mot.MotRecord], callback: Callable = None) -> bool:
    cond_expected = True
    condition_strings = []
    for cond in t['conditions']:
        if cond['operator'] not in _task_cond_op:
            raise UserWarning(f"Unsupported condition operator: {cond['operator']}")
        if cond['field'] not in it[1].__dict__:
            raise UserWarning(f"Unsupported condition field: {cond['field']}")

        cond_op = _task_cond_op[cond['operator']]
        a = it[1].__dict__[cond['field']]
        b = _util_conv_int(cond['value'])
        if cond_expected != cond_op(a, b):
            return False
        
        if callback != None:
            _field_repr = {
                "_default": lambda v: f"{v}",
                "boneIndex": lambda v: f"{v} ({v:0x})"
            }
            field_repr = _field_repr['_default']
            if cond['field'] in _field_repr:
                field_repr = _field_repr[cond['field']]
            astr = field_repr(a)
            condition_strings.append(f"\tfield:[{cond['field']}: {astr}] operator:[{cond['operator']}] value:[{b}]")
    
    # call callable when full matching only
    if callback != None:
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


def apply(path: str, it: tuple[int, mot.MotRecord]) -> bool:
    import json

    jobj = None
    with open(path, "r") as f:
        jobj = json.load(f)
    if jobj is None:
        raise RuntimeError("Task file")

    ret = False
    for t in jobj:
        # check conditions
        if not _task_op_conditon(t, it):
            continue
        print(f"Record[{it[0]}] matches condition, do task modifier ...", file=sys.stderr)
        ret = True

        # apply modifications
        _task_op_modifier(t, it)
    return ret


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
            callback=lambda cond_str: print(f"Record[{it[0]}] matches conditions ...\n{cond_str}", file=sys.stderr)
        )