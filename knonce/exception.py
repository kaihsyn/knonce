class PreconditionError(Exception):
    def __init__(self, value='Precondition not met.'):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class PostconditionError(Exception):
    def __init__(self, value='Postcondition not met.'):
        self.value = value
    
    def __str__(self):
        return repr(self.value)