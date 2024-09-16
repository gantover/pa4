#!/usr/bin/env python3
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
# from pydantic import validate_arguments
from typing import List as PyList
# from dataclass_wizard import fromdict

import Data

class Type(Enum):
    Integer = 0     # i integer
    Long    = 1     # l	long
    Short   = 2     # s	short
    Byte    = 3     # b	byte
    Char    = 4     # c	character
    Float   = 5     # f	float
    Double  = 6     # d	double
    Ref     = 7     # a	reference

class Data:
    type: Type
    value: any
    
    def __init__(self, type, value) -> None:
        self.type = type
        self.value = value
        
    def __repr__(self) -> str:
        return f'<Data t: {self.type}, v: {self.value}>'
    
    @property
    def __key(self):
        return self.type, self.value

    def __hash__(self):
        return hash(self.__key)

    def __eq__(self, other):
        if isinstance(other, Data):
            return self.__key == other.__key
        return False

class Condition(Enum):
    GreaterThan = "gt"
    GreaterEqual = "ge"
    NotEqual = "ne"
    Equal = "eq"
    LessThan = "lt"
    LessEqual = "le"

class Result(Enum):
    RunsForever = "*"
    AssertionError = "assertion error"
    DivisionByZero = "divide by zero"
    NullPointer = "null pointer"
    OutOfBounds = "out of bounds"
    Success = "ok"
    Unknown = "Unknown result" #TODO:: REMOVE, pending implementation of everything else
    
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

class JavaArray(dict): #TODO:: make immutable and ensure changes don't backflow
    length: Data
    
    def __init__(self, length):
        self.length = length
    
    def __repr__(self):
        return f'<JavaArray l: {self.length}>'
    
    @property
    def __key(self):
        return (self.length)
    
    def __hash__(self):
        return hash(self.__key)
    
    # def __eq__(self, value: object) -> bool:
    #     return super().__eq__(value)

class State:
    pc: int
    memory: tuple
    stack: list[Data]
    
    def __init__(self, pc, memory, *stack):
        self.stack = stack
        self.memory = tuple(sorted(memory.items()))
        self.pc = pc
    
    @property
    def __key(self):
        return self.pc, self.memory, self.stack
    
    def __iter__(self):
        return iter((self.pc, dict(self.memory), self.stack))
    
    def __eq__(self, other):
        if isinstance(other, State):
            return self.__key == other.__key
        return False
    
    def __hash__(self):
        return hash(self.__key)
    
    def __repr__(self):
        return f'<state {self.pc} {self.memory} {self.stack}>'

class Instruction:
    name: str
    
    @abstractmethod
    def execute(self, pc, memory, *stack) -> list[State]:
        print("BAD person, dont create an instance of an abstract base class") # raise Exception("Base instruction should be consider")

class Push(Instruction):
    value: Data
    
    def __init__(self, opr, value, **_):
        self.name = opr
        
        if value is None:
            self.value = Data(None, None)
        else:
            self.value = Data(**value)
    
    def execute(self, pc, memory, *stack) -> State:
        return [State(pc, memory, self.value, *stack)]

class Store(Instruction):
    index: int
    type: Type
    
    def __init__(self, opr, index, type, **_):
        self.name = opr
        self.index = index
        self.type = type
    
    def execute(self, pc, memory, *stack) -> State:
        memory[self.index], *stack = stack
        
        return [State(pc, memory, *stack)]

class Load(Instruction):
    index: int
    type: Type
    
    def __init__(self, opr, index, type, **_):
        self.name = opr
        self.index = index
        self.type = type
        
    def execute(self, pc, memory, *stack) -> State:
        return [State(pc, memory, memory[self.index], *stack)]

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
        
        return [State(pc, memory, array, *stack)]
    
class Dup(Instruction):
    # words: int
    
    def __init__(self, opr, words, **_):
        self.name = opr
        
        if words != 1:
            print("Can't handle dub words different than 1 atm") #TODO:: fix
    
    def execute(self, pc, memory, head, *stack) -> list[State]:
        return [State(pc, memory, head, head, *stack)]
    
class Array_Store(Instruction):
    type: Type
    
    def __init__(self, opr, type, **_):
        self.name = opr
        self.type = type
    
    def execute(self, pc, memory, value, index : Data, arrayRef: Data, *stack) -> list[State]:
        
        array = arrayRef.value
        
        if array == None:
            return Result.NullPointer
        
        # TODO:: Improve bounds check
        # print(index.value)
        
        if isinstance(index.value, int):
            # print("instance of int")
            if index.value < 0:
                return Result.OutOfBounds
            if isinstance(array.length.value, int) and index.value >= array.length.value:
                return Result.OutOfBounds
        
        arrayRef.value[index.value] = value # TODO:: implement type safety
        
        return [State(pc, memory, *stack)]

class array_load(Instruction):
    type: Type
    
    def __init__(self, opr, type, **_):
        self.name = opr
        self.type = type
    
    def execute(self, pc, memory, index, arrayRef : Data, *stack) -> list[State]:
        
        if arrayRef.value == None:
            return Result.NullPointer
        
        if isinstance(index.value, int):
            # print("instance of int")
            if index.value < 0:
                return Result.OutOfBounds
            if isinstance(arrayRef.value.length.value, int) and index.value >= arrayRef.value.length.value:
                return Result.OutOfBounds
        
        value = arrayRef.value[index] #TODO:: type safety, failiure handling
        
        return [State(pc, memory, value, *stack)]
  
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
    
    def execute(self, pc, memory, ref : Data, *stack) -> PyList[State]:
        # TODO:: return array length
        
        if ref.value == None:
            return Result.NullPointer
        
        length = ref.value.length #length(ref)
        
        return [State(pc, memory, length, *stack)]

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
        
        value = Data(self.field.type, None) # TODO:: get data from field
        
        return [State(pc, memory, value, *stack)]

class New(Instruction):
    javaClass: any # TODO:: create type
    
    def __init__(self, opr, **kwargs):
        self.name = opr
        self.javaClass = kwargs["class"]
        
    def execute(self, pc, memory, *stack) -> PyList[State]:
        
        if "AssertionError" in self.javaClass:
            return Result.AssertionError
        
        return Result.Unknown
        
        ref = Data(Type.Ref, None) # TODO:: null refrence for now
        
        return [State(pc, memory, ref, *stack)]
    
class Invoke(Instruction):
    access: any
    method: any
    
    def __init__(self, opr, access, method, **_):
        self.name = opr
        self.access = access
        self.method = method
    
    def execute(self, pc, memory, *stack) -> PyList[State]:
        
        return Result.Unknown # TODO::
        print("Invoking is illegal and you should feel bad <3")
        
        return [State(pc, memory, *stack)]
        
class Throw(Instruction):
    def __init__(self, opr, **_):
        self.name = opr
    
    def execute(self, pc, memory, ref, *stack) -> PyList[State]:
        
        print("Throwable thrown")
        
        return [State(pc, memory, ref)]

class Incr(Instruction): # TODO:: give better name, needs factory update first
    index: int
    amount: int
    
    def __init__(self, opr, index, amount, **_):
        self.name = opr
        self.index = index
        self.amount = amount
    
    def execute(self, pc, memory, *stack):
        
        memory[self.index].value += self.amount
        
        return [State(pc, memory, *stack)]

class GoTo(Instruction):
    target: int
    
    def __init__(self, target, **_):
        self.target = target
    
    def execute(self, pc, memory, *stack):
        return [State(self.target, memory, *stack)]

class Binary(Instruction):
    operant: str # TODO:: consider enum
    type: Type
    
    def __init__(self, opr, operant, type, **_):
        self.name = opr
        self.operant = operant
        self.type = type
    
    def execute(self, pc, memory, val1, val2, *stack):
        
        return Result.Unknown # TODO:: implement
        
        print("Not Implemented Yet:: Binary.execute") #TODO
        result = Data(self.type, None) # TODO
        
        return [State(pc, memory, result, *stack)]

class Cast(Instruction):
    fromType: Type
    toType: Type
    
    def __init__(self, opr, to, **kwargs):
        self.name = opr
        self.fromType = kwargs["from"]
        self.toType = to
    
    def execute(self, pc, memory, head : Data, *stack):
        return [State(pc, memory, Data(self.toType, head.value), stack)]

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

class JavaSimulator:
    instructions: list[Instruction]
    
    frontier: list[State]
    explored: set
    
    def __init__(self, instructions, initial_state):
        self.instructions = instructions
        self.frontier = [initial_state]
        self.explored = {initial_state}
    
    def run(self, depth):
        results = dict()
        unknowns = 0
        
        for result in Result:
            results.setdefault(result, 0)
    
        for i in range(depth):
            if(len(self.frontier) > 0):
                state = self.frontier.pop()
                instruction = self.instructions[state.pc]
                
                pc, memory, stack = state
                
                # print(state, hash(state))
                
                try:
                    result = instruction.execute(pc + 1, memory, *stack)
                except:
                    print(f'exception at {i}, while running instruction {instruction}')
                    break
                
                if isinstance(result, Result):
                    if result == Result.Unknown:
                        unknowns += 1
                    else:
                        results[result] += 1
                else:
                    for state in result:
                        if state not in self.explored:
                            self.frontier.append(state)
                            self.explored.add(state)
                        else:
                            results[Result.RunsForever] += 1
            else:
                break
        
        if i + 1 != depth:
            sum = 0
            
            for value in results.values():
                sum += value
            
            if sum > 0.5 and unknowns == 0:
                for result in Result:
                    if (result == Result.Unknown):
                        continue
                    
                    value = results[result]
                    
                    print(f'{result.value};{value/sum*100}%')

def parseMethod(method):
    instructions = []
    pc, memory, stack = State(0, dict())
    
    for instruction in method["code"]["bytecode"]:
        instructions.append(instructionFactory.parse(instruction))
    
    for i, param in enumerate(method["params"]):
        memory[i] = Data(param["type"]["base"], None)
        
    return JavaSimulator(instructions, State(pc, memory, *stack))