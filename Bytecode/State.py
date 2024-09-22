#!/usr/bin/env python3

from Datatypes import Data, dataFactory
from enum import Enum

class State:
    pc: int
    memory: tuple[any, Data]
    stack: list[Data]
    
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
        self.type = dataFactory.get(type)
        
        if self.type == None:
            print(f"unknown type: {type}")

class MethodDefinition:
    args : list[classmethod]
    is_interface: bool 
    methodName: any
    ref: any
    returns: classmethod
    
    def __init__(self, args, is_interface, name, ref, returns, **kwargs):
        self.args = [dataFactory.get(arg) for arg in args]
        self.is_interface = is_interface #kwargs.get("is_interface") or False
        self.name = name
        self.ref = ref
        self.returns = dataFactory.get(returns)
