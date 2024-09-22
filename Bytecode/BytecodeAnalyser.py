#!/usr/bin/env python3

# from pydantic import validate_arguments
from typing import List as PyList
# from dataclass_wizard import fromdict
from enum import Enum
from Debug import l

from Instructions import Instruction, instructionFactory
from Datatypes import dataFactory, Unknown
from State import State, Result

class JavaSimulator:
    instructions: list[Instruction]
    
    frontier: list[State]
    explored: set
    
    def __init__(self, instructions, initial_state):
        self.instructions = instructions
        self.frontier = [initial_state]
        self.explored = {initial_state}
    
    def run(self, depth=100):
        results = dict()
        
        for result in Result:
            results.setdefault(result, 0)
    
        for i in range(depth):
            # to explore branches
            if(len(self.frontier) > 0):
                state = self.frontier.pop()
                instruction = self.instructions[state.pc]
                
                pc, memory, *stack = state

                l.debug(f"-----")
                l.debug(f"PC : {pc}")
                l.debug(f"current instruction : {instruction.name}")
                l.debug(f"Stack : {stack}")
                l.debug(f"Memory : {memory}")
                
                try:
                    result = instruction.execute(pc + 1, memory, *stack)
                    
                    l.debug(f'Result: {result}')
                except Exception as e:
                    print(f'exception at {i}, while running instruction {instruction}: {e}')
                    result = Result.Unknown
                    
                
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
                    elif r not in self.explored:
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
        
        if i + 1 != depth:
            # sum is used to weight the probabilites of each result
            sum = 0 #-results[Result.Unknown]
            
            for value in results.values():
                sum += value
            
            if results[Result.Unknown] == 0:
                for result in Result:
                    if (result == Result.Unknown):
                        continue
                    
                    value = results[result]
                    
                    print(f'{result.value};{value/sum*100}%')

def parseMethod(method):
    instructions = []
    pc, memory, *stack = State(0, dict())
    
    for instruction in method["code"]["bytecode"]:
        instructions.append(instructionFactory.parse(instruction))
    
    for i, param in enumerate(method["params"]):
        memory[i] = dataFactory.get(param["type"]["base"])(Unknown())
        
    return JavaSimulator(instructions, State(pc, memory, *stack))