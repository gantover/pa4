﻿#!/usr/bin/env python3

from pathlib import Path
from Datatypes import Ref, Unknown, Array, Keystone
from State import State, Comparison, Result, FieldDefinition, MethodDefinition, InvokeType, BinaryOperation
from Parsing import SubclassFactory
from Debug import l
from copy import deepcopy

class Instruction:
    name: str
    
    def __repr__(self): return str(self.__dict__).replace("'", "")[7:-1]
    
    def execute(self, pc, memory, *stack):
        raise Exception("BAD person, dont create an instance of an abstract base class")

class Push(Instruction):
    value: int | bool | float
    
    def __init__(self, opr, value, offset):
        self.name = opr
        self.value = value and value["value"]
    
    def execute(self, pc, memory, *stack):
        return [State(pc, memory, self.value, *stack)]

class Store(Instruction):
    index: int
    # type: classmethod
    
    def __init__(self, opr, index, type, offset):
        self.name = opr
        self.index = index
        # self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, *stack):
        memory[self.index], *stack = stack
        
        return [State(pc, memory, *stack)]

class Load(Instruction):
    index: int
    # type: classmethod
    
    def __init__(self, opr, index, type, offset):
        self.name = opr
        self.index = index
        # self.type = dataFactory.get(type)
        
    def execute(self, pc, memory, *stack):
        return [State(pc, memory, memory[self.index], *stack)]

class If(Instruction):
    condition: Comparison
    target: int
    
    def __init__(self, opr, condition, target, offset):
        self.name = opr
        self.condition = Comparison(condition)
        self.target = target
    
    def __repr__(self): return f'If {self.condition} jump to {self.target}'
    
    def execute(self, pc, memory, val1, val2, *stack):
        
        result = {
            Comparison.GreaterThan: lambda: val2 > val1,
            Comparison.GreaterEqual: lambda: val2 >= val1,
            Comparison.NotEqual: lambda: val2 != val1,
            Comparison.Equal: lambda: val2 == val1,
            Comparison.LessThan: lambda: val2 < val1,
            Comparison.LessEqual: lambda: val2 <= val1
        }[self.condition]()
        
        l.debug(f"If: {val2} {self.condition} {val1} is {result}")
        
        if isinstance(val2, Keystone) and isinstance(val1, int):
            val2.update(val1, self.condition)
        elif isinstance(val2, int) and isinstance(val1, Keystone):
            val1.update(val2, self.condition.reversed)
        
        jump = State(self.target, memory, *stack).deepcopy
        
        if isinstance(val2, Keystone) and isinstance(val1, int):
            val2.update(val1, self.condition.inverse)
        elif isinstance(val2, int) and isinstance(val1, Keystone):
            val1.update(val2, self.condition.reversed.inverse)
        
        stay = State(pc, memory, *stack)
        
        match result:
            case True:
                l.debug("jumping")
                return [jump]
            case False:
                l.debug("staying")
                return [stay]
            case _:
                l.debug("Cannot evaluate if early")
                return [stay, jump]

class IfZ(Instruction):
    condition: Comparison
    target: int
    
    def __init__(self, opr, condition, target, offset):
        self.name = opr
        self.condition = Comparison(condition)
        self.target = target
    
    def execute(self, pc, memory, val, *stack):
        
        result = {
            Comparison.GreaterThan: lambda: val > 0,
            Comparison.GreaterEqual: lambda: val >= 0,
            Comparison.NotEqual: lambda: val != 0,
            Comparison.Equal: lambda: val == 0,
            Comparison.LessThan: lambda: val < 0,
            Comparison.LessEqual: lambda: val <= 0
        }[self.condition]()
        
        l.debug(f"If: {val} {self.condition} {0} is {result}")
        
        if isinstance(val, Keystone):
            val.update(0, self.condition)
        
        jump = State(self.target, memory, *stack).deepcopy
        
        if isinstance(val, Keystone):
            val.update(0, self.condition.inverse)
        
        stay = State(pc, memory, *stack)
        
        match result:
            case True:
                l.debug("jumping")
                return [jump]
            case False:
                l.debug("staying")
                return [stay]
            case _:
                l.debug("Cannot evaluate if early")
                return [stay, jump]

    
class NewArray(Instruction):
    dimensions: int
    # type:  classmethod
    
    def __init__(self, opr, type, dim, offset):
        self.name = opr
        self.dimensions = dim
        self.type = type
        # self.type = dataFactory.get(type)
        
        if (dim != 1): #TODO:: implement support for multi dimentional arrays
            print("Can't handle multidimentional array's at the moment")
    
    def execute(self, pc, memory, length, *stack):
        # for i in range(self.dimensions):
        #     dimension_size, *stack = stack
        
        array = Array(length, lambda: 0) #TODO:: implement default values per type
        
        return [State(pc, memory, array, *stack)]
    
class Dup(Instruction):
    # words: int
    
    def __init__(self, opr, words, offset):
        self.name = opr
        
        if words != 1:
            print("Can't handle dub words different than 1 atm") #TODO:: fix
    
    def execute(self, pc, memory, head, *stack):
        return [State(pc, memory, head, head, *stack)]
    
class Array_Store(Instruction):
    # type:  classmethod
    
    def __init__(self, opr, type, offset):
        self.name = opr
        # self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, value, index, array: Array, *stack):
        
        if array is None:
            return Result.NullPointer
        
        # TODO:: Improve bounds check
        # print(index.value)
        array[index] = value
        
        lowerBound = index < 0
        upperBound = index >= array.length
        
        state = State(pc, memory, *stack)
        
        if lowerBound is False and upperBound is False:
            return state
        
        if lowerBound is True or upperBound is True:
            return Result.OutOfBounds
        
        return [state, Result.OutOfBounds]

class Array_Load(Instruction):
    # type:  classmethod
    
    def __init__(self, opr, type, offset):
        self.name = opr
        # self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, index, array : Array, *stack):
        
        l.debug(array)
        
        if array is None:
            return Result.NullPointer
        
        value = array[index] #TODO:: type safety, failiure handling, is value known
        
        state = State(pc, memory, value, *stack)
        
        
        # if not isinstance(len(array), (int)):
        #     return [state, Result.OutOfBounds]
        
        lowerBound = index < 0
        upperBound = index >= array.length
        
        if lowerBound is False and upperBound is False:
            return state
        
        if lowerBound is True or upperBound is True:
            return Result.OutOfBounds
        
        return [state, Result.OutOfBounds]
  
class Return(Instruction):
    # type:  classmethod
    
    def __init__(self, opr, type, offset):
        self.name = opr
        # self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, *stack):
        if len(stack) == 0:
            return None
        else:
            return stack[0]

class ArrayLength(Instruction):
    def __init__(self, opr, offset):
        self.name = opr
    
    def execute(self, pc, memory, array : Array, *stack):
        
        if array == None:
            return Result.NullPointer
        
        length = array.length
        
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
        
        if self.field.fieldName == "$assertionsDisabled":
            value = False
        elif self.field.type == None:
            l.warning("Field type in get is None")
        else:
            value = Unknown() # TODO:: get data from field
        
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
        
        from BytecodeAnalyser import parseMethod
        match(self.access):
            case InvokeType.Static | InvokeType.Dynamic:
                # get the method form json
                m = self.method.get_bytecode()

                # get the arguments list
                args = self.method.args
                args_length = len(args)
                args_memory_list = stack[:args_length] 
                args_memory = dict() 
                for i in range(args_length):
                    args_memory[i] = args_memory_list[i]

                stack = stack[args_length:]

                parsed = parseMethod(m, args_memory)
                l.debug("running invoke function")
                results = parsed.run(depth=400, debug=True)
                
                # l.debug(f'Results: {results}')
                # we unwrap the results to have branches
                # we swap success result with the new stack
                return_values = []
                
                for key, value in results.items():
                    if key != Result.Success and value != 0:
                        return_values.append(key)
                
                if results[Result.Success] != 0:
                    if self.method.returns is not None:
                        for returnValue in results.returnValues:
                            return_values.append(State(pc, memory, returnValue, *stack))    
                    else:
                        return_values.append(State(pc, memory, *stack))
                    
                # l.debug(f"!! Return values from invoke !!: {return_values}")
                return return_values
            case _:
                l.error(f"unhandled invoke access type : {self.access}")

        # return Result.Unknown
        
        # args = stack[:len(self.method.args)]
        # stack = stack[len(self.method.args):]
        # classfile = (Path("decompiled") / self.name).with_suffix(
        #     ".json"
        # )

        # with open(classfile) as f:
        #     l.debug("read decompiled classfile %s", classfile)
        #     classfile = json.load(f)

        # l.debug("looking up method")
        # # Lookup method
        # for m in classfile["methods"]:
        #     if (
        #         m["name"] == i["method_name"]
        #         and len(i["params"]) == len(m["params"])
        #         and all(
        #             TYPE_LOOKUP[tn] == t["type"]["base"]
        #             for tn, t in zip(i["params"], m["params"])
        #         )
        #     ):
        #         break
        # else:
        #     print("Could not find method")

        # For simplicity we invoke all methods the same way.
        # TODO: "Virtual" and "Interface" should be called on an object.
        if self.access in [InvokeType.Static, InvokeType.Dynamic]:
            return Result.Unknown
        else:
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
        
        memory[self.index] = type(cur)(cur + self.amount)
        
        return [State(pc, memory, *stack)]

class GoTo(Instruction):
    target: int
    
    def __init__(self, opr, target, offset):
        self.name = opr
        self.target = target
    
    def execute(self, pc, memory, *stack):
        
        # if self.target <= pc:
        #     return Result.RunsForever
        
        return [State(self.target, memory, *stack)]

class Binary(Instruction):
    operant: BinaryOperation
    # type: classmethod
    
    def __init__(self, opr, operant, type, offset):
        # TODO : issue to fix with int/integer types
        self.name = opr
        self.operant = BinaryOperation(operant)
        # self.type = dataFactory.get(type)
    
    def execute(self, pc, memory, val2, val1, *stack):
        results = []
        
        if self.operant == BinaryOperation.Division and val2 == 0:
            results.append(Result.DivisionByZero)
        
        op = {
            BinaryOperation.Addition: lambda: val1 + val2,
            BinaryOperation.Subtraction: lambda: val1 - val2,
            BinaryOperation.Multiplication: lambda: val1 * val2,
            BinaryOperation.Remainder: lambda: val1 % val2,
            BinaryOperation.Division: lambda: val1 // val2
        }[self.operant]
        
        try:
            results.append(State(pc, memory, op(), *stack))
        except TypeError as e:
            print(f"Implement Keystone {self.operant.name} you lazy son of a sun, {val1} {val2}")
            l.debug(f'Exception caught in binary: {e}')
            return Result.Unknown
        except Exception as e:
            l.debug(f'Exception caught in binary: {e}')

        return results
        # the result is simply put on top of the stack, waiting to be stored
        

class Cast(Instruction):
    # fromType: classmethod
    # toType: classmethod
    
    def __init__(self, opr, to, **kwargs):
        self.name = opr
        # self.fromType = dataFactory.get(kwargs["from"])
        # self.toType = dataFactory.get(to)
    
    def execute(self, pc, memory, head, *stack):
        # raise NotImplementedError() #TODO:: fix
        
        return [State(pc, memory, head, *stack)] # TODO:: ensure cast is valid
    
instructionFactory = SubclassFactory(Instruction, "opr")