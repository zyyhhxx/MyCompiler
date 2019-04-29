from parser import Node

binary_operator = ['OP_MULT', 'OP_DIV', 'OP_PLUS', 'OP_MINUS', 'OP_LESSEQUAL',
                   'OP_GREATEREQUAL', 'OP_LESS', 'OP_GREATER', 'OP_EQUAL',
                   'OP_NOTEQUA']


class Scoper():
    def __init__(self):
        self.symbol_table = {}
        self.symbol_use = []
        self.error = []

    def scope(self, input_item, function=None):
        if type(input_item) is Node:
            # For variable declaration
            if input_item.grammar_name == "decl":
                self.check_variable_declaration(input_item, function)
            # For fuction declaration
            elif input_item.grammar_name == "def":
                self.check_function_definition(input_item, function)
            # For foreach declaration
            elif input_item.grammar_name == "stat" and \
                    type(input_item.token_list[0]) is not Node and \
                    input_item.token_list[0].name == "KW_FOREACH":
                self.check_foreach_declaration(input_item, function)
            # For binary operations
            elif (input_item.grammar_name == "expr" or
                    input_item.grammar_name == "bool_expression") and \
                    len(input_item.token_list) >= 3 and \
                    type(input_item.token_list[1]) is not Node:
                left_type = self.scope(input_item.token_list[0])
                right_type = self.scope(input_item.token_list[2])
                lineno = input_item.token_list[1].source_pos.lineno
                if left_type != INT or right_type != INT:
                    self.error.append("operand types do not match on line " +
                                      str(lineno))
            # For int values
            elif input_item.grammar_name == "expr" and \
                    type(input_item.token_list[0]) is not Node and \
                    input_item.token_list[0].name == "INT_LIT":
                return INT
            # For lhs items
            elif input_item.grammar_name == "expr" and \
                    type(input_item.token_list[0]) is Node and \
                    input_item.token_list[0].grammar_name == "lhs_item":
                return self.scope(input_item.token_list[0])
            elif input_item.grammar_name == "lhs_item":
                var_name = input_item.token_list[0].value
                # Single ID
                if len(input_item.token_list) <= 1:
                    for item in input_item.token_list:
                        self.scope(item, function)
                    if (var_name, function) in self.symbol_table:
                        return self.symbol_table[(var_name, function)].type
                # Tuple element
                elif len(input_item.token_list) <= 3:
                    index = input_item.token_list[2].value
                    for item in input_item.token_list:
                        self.scope(item, function)
                    if (var_name, function) in self.symbol_table:
                        var = self.symbol_table[(var_name, function)]
                        if int(index) > var.tuple_size:
                            lineno = input_item.token_list[0].source_pos.lineno
                            self.error.append("Index out of range on line " +
                                              str(lineno))
                        return INT
                # Tuple element
                elif len(input_item.token_list) <= 4:
                    for item in input_item.token_list:
                        self.scope(item, function)
                    if (var_name, function) in self.symbol_table:
                        return INT
                return UNKNOWN

            # For everything else
            else:
                for item in input_item.token_list:
                    self.scope(item, function)

        # Check variable usage
        elif input_item is not None:
            if input_item.name == "ID":
                pass
                # self.check_variable_use(input_item, function)

    def check_variable_declaration(self, input_item, function):
        var_name = input_item.token_list[1].value
        if input_item.token_list[0].name == "KW_LOCAL":
            if not function:
                error = var_name +\
                    " cannot be delcared local outside a function"
                self.error.append(error)
            else:
                # If variable not already declared, add it to the table
                if (var_name, function) not in self.symbol_table:
                    var_type, tuple_count = \
                        self.decide_type(input_item.token_list[2])
                    var = Variable(var_type,
                                   input_item.token_list[1].source_pos,
                                   LOCAL,
                                   function,
                                   tuple_count
                                   )
                    self.add_to_symbol_table([(var_name, function)], var)
                else:
                    self.error.append(var_name +
                                      " is already declared for " +
                                      function)
        elif input_item.token_list[0].name == "KW_GLOBAL":
            # If variable not already declared, add it to the table
            if (var_name, None) not in self.symbol_table:
                var_type, tuple_count = \
                    self.decide_type(input_item.token_list[2])
                var = Variable(var_type,
                               input_item.token_list[1].source_pos,
                               GLOBAL,
                               function,
                               tuple_count
                               )
                self.add_to_symbol_table((var_name, None), var)
            else:
                self.error.append(var_name +
                                  " is already declared globally")
        # Handle array initialization
        elif input_item.token_list[0].name == "KW_ARRAY":
            # If variable not already declared, add it to the table
            if (var_name, function) not in self.symbol_table:
                self.error.append(var_name +
                                  " is not yet declared for " +
                                  function)
            else:
                var = self.symbol_table[(var_name, function)]
                var.type = ARRAY
                self.add_to_symbol_table((var_name, function), var)

    def check_foreach_declaration(self, input_item, function):
        # Add local index to the table
        var_name = input_item.token_list[1].value
        var = Variable(INT, input_item.token_list[1].source_pos, LOCAL,
                       function)
        self.add_to_symbol_table((var_name, "foreach"), var)
        self.scope(input_item.token_list[3], "foreach")
        self.scope(input_item.token_list[5], "foreach")

    def check_function_definition(self, input_item, function):
        var_name = input_item.token_list[1].value
        # If function not already declared, add it to the table
        if (var_name, None) not in self.symbol_table:
            func = Variable(FUNC, input_item.token_list[1].source_pos, GLOBAL)
            self.add_to_symbol_table()
            self.symbol_table((var_name, None), func)
            self.scope(input_item.token_list[6],
                       input_item.token_list[1].value)
        else:
            self.error.append("function " + var_name + " is not declared")

    def check_variable_use(self, input_item, function):
        var_name = input_item.value
        # Check if the variable is already declared globally
        var = None
        if (var_name, None) in self.symbol_table:
            var = self.symbol_table[(var_name, None)]
        if (var_name, function) in self.symbol_table:
            var = self.symbol_table[(var_name, function)]
        if var is None:
            self.error.append(var_name + " is not declared yet on line " +
                              str(input_item.source_pos.lineno))
            return
        # The existence of the variable confirmed, can now check
        # other things
        print("using \"" + var_name + "\" on line " +
              str(input_item.source_pos.lineno) + ", " + str(var))
        self.symbol_use.append((var, var_name, input_item.source_pos.lineno))

    def decide_type(self, input_item, tuple_count=1):
        if len(input_item.token_list) <= 0:
            return UNKNOWN, None
        elif input_item.grammar_name == "assign":
            return self.decide_type(input_item.token_list[1])
        elif input_item.grammar_name == "expr":
            if type(input_item.token_list[0]) is not Node and \
                    input_item.token_list[0].name == "INT_LIT":
                if tuple_count > 1:
                    return TUPLE, tuple_count
                else:
                    return INT, None
            elif input_item.token_list[1].name == "OP_COMMA":
                return self.decide_type(input_item.token_list[2],
                                        tuple_count+1)
        return INT, None

    def add_to_symbol_table(self, key, value):
        self.symbol_table[key] = value
        print("\"" + key[0] + "\": " + str(self.symbol_table[key]))

    def __str__(self):
        result = ""
        for use in self.symbol_use:
            result += "using \"" + use[1] + "\" on line " +\
                str(use[2]) + ", " + str(use[0]) + "\n"
        for error in self.error:
            result += "ERROR: " + error + "\n"
        return result


class Variable():
    def __init__(self, var_type, line, scope, function=None, tuple_size=None):
        if var_type in TYPES:
            self.type = var_type
        else:
            self.type = UNKNOWN
        self.line = line.lineno
        self.scope = scope
        self.function = function
        self.tuple_size = tuple_size

    def __str__(self):
        if self.type == TUPLE:
            return "%s %s with %s elements declared on line %s" % \
                (self.scope, self.type, self.tuple_size, str(self.line))
        else:
            return "%s %s declared on line %s" % (self.scope, self.type,
                                                  str(self.line))


INT = "int"
TUPLE = "tuple"
ARRAY = "array"
FUNC = "function"
UNKNOWN = "unknown"
TYPES = [INT, TUPLE, ARRAY, FUNC, UNKNOWN]

LOCAL = "local"
GLOBAL = "global"
