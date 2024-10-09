#!/usr/bin/env python3

from State import BranchCondition

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
    
class SignedUnknown:
    positive: bool
    zero: bool
    negative: bool
    
    def __init__(self, positive = True, zero = True, negative = True):
        self.positive = positive
        self.zero = zero
        self.negative = negative
    
    @property
    def __key(self):
        return self.positive, self.zero, self.negative
    
    @property
    def min(self):
        if self.negative:   return -1
        if self.zero:       return  0
        if self.positive:   return  1
        raise Exception("Null interger in Signed Unkown")
    
    @property
    def max(self):
        if self.positive:   return  1
        if self.zero:       return  0
        if self.negative:   return -1
        raise Exception("Null interger in Signed Unkown")
    
    def __hash__(self):
        return hash(self.__key)
    
    def __eq__(self, other):
        if isinstance(other, SignedUnknown):
            return self.__key == other.__key
        return False
    
    def __ne__(self, other):
        if isinstance(other, SignedUnknown):
            return self.__key != other.__key
        return True
    
    def __repr__(self):
        return f"<Signed Unkown {self.positive * '+'}{self.zero * '0'}{self.negative * '-'}>"
    
    def __add__(self, other):
        if isinstance(other, SignedUnknown):
            p = self.positive or other.positive
            z = self.zero and other.zero or self.positive and other.negative or self.negative and other.positive
            n = self.negative or other.negative
            return SignedUnknown(p, z, n)
        return NotImplemented
        
    def __sub__(self, other):
        if isinstance(other, SignedUnknown):
            p = self.positive or other.negative
            z = self.zero and other.zero or self.positive and other.positive or self.negative and other.negative
            n = self.negative or other.positive
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __mul__(self, other): 
        if isinstance(other, SignedUnknown):
            p = self.positive and other.positive or self.positive and self.positive
            z = self.zero or other.zero
            n = self.negative and other.positive or self.positive and other.negative
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, SignedUnknown):
            p = self.positive and other.positive or self.positive and self.positive
            z = False
            n = self.negative and other.positive or self.positive and other.negative
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __floordiv__(self, other):
        if isinstance(other, SignedUnknown):
            p = self.positive and other.positive or self.positive and self.positive
            z = False
            n = self.negative and other.positive or self.positive and other.negative
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __mod__(self, other):
        if isinstance(other, SignedUnknown):
            p = other.positive and not other.zero
            z = not other.zero
            n = other.negative and not other.zero
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __lt__(self, other): 
        if isinstance(other, SignedUnknown):
            if self.max < other.min:
                return True
            if self.min == 0 and other.max == 0:
                return False
            if self.min > other.max:
                return False
            return Unknown()
        return NotImplemented
    
    def __gt__(self, other): 
        if isinstance(other, SignedUnknown):
            if self.min > other.max:
                return True
            if self.max == 0 and other.min == 0:
                return False
            if self.max < other.min:
                return False
            return Unknown()
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, SignedUnknown):
            if self.max < other.min:
                return True
            if self.max == 0 and other.min == 0:
                return True
            if self.min > other.max:
                return False
            return Unknown()
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, SignedUnknown):
            if self.min > other.max:
                return True
            if self.min == 0 and other.max == 0:
                return True
            if self.max < other.min:
                return False
            return Unknown()
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, SignedUnknown):
            p = self.positive and other.positive
            z = self.zero and other.zero
            n = self.negative and other.negative
            
            if z and not self.positive and not self.negative and not other.positive and not other.negative:
                return True
            if not p and not z and not n:
                return False
            
            return Unknown()
        return NotImplemented
        
    def __ne__(self, other):
        if isinstance(other, SignedUnknown):
            p = self.positive and other.positive
            z = self.zero and other.zero
            n = self.negative and other.negative
            
            if z and not self.positive and not self.negative and not other.positive and not other.negative:
                return False
            if not p and not z and not n:
                return True
            
            return Unknown()
        return NotImplemented
    
    def __radd__(self, other): return Unknown()
    def __rsub__(self, other): return Unknown()
    def __rmul__(self, other): return Unknown()
    def __rmatmul__(self, other): return Unknown()
    def __rtruediv__(self, other): return Unknown()
    def __rfloordiv__(self, other): return Unknown()
    def __rmod__(self, other): return Unknown()

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
    
    
    class Lattice:
        def __init__(self):
            pass
        
        
    
    # class SmartUnkownInt:
        
    #     dict = {(x, y): 'gt', (y, x): 'le'}
        
        
    #     def __init__(self):
    #         pass
        
    #     def Compare(self):
    #         pass