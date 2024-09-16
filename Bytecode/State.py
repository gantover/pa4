#!/usr/bin/env python3

from Datatypes import Data, dataFactory
from enum import Enum

class MutableMemory(dict):
    def __setitem__(self, *keys, value):
        super().__setitem__(keys, value)

    def __getitem__(self, *keys):
        return super().__getitem__(keys)

class State:
    pc: int
    memory: tuple[any, Data]
    stack: list[Data]
    
    def __init__(self, pc, memory, *stack):
        self.stack = stack
        self.memory = tuple(sorted(memory.items()))
        self.pc = pc
    
    @property
    def __key(self):
        return self.pc, self.memory, self.stack
    
    def __iter__(self):
        return iter((self.pc, MutableMemory(self.memory), *self.stack))
    
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
    
class FieldDefinition:
    className : str
    fieldName: str 
    type: classmethod
    
    def __init__(self, name, type, **kwargs):
        self.className = kwargs["class"]
        self.fieldName = name
        self.type = dataFactory.get(type)

class MethodDefinition:
    args : list[any]
    is_interface: bool 
    methodName: any
    ref: any
    returns: classmethod
    
    def __init__(self, args, is_interface, name, ref, returns, **kwargs):
        self.args = args
        self.is_interface = is_interface
        self.name = name
        self.ref = ref
        self.returns = dataFactory.get(returns)
