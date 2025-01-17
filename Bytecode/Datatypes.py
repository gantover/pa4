﻿#!/usr/bin/env python3

from State import Comparison
from math import isinf

def jmod(a, b):
    # non-optimal implementation of remainder (%) operator that behaves the same as in Java
    res = (abs(a) - (abs(a) // abs(b)) * abs(b))
    return -res if a < 0 else res


class IntegerAbstracion:
    def update(self):
        raise NotImplementedError("Abstract method")


class Array(dict):
    length: any
    default: any
    
    def __init__(self, length, default, **kwargs):
        self.length = length
        self.default = default
        super(Array, self).__init__(**kwargs)
    
    def __repr__(self) -> str:
        return f'<Array {super().__repr__()}>'

    def __getitem__(self, key):
        if key in self:
            return super(Array, self).__getitem__(key)
        return self.default()
    
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
    
class SignedUnknown(IntegerAbstracion):
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
    
    def update(self, value, relation):
        pos = value > 0
        zero = value == 0
        neg = value < 0
        
        lt, eq, gt = {
            Comparison.GreaterThan: (neg, neg, True),
            Comparison.GreaterEqual: (neg, not pos, True),
            Comparison.LessThan: (True, pos, pos),
            Comparison.LessEqual: (True, not neg, pos),
            Comparison.NotEqual: (not neg, not zero, not pos),
            Comparison.Equal: (neg, zero, pos),
            Comparison.Incomparable: (False, False, False)
        }[relation]
        
        self.positive = self.positive and gt
        self.zero = self.zero and eq
        self.negative = self.negative and lt
        
        if not (self.positive or self.zero or self.negative):
            raise Exception("Impossible signed unknown")
        
        return self
    
    @staticmethod
    def fromValue(value):
        return SignedUnknown(value > 0, value == 0, value < 0)
        
    
    def __hash__(self):
        return hash(self.__key)
    
    def __repr__(self):
        return f"<Signed Unkown {self.positive * '+'}{self.zero * '0'}{self.negative * '-'}>"
    
    def __add__(self, other):
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
        
        if isinstance(other, SignedUnknown):
            p = self.positive or other.positive
            z = (self.zero and other.zero) or (self.positive and other.negative) or (self.negative and other.positive)
            n = self.negative or other.negative
            return SignedUnknown(p, z, n)
        return NotImplemented
        
    def __sub__(self, other):
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
            
        if isinstance(other, SignedUnknown):
            p = self.positive or other.negative
            z = (self.zero and other.zero) or (self.positive and other.positive) or (self.negative and other.negative)
            n = self.negative or other.positive
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __mul__(self, other): 
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
        
        if isinstance(other, SignedUnknown):
            p = (self.positive and other.positive) or (self.negative and other.negative)
            z = self.zero or other.zero
            n = (self.negative and other.positive) or (self.positive and other.negative)
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
        
        if isinstance(other, SignedUnknown):
            if other.zero:
                return SignedUnknown(False, False, False)

            p = (self.positive and other.positive) or (self.negative and other.negative)
            z = self.zero
            n = (self.negative and other.positive) or (self.positive and other.negative)
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __floordiv__(self, other):
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
            
        if isinstance(other, SignedUnknown):
            if other.zero:
                return SignedUnknown(False, False, False)

            p = (self.positive and other.positive) or (self.negative and other.negative)
            z = (self.positive or self.negative or self.zero) and (other.positive or other.negative)
            n = (self.negative and other.positive) or (self.positive and other.negative)
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __mod__(self, other):
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
            
        if isinstance(other, SignedUnknown):
            if other.zero:
                return SignedUnknown(False, False, False)

            p = self.positive
            z = (self.positive or self.negative or self.zero) and (other.positive or other.negative)
            n = self.negative
            return SignedUnknown(p, z, n)
        return NotImplemented
    
    def __lt__(self, other): 
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
            
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
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
            
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
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
            
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
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
            
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
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
            
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
        if isinstance(other, (int, bool)):
            other = self.fromValue(other)
            
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
    def __neg__(self): return Unknown()
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

INFINITY = float('inf')
NAN = float('nan')



class Keystone(IntegerAbstracion):
    lt: bool
    eq: bool
    gt: bool
    value: int
    
    def __init__(self, value = NAN, lt = True, eq = True, gt = True):
        self.value = value
        self.lt = lt
        self.eq = eq
        self.gt = gt
        
        if eq or lt and gt:
            pass
        elif lt:
            self.eq = True
            self.value = value + 1
        elif gt:
            self.eq = True
            self.value = value + 1
        else:
            raise Exception("void keystone detected")
    
    @property
    def __key(self):
        return self.value, self.lt, self.eq, self.gt
    
    def __hash__(self) -> int:
        if not self.lt and self.eq and not self.gt:
            return hash(self.value)
        
        return hash(self.__key)
    
    @property
    def max(self):
        if self.gt: return INFINITY
        if self.eq: return self.value
        raise Exception("incomparible keystone detected")
        # return -infinity
    @property
    def min(self):
        if self.lt: return -INFINITY
        if self.eq: return self.value
        raise Exception("incomparible keystone detected")
        # return infinity
    @property
    def exact(self):
        if not self.lt and self.eq and not self.gt: return self.value
        return NAN
    
    def update(self, value, relation):
        self.value = value
        
        self.lt, self.eq, self.gt = {
            Comparison.GreaterThan: (False, False, True),
            Comparison.GreaterEqual: (False, True, True),
            Comparison.LessThan: (True, False, False),
            Comparison.LessEqual: (True, True, False),
            Comparison.NotEqual: (True, False, True),
            Comparison.Equal: (False, True, False),
            Comparison.Incomparable: (False, False, False)
        }[relation]
        
        if self.eq or self.lt and self.gt:
            pass
        elif self.lt:
            self.eq = True
            self.value = value + 1
        elif self.gt:
            self.eq = True
            self.value = value + 1
        else:
            raise Exception("void keystone detected")
        
        return self
        
    
    def __repr__(self):
        return f"<{type(self).__name__} {self.lt * '<'}{self.eq * '='}{self.gt * '>'} {self.value}>"
    
    def duck(self, other):
        if isinstance(other, Keystone):
            min = other.min
            value = other.value
            max = other.max
        elif isinstance(other, (int, float)):
            min = value = max = other
        else:
            raise NotImplementedError(f'Cannot operate on types {type(self).__name__} and {type(other).__name__}')
        
        return min, value, max
    
    def compare(self, other):
        if id(self) == id(other):
            return Comparison.Equal
        
        min, value, max = self.duck(other)
        
        # print(self.min, self.value, self.max, min, value, max, self.max < min, (self.max < min) is True)
        
        if (self.max < min) is True: return Comparison.LessThan
        if (self.min > max) is True: return Comparison.GreaterThan
        
        # Ranges are intersecting
        
        le = (self.max == min) is True
        ge = (self.min == max) is True
        
        if le and ge: return Comparison.Equal
        elif le:      return Comparison.LessEqual
        elif ge:      return Comparison.GreaterEqual
        elif value == self.value:
            return Comparison.NotEqual    #TODO:: This not equal reads very poorly... im convinced it *works* but make readable
        
        return Comparison.Incomparable
    
    def __lt__(self, other): 
        # if self.max < other.min: return True
        # if self.min >= other.max: return False
        # return Unknown() TODO::this might be a better way to compare them, doen't use the .compare() but is lighter and shorter
        # print(f'{self} < {other} is {self.compare(other)}')
        
        match self.compare(other):
            case Comparison.LessThan: return True
            case Comparison.LessEqual: return Unknown()
            case Comparison.NotEqual: return Unknown()
            case Comparison.Incomparable: return Unknown()
            case _: return False     
    def __gt__(self, other):
        match self.compare(other):
            case Comparison.GreaterThan: return True
            case Comparison.GreaterEqual: return Unknown()
            case Comparison.NotEqual: return Unknown()
            case Comparison.Incomparable: return Unknown()
            case _: return False     
    def __le__(self, other):
        match self.compare(other):
            case Comparison.Equal: return True
            case Comparison.LessThan: return True
            case Comparison.LessEqual: return True
            case Comparison.GreaterEqual: return Unknown()
            case Comparison.NotEqual: return Unknown()
            case Comparison.Incomparable: return Unknown()
            case _: return False        
    def __ge__(self, other):
        match self.compare(other):
            case Comparison.Equal: return True
            case Comparison.GreaterThan: return True
            case Comparison.GreaterEqual: return True
            case Comparison.LessEqual: return Unknown()
            case Comparison.NotEqual: return Unknown()
            case Comparison.Incomparable: return Unknown()
            case _: return False     
    def __eq__(self, other):
        
        # print(f'{self} == {other} is {self.compare(other)}')
        
        match self.compare(other):
            case Comparison.Equal: return True
            case Comparison.LessEqual: return Unknown()
            case Comparison.GreaterEqual: return Unknown()
            case Comparison.Incomparable: return Unknown()
            case _: return False
    def __ne__(self, other):
        match self.compare(other):
            case Comparison.LessThan: return True
            case Comparison.NotEqual: return True
            case Comparison.GreaterThan: return True
            case Comparison.LessEqual: return Unknown()
            case Comparison.GreaterEqual: return Unknown()
            case Comparison.Incomparable: return Unknown()
            case _: return False
    
    def __neg__(self):
        return Keystone(-self.value, self.gt, self.eq, self.lt)
    
    def __add__(self, other):
        # min, value, max = self.duck(other)
        
        # self.min + min
        # self.max + max
        # min += self.min
        
        if isinstance(other, Keystone):
            value = self.value + other.value
            lt = self.lt or other.lt
            eq = self.eq and other.eq or self.lt and other.gt or self.gt and other.lt
            gt = self.gt or other.gt
        elif isinstance(other, int):
            value = self.value + other
            lt = self.lt
            eq = self.eq
            gt = self.gt
        else:
            return NotImplemented
    
        return Keystone(value, lt, eq, gt)
    
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + -other
    def __rsub__(self, other): return -self + other
    
    def __floordiv__(self, other):
        if id(self) == id(other):
            return 1
        
        return Keystone() #TODO:: Implement
        
        o_min, value, o_max = self.duck(other)
        
        if other == 0 is False:
            v = self.value // other.value
        else:
            v = NAN

        vals = self.max//o_max, self.min//o_max, self.max//o_min, self.min//o_min
        
        gt = max(vals) == INFINITY
        lt = min(vals) == -INFINITY
        
        result = Keystone(v, lt, not (gt or lt), gt)
        
        l.debug({f'{self} // {other} == {result}'})
        
        return result

    def __rfloordiv__(self, other):
        return Keystone() #TODO:: Implement
    
        if not isinstance(other, (int, float)):
            l.debug(f"Cant divide for type {type(other)}")
            return NotImplemented
        
        l.debug([val == self for val in (self.min, -1, 0, 1, self.max)])
        
        values = [other // val for val in (self.min, -1, 1, self.max) if val == self and val != 0]
        
        l.debug(f'{other} // {self} produces: {values}')
        
    def __mod__(self, other):
        return Keystone() # TODO:: Implement
        
    def __mul__(self, other):
        return Keystone() # TODO:: Implement


class intRange(IntegerAbstracion):
    lb: int
    ub: int
    
    def __new__(cls, lb = -2147483648, ub = 2147483647):
        if lb == ub:
            return lb
        elif lb < ub:
            return super().__new__(cls)
        else:
            return None

    def __repr__(self):
        return f"<{type(self).__name__} [{self.lb}, {self.ub}]>"
    
    def __init__(self, lb = -INFINITY, ub = INFINITY):
        self.lb = lb
        self.ub = ub

    @property
    def __key(self):
        return self.lb, self.ub

    def __hash__(self) -> int:
        return hash(self.__key)
    
    def update(self, value, relation):
        if relation == Comparison.NotEqual:
            raise ValueError(f"{type(self)} cannot be updated with {relation}")
        
        keeplb, keepub, adjustedValue = {
            Comparison.GreaterThan: (self.lb > value, self.ub > value, value + 1),
            Comparison.GreaterEqual: (self.lb >= value, self.ub >= value, value),
            Comparison.LessThan: (self.lb < value, self.ub < value, value - 1),
            Comparison.LessEqual: (self.lb <= value, self.ub <= value, value),
            Comparison.Equal: (self.lb == value, self.ub == value, value),
            Comparison.NotEqual: (self.lb != value, self.ub != value, value), #can't really do this
            Comparison.Incomparable: (self.lb > value, self.ub > value, value + 1) #hmmm
        }[relation]

        self.lb = self.lb if keeplb else adjustedValue
        self.ub = self.ub if keepub else adjustedValue
        # return intRange(self.lb if keeplb else adjustedValue, self.ub if keepub else adjustedValue)
    
    def __contains__(self, val):
        if isinstance(val, (int, bool, float)):
            return self.lb <= val and val <= self.ub
        raise ValueError(f"val of unexpected type {type(val)}")
    
    def intersect(self, other):
        if isinstance(other, intRange):
            lb = max(self.lb, other.lb)
            ub = min(self.ub, other.ub)
        elif isinstance(other, int):
            lb = ub = other
        
        return intRange(lb, ub)
    
    def merge(self, other):
        if isinstance(other, intRange):
            lb = other.lb
            ub = other.ub
        elif isinstance(other, int):
            lb = ub = other
            
        if self.lb - 1 <= ub and lb - 1 <= self.ub:
            return intRange(min(self.lb, lb), max(self.ub, ub))

    @staticmethod
    def asRange(value):
        if isinstance(value, intRange):
            return value
        if isinstance(value, (int, bool)):
            # Necessary hack to allow initialisation of range [x, x]
            r = intRange()
            r.lb, r.ub = value, value
            return r
        
        raise TypeError(f"Attemped unimplemented conversion from type {type(value)} to {intRange}")
        
    def __neg__(self):
        return intRange(-self.ub, -self.lb)

    ################################################
    ############## Binary Operationss ##############
    ################################################
    
    def __add__(self, other):
        if isinstance(other, (int, bool)):
            return intRange(self.lb + other, self.ub + other)
        
        if isinstance(other, intRange):
            return intRange(
                self.lb + other.lb, 
                self.ub + other.ub)
        return NotImplemented
    
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + -other
    def __rsub__(self, other): return -self + other
    
    def __mul__(self, other):
        if isinstance(other, (int, bool)):
            return intRange(self.lb * other, self.ub * other)
        
        if isinstance(other, intRange):
            pBounds = self.lb * other.lb, self.lb * other.ub, self.ub * other.lb, self.ub * other.ub
            return intRange(
                min(pBounds), 
                max(pBounds))
        return NotImplemented
    
    def __rmul__(self, other): return self * other
    
    
    def __div__(self, other):
        if isinstance(other, (int, bool)):
            return intRange(self.lb / other, self.ub / other)
        
        if isinstance(other, intRange):
            
            pBounds = []
            
            for x in (other.lb, -1, 1, other.ub):
                if x in other and x != 0:
                    pBounds.extend((self.lb / x, self.ub / x))
            
            if len(pBounds) == 0:
                raise Exception(f"No valid divison between {self} and {other}")
            
            return intRange(
                min(pBounds), 
                max(pBounds))
        return NotImplemented


    def __floordiv__(self, other):
        if isinstance(other, (int, bool)):
            return intRange(
                self.lb / other if self.lb == -INFINITY else self.lb // other,
                self.ub / other if self.ub == INFINITY else self.ub // other
            )
        if isinstance(other, intRange):
            
            pBounds = []
            
            for x in (other.lb, -1, 1, other.ub):
                if x in other and x != 0:
                    pBounds.extend((self.lb // x, self.ub // x))

            if len(pBounds) == 0:
                raise Exception(f"No valid divison between {self} and {other}")

            return intRange(min(pBounds), max(pBounds))
        return NotImplemented

    def __rfloordiv__(self, other):
        return self.__floordiv__(other)

    def __rdiv__(self, other):
        if isinstance(other, (int, bool)):
            pBounds = []
            
            for x in (self.lb, -1, 1, self.ub):
                if x in self and x != 0:
                    pBounds.append(other / x)
            
            if len(pBounds) == 0:
                raise Exception(f"No valid divison between {self} and {other}")
            
            return intRange(min(pBounds), max(pBounds))
        
        if isinstance(other, intRange):
            
            pBounds = []
            
            for x in (self.lb, -1, 1, self.ub):
                if x in other and x != 0:
                    pBounds.extend((other.lb / x, other.ub / x))
            
            if len(pBounds) == 0:
                raise Exception(f"No valid divison between {other} and {self}")
            
            return intRange(
                min(pBounds), 
                max(pBounds))
        return NotImplemented

    def __mod__(self, other):
        new = intRange()
        if isinstance(other, (int, bool)):
            other = abs(other) # in Java remainder, the sign of the second operant is irrelevant
            diff = self.lb - self.ub
            if not isinf(diff) and diff < other:
                new.lb = jmod(self.lb, other)
                new.ub = jmod(self.ub, other)
            else:
                new.lb = max(self.lb, -(other - 1))
                new.ub = min(self.ub, other - 1)
            return new
        if isinstance(other, intRange):
            return self % max(abs(other.lb), abs(other.ub))
        if other == INFINITY:
            return self
        return NotImplemented

    def __rmod__(self, other):
        return intRange.asRange(other) % self

    #########################################
    ############## Comparisons ##############
    #########################################

    def __lt__(self, other):
        other = intRange.asRange(other)
        
        if self.ub < other.lb:
            return True
        if self.lb >= other.ub:
            return False

        return Unknown()


    def __gt__(self, other):
        return intRange.asRange(other) < self


    def __le__(self, other):
        other = intRange.asRange(other)

        if self.ub <= other.lb:
            return True
        if self.lb > other.ub:
            return False

        return Unknown()


    def __ge__(self, other):
        return intRange.asRange(other) <= self

    
    def __eq__(self, other):
        other = intRange.asRange(other)

        if self.lb == other.lb and self.ub == other.ub:
            return True
        if self.ub < other.lb or self.lb > other.ub:
            return False

        return Unknown()


    def __ne__(self, other):
        eq = self == intRange.asRange(other)
        if isinstance(eq, Unknown):
            return eq
        return not eq



class Identity:
    def __hash__(self):
        return hash(id(self))
    
    def __repr__(self):
        return f'Identity {hash(self) % 1000}'
