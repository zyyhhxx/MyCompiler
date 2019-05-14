from rply.token import BaseBox, Token
errors = []
declarations = []
usage = []
print_queue = []

# Functions
global return_value, return_flag
return_value = None
return_flag = False


def error(message):
    errors.append(message)


class Scopes():
    def __init__(self):
        self.scopes = []
        self.globals = {}

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) > 0:
            self.scopes.pop()

    def get_symbol(self, id):
        # Try local vars first
        if len(self.scopes) > 0:
            if id.name in self.scopes[-1]:
                var = self.scopes[-1][id.name]
                usage.append(("local", id.name, id.line(), type(var.value),
                              var.line()))
                return var
        # Global vars
        if id.name in self.globals:
            var = self.globals[id.name]
            usage.append(("global", id.name, id.line(), type(var.value),
                         var.line()))
            return var
        error("%s: Variable %s is not declared yet" %
              (str(id.line()), id.name))

    def add_symbol_local(self, id):
        declarations.append(("local", id.name, id.line(), type(id.value)))
        if len(self.scopes) > 0:
            self.scopes[-1][id.name] = id
        else:
            error("%s: Cannot declare local variable %s outside a function" %
                  (str(id.line()), id.name))

    def add_symbol_global(self, id):
        declarations.append(("global", id.name, id.line(), type(id.value)))
        if len(self.scopes) <= 0:
            self.globals[id.name] = id
        else:
            error("%s: Cannot declare global variable %s inside a function" %
                  (str(id.line()), id.name))


scopes = Scopes()
functions = Scopes()


class ASTBase(BaseBox):
    def __init__(self, token):
        self.token = token

    def line(self):
        return "Line " + str(self.token.source_pos.lineno)

    def eval(self):
        return self.line()


class Node(BaseBox):
    def __init__(self, name, token_list):
        self.grammar_name = name
        self.token_list = token_list

    def __str__(self):
        return "Node: " + str(self.token_list)

    def __repr__(self):
        return str(self)

    def eval(self):
        # Find all non-tokens in the list and eval it
        for item in self.token_list:
            # If function has returned, do nothing
            if return_flag:
                return
            if type(item) is not Token:
                item.eval()

    def line(self):
        for item in self.token_list:
            if type(item) is Token:
                return "Line " + str(item.source_pos.lineno)
        error("No token found")


class ID(ASTBase):
    def __init__(self, token, value=None):
        super().__init__(token)
        self.name = token.value
        self.value = value

    def eval(self):
        return self

# 3 basic types + bool


class IntegerType(ASTBase):
    def __init__(self, token, value=None):
        super().__init__(token)
        try:
            if value is None:
                self.value = int(self.token.value)
            else:
                self.value = int(value)
        except ValueError:
            self.value = int(0)

    def eval(self):
        return self


class ArrayType(ASTBase):
    def __init__(self, token, size):
        super().__init__(token)
        self.values = [IntegerType(self.token, 0)] * size
        self.size = size

    def tuple_assign(self, assignment):
        values = assignment.values
        for i in range(len(values)):
            self.values[i] = values[i]

    def eval(self):
        return self


class TupleType(ASTBase):
    def __init__(self, token, values):
        super().__init__(token)
        self.values = []
        for value in values:
            self.values.append(value)
        # Tuple elements come in reversed
        self.values.reverse()
        self.size = len(self.values)

    def eval(self):
        return self


class BoolType(ASTBase):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

    def eval(self):
        return self

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

        if lhs is None or rhs is None:
            return

        if type(lhs) is ID:
            lhs = scopes.get_symbol(lhs)
            if lhs is None:
                return
            else:
                lhs = lhs.value

        # Tuple assignment
        if type(lhs) is list:
            for item in lhs:
                if type(item) is not IntegerType:
                    error("%s: tuple element must be integers" %
                          (self.line()))
                    return
            lhs = TupleType(self.token, lhs)

        if type(rhs) is ID:
            rhs = scopes.get_symbol(rhs)
            if rhs is None:
                return
            else:
                rhs = rhs.value

        # Tuple assignment
        if type(rhs) is list:
            for item in rhs:
                if type(item) is not IntegerType:
                    error("%s: tuple element must be integers" %
                          (self.line()))
                    return
            rhs = TupleType(self.token, rhs)

        if not (type(lhs) is IntegerType and type(rhs) is IntegerType) and\
                not (type(lhs) is BoolType and type(rhs) is BoolType):
            error("%s: operator \"%s\" cannot operate on %s and %s" %
                  (self.line(), self.token.value, str(type(lhs)),
                   str(type(rhs))))
            return

        # Numeric operations
        if op == 'OP_PLUS':
            return IntegerType(self.token, int(lhs.value + rhs.value))
        elif op == 'OP_MINUS':
            return IntegerType(self.token, int(lhs.value - rhs.value))
        elif op == 'OP_MULT':
            return IntegerType(self.token, int(lhs.value * rhs.value))
        elif op == 'OP_DIV':
            return IntegerType(self.token, int(lhs.value / rhs.value))
        # Logical operations
        elif op == 'OP_LESSEQUAL':
            return BoolType(self.token, lhs.value <= rhs.value)
        elif op == 'OP_GREATEREQUAL':
            return BoolType(self.token, lhs.value >= rhs.value)
        elif op == 'OP_LESS':
            return BoolType(self.token, lhs.value < rhs.value)
        elif op == 'OP_GREATER':
            return BoolType(self.token, lhs.value > rhs.value)
        elif op == 'OP_EQUAL':
            return BoolType(self.token, lhs.value == rhs.value)
        elif op == 'OP_NOTEQUA':
            return BoolType(self.token, lhs.value != rhs.value)


class CommaOperation(BinaryOperation):
    def eval(self):
        # Comma for tuple declaration
        rhs = self.right.eval()
        lhs = self.left.eval()
        result_list = []

        if type(lhs) is ID:
            lhs = scopes.get_symbol(lhs)
            if lhs is None:
                return
            else:
                lhs = lhs.value

        if type(rhs) is ID:
            rhs = scopes.get_symbol(rhs)
            if rhs is None:
                return
            else:
                rhs = rhs.value

        if type(rhs) is list:
            for i in rhs:
                result_list.append(i)
        else:
            result_list.append(rhs)

        if type(lhs) is list:
            for i in lhs:
                result_list.append(i)
        else:
            result_list.append(lhs)

        return result_list


class Expression(Node):
    def eval(self):
        # Find the only non-token in the list and eval it
        return self.token_list[1].eval()


class Indexed(Node):
    def eval(self):
        id = ID(self.token_list[0])
        var = scopes.get_symbol(id).value
        if type(var) is not ArrayType and type(var) is not TupleType:
            error("%s: variable \"%s\" is not subscriptable" %
                  (self.line(), self.token.value, str(type(self.left)),
                   str(type(self.right))))
        else:
            index = None
            # Index is an expression
            if type(self.token_list[2]) is not Token:
                index = self.token_list[2].eval()
            # Index is an integer
            else:
                index = IntegerType(self.token_list[2])

            if type(index) is not IntegerType:
                error("%s: index must be an integer" %
                      (self.line()))
            # Check if the index is in range
            if index.value >= var.size or index.value < 0:
                error("%s: index %s out of range" %
                      (self.line(), str(index.value)))
                return
            return var.values[index.value]


class Range(BinaryOperation):
    def eval(self):
        lhs = self.left.eval()
        rhs = self.right.eval()
        if type(lhs) is not IntegerType or type(rhs) is not IntegerType:
            error("%s: two sides of range must be integers" %
                  (self.line()))
            return
        elif lhs.value > rhs.value:
            error("%s: range left side %s is larger than right side %s" %
                  (self.line(), str(lhs), str(rhs)))
            return
        return (lhs, rhs)


class Assign(ASTBase):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

    def eval(self):
        result = self.value.eval()

        if result is None:
            return

        # Tuple assignment
        if type(result) is list:
            for item in result:
                if type(item) is not IntegerType:
                    error("%s: tuple element must be integers" %
                          (self.line()))
                    return
            result = TupleType(self.token, result)

        return result


class Declaration(ASTBase):
    def __init__(self, token, id, assignment):
        super().__init__(token)
        self.id = ID(id)
        self.assignment = assignment

    def eval(self):
        assignment_result = self.assignment.eval()
        self.id.value = assignment_result
        key = self.token.name

        # Global variables
        if key == "KW_GLOBAL":
            scopes.add_symbol_global(self.id)
            return

        # Local variables
        if key == "KW_LOCAL":
            scopes.add_symbol_local(self.id)


class ArrayDeclaration(ASTBase):
    def __init__(self, token, id, array_range, assignment):
        super().__init__(token)
        self.id = ID(id)
        self.range = array_range
        self.assignment = assignment

    def eval(self):
        assignment_result = self.assignment.eval()
        range_result = self.range.eval()

        if range_result is None:
            return

        var = scopes.get_symbol(self.id)
        if var is None:
            return

        if var.value is not None and type(var.value) is not ArrayType:
            error("%s: %s cannot be declared as an array" %
                  (self.line(), self.id.name))
            return

        var.value = ArrayType(self.token,
                              range_result[1].value - range_result[0].value)

        if assignment_result is None:
            return

        if type(assignment_result) is TupleType:
            if assignment_result.size == var.value.size:
                var.value.assign(assignment_result)
            else:
                error("%s: sizes of tuple and array do not match" %
                      (self.line()))
        else:
            error("%s: cannot assign %s to an array" %
                  (self.line(), str(type(assignment_result))))


class AssignStatement(BinaryOperation):
    def eval(self):
        lhs = self.left.eval()
        rhs = self.right.eval()

        if lhs is None or rhs is None:
            return

        if type(lhs) is ID:
            lhs = scopes.get_symbol(lhs)
            if lhs is None:
                return
        else:
            error("%s: can only assign to a variable" %
                  (self.line()))
            return

        if type(lhs.value) is ArrayType:
            error("%s: cannot assign to a whole array" %
                  (self.line()))
            return

        if type(rhs) is ID:
            rhs = scopes.get_symbol(rhs)
            if rhs is None:
                return

            if rhs.value is None:
                error("%s: %s has no value to assign" %
                      (self.line(), rhs.name))
                return

            if type(rhs.value) is ArrayType:
                error("%s: cannot assign a whole array to a variable" %
                      (self.line()))
                return

            rhs = rhs.value

        # Tuple assignment
        if type(rhs) is list:
            for item in rhs:
                if type(item) is not IntegerType:
                    error("%s: tuple element must be integers" %
                          (self.line()))
                    return
            rhs = TupleType(self.token, rhs)

        if type(lhs.value) is not type(rhs):
            error("%s: cannot assign %s to %s" %
                  (self.line(), str(type(rhs)), str(type(lhs.value))))
            return

        if type(lhs.value) is TupleType and type(rhs) is TupleType:
            if lhs.value.size != rhs.size:
                error("%s: tuple sizes do not match" % (self.line()))

        else:
            lhs.value = rhs


class ExchangeStatement(BinaryOperation):
    def eval(self):
        lhs = self.left.eval()
        rhs = self.right.eval()

        if lhs is None or rhs is None:
            return

        if type(lhs) is not ID or type(rhs) is not ID:
            error("%s: can only exchange between variables" %
                  (self.line()))
            return

        lhs_id = scopes.get_symbol(lhs)
        rhs_id = scopes.get_symbol(rhs)

        if lhs_id is None or rhs_id is None:
            return

        lhs_id.value, rhs_id.value = rhs_id.value, lhs_id.value


class PrintStatement(ASTBase):
    def __init__(self, token, message):
        super().__init__(token)
        self.message = message

    def eval(self):
        message = self.message.eval()

        if message is None:
            return

        # A lits of messages
        if type(message) is list:
            for item in message:
                print_item = item
                if type(print_item) is ID:
                    result = scopes.get_symbol(print_item)
                    if result is None:
                        return
                    print_item = result.value

                if type(print_item) is IntegerType or\
                        type(print_item) is BoolType:
                    print_queue.append(print_item.value)
                else:
                    error("%s: type %s cannot be printed" %
                          (self.line(), str(type(print_item))))
                    return
            return

        # Single message
        if type(message) is ID:
            result = scopes.get_symbol(message)
            if result is None:
                return
            message = result.value

        if type(message) is IntegerType or type(message) is BoolType:
            print_queue.append(message.value)
        else:
            error("%s: type %s cannot be printed" %
                  (self.line(), str(type(message))))


class WhileLoop(ASTBase):
    def __init__(self, token, condition, statements):
        super().__init__(token)
        self.condition = condition
        self.statements = statements

    def eval(self):
        scopes.push_scope()
        while True:
            condition = self.condition.eval()
            if type(condition) is not BoolType:
                break
            # Flow control
            if condition.value:
                self.statements.eval()
            else:
                break
        scopes.pop_scope()


class ForeachLoop (ASTBase):
    def __init__(self, token, counter, iterator, statements):
        super().__init__(token)
        self.counter = counter
        self.iterator = iterator
        self.statements = statements

    def eval(self):
        scopes.push_scope()
        counter_id = ID(self.counter)
        scopes.add_symbol_local(counter_id)

        if type(self.iterator) is Token:
            iterator = scopes.get_symbol(ID(self.iterator))
            if iterator is None:
                scopes.pop_scope()
                return
            iterator = iterator.value
        else:
            iterator = self.iterator.eval()

        if iterator is None:
            scopes.pop_scope()
            return

        target = 0
        # Range
        if type(iterator) is tuple:
            target = iterator[1]
            for i in range(target):
                counter_id = scopes.get_symbol(counter_id)
                counter_id.value = IntegerType(self.token, i)
                self.statements.eval()
        # Array
        elif type(iterator) is ArrayType:
            target = iterator.size
            for i in range(target):
                counter_id.value = iterator.values[i]
                self.statements.eval()
        else:
            error("%s: cannot only loop over type %s" %
                  (self.line(), str(type(iterator))))
        scopes.pop_scope()


class IfStatement(ASTBase):
    def __init__(self, token, condition, statements, else_statements):
        super().__init__(token)
        self.condition = condition
        self.statements = statements
        self.else_statements = else_statements

    def eval(self):
        condition = self.condition.eval()

        if type(condition) is not BoolType:
            return

        if condition.value:
            self.statements.eval()
        else:
            self.else_statements.eval()


class ElseStatement(ASTBase):
    def __init__(self, token, statements):
        super().__init__(token)
        self.statements = statements

    def eval(self):
        self.statements.eval()


class CommaIdBinary(BinaryOperation):
    def eval(self):
        # Comma for tuple declaration
        rhs = self.right.eval()
        lhs = self.left.eval()
        result_list = []

        if type(lhs) is Token:
            lhs = ID(lhs)

        if type(rhs) is Token:
            rhs = ID(rhs)

        if type(rhs) is list:
            for i in rhs:
                result_list.append(i)
        else:
            result_list.append(rhs)

        if type(lhs) is list:
            for i in lhs:
                result_list.append(i)
        else:
            result_list.append(lhs)

        return result_list


class CommaIdSingle(ASTBase):
    def __init__(self, token, id):
        super().__init__(token)
        self.id = id

    def eval(self):
        return ID(self.id)


class Function(ASTBase):
    def __init__(self, token, name, param, params, body):
        super().__init__(token)
        self.name = name
        self.param = param
        self.params = params
        self.body = body
        self.parameters = None

    def eval(self):
        # Get all parameters
        params = self.params.eval()
        if type(params) is list:
            self.parameters = params
            self.parameters.append(ID(self.param))
            self.parameters.reverse()
        elif type(params) is ID:
            self.parameters = []
            self.parameters.append(ID(self.param))
            self.parameters.append(params)
        functions.add_symbol_global(ID(self.name, self))

    def call(self, params):
        scopes.push_scope()

        # Add parameters
        for i in range(len(self.parameters)):
            self.parameters[i].value = params.values[i]
            scopes.add_symbol_local(self.parameters[i])
        self.body.eval()

        global return_flag
        return_flag = False
        scopes.pop_scope()


class FunctionCall(ASTBase):
    def __init__(self, token, params):
        super().__init__(token)
        self.params = params

    def eval(self):
        # Parse parameters
        params = self.params.eval()
        if params is None:
            return

        if type(params) is list:
            for item in params:
                if type(item) is not IntegerType:
                    error("%s: tuple element must be integers" %
                          (self.line()))
                    return
            params = TupleType(self.token, params)

        elif type(params) is ID:
            item = scopes.get_symbol(params)
            if item is None:
                return
            params = item.value

        if type(params) is not TupleType:
            error("%s: function parameter must be a tuple, have %s" %
                  (self.line(), str(type(params))))
            return

        # Find the function and check parameters
        function_id = functions.get_symbol(ID(self.token))
        if function_id is None:
            return
        if params.size != len(function_id.value.parameters):
            error("%s: tuple size does not match parameter size" %
                  (self.line()))
            return
        function_id.value.call(params)
        return return_value


class ReturnValue(ASTBase):
    def __init__(self, token, value):
        super().__init__(token)
        self.value = value

    def eval(self):
        global return_value, return_flag
        return_value = self.value.eval()
        return_flag = True
        return


class Template(ASTBase):
    def __init__(self, token, value=None):
        super().__init__(token)
        self.name = token.value
        self.value = value

    def eval(self):
        return self.value
