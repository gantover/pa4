#!/usr/bin/env python3

from Parsing import SubclassFactory

class Data:
    def __init__(self) -> None:
        raise Exception("Data is abstract")
    
    def __repr__(self) -> str:
        return f'<{self.__class__}>'
    
    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        if isinstance(other, Data):
            return id(self) == id(other)
        return False

class Byte(Data):
    value: int
    
    def __init__(self, value, **_):
        self.value = value
        
    def __repr__(self) -> str:
        return f'<Byte = {self.value}>'

class BinaryOpMixin:
    def __add__(self, other):
        return self.__class__(self.value + other.value)

    def __sub__(self, other):
        return self.__class__(self.value - other.value)

    def __mul__(self, other):
        return self.__class__(self.value * other.value)

    def __truediv__(self, other):
        return self.__class__(self.value / other.value)
        
    def __floordiv__(self, other): 
        return self.__class__(self.value // other.value)

    def __mod__(self, other):
        return self.__class__(self.value % other.value)

class IntegerOpMixin(BinaryOpMixin):
    def __truediv__(self, other):
        return self.__floordiv__(other)

    def __hash__(self):
        return self.value


class Short(Data, IntegerOpMixin):
    value: int
    
    def __init__(self, value, **_):
        self.value = value
        
    def __repr__(self) -> str:
        return f'<Short = {self.value}>'

class Integer(Data, IntegerOpMixin):
    value: int
    
    def __init__(self, value, **_):
        self.value = value
    
    def __repr__(self) -> str:
        return f'<Integer = {self.value}>'
    
class Long(Data, IntegerOpMixin):
    value: int
    
    def __init__(self, value, **_):
        self.value = value
        
    def __repr__(self) -> str:
        return f'<Long = {self.value}>'

class Float(Data, BinaryOpMixin):
    value: float
    
    def __init__(self, value, **_):
        self.value = value
        
    def __repr__(self) -> str:
        return f'<Float = {self.value}>'

class Double(Data, BinaryOpMixin):
    value: float
    
    def __init__(self, value, **_):
        self.value = value
        
    def __repr__(self) -> str:
        return f'<Double = {self.value}>'

class Char(Data, BinaryOpMixin):
    value: str
    
    def __init__(self, value, **_):
        self.value = value
        
    def __repr__(self) -> str:
        return f'<Char = {self.value}>'

class Ref(Data):
    refType: str
    
    def __getitem__(self, *key):
        return (self, *key)
    
    def __init__(self, refType):
        self.refType = refType
    
    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)
    
class Unknown:
    def __add__(self, other): return Unknown()
    def __sub__(self, other): return Unknown()
    def __mul__(self, other): return Unknown()
    def __truediv__(self, other): return Unknown()
    def __floordiv__(self, other): return Unknown()
    def __mod__(self, other): return Unknown()
    
    def __lt__(self, other): return Unknown()
    def __gt__(self, other): return Unknown()
    def __le__(self, other): return Unknown()
    def __ge__(self, other): return Unknown()
    def __eq__(self, other): return Unknown()
    def __ne__(self, other): return Unknown()
    
    def __radd__(self, other): return Unknown()
    def __rsub__(self, other): return Unknown()
    def __rmul__(self, other): return Unknown()
    def __rmatmul__(self, other): return Unknown()
    def __rtruediv__(self, other): return Unknown()
    def __rfloordiv__(self, other): return Unknown()
    def __rmod__(self, other): return Unknown()

    def __repr__(self):
        return "<Unkown>"

    
dataFactory = SubclassFactory(Data, "type")
dataFactory["int"] = Integer
dataFactory["boolean"] = Byte