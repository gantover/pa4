#!/usr/bin/env python3

from enum import Enum
from copy import deepcopy
import parsing

class State:
    pc: int
    memory: tuple[any]
    stack: list[any]
    
    def __init__(self, pc, memory, *stack):
        self.stack = stack
        self.memory = tuple(memory.items())
        self.pc = pc
    
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
    
    @property
    def deepcopy(self):
        return deepcopy(self)

class Result(Enum):
    RunsForever = "*"
    AssertionError = "assertion error"
    DivisionByZero = "divide by zero"
    NullPointer = "null pointer"
    OutOfBounds = "out of bounds"
    Success = "ok"
    Unknown = "Unknown result" #TODO:: REMOVE, pending implementation of everything else
    
class BranchCondition(Enum):
    GreaterThan = "gt"
    GreaterEqual = "ge"
    NotEqual = "ne"
    Equal = "eq"
    LessThan = "lt"
    LessEqual = "le"
    
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
        unique_ref += f"({"".join([parsing.print_type(arg) for arg in self.args])})"
        # Append return type
        unique_ref += parsing.print_type(self.returns)

        return parsing.MethodId.parse(unique_ref).load()
