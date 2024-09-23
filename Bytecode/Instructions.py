#!/usr/bin/env python3

from Datatypes import Data, Ref, dataFactory, Unknown
from State import State, BranchCondition, Result, FieldDefinition, MethodDefinition, InvokeType, BinaryOperation
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
        jump = State(self.target, memory, *stack)
        stay = State(pc, memory, *stack)
        
        case = {
            BranchCondition.GreaterThan: lambda: val2.value > val1.value,
            BranchCondition.GreaterEqual: lambda: val2.value >= val1.value,
            BranchCondition.NotEqual: lambda: val2.value != val1.value,
            BranchCondition.Equal: lambda: val2.value == val1.value,
            BranchCondition.LessThan: lambda: val2.value < val1.value,
            BranchCondition.LessEqual: lambda: val2.value <= val1.value
        }[self.condition]
        
        l.debug(f"If: {val2.value} {self.condition} {val1.value}")
        
        result = case()
        
        if isinstance(result, Unknown):
            l.debug("Cannot evaluate if early")
        elif result:
            l.debug("jumping")
            return [jump]
        else:
            l.debug("staying")
            return [stay]
        
        # TODO:: Implement branching chance
        
        return [stay, jump]

class IfZ(Instruction): # TODO:: rename, something like "if compare zero"
    condition: BranchCondition
    target: int
    
    def __init__(self, opr, condition, target, offset):
        self.name = opr
        self.condition = BranchCondition(condition)
        self.target = target
    
    def execute(self, pc, memory, val, *stack):
        l.debug(f"{val} {self.condition} 0 ?")

        jump = State(self.target, memory, *stack)
        stay = State(pc, memory, *stack)
        
        case = {
            BranchCondition.GreaterThan: lambda: val.value > 0,
            BranchCondition.GreaterEqual: lambda: val.value >= 0,
            BranchCondition.NotEqual: lambda: val.value != 0,
            BranchCondition.Equal: lambda: val.value == 0,
            BranchCondition.LessThan: lambda: val.value < 0,
            BranchCondition.LessEqual: lambda: val.value <= 0,
        }[self.condition]
        
        l.debug(f"If: {val.value} {self.condition} 0 ")
        
        result = case()
        
        if isinstance(result, Unknown):
            l.debug("Cannot evaluate if early")
        elif result:
            l.debug("jumping")
            return [jump]
        else:
            l.debug("staying")
            return [stay]
        
        # TODO:: Implement branching chance
        
        return [stay, jump]

    
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
        
        if memory[ref] == None:
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
            l.warning("Field type in get is None")
        else:
            value = self.field.type(Unknown()) # TODO:: get data from field
        
        return [State(pc, memory, value, *stack)]

class New(Instruction):
    javaClass: any # TODO:: create type
    
    def __init__(self, opr, **kwargs):
        self.name = opr
        self.javaClass = kwargs["class"]
        
    def execute(self, pc, memory, *stack):
        return [State(pc, memory, Ref(self.javaClass), *stack)]

class Invoke(Instruction):
    access: InvokeType
    method: MethodDefinition
    
    def __init__(self, opr, access, method, offset):
        self.name = opr
        self.access = InvokeType(access)
        self.method = MethodDefinition(**method)
    
    def execute(self, pc, memory, *stack):
        
        args = stack[:len(self.method.args)]
        stack = stack[len(self.method.args):]
        
        #find the method somehow...
        
        # match self.access:
        #     case InvokeType.Dynamic:
                
        #     case InvokeType.Static:
                
        #     case InvokeType.Virtual:
        #         methodRef, *stack = stack
                
        #     case InvokeType.Special:
        #         methodRef, *stack = stack
                
        #     case InvokeType.Interface:
        #         methodRef, *stack = stack
                
        
        if self.access not in {InvokeType.Dynamic, InvokeType.Static}:
            methodRef, *stack = stack
        
            if isinstance(methodRef, Ref) and methodRef.refType == "java/lang/AssertionError": #TODO::TEMP
                return [State(pc, memory, *stack)]
        
        return Result.Unknown # TODO::
        print("Invoking is illegal and you should feel bad <3")
        
        return [State(pc, memory, *stack)]
        
class Throw(Instruction):
    def __init__(self, opr, offset):
        self.name = opr
    
    def execute(self, pc, memory, ref, *stack):
        
        if isinstance(ref, Ref) and ref.refType == "java/lang/AssertionError":
            return Result.AssertionError
        
        return Result.Unknown # An exception was thrown, but not one we're looking for

        #TODO: consider moving to return
        
        return [State(pc, memory, ref)]

class Incr(Instruction): # TODO:: give better name, needs factory update first
    index: int
    amount: int
    
    def __init__(self, opr, index, amount, offset):
        self.name = opr
        self.index = index
        self.amount = amount
    
    def execute(self, pc, memory, *stack):
        
        cur = memory[self.index]
        
        memory[self.index] = type(cur)(cur.value + self.amount)
        
        return [State(pc, memory, *stack)]

class GoTo(Instruction):
    target: int
    
    def __init__(self, opr, target, offset):
        self.name = opr
        self.target = target
    
    def execute(self, pc, memory, *stack):
        
        if self.target <= pc:
            return Result.RunsForever
        
        return [State(self.target, memory, *stack)]

class Binary(Instruction):
    operant: BinaryOperation
    type: classmethod
    
    def __init__(self, opr, operant, type, offset):
        # TODO : issue to fix with int/integer types
        self.name = opr
        self.operant = BinaryOperation(operant)
        self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, val2, val1, *stack):
        results = []
        
        # val2, val1 are the two top values on the stack
        if self.type == None:
            l.warning("type None detected on binary operation")
            return Result.Unknown
        
        if self.operant == BinaryOperation.Division and val2.value == 0 or isinstance(val2.value, Unknown):
            results.append(Result.DivisionByZero)
        
        op = {
            BinaryOperation.Addition: lambda: val1 + val2,
            BinaryOperation.Subtraction: lambda: val1 - val2,
            BinaryOperation.Multiplication: lambda: val1 * val2,
            BinaryOperation.Remainder: lambda: val1 % val2,
            BinaryOperation.Division: lambda: val1 / val2
        }[self.operant]
        
        try:
            results.append(State(pc, memory, op(), *stack))
        except Exception as e:
            l.debug(f'Exception caught in binary: {e}')

        return results
        # the result is simply put on top of the stack, waiting to be stored
        

class Cast(Instruction):
    fromType: classmethod
    toType: classmethod
    
    def __init__(self, opr, to, **kwargs):
        self.name = opr
        self.fromType = dataFactory.get(kwargs["from"])
        self.toType = dataFactory.get(to)
    
    def execute(self, pc, memory, head, *stack):
        return [State(pc, memory, self.toType(head.value), *stack)]
    
instructionFactory = SubclassFactory(Instruction, "opr")