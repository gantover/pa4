#!/usr/bin/env python3

# from pydantic import validate_arguments
from typing import List as PyList
# from dataclass_wizard import fromdict
from enum import Enum
from Debug import l

from Instructions import Call, Instruction, Push, instructionFactory
from Datatypes import IntegerAbstracion, Array, intRange
from WideIntRange import constants
from State import BinaryOperation, State, Result, Comparison
from random import randint

def trace(state):
    trace = []
    
    while(state):
        trace.append(state)
        state = state.prev
    
    return trace

def extractAbstractions(state : State):
    abstractions = set()
    
    for key, value in state.memory:
        if isinstance(value, IntegerAbstracion):
            abstractions.add((value.tracking.identity, value))
    
    for value in state.stack:
        if isinstance(value, IntegerAbstracion):
            abstractions.add((value.tracking.identity, value))
    
    return abstractions

def calculate_trace(state, instruction):
    traces = [(i, a.tracking.reverse(a.lb), a.tracking.reverse(a.ub)) for i, a in extractAbstractions(state)]
                        
    # print(instruction.name)
    
    if instruction.name == "binary" and instruction.operant == BinaryOperation.Division:
        # print("Binary")
        
        i = state.stack[0].tracking.identity
        
        # print(i, self.important_abstractions, state.memory[0][1].tracking.identity, state.memory[1][1].tracking.identity, traces)
        
        traces = [trace if trace[0] != i else (i, 0 ,0) for trace in traces]
    
    traces = {trace[0]: trace[1:3] for trace in traces}
    
    return traces

class Results(dict):
    def __init__(self):
        super(Results, self).__init__()
        self.returnValues = []




class JavaSimulator:
    instructions: list[Instruction]
    frontier: list[State]
    explored: set
    analysis_cls: IntegerAbstracion
    
    def __init__(self, analysis_cls, instructions, initial_state):
        initial_state.prev = None
        
        self.instructions = instructions
        self.frontier = [initial_state]
        self.explored = {initial_state}
        self.analysis_cls = analysis_cls
        self.toVisit = {pc for pc in range(len(instructions))}
        
        self.important_abstractions = extractAbstractions(initial_state)
    
    def update(self, initial_state):
        self.frontier = [initial_state]
        self.explored = {initial_state}
    
    def run(self, allowed_depth=100, recursion_limit=100, debug=True) -> Results | None:
        results = Results()
        
        for result in Result:
            results.setdefault(result, 0)
    
        for i in range(allowed_depth):
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
                    if not isinstance(r, State) and r is not Result.NoResult:
                        # print(trace(state))
                        # print(extractAbstractions(state))
                        pass
                    
                    if isinstance(r, Result):
                        results[r] += 1
                    elif isinstance(r, State):
                        if r in self.explored:
                            results[Result.RunsForever] += 1
                        else:
                            r.prev = state
                            
                            self.frontier.append(r)
                            self.explored.add(r)
                    elif isinstance(r, Call):
                        if r.method.name == self.name:
                            traces = calculate_trace(state, instruction)
                            
                            infinite = False
                            
                            if len(traces) == 0:
                                infinite = True
                                results[Result.DepthExceeded] += 1
                                
                            
                            for j, altered in extractAbstractions(state):
                                base = traces[j]
                                
                                lb = altered.lb if altered.lb > base[0] else base[0]
                                ub = altered.ub if altered.ub < base[1] else base[1]
                                
                                base_size = base[1] - base[0]
                                internal_size = ub - lb
                                
                                # print(base_size, internal_size)
                                
                                if base_size > internal_size:
                                    predicted_depth = base_size / (base_size - internal_size)
                                    
                                    # print("Depth: ", predicted_depth)
                                    
                                    if predicted_depth > allowed_depth:
                                        results[Result.DepthExceeded] += 1
                                    # else:
                                    #     print("Finite")
                                else:
                                    infinite = True
                                    results[Result.DepthExceeded] += 1
                            
                            # print(r.method.name, traces, " -> ", r)
                            
                            if not infinite:
                                if r.method.returns is not None:
                                    result.append(State(r.return_pc, r.return_memory, intRange(), *r.return_stack))    
                                else:
                                    result.append(State(r.return_pc, r.return_memory, *r.return_stack))
                                
                        else:
                            # print(invoke_call(r, self.analysis_cls, allowed_depth - i, recursion_limit - 1, debug))
                            
                            result.extend(invoke_call(r, self.analysis_cls, allowed_depth - i, recursion_limit - 1, debug))
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
        
        if i + 1 == allowed_depth:
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

def invoke_call(call, analysis_cls, depth, recursion_limit, debug):
    from BytecodeAnalyser import parseMethod
    from State import InvokeType

    if recursion_limit == 0:
        return Result.DepthExceeded

    match(call.access):
        case InvokeType.Static | InvokeType.Dynamic:
            # get the arguments list
            
            # get the method form json
            m = call.method.get_bytecode()

            parsed = parseMethod(m, analysis_cls, call.args)
            l.debug("running invoke function")
            results = parsed.run(depth, recursion_limit, debug)
            
            # l.debug(f'Results: {results}')
            # we unwrap the results to have branches
            # we swap success result with the new stack
            return_values = []
            
            for key, value in results.items():
                if key != Result.Success and value != 0:
                    return_values.append(key)
            
            if results[Result.Success] != 0:
                if call.method.returns is not None:
                    for returnValue in results.returnValues:
                        return_values.append(State(call.return_pc, call.return_memory, returnValue, *call.return_stack))    
                else:
                    return_values.append(State(call.return_pc, call.return_memory, *call.return_stack))
                
            # l.debug(f"!! Return values from invoke !!: {return_values}")
            return return_values
        case InvokeType.Interface | InvokeType.Virtual:
            # TODO: Implement for classes
            pass
        case _:
            l.error(f"unhandled invoke access type : {call.access}")

    return Result.Unknown


def parseMethod(method, analysis_cls = intRange, injected_memory = None):
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

    simulator = JavaSimulator(analysis_cls, instructions, State(pc, memory, *stack))
    
    if hasattr(method, "name"):
        simulator.name = method.name
    else:
        simulator.name = method["name"]
    
    # print(simulator.name)
    
    return simulator


# def generate(param, memory: dict, index: int):
#     try:
#         match(param := param["type"]["base"]):
#             case "int":
#                 var = randint(-10,10)
#                 """TODO : implement a number generation algorithm
#                 based on static values loaded in the binary
#                 we therefore need to have the static
#                 analysis run before the dynamic one"""
#             case "boolean":
#                 var = bool(randint(0,1))
#             case _:
#                 l.error(f"unhandled data type in parameter : {param}")
#                 # TODO implement more types
#         memory[index] = var
#     except:
#         # we should then have an array
#         try:
#             match(sup_param := param["type"]["kind"]):
#                 case "array":
#                     lenght = randint(1, 10)
#                     ref = Array(lenght, 0)
#                     memory[index] = ref
#                     memory[ref] = lenght
#                     param = param["type"]
#                     for i in range(lenght):
#                         generate(param, memory, ref[i])
#                 case _:
#                     l.error(f"unhandled data type in parameter : {param}")
#         except:
#             l.error(f"unhandled method parameter type : {param}")
