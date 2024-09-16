#!/usr/bin/env python3

from Parsing import SubclassFactory

class Data:
    def __init__(self) -> None:
        raise Exception("Data is abstract")
    
    def __repr__(self) -> str:
        return f'<{self.__class__}>'

class Byte(Data):
    value: int
    
    def __init__(self, value, type):
        self.value = value
    
class Short(Data):
    value: int
    
    def __init__(self, value, type):
        self.value = value

class Integer(Data):
    value: int
    
    def __init__(self, value, type):
        self.value = value
    
class Long(Data):
    value: int
    
    def __init__(self, value, type):
        self.value = value

class Float(Data):
    value: float
    
    def __init__(self, value, type):
        self.value = value

class Double(Data):
    value: float
    
    def __init__(self, value, type):
        self.value = value

class Char(Data):
    value: str
    
    def __init__(self, value, type):
        self.value = value

class Ref(Data):
    refType: str
    
    def __getitem__(self, key):
        return (self, key)
    
    def __init__(self, refType):
        self.refType = refType
    
    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        if isinstance(other, Ref):
            return id(self) == id(other)
        return False
    
    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)
    
dataFactory = SubclassFactory(Data, "type")