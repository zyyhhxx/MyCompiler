# Author: Yiyang Zeng yz3622
from rply import LexerGenerator


class Lexer():
    def __init__(self, input=None):
        # Initialize the lexer
        self.lexer = LexerGenerator()
        self._initialize_tokens()
        self.built_lexer = self.lexer.build()
        self.tokens = None
        self.valid_tokens = []
        self.char = 0
        self.line = 0
        self.token_pos = 0

        # Try to parse the input, if there is any
        if input:
            self.input(input)

    # Add all tokens to the lexer
    def _initialize_tokens(self):
        self.lexer.add('KW_ARRAY', r'array')
        self.lexer.add('OP_DOTDOT', r'\.\.')
        self.lexer.add('LBRAK', r'\[')
        self.lexer.add('RBRAK', r'\]')
        self.lexer.add('SEMI', r'\;')
        self.lexer.add('KW_TUPLE', r'tuple')
        self.lexer.add('KW_LOCAL', r'local')
        self.lexer.add('KW_GLOBAL', r'global')
        self.lexer.add('KW_DEFUN', r'defun')
        self.lexer.add('LPAR', r'\(')
        self.lexer.add('RPAR', r'\)')
        self.lexer.add('OP_COMMA', r'\,')
        self.lexer.add('KW_END', r'end')
        self.lexer.add('KW_WHILE', r'while')
        self.lexer.add('KW_DO', r'do')
        self.lexer.add('KW_IF', r'if')
        self.lexer.add('KW_THEN', r'then')
        self.lexer.add('KW_ELSIF', r'elsif')
        self.lexer.add('KW_ELSE', r'else')
        self.lexer.add('KW_FOREACH', r'foreach')
        self.lexer.add('KW_FOR', r'for')
        self.lexer.add('KW_IN', r'in')
        self.lexer.add('OP_DOT', r'\.')
        self.lexer.add('INT_LIT', r'\d+')
        self.lexer.add('RETURN', r'return')
        self.lexer.add('PRINT', r'print')
        self.lexer.add('EXCHANGE', r'\<\-\>')
        self.lexer.add('OP_LESSEQUAL', r'\<\=')
        self.lexer.add('OP_GREATEREQUAL', r'\>\=')
        self.lexer.add('OP_LESS', r'\<')
        self.lexer.add('OP_GREATER', r'\>')
        self.lexer.add('OP_EQUAL', r'\=\=')
        self.lexer.add('OP_NOTEQUA', r'\!\=')
        self.lexer.add('ASSIGN', r'\=')
        self.lexer.add('OP_PLUS', r'\+')
        self.lexer.add('OP_MINUS', r'\-')
        # self.lexer.add('COMMENT', r'\*\*\*.*[^\r\n]')
        self.lexer.add('OP_MULT', r'\*')
        self.lexer.add('OP_DIV', r'\/')
        self.lexer.add('ID', r'[A-Za-z_]+')
        # self.lexer.add('END-OF-LINE', r'\r\n|\n\r|\r|\n')
        # self.lexer.add('WS', r'\s+')
        self.lexer.add('UNKNOWN', r'.')

        # Ignore comments for now
        self.lexer.ignore(r'\*\*\*.*[^\r\n]')
        self.lexer.ignore(r'\r\n|\n\r|\r|\n')
        self.lexer.ignore(r'\s+')

    # Make the lexer to lex an input
    def input(self, input):
        self.char = 0
        self.line = 0
        self.token_pos = 0
        return self.built_lexer.lex(input)
        self.tokens = [i for i in self.built_lexer.lex(input)]
        self.valid_tokens = []

        # Iteratively lex the input
        token = self._next()
        while token:
            # When the token is an ID and it is too long, truncate it
            if token.name == "ID" and len(token.value) > 80:
                truncated = token.value[:80]
                print("ERROR: ID " + token.value +
                      " is too long, truncated to " + truncated)
                token.value = truncated
            if token.name == "INT_LIT" and (int(token.value) > 2147483647 or
                                            int(token.value) < -2147483648):
                print("ERROR: " + token.value + " does not fit in INT_LIT. "
                      + "The proper range is [−2147483648, 2147483647]")
                token.value = "0"
            self.valid_tokens.append(token)
            token = self._next()

        # Reset the value of this counter for further use
        self.token_pos = 0

    # Recursively return the next valid token in the token list
    def _next(self):
        if self.token_pos < len(self.tokens):
            token = self.tokens[self.token_pos]

            if token.name != "WS" and token.name != "END-OF-LINE"\
               and token.name != "UNKNOWN":
                char_pos = self.char
                self.char += len(token.value)
                self.token_pos += 1

                return Token(token.name, token.value, self.line,
                             char_pos)

            elif token.name == "WS":
                self.char += len(token.value)
                self.token_pos += 1
                return self._next()

            elif token.name == "END-OF-LINE":
                self.line += 1
                self.char = 0
                self.token_pos += 1
                return self._next()

            elif token.name == "UNKNOWN":
                print("ERROR: " + token.value + " is not a valid token")
                self.char += len(token.value)
                self.token_pos += 1
                return self._next()

        else:
            return None

    # Advance the counter and return the next token
    def next(self):
        pos = self.token_pos
        if pos < len(self.valid_tokens):
            self.token_pos += 1
            return self.valid_tokens[pos]
        else:
            return None

    # Return the next token without advancing the counter
    def peek(self):
        pos = self.token_pos
        if pos < len(self.valid_tokens):
            return self.valid_tokens[pos]
        else:
            return None


class Token:

    def __init__(self, name, value, line, char_pos):
        self.name = name
        self.value = value
        self.line = line
        self.char_pos = char_pos

    def __str__(self):
        if self.name == "COMMENT":
            return "Comment \"" + self.value + "\" on line "\
                + str(self.line) + ", char " + str(self.char_pos)\
                + " to " + str(self.char_pos + len(self.value) - 1)
        if len(self.value) > 1:
            return self.name + " value " + self.value + " on line "\
                + str(self.line) + ", char " + str(self.char_pos)\
                + " to " + str(self.char_pos + len(self.value) - 1)
        else:
            return self.name + " value " + self.value + " on line "\
                + str(self.line) + ", char " + str(self.char_pos)

    def __repr__(self):
        return str(self)
