#!/usr/bin/env python3

from enum import Enum
from copy import deepcopy
import parsing
from Debug import l

METHOD_BYTECODE_STORE = dict()

class State:
    pc: int
    memory: tuple[any]
    stack: list[any]
    
    postCopyQueue: list[tuple]
    
    def __init__(self, pc, memory, *stack):
        self.stack = stack
        self.memory = tuple(memory.items())
        self.pc = pc
        self.postCopyQueue = []
    
    @property
    def __key(self):
        return self.pc, self.memory, self.stack
    
    def __iter__(self):
        return iter((self.pc, dict(self.memory), *self.stack))
    
    def __eq__(self, other):
        if isinstance(other, State):
            return self.__key == other.__key
        return False
    
    def __hash__(self):
        return hash(self.__key)
    
    def __repr__(self):
        return f'<state {self.pc} {self.memory} {self.stack}>'
    
    def queuePostCopyFunction(self, function, *parameters):
        self.postCopyQueue.append((function, *parameters))
        return self
    
    @property
    def deepcopy(self):
        copy = deepcopy(self)
        
        while (copy.postCopyQueue):
            function, *parameters = copy.postCopyQueue.pop(0)
            
            function(*parameters)
        
        return copy

class Result(Enum):
    RunsForever = "*"
    AssertionError = "assertion error"
    DivisionByZero = "divide by zero"
    NullPointer = "null pointer"
    OutOfBounds = "out of bounds"
    Success = "ok"
    DepthExceeded = "depth exceeded"
    NoResult = "No result"
    Unknown = "Unknown result" #TODO:: REMOVE, pending implementation of everything else
    
class Comparison(Enum):
    GreaterThan = "gt"
    GreaterEqual = "ge"
    NotEqual = "ne"
    Equal = "eq"
    LessThan = "lt"
    LessEqual = "le"
    Incomparable = "na"
    
    @property
    def inverse(self):
        return {
            Comparison.GreaterThan: Comparison.LessEqual,
            Comparison.GreaterEqual: Comparison.LessThan,
            Comparison.LessThan: Comparison.GreaterEqual,
            Comparison.LessEqual: Comparison.GreaterThan,
            Comparison.NotEqual: Comparison.Equal,
            Comparison.Equal: Comparison.NotEqual,
            Comparison.Incomparable: Comparison.Incomparable
        }[self]
        
    @property
    def reversed(self):
        return {
            Comparison.GreaterThan: Comparison.LessThan,
            Comparison.GreaterEqual: Comparison.LessEqual,
            Comparison.LessThan: Comparison.GreaterThan,
            Comparison.LessEqual: Comparison.GreaterEqual,
            Comparison.NotEqual: Comparison.NotEqual,
            Comparison.Equal: Comparison.Equal,
            Comparison.Incomparable: Comparison.Incomparable
        }[self]
        
    # TODO: let Comparison compare values directly
    # def compare(self, left, rigth):
    #     return {
    #         Comparison.GreaterThan: lambda: left > 0,
    #         Comparison.GreaterEqual: lambda: left >= 0,
    #         Comparison.NotEqual: lambda: left != 0,
    #         Comparison.Equal: lambda: left == 0,
    #         Comparison.LessThan: lambda: left < 0,
    #         Comparison.LessEqual: lambda: left <= 0,
    #         Comparison.Incomparable: Comparison.Incomparable
    #     }[self]()
        
    
class InvokeType(Enum):
    Special = "special"
    Virtual = "virtual"
    Static = "static"
    Dynamic = "dynamic"
    Interface = "interface"
    
class BinaryOperation(Enum):
    Addition = "add"
    Subtraction = "sub"
    Multiplication = "mul"
    Division = "div"
    Remainder = "rem"
    
class FieldDefinition:
    className : str
    fieldName: str 
    type: classmethod
    
    def __init__(self, name, type, **kwargs):
        self.className = kwargs["class"]
        self.fieldName = name
        self.type = type

class MethodDefinition:
    args : list[classmethod]
    is_interface: bool 
    methodName: any
    ref: any
    returns: classmethod
    
    def __init__(self, args, is_interface, name, ref, returns, **kwargs):
        self.args = args
        self.is_interface = is_interface #kwargs.get("is_interface") or False
        self.name = name
        self.ref = ref
        self.returns = returns

    def get_bytecode(self):
        # Method path
        unique_ref = f"{self.ref["name"].replace("/", ".")}.{self.name}:"
        # Append parameters
        unique_ref += f"({"".join([self.__get_valuetype(arg) for arg in self.args])})"
        # Append return type
        unique_ref += self.__get_valuetype(self.returns)
        l.debug(unique_ref)

        bytecode = METHOD_BYTECODE_STORE.get(unique_ref)
        if not bytecode:
            bytecode = parsing.MethodId.parse(unique_ref).load()
            METHOD_BYTECODE_STORE[unique_ref] = bytecode

        return bytecode

    @staticmethod
    def __get_valuetype(val):
        if isinstance(val, dict) and val.get("kind") == "array":
            return parsing.print_type(f"{val["type"]}[]")
        return parsing.print_type(val)