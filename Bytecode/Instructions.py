#!/usr/bin/env python3

from Datatypes import Data, Ref, dataFactory
from State import State, BranchCondition, Result, FieldDefinition, MethodDefinition
from Parsing import SubclassFactory
from Debug import l

class Instruction:
    name: str
    
    def execute(self, pc, memory, *stack):
        raise Exception("BAD person, dont create an instance of an abstract base class")

class Push(Instruction):
    value: Data
    
    def __init__(self, opr, value, offset):
        self.name = opr
        self.value = dataFactory.parse(value)
    
    def execute(self, pc, memory, *stack):
        return [State(pc, memory, self.value, *stack)]

class Store(Instruction):
    index: int
    type: classmethod
    
    def __init__(self, opr, index, type, offset):
        self.name = opr
        self.index = index
        self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, *stack):
        memory[self.index], *stack = stack
        
        return [State(pc, memory, *stack)]

class Load(Instruction):
    index: int
    type: classmethod
    
    def __init__(self, opr, index, type, offset):
        self.name = opr
        self.index = index
        self.type = dataFactory.get(type)
        
    def execute(self, pc, memory, *stack):
        return [State(pc, memory, memory[self.index], *stack)]

class If(Instruction):
    condition: BranchCondition
    target: int
    
    def __init__(self, opr, condition, target, offset):
        self.name = opr
        self.condition = BranchCondition(condition)
        self.target = target
    
    def execute(self, pc, memory, val1, val2, *stack):
        
        # TODO:: Implement branching chance
        
        return [State(pc, memory, *stack), State(self.target, memory, *stack)]

class IfZ(Instruction): # TODO:: rename, something like "if compare zero"
    condition: BranchCondition
    target: int
    
    def __init__(self, opr, condition, target, offset):
        self.name = opr
        self.condition = BranchCondition(condition)
        self.target = target
    
    def execute(self, pc, memory, val1, *stack):
        
        # TODO:: Implement branching chance
        
        return [State(pc, memory, *stack), State(self.target, memory, *stack)]
    
class NewArray(Instruction):
    dimensions: int
    type:  classmethod
    
    def __init__(self, opr, type, dim, offset):
        self.name = opr
        self.dimensions = dim
        self.type = dataFactory.get(type)
        
        if (dim != 1): #TODO:: implement support for multi dimentional arrays
            print("Can't handle multidimentional array's at the moment")
    
    def execute(self, pc, memory, length, *stack):
        # for i in range(self.dimensions):
        #     dimension_size, *stack = stack
        
        ref = Ref("Array")
        memory[ref] = length
        
        return [State(pc, memory, ref, *stack)]
    
class Dup(Instruction):
    # words: int
    
    def __init__(self, opr, words, offset):
        self.name = opr
        
        if words != 1:
            print("Can't handle dub words different than 1 atm") #TODO:: fix
    
    def execute(self, pc, memory, head, *stack):
        return [State(pc, memory, head, head, *stack)]
    
class Array_Store(Instruction):
    type:  classmethod
    
    def __init__(self, opr, type, offset):
        self.name = opr
        self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, value, index, ref: Ref, *stack):
        
        if ref == None:
            return Result.NullPointer
        
        # TODO:: Improve bounds check
        # print(index.value)
        
        if isinstance(index.value, int):
            # print("instance of int")
            if index.value < 0:
                return Result.OutOfBounds
            if index.value >= memory[ref].value:
                return Result.OutOfBounds
        
        memory[ref[index]] = value # TODO:: implement type safety
        
        return [State(pc, memory, *stack)]

class array_load(Instruction):
    type:  classmethod
    
    def __init__(self, opr, type, offset):
        self.name = opr
        self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, index, ref : Data, *stack):
        
        if ref.value == None:
            return Result.NullPointer
        
        if isinstance(index.value, int):
            # print("instance of int")
            if index.value < 0:
                return Result.OutOfBounds
            if index.value >= memory[ref[index]]:
                return Result.OutOfBounds
        
        value = memory[ref[index]] #TODO:: type safety, failiure handling
        
        return [State(pc, memory, value, *stack)]
  
class Return(Instruction):
    type:  classmethod
    
    def __init__(self, opr, type, offset):
        self.name = opr
        self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, *stack):
        return Result.Success

class ArrayLength(Instruction):
    def __init__(self, opr, offset):
        self.name = opr
    
    def execute(self, pc, memory, ref : Ref, *stack):
        
        if ref == None:
            return Result.NullPointer
        
        length = memory[ref]
        
        return [State(pc, memory, length, *stack)]

class Get(Instruction):
    static: bool
    field: FieldDefinition
    
    def __init__(self, opr, static, field, offset):
        self.name = opr
        self.static = static
        self.field = FieldDefinition(**field)
    
    def execute(self, pc, memory, *stack):
        if not self.static:
            ref, *stack = stack
        
        if self.field.type == None:
            value = None
        else:
            value = self.field.type(None) # TODO:: get data from field
        
        return [State(pc, memory, value, *stack)]

class New(Instruction):
    javaClass: any # TODO:: create type
    
    def __init__(self, opr, **kwargs):
        self.name = opr
        self.javaClass = kwargs["class"]
        
    def execute(self, pc, memory, *stack):
        
        if "AssertionError" in self.javaClass:
            return Result.AssertionError
        
        return Result.Unknown
        
        ref = Ref(self.javaClass) # TODO:: null refrence for now
        
        return [State(pc, memory, ref, *stack)]
    
class Invoke(Instruction):
    access: any
    method: any
    
    def __init__(self, opr, access, method, offset):
        self.name = opr
        self.access = access
        self.method = method
    
    def execute(self, pc, memory, *stack):
        
        return Result.Unknown # TODO::
        print("Invoking is illegal and you should feel bad <3")
        
        return [State(pc, memory, *stack)]
        
class Throw(Instruction):
    def __init__(self, opr, offset):
        self.name = opr
    
    def execute(self, pc, memory, ref, *stack):
        
        print("Throwable thrown")
        
        return [State(pc, memory, ref)]

class Incr(Instruction): # TODO:: give better name, needs factory update first
    index: int
    amount: int
    
    def __init__(self, opr, index, amount, offset):
        self.name = opr
        self.index = index
        self.amount = amount
    
    def execute(self, pc, memory, *stack):
        
        memory[self.index].value += self.amount
        
        return [State(pc, memory, *stack)]

class GoTo(Instruction):
    target: int
    
    def __init__(self, opr, target, offset):
        self.name = opr
        self.target = target
    
    def execute(self, pc, memory, *stack):
        return [State(self.target, memory, *stack)]

class Binary(Instruction):
    operant: str # TODO:: consider enum
    type: classmethod
    
    def __init__(self, opr, operant, type, offset):
        self.name = opr
        self.operant = operant
        self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, val2, val1, *stack):
        # val2, val1 are the two top values on the stack
        if self.type == None:
            l.error("type None detected on binary operation")
            return Result.Unknown
        match(self.operant):
            case "add":
                result = self.type(val1.value + val2.value)
            case "sub":
                result = self.type(val1.value - val2.value)
            case "mul":
                result = self.type(val1.value * val2.value)
            case "div":
                print(f"division detected : val1 {val1.value} / val2 {val2.value}")
                try:
                    result = self.type(val1.value / val2.value)
                except ZeroDivisionError:
                    return Result.DivisionByZero
                except:
                    l.error(f"unimplemented division operation for type {self.type}")
                    return Result.Unknown
            case "rem":
                result = self.type(val1.value % val2.value)
            case _:
                l.error("unimplemented binary operation")
                return Result.Unknown

        return [State(pc, memory, result, *stack)]
        # the result is simply put on top of the stack, waiting to be stored
        

class Cast(Instruction):
    fromType: classmethod
    toType: classmethod
    
    def __init__(self, opr, to, **kwargs):
        self.name = opr
        self.fromType = dataFactory.get(kwargs["from"])
        self.toType = dataFactory.get(to)
    
    def execute(self, pc, memory, head, *stack):
        return [State(pc, memory, self.toType(head.value), stack)]
    
instructionFactory = SubclassFactory(Instruction, "opr")