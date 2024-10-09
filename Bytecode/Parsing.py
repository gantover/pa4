#!/usr/bin/env python3

from Debug import l

class SubclassFactory(dict):
    typeField: str
    
    def get(self, value):
        result = super().get(value)
        
        if result == None:
            l.debug(f'Sublassfactory returned None for value {value}')
            
        return result
    
    def __init__(self, base_class, typeField):
        # ex : base_class can be Data and subclass will be Integer, Short,...
        self.typeField = typeField 
        
        for subclass in base_class.__subclasses__():
            self[subclass.__name__.lower()] = subclass
            # this fills in the dictionnary of "type" -> actual DataType
    
    def parse(self, data: dict):
        if data is None:
            l.debug(f'None value passed into subclass factory')
            return None
        
        constructor = self.get(data[self.typeField])

        if constructor is None:
            l.debug(f'Unknown instruction encountered: {data[self.typeField]}')
            return None # raise Exception(f'Unknown instruction encountered: {data["opr"]}')
        
        return constructor(**data)