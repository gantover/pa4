from State import Comparison 
from Datatypes import IntegerAbstracion, Unknown, INFINITY, intRange
from Debug import l

# initialized after program run
constants = []

def minK(a,b):
    available_values = [k for k in [-INFINITY, INFINITY, *constants] if (k <= min(a,b))]
    return max(available_values)
def maxK(a,b):
    available_values = [k for k in [-INFINITY, INFINITY, *constants] if (k >= max(a,b))]
    return min(available_values)


class WideIntRange(intRange):
    lb: int
    ub: int
    def __init__(self, lb=-INFINITY, ub=INFINITY):
        super().__init__(lb, ub)

    # this is where the windeing operator is supposed to act
    def merge(self, other):
        if isinstance(other, WideIntRange):
            lb = other.lb
            ub = other.ub
        elif isinstance(other, int):
            lb = ub = other
        if self.lb - 1 <= ub and lb - 1 <= self.ub:
            return WideIntRange(minK(self.lb, lb), maxK(self.ub, ub))

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

    @property
    def __key(self):
        return self.lb, self.ub

    def __hash__(self) -> int:
        return hash(self.__key)
    
    def update(self, value, relation):
        keeplb, keepub, adjustedValue = {
            Comparison.GreaterThan: (self.lb > value, self.ub > value, value + 1),
            Comparison.GreaterEqual: (self.lb >= value, self.ub >= value, value),
            Comparison.LessThan: (self.lb < value, self.ub > value, value - 1),
            Comparison.LessEqual: (self.lb <= value, self.ub <= value, value),
            Comparison.Equal: (self.lb == value, self.ub == value, value),
            Comparison.NotEqual: (self.lb!= value, self.ub !=value, value),    #can't really do this
            Comparison.Incomparable: (self.lb > value, self.ub > value, value + 1) #hmmm
        }[relation]
        
        return WideIntRange(self.lb if keeplb else adjustedValue, self.ub if keepub else adjustedValue)
    
    def __contains__(self, val):
        if isinstance(val, (int, bool, float)):
            return self.lb <= val and val <= self.ub
        raise ValueError(f"val of unexpected type {type(val)}")
    
    def intersect(self, other):
        if isinstance(other, WideIntRange):
            lb = max(self.lb, other.lb)
            ub = min(self.ub, other.ub)
        elif isinstance(other, int):
            lb = ub = other
        
        return WideIntRange(lb, ub)
    

    @staticmethod
    def asRange(value):
        if isinstance(value, WideIntRange):
            return value
        if isinstance(value, (int, bool)):
            # Necessary hack to allow initialisation of range [x, x]
            r = WideIntRange()
            r.lb, r.ub = value, value
            return r
        
        raise TypeError(f"Attemped unimplemented conversion from type {type(value)} to {WideIntRange}")
        
    def __neg__(self):
        return WideIntRange(-self.ub, -self.lb)

    ################################################
    ############## Binary Operationss ##############
    ################################################
    
    def __add__(self, other):
        if isinstance(other, (int, bool)):
            return WideIntRange(self.lb + other, self.ub + other)
        
        if isinstance(other, WideIntRange):
            return WideIntRange(
                self.lb + other.lb, 
                self.ub + other.ub)
        return NotImplemented
    
    def __radd__(self, other): return self + other
    def __sub__(self, other): return self + -other
    def __rsub__(self, other): return -self + other
    
    def __mul__(self, other):
        if isinstance(other, (int, bool)):
            return WideIntRange(self.lb * other, self.ub * other)
        
        if isinstance(other, WideIntRange):
            pBounds = self.lb * other.lb, self.lb * other.ub, self.ub * other.lb, self.ub * other.ub
            return WideIntRange(
                min(pBounds), 
                max(pBounds))
        return NotImplemented
    
    def __rmul__(self, other): return self * other
    
    
    def __div__(self, other):
        if isinstance(other, (int, bool)):
            return WideIntRange(self.lb / other, self.ub / other)
        
        if isinstance(other, WideIntRange):
            
            pBounds = []
            
            for x in (other.lb, -1, 1, other.ub):
                if x in other and x != 0:
                    pBounds.extend((self.lb / x, self.ub / x))
            
            if len(pBounds) == 0:
                raise Exception(f"No valid divison between {self} and {other}")
            
            return WideIntRange(
                min(pBounds), 
                max(pBounds))
        return NotImplemented


    def __floordiv__(self, other):
        if isinstance(other, (int, bool)):
            return WideIntRange(self.lb // other, self.ub // other)
        if isinstance(other, WideIntRange):
            
            pBounds = []
            
            for x in (other.lb, -1, 1, other.ub):
                if x in other and x != 0:
                    pBounds.extend((self.lb // x, self.ub // x))

            if len(pBounds) == 0:
                raise Exception(f"No valid divison between {self} and {other}")

            return WideIntRange(min(pBounds), max(pBounds))
        return NotImplemented


    def __rdiv__(self, other):
        if isinstance(other, (int, bool)):
            pBounds = []
            
            for x in (self.lb, -1, 1, self.ub):
                if x in self and x != 0:
                    pBounds.append(other / x)
            
            if len(pBounds) == 0:
                raise Exception(f"No valid divison between {self} and {other}")
            
            return WideIntRange(min(pBounds), max(pBounds))
        
        if isinstance(other, WideIntRange):
            
            pBounds = []
            
            for x in (self.lb, -1, 1, self.ub):
                if x in other and x != 0:
                    pBounds.extend((other.lb / x, other.ub / x))
            
            if len(pBounds) == 0:
                raise Exception(f"No valid divison between {other} and {self}")
            
            return WideIntRange(
                min(pBounds), 
                max(pBounds))
        return NotImplemented

    #########################################
    ############## Comparisons ##############
    #########################################

    def __lt__(self, other):
        other = WideIntRange.asRange(other)
        
        if self.ub < other.lb:
            return True
        if self.lb >= other.ub:
            return False

        return Unknown()


    def __gt__(self, other):
        return WideIntRange.asRange(other) < self


    def __le__(self, other):
        other = WideIntRange.asRange(other)

        if self.ub <= other.lb:
            return True
        if self.lb > other.ub:
            return False

        return Unknown()


    def __ge__(self, other):
        return WideIntRange.asRange(other) <= self

    
    def __eq__(self, other):
        other = WideIntRange.asRange(other)

        if self.lb == other.lb and self.ub == other.ub:
            return True
        if self.ub < other.lb or self.lb > other.ub:
            return False

        return Unknown()


    def __ne__(self, other):
        eq = self == WideIntRange.asRange(other)
        if isinstance(eq, Unknown):
            return eq
        return not eq
