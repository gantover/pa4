#!/usr/bin/env python3

class Array(dict):
    length: any
    default: any
    
    def __init__(self, length, default, **kwargs):
        self.length = length
        self.default = default
        super(Array, self).__init__(**kwargs)

    def __getitem__(self, key):
        if key in self:
            return super(Array, self).__getitem__(key)
        return self.default
    
    def __len__(self):
        return self.length
    
    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        if isinstance(other, Array):
            return id(self) == id(other)
        return False
    
    def __ne__(self, other):
        return not(self == other)

class Ref:
    refType: str
    
    def __getitem__(self, *key):
        return (self, *key)
    
    def __init__(self, refType):
        self.refType = refType
    
    def __repr__(self) -> str:
        return f'<Ref 0x{id(self)}>'
    
    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        if isinstance(other, Ref):
            return id(self) == id(other)
        return False
    
    def __ne__(self, other):
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

    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        if other is None:
            return False
        if isinstance(other, Unknown):
            return id(self) == id(other)
        return Unknown()
    
    def __ne__(self, other):
        if other is None:
            return True
        if isinstance(other, Unknown):
            return id(self) != id(other)
        return Unknown()
    
    def __repr__(self):
        return "<Unkown>"