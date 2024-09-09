# BytecodeAnalyser.py
from enum import Enum
from abc import ABC, abstractmethod

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

class State:
    stack: list[Data]
    memory: dict[int, Data]
    # instructions: list['Instruction']
    pc: int
    
    # @staticmethod
    # def FunctionStart(*function_arguments) -> 'State':
    #     stack = []
    #     memory = {index: arg for (index, arg) in enumerate(function_arguments)}
    #     pc = 0
        
    #     return State(stack, memory, pc)
    
    def __init__(self, state):
        self.stack = list(state.stack)
        self.memory = dict(state.memory)
        self.pc = state.pc
    
    def __init__(self, stack, memory, pc):
        self.stack = stack
        self.memory = memory
        self.pc = pc
    
    # def getSuccesorStates(self) -> list['State']:
    #     return self.instructions[self.pc].apply()
    
    
    

class Instruction(ABC):
    name: str
    
    @abstractmethod
    def apply(self, state: State) -> list[State]:
        raise Exception("Base instruction should be consider")



class Push(Instruction):
    value: Data
    
    def apply(self, state: State) -> list[State]:
        state.stack = self.value, *state.stack
        
        return [state]
    
class Store(Instruction):
    index: int
    type: Type
    
    def apply(self, state: State) -> list[State]:
        state.memory[self.index], *state.stack = state.stack
        
        return [state]
    
class Load(Instruction):
    index: int
    type: Type
    
    def apply(self, state: State) -> list[State]:
        state.stack = state.memory[self.index], *state.stack
        
        return [state]

class If(Instruction):
    condition: str #TODO:: make enum
    target: int
    
    def apply(self, state: State) -> list[State]:
        val1, val2, *state.stack = state.stack
        
        jumpState = State(state)
        jumpState.pc = self.target
        
        return [state, jumpState]
    
class NewArray(Instruction):
    dimensions: int
    type: Type
    
    def apply(self, state: State) -> list[State]:
        for i in range(self.dimensions):
            dimension_size, *state.stack = state.stack
        
        return [state]
    
class Dup(Instruction):
    # words: int
    
    def apply(self, state: State) -> list[State]:
        head, *state.stack = state.stack
        state.stack = head, head, *state.stack
        
        return [state]