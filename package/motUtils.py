from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

class Spline:
	frame: int
	value: float
	m0: float
	m1: float

	def __init__(self, frame: int = None, value: float = None, m0: float = None, m1: float = None):
		self.frame = frame
		self.value = value
		self.m0 = m0
		self.m1 = m1

def alignTo4(num: int) -> int:
	return (num + 3) & ~3
