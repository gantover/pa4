#!/usr/bin/env python3

from State import Comparison

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

INFINITY = float('inf')
NAN = float('nan')



class Keystone:
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
        
        print({f'{self} // {other} == {result}'})
        
        return result

    def __rfloordiv__(self, other):
        return Keystone() #TODO:: Implement
    
        if not isinstance(other, (int, float)):
            print(f"Cant divide for type {type(other)}")
            return NotImplemented
        
        print([val == self for val in (self.min, -1, 0, 1, self.max)])
        
        values = [other // val for val in (self.min, -1, 1, self.max) if val == self and val != 0]
        
        print(f'{other} // {self} produces: {values}')
        
    def __mod__(self, other):
        return Keystone() # TODO:: Implement
        
    def __mul__(self, other):
        return Keystone() # TODO:: Implement
        
        
        
        
    # class SmartUnkownInt:
        
    #     dict = {(x, y): 'gt', (y, x): 'le'}
        
        
    #     def __init__(self):
    #         pass
        
    #     def Compare(self):
    #         pass
    

class opRange():
    lb: int | float
    ub: int | float
    step: int | float
    
    def __init__(self, start, stop, step=1):
        # if step < 0: # TODO:: Ensure lb is lower than ub, and that stepsize is positive... makes math easier
        #     start, stop, step = stop, start, -step
        
        self.lb = start
        self.ub = stop - (stop - start) % step
        self.step = step
    
    def __neg__(self):
        return opRange(-self.ub, -self.lb, -self.step)
    
    def __add__(self, other):
        if isinstance(other, opRange):
            return opRange(
                self.lb + other.lb, 
                self.ub + other.ub, 
                1) # min(self.step, other.step)) #TODO: implement step size calculation
        return NotImplemented
    
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + -other
    def __rsub__(self, other): return -self + other
    # def __iter__(self):
    #     return iter(range(self.lb, self.ub + self.step, self.step))
    
    def intersection(self, other):
        if isinstance(other, opRange):
            return opRange(
                max(self.lb, other.lb),
                min(self.ub, other.ub),
                1) # max(self.step, other.step)) #TODO: implement step size calculation
        return NotImplemented
    
    def is_intersecting(self, other):
        if isinstance(other, opRange):
            return self.lb <= other.ub and other.lb <= self.ub
    
    
class intRange:
    lb: int
    ub: int
    
    def __new__(cls, lb = -INFINITY, ub = INFINITY):
        if lb == ub:
            return lb
        elif lb < ub:
            return super().__new__(cls)
        else:
            return None
    
    def __init__(self, lb = -INFINITY, ub = INFINITY):
        self.lb = lb
        self.ub = ub
    
    def contains(self, val):
        return self.lb <= val and val <= self.ub
    
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

class Identity:
    def __hash__(self):
        return hash(id(self))
    
    def __repr__(self):
        return f'Identity {hash(self) % 1000}'
    
    
    
class linearUnknown:
    def __init__(self, a, b, original = None):
        self.a = a
        self.b = b
        self.original = original if original is not None else Identity()
    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return linearUnknown(self.a, self.b + other, self.original)
        elif issubclass(other, linearUnknown) and self.original == other.original:
            return linearUnknown(self.a + other.a, self.b + other.b, self.original)
            
        return NotImplemented
    
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + -other
    def __rsub__(self, other): return -self + other
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return linearUnknown(self.a * other, self.b * other, self.original)
        
        return NotImplemented
    
    def __rmul__(self, other): return self * other
    
    def __floordiv__(self, other):
        return NotImplemented
        
        if isinstance(other, (int,float)):
            return linearUnknown(self.a / other, self.b / other, self.original)
        
        
    def __mod__(self, other):
        if isinstance(other, (int,float)):
            
            if self.a % other == 0:
                return self.b % other
            
        return NotImplemented
    
    
        # val = (self.a * input + self.b) % 
        
        # return linearUnknown(self.a / other, self.b / other, self.original)

from dataclasses import dataclass, field, asdict
from math import lcm, floor
from fractions import Fraction

@dataclass
class divisibleLinearUnkown:
    base: Identity = field(default_factory=Identity)
    slope: Fraction = 1
    offset: Fraction = 0
    steps: list[Fraction] = field(default_factory = lambda: [Fraction(1)])
    
    def __post_init__(self):
        self.slope = Fraction(self.slope)
        self.offset = Fraction(self.offset)
        
    def extract(self, value):
        if isinstance(value, (int, float)):
            return True, 0, value, [1], 1
        
        if isinstance(value, divisibleLinearUnkown):
            if self.base == value.base or self.slope == 0:
                return value.base, value.slope, value.offset, value.steps, value.lcd
            elif value.slope == 0:
                return self.base, value.slope, value.offset, value.steps, value.lcd
        
        raise Exception(f"Cannot extract type {type(value)} for operation with divisibleLinearUnkown")
    
    def __iter__(self):
        yield from asdict(self).values()
    
    def __neg__(self):
        return divisibleLinearUnkown(self.base, -self.slope, -self.offset, -self.steps) #TODO:: should step be negative??
    
    def __add__(self, other):
        # base, slope, offset, step = self.extract(other)
        
        # if base is not None:
        return divisibleLinearUnkown(self.base, self.slope, self.offset + other, self.steps)
        
        # return NotImplemented
    
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + -other
    def __rsub__(self, other): return -self + other
    
    def __mul__(self, other):
        # base, slope, offset, steps, lcd = self.extract(other)
        
        # if slope != 0 and self.slope != 0:
        #     raise Exception("Cannot multiply two divisibleLinearUnkown with each other")
        
        # if slope == 0:
        # steps = 
        # elif self.slope == 0:
        #     steps = [step * self.offset for step in steps]
        
        # if base is not None:
        return divisibleLinearUnkown(
            base= self.base, 
            slope= self.slope * other, # offset + self.offset * slope, 
            offset= self.offset * other, #offset,
            steps= [step * other for step in self.steps])

    def __floordiv__(self, other):
        return divisibleLinearUnkown(
            base= self.base, 
            slope= self.slope / other, # offset + self.offset * slope, 
            offset= self.offset / other, #offset,
            steps= [step / other for step in self.steps] + [Fraction(1)])
    
    def concrete(self, value):
        value = self.slope * value + self.offset
        
        for step in self.steps:
            value = floor(value / step) * step
            
        return value
    
    