from rply.token import BaseBox, Token


class Scopes():
    def __init__(self):
        self.scopes = []
        self.globals = {}

    def push_scope(self, token):
        self.scopes.append({})

    def pop_scope(self, token):
        if len(self.scopes) > 0:
            self.scopes.pop()
        else:
            print("%s: Cannot pop scope because the stack is empty" %
                  (str(token.source_pos.lineno)))

    def get_symbol(self, id):
        # Try local vars first
        if len(self.scopes) > 0:
            if id.name in self.scopes[-1]:
                return self.scopes[-1][id.name]
        # Global vars
        else:
            if id.name in self.globals:
                return self.globals[id.name]
            else:
                print("%s: Variable %s is not declared yet" %
                      (str(id.line()), id.name))

    def add_symbol_local(self, id):
        if len(self.scopes) > 0:
            self.scopes[-1][id.name] = id.value
        else:
            print("%s: Cannot declare local variable %s outside a function" %
                  (str(id.line()), id.name))

    def add_symbol_global(self, id):
        if len(self.scopes) <= 0:
            self.globals[id.name] = id.value
        else:
            print("%s: Cannot declare global variable %s inside a function" %
                  (str(id.line()), id.name))


scopes = Scopes()


class ASTBase(BaseBox):
    def __init__(self, token):
        self.token = token

    def line(self):
        return "Line " + str(self.token.source_pos.lineno)

    def eval(self):
        return self.line()

    def validate(self):
        print("validate is not implememnted for ASTBase")
        return False


class Node(BaseBox):
    def __init__(self, token_list):
        self.token_list = token_list

    def __str__(self):
        return "Node: " + str(self.token_list)

    def eval(self):
        # Find all non-tokens in the list and eval it
        for item in self.token_list:
            if type(item) is not Token:
                item.eval()

    def validate(self):
        for item in self.token_list:
            # Only check non token items
            if type(item) is not Token:
                validation_result = item.validate()
                if not validation_result:
                    return False
        return True

    def line(self):
        for item in self.token_list:
            if type(item) is Token:
                return "Line " + str(item.source_pos.lineno)
        print("No token found")


class ID(ASTBase):
    def __init__(self, token, value=None):
        super().__init__(token)
        self.name = token.value
        self.value = value

    def eval(self):
        return self

    def validate(self):
        return True

# 3 basic types


class IntegerType(ASTBase):
    def __init__(self, token):
        super().__init__(token)
        try:
            self.value = int(self.token.value)
        except ValueError:
            self.value = int(0)

    def eval(self):
        return self.value

    def validate(self):
        return True


class ArrayType(ASTBase):
    def __init__(self, token, size):
        super().__init__(token)
        self.values = [None] * size
        self.size = self.size

    def eval(self):
        return self.values

    def validate(self):
        return True


class TupleType(ASTBase):
    def __init__(self, token, values):
        super().__init__(token)
        self.values = []
        for value in values:
            values.append(value)
        self.size = len(self.values)

    def eval(self):
        return self.values

    def validate(self):
        return True

# Expressions


class BinaryOperation(ASTBase):
    def __init__(self, token, left, right):
        super().__init__(token)
        self.left = left
        self.right = right

    def eval(self):
        op = self.token.name
        lhs = self.left.eval()
        rhs = self.right.eval()

        if type(lhs) is not int or type(rhs) is not int:
            print("%s: operator \"%s\" cannot operate on %s and %s" %
                  (self.line(), self.token.value, str(type(self.left)),
                   str(type(self.right))))
            return None

        # Numeric operations
        if op == 'OP_PLUS':
            return lhs + rhs
        elif op == 'OP_MINUS':
            return lhs - rhs
        elif op == 'OP_MULT':
            return lhs * rhs
        elif op == 'OP_DIV':
            return lhs / rhs
        # Logical operations
        elif op == 'OP_LESSEQUAL':
            return lhs <= rhs
        elif op == 'OP_GREATEREQUAL':
            return lhs >= rhs
        elif op == 'OP_LESS':
            return lhs < rhs
        elif op == 'OP_GREATER':
            return lhs > rhs
        elif op == 'OP_EQUAL':
            return lhs == rhs
        elif op == 'OP_NOTEQUA':
            return lhs != rhs

    def validate(self):
        return True


class CommaOperation(BinaryOperation):
    def eval(self):
        # Comma for tuple declaration
        rhs = self.right.eval()
        lhs = self.left.eval()
        result_list = []
        if type(rhs) is int:
            result_list.append(rhs)
        else:
            for i in rhs:
                result_list.append(i)
        if type(lhs) is int:
            result_list.append(lhs)
        else:
            for i in lhs:
                result_list.append(i)
        return result_list

    def validate(self):
        return True


class Expression(Node):
    def eval(self):
        # Find the only non-token in the list and eval it
        for item in self.token_list:
            if type(item) is not Token:
                return item.eval()


class Indexed(Node):
    def eval(self):
        id = ID(self.token_list[0])
        var = scopes.get_symbol(id).value
        if type(var) is not ArrayType and type(var) is not TupleType:
            print("%s: variable \"%s\" is not subscriptable" %
                  (self.line(), self.token.value, str(type(self.left)),
                   str(type(self.right))))
        else:
            index = self.token_list[2].eval()
            # Check if the index is in range
            if index >= var.size or index < 0:
                print("%s: index %s out of range of variable \"%s\"" %
                      (self.line(), str(index), var.name))
            return var.values[index]

    def validate(self):
        # Array index
        if len(self.token_list) == 4:
            return self.token_list[2].validate()
        # Tuple index
        return True


class ID(ASTBase):
    def __init__(self, token, value=None):
        super().__init__(token)
        self.name = token.value
        self.value = value

    def eval(self):
        return self.value

    def validate(self):
        return True
