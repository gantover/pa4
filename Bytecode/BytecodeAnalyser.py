#!/usr/bin/env python3

# from pydantic import validate_arguments
from typing import List as PyList
# from dataclass_wizard import fromdict
from enum import Enum
from Debug import l

from Instructions import Call, Instruction, Push, instructionFactory
from Datatypes import Unknown, Array, Keystone
from WideIntRange import constants
from State import State, Result, Comparison
from random import randint

class Results(dict):
    def __init__(self):
        super(Results, self).__init__()
        self.returnValues = []

class JavaSimulator:
    instructions: list[Instruction]
    frontier: list[State]
    explored: set
    
    def __init__(self, instructions, initial_state):
        self.instructions = instructions
        self.frontier = [initial_state]
        self.explored = {initial_state}
        self.toVisit = {pc for pc in range(len(instructions))}
    
    def update(self, initial_state):
        self.frontier = [initial_state]
        self.explored = {initial_state}
    
    def run(self, depth=100, debug=True) -> Results | None:
        results = Results()
        
        for result in Result:
            results.setdefault(result, 0)
    
        for i in range(depth):
            # to explore branches
            if(len(self.frontier) > 0):
                state = self.frontier.pop()
                instruction = self.instructions[state.pc]
                
                pc, memory, *stack = state.deepcopy
                
                if pc in self.toVisit:
                    self.toVisit.remove(pc)

                if debug:
                    l.debug(f"-----")
                    l.debug(f"PC : {pc}")
                    l.debug(f"current instruction : {instruction}")
                    l.debug(f"Stack : {stack}")
                    l.debug(f"Memory : {memory}")
                
                try:
                    result = instruction.execute(pc + 1, memory, *stack)
                    
                    if debug:
                        l.debug(f'Result: {result}')
                        l.debug(self.frontier)
                except Exception as e:
                    l.error(f'exception at {i}, while running instruction {instruction}: {e}')
                    result = Result.Unknown
                    
                
                # if we don't have a list, make it a list
                if not isinstance(result, list):
                    result = [result]
                
                # checks wheter we have a final result or if the state
                # should continue to be updated or if we branched
                # if isinstance(result, Result):
                #     if result == Result.Unknown:
                #         unknowns += 1
                #     else:
                #         results[result] += 1
                # else:
                    # there could be multiple branch states
                    # for instance if statement returns two states 
                    
                    
                for r in result:
                    if isinstance(r, Result):
                        results[r] += 1
                    elif isinstance(r, State):
                        if r in self.explored:
                            results[Result.RunsForever] += 1
                        else:
                            self.frontier.append(r)
                            self.explored.add(r)
                    elif isinstance(r, Call):
                        results[Result.Unknown] += 1
                        pass
                    else:
                        results[Result.Success] += 1
                        results.returnValues.append(r)
                        # if the same exact state is added twice to explored
                        # it means that we are into a running forever scenario
                        # the condition to loop was true and since the state has not
                        # been updated, the condition stays true
                        # else:
                        #     results[Result.RunsForever] += 1
                l.debug(self.frontier)
            else:
                break
        
        if i + 1 == depth:
            l.debug("reached max depth")
            results[Result.Unknown] += 1
            
        # if len(self.toVisit) > 0: #TODO
        #     l.debug(f"Didn't visit the instructions {self.toVisit}")
        #     return {Result.Unknown: 1}
        
        return results
            # if it fails and return None, this will be intercepted in the exception

    @staticmethod
    def interpretResults(results):
        printFunction = l.debug if results[Result.Unknown] != 0 else print
        
        certainty = 95
                    
        printFunction(f'{Result.AssertionError.value};{certainty if results[Result.AssertionError]  > 0 else 100 - certainty }%')
        printFunction(f'{Result.DivisionByZero.value};{certainty if results[Result.DivisionByZero]  > 0 else 100 - certainty }%')
        printFunction(f'{Result.NullPointer.value   };{certainty if results[Result.NullPointer]     > 0 else 100 - certainty }%')
        printFunction(f'{Result.OutOfBounds.value   };{certainty if results[Result.OutOfBounds]     > 0 else 100 - certainty }%')
        printFunction(f'{Result.Success.value       };{certainty if results[Result.Success]         > 0 else 100 - certainty }%')
        printFunction(f'{Result.RunsForever.value   };{certainty if results[Result.RunsForever]     > 0 else 100 - certainty }%')
        printFunction(f'{Result.DepthExceeded.value };{certainty if results[Result.DepthExceeded]   > 0 else 100 - certainty }%')

def Invokation():
    from BytecodeAnalyser import parseMethod
    match(self.access):
        case InvokeType.Static | InvokeType.Dynamic:
            if memory["recursion_depth_limit"] == 0:
                return Result.DepthExceeded

            
            # get the arguments list
            
            
            
            # get the method form json
            m = self.method.get_bytecode()

            parsed = parseMethod(m, memory["analysis_class"], args_memory, memory["recursion_depth_limit"] - 1)
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
        case InvokeType.Interface | InvokeType.Virtual:
            # TODO: Implement for classes
            pass
        case _:
            l.error(f"unhandled invoke access type : {self.access}")

    methodRef, *stack = stack

    if isinstance(methodRef, Ref) and methodRef.refType == "java/lang/AssertionError": #TODO::TEMP
        return [State(pc, memory, *stack)]

    return Result.Unknown


def parseMethod(method, analysis_cls = Keystone, injected_memory = None, recursion_limit = 100):
    instructions = []
    pc, memory, *stack = State(0, dict())
    
    for counter, instruction in enumerate(method["code"]["bytecode"]):
        # l.debug(f'Parsing instruction {instruction}')
        # l.debug(f'parsing instruction {counter}')
        # l.debug(f"treating {instruction}")
        instructions.append(instructionFactory.parse(instruction))

    # constants for latter use with a widening operator
    for instruction in instructions:
        if isinstance(instruction, Push):
            # this constants list, was declared in the datatypes file
            constants.append(instruction.value)

    if injected_memory == None:
        for i, param in enumerate(method["params"]):
            if param["type"].get("kind") == "array":
                arrayLength = analysis_cls()
                arrayLength.update(0, Comparison.GreaterEqual)
                
                memory[i] = Array(arrayLength, lambda: analysis_cls())
            else:
                memory[i] = analysis_cls()
    else:
        memory = injected_memory

    memory["recursion_depth_limit"] = recursion_limit
    memory["analysis_class"] = analysis_cls

    return JavaSimulator(instructions, State(pc, memory, *stack))


def generate(param, memory: dict, index: int):
    try:
        match(param := param["type"]["base"]):
            case "int":
                var = randint(-10,10)
                """TODO : implement a number generation algorithm
                based on static values loaded in the binary
                we therefore need to have the static
                analysis run before the dynamic one"""
            case "boolean":
                var = bool(randint(0,1))
            case _:
                l.error(f"unhandled data type in parameter : {param}")
                # TODO implement more types
        memory[index] = var
    except:
        # we should then have an array
        try:
            match(sup_param := param["type"]["kind"]):
                case "array":
                    lenght = randint(1, 10)
                    ref = Array(lenght, 0)
                    memory[index] = ref
                    memory[ref] = lenght
                    param = param["type"]
                    for i in range(lenght):
                        generate(param, memory, ref[i])
                case _:
                    l.error(f"unhandled data type in parameter : {param}")
        except:
            l.error(f"unhandled method parameter type : {param}")
