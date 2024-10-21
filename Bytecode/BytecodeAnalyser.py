#!/usr/bin/env python3

# from pydantic import validate_arguments
from typing import List as PyList
# from dataclass_wizard import fromdict
from enum import Enum
from Debug import l

from Instructions import Instruction, instructionFactory
from Datatypes import Unknown, Array, Keystone
from State import State, Result
from random import randint

class Results(dict):
    def __init__(self):
        super(Results, self).__init__()
        self.success_states = [] 

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
                except Exception as e:
                    print(f'exception at {i}, while running instruction {instruction}: {e}')
                    result = Result.Unknown
                    
                
                # if we don't have a list, make it a list
                if isinstance(result, Result) or isinstance(result, State):
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
                        if r == Result.Success:
                            results.success_states.append(state.deepcopy)
                    elif r in self.explored:
                        results[Result.RunsForever] += 1
                    else:
                        self.frontier.append(r)
                        self.explored.add(r)
                        # if the same exact state is added twice to explored
                        # it means that we are into a running forever scenario
                        # the condition to loop was true and since the state has not
                        # been updated, the condition stays true
                        # else:
                        #     results[Result.RunsForever] += 1
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
                    
        printFunction(f'{Result.AssertionError.value};{(results[Result.AssertionError]  > 0) * 100}%')
        printFunction(f'{Result.DivisionByZero.value};{(results[Result.DivisionByZero]  > 0) * 100}%')
        printFunction(f'{Result.NullPointer.value   };{(results[Result.NullPointer]     > 0) * 100}%')
        printFunction(f'{Result.OutOfBounds.value   };{(results[Result.OutOfBounds]     > 0) * 100}%')
        printFunction(f'{Result.Success.value       };{(results[Result.Success]         > 0) * 100}%')
        printFunction(f'{Result.RunsForever.value   };{(results[Result.RunsForever]     > 0) * 100}%')


def parseMethod(method, injected_memory = None):
    instructions = []
    pc, memory, *stack = State(0, dict())
    
    for counter, instruction in enumerate(method["code"]["bytecode"]):
        # l.debug(f'Parsing instruction {instruction}')
        l.debug(f'parsing instruction {counter}')
        l.debug(f"treating {instruction}")
        instructions.append(instructionFactory.parse(instruction))
    
    if injected_memory == None:
        for i, param in enumerate(method["params"]):
            if param["type"].get("kind") == "array":
                # TODO: Array (Ref) should be initialized with "Array" rather than Unknown()
                # We should probably instead somehow flag a param Array (Ref) and make it produce Unknown values of its type
                # arrayOfType = param["type"]["type"]["base"]
                memory[i] = Array(Keystone(), lambda: Keystone())
            else:
                memory[i] = Keystone()
    else:
        memory = injected_memory

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