#!/usr/bin/env python3

class SubclassFactory(dict):
    typeField: str
    
    def __init__(self, base_class, typeField):
        self.typeField = typeField 
        
        for subclass in base_class.__subclasses__():
            self[subclass.__name__.lower()] = subclass
    
    def parse(self, data: dict):
        if data == None:
            return None
        
        constructor = self.get(data[self.typeField])

        if constructor is None:
            print(f'Unknown instruction encountered: {data[self.typeField]}')
            return None # raise Exception(f'Unknown instruction encountered: {data["opr"]}')
        
        return constructor(**data)