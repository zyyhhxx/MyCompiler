from rply.token import BaseBox

class ASTBase(BaseBox):
    def __init__(self, token):
        self.token = token
    
    def line(self):
        return self.token.source_pos.lineno

    def eval(self):
        return "Line: " + str(self.line())

    def validate(self):
        return (False, "validate is not implememnted for ASTBase")

class Node(BaseBox):
    def __init__(self, token_list):
        self.token_list = token_list

    def __str__(self):
        return "Node: " + str(self.token_list)

    def eval(self):
        return str(self)

    def validate(self):
        err_list = []
        is_valid = True
        for item in self.token_list:
            validation_result = item.validate()
            if not validation_result[0]:
                is_valid = False
                if type(item) is not Node:
                    err_list.append(validation_result[1])
                else:
                    for err in validation_result[1]:
                        err_list.append(err)
        return (is_valid, err_list)

class ID(ASTBase):
    def __init__(self, token, name, value=None):
        super().__init__(token)
        self.name = name
        self.value = value

    def eval(self):
        return self.value

    def validate(self):
        return (True, None)

# 3 basic types

class Integer(ASTBase):
    def __init__(self, token, value):
        super().__init__(token)
        try:
            self.value = int(value)
        except:
            self.value = 0

    def eval(self):
        return self.value

    def validate(self):
        return (True, None)

class Array(ASTBase):
    def __init__(self, token, size):
        super().__init__(token)
        self.array = [None]*self.size
        self.size = self.size

    def eval(self):
        return self.array

    def validate(self):
        return (True, None)

class Tuple(ASTBase):
    def __init__(self, token, values):
        super().__init__(token)
        self.values = []
        for value in values:
            values.append(value)

    def eval(self):
        return self.values

    def validate(self):
        return (True, None)

# Expressions

class BinaryOperation(ASTBase):
    def __init__(self, token, left, right):
        super().__init__(token)
        self.left = left
        self.right = right

    def eval(self):
        # Numeric operations
        pass

    def validate(self):
        if type(self.left) is Integer and type(self.right) is Integer:
            return (True, None)
        else:
            return (False, "%s: operator \"%s\" cannot operate on %s and %s" % (self.line(), self.token.value, type(self.left), type(self.right)))

class ArrayIndex(ASTBase):
    def __init__(self, value):
        try:
            self.value = int(value)
        except:
            self.value = 0

    def eval(self):
        return self.value

    def validate(self):
        return (True, None)

class Integer(BaseBox):
    def __init__(self, value):
        try:
            self.value = int(value)
        except:
            self.value = 0

    def eval(self):
        return self.value

    def validate(self):
        return (True, None)

class Integer(BaseBox):
    def __init__(self, value):
        try:
            self.value = int(value)
        except:
            self.value = 0

    def eval(self):
        return self.value

    def validate(self):
        return (True, None)