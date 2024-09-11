#!/usr/bin/env python3

from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
# from pydantic import validate_arguments
from typing import List as PyList
# from dataclass_wizard import fromdict

class Type(Enum):
    Integer = 0     # i integer
    Long    = 1     # l	long
    Short   = 2     # s	short
    Byte    = 3     # b	byte
    Char    = 4     # c	character
    Float   = 5     # f	float
    Double  = 6     # d	double
    Ref     = 7     # a	reference

class Condition(Enum):
    GreaterThan = "gt"
    GreaterEqual = "ge"
    NotEqual = "ne"
    Equal = "eq"
    LessThan = "lt"
    LessEqual = "le"

class Result(Enum):
    RunsForever = "*",
    AssertionError = "assertion error",
    DivisionByZero = "divide by zero",
    NullPointer = "null pointer",
    OutOfBounds = "out of bounds",
    Success = "ok",
    
class Data:
    type: Type
    value: any
    
    def __init__(self, type, value) -> None:
        self.type = type
        self.value = value

class FieldDefinition:
    className : str
    fieldName: str 
    type: Type
    
    def __init__(self, name, type, **kwargs):
        self.className = kwargs["class"]
        self.fieldName = name
        self.type = type

class MethodDefinition:
    args : list[Type]
    is_interface: bool 
    methodName: Type
    ref: any
    returns: Type
    
    def __init__(self, args, is_interface, name, ref, returns, **kwargs):
        self.args = args
        self.is_interface = is_interface
        self.name = name
        self.ref = ref
        self.returns = returns

class JavaArray:
    length: Data
    values: dict[int, Data]
    
    def __init__(self, length):
        self.length = length

class State:
    pc: int
    memory: dict[int, Data]
    stack: list[Data]
    
    def __init__(self, pc, memory, *stack):
        self.stack = stack
        self.memory = dict(memory)
        self.pc = pc
    
    def __iter__(self):
        return iter((self.pc, dict(self.memory), self.stack))

class Instruction:
    name: str
    
    @abstractmethod
    def execute(self, pc, memory, *stack) -> list[State]:
        print("BAD person, dont create an instance of an abstract base class") # raise Exception("Base instruction should be consider")

class Push(Instruction):
    value: Data
    
    def __init__(self, opr, value, **_):
        self.name = opr
        self.value = value
    
    def execute(self, pc, memory, *stack) -> State:
        return State(pc, memory, self.value, *stack)

class Store(Instruction):
    index: int
    type: Type
    
    def __init__(self, opr, index, type, **_):
        self.name = opr
        self.index = index
        self.type = type
    
    def execute(self, pc, memory, *stack) -> State:
        memory[self.index], *stack = stack
        
        return State(pc, memory, *stack)

class Load(Instruction):
    index: int
    type: Type
    
    def __init__(self, opr, index, type, **_):
        self.name = opr
        self.index = index
        self.type = type
        
    def execute(self, pc, memory, *stack) -> State:
        return State(pc, memory, memory[self.index], *stack)

class If(Instruction):
    condition: Condition
    target: int
    
    def __init__(self, opr, condition, target, **_):
        self.name = opr
        self.condition = Condition(condition)
        self.target = target
    
    def execute(self, pc, memory, val1, val2, *stack) -> list[State]:
        
        # TODO:: Implement branching chance
        
        return [State(pc, memory, *stack), State(self.target, memory, *stack)]

class IfZ(Instruction): # TODO:: rename, something like "if compare zero"
    condition: Condition
    target: int
    
    def __init__(self, opr, condition, target, **_):
        self.name = opr
        self.condition = Condition(condition)
        self.target = target
    
    def execute(self, pc, memory, val1, *stack) -> list[State]:
        
        # TODO:: Implement branching chance
        
        return [State(pc, memory, *stack), State(self.target, memory, *stack)]
    
class NewArray(Instruction):
    dimensions: int
    type: Type
    
    def __init__(self, opr, type, dim, **_):
        self.name = opr
        self.dimensions = dim
        self.type = type
        
        if (dim != 1): #TODO:: implement support for multi dimentional arrays
            print("Can't handle multidimentional array's at the moment")
    
    def execute(self, pc, memory, length, *stack) -> list[State]:
        # for i in range(self.dimensions):
        #     dimension_size, *stack = stack
        
        array = Data(Type.Ref, JavaArray(length))
        
        return State(pc, memory, array, *stack)
    
class Dup(Instruction):
    # words: int
    
    def __init__(self, opr, **_):
        self.name = opr
    
    def execute(self, pc, memory, head, *stack) -> list[State]:
        return State(pc, memory, head, head, *stack)
    
class Array_Store(Instruction):
    type: Type
    
    def __init__(self, opr, type, **_):
        self.name = opr
        self.type = type
    
    def execute(self, pc, memory, value, index, arrayRef, *stack) -> list[State]:
        
        # TODO:: store value in array at index
        
        return State(pc, memory, *stack)

class array_load(Instruction):
    type: Type
    
    def __init__(self, opr, type, **_):
        self.name = opr
        self.type = type
    
    def execute(self, pc, memory, index, arrayRef, *stack) -> list[State]:
        
        # TODO:: load value in array at index
        
        value = Data(self.type, None) #TODO
        
        return State(pc, memory, value, *stack)
  
class Return(Instruction):
    type: Type
    
    def __init__(self, opr, type, **_):
        self.name = opr
        self.type = type
    
    def execute(self, pc, memory, *stack):
        return Result.Success

class ArrayLength(Instruction):
    def __init__(self, opr, **_):
        self.name = opr
    
    def execute(self, pc, memory, ref, *stack) -> PyList[State]:
        # TODO:: return array length
        
        length = Data(Type.Integer, None) #length(ref)
        
        return State(pc, memory, length, *stack)

class Get(Instruction):
    static: bool
    field: FieldDefinition
    
    def __init__(self, opr, static, field, **_) -> None:
        self.name = opr
        self.static = static
        self.field = FieldDefinition(**field)
    
    def execute(self, pc, memory, *stack) -> PyList[State]:
        if not self.static:
            ref, *stack = stack
        
        value = Data(Type.Ref, None) # TODO
        
        return State(pc, memory, value, *stack)

class New(Instruction):
    javaClass: any # TODO:: create type
    
    def __init__(self, opr, **kwargs) -> None:
        self.name = opr
        self.javaClass = kwargs["class"]
        
    def execute(self, pc, memory, *stack) -> PyList[State]:
        
        ref = Data(Type.Ref, None) # TODO:: null refrence for now
        
        return State(pc, memory, ref, *stack)

class Invoke(Instruction):
    access: any
    method: any
    
    def __init__(self, opr, access, method, **_):
        self.name = opr
        self.access = access
        self.method = method
    
    def execute(self, pc, memory, *stack) -> PyList[State]:
        
        # TODO::
        print("Invoking is illegal and you should feel bad <3")
        
        return State(pc, memory, *stack)
        
class Throw(Instruction):
    def __init__(self, opr, **_) -> None:
        self.name = opr
    
    def execute(self, pc, memory, ref, *stack) -> PyList[State]:
        
        print("Throwable thrown")
        
        return State(pc, memory, ref)

class Incr(Instruction): # TODO:: give better name, needs factory update first
    index: int
    amount: int
    
    def __init__(self, opr, index, amount, **_):
        self.name = opr
        self.index = index
        self.amount = amount
    
    def execute(self, pc, memory, *stack):
        
        memory[self.index] += self.amount # TODO:: this will probably crash, as data is stored with type atm 
        
        return State(pc, memory, *stack)

class GoTo(Instruction):
    target: int
    
    def __init__(self, target, **_):
        self.target = target
    
    def execute(self, pc, memory, *stack):
        return State(self.target, memory, *stack)

class Binary(Instruction):
    operant: str # TODO:: consider enum
    type: Type
    
    def __init__(self, opr, operant, type, **_) -> None:
        self.name = opr
        self.operant = operant
        self.type = type
    
    def execute(self, pc, memory, val1, val2, *stack) -> PyList[State]:
        
        result = Data(self.type, None) # TODO
        
        return State(pc, memory, result, *stack)

class Cast(Instruction):
    fromType: Type
    toType: Type
    
    def __init__(self, opr, to, **kwargs):
        self.name = opr
        self.fromType = kwargs["from"]
        self.toType = to
    
    def execute(self, pc, memory, head : Data, *stack):
        
        toValue = Data(self.toType, head.value)
        
        return State(pc, memory, toValue, stack)

class SubclassFactory(dict):
    def __init__(self, base_class):
        for subclass in base_class.__subclasses__():
            self[subclass.__name__.lower()] = subclass
    
    def parse(self, data: dict):
        constructor = self.get(data["opr"])

        if constructor is None:
            print(f'Unknown instruction encountered: {data["opr"]}')
            return None # raise Exception(f'Unknown instruction encountered: {data["opr"]}')
        
        return constructor(**data)


instructionFactory = SubclassFactory(Instruction)

def parseMethod(method):
    instructions = []
    
    for instruction in method["code"]["bytecode"]:
        instructions.append(instructionFactory.parse(instruction))