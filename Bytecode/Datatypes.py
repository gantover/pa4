#!/usr/bin/env python3

from enum import Enum
from Parsing import SubclassFactory

class Data:
    def __repr__(self) -> str:
        return f'<{self.__class__}>'

class Byte(Data):
    value: int
    
class Short(Data):
    value: int

class Integer(Data):
    value: int
    
class Long(Data):
    value: int

class Float(Data):
    value: float

class Double(Data):
    value: float

class Char(Data):
    value: str

class Ref(Data):
    type: str
    
    def __init__(self, type):
        self.type = type
    
    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        return id(self) == id(other)
    
dataFactory = SubclassFactory(Data, "type")