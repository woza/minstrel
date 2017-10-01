class enum_type:
    def __init__(self, names):
        '''
        @names is an array of names of values that the type can take on
        The names must be syntactically valid as the names of object fields
        '''
        self.names = names
        for i,name in enumerate(names):
            setattr(self, name, i)

    def __iter__(self):
        return self.names

    def name(self, val):
        return self.names[val]
