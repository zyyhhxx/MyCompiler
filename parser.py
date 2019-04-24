from rply import ParserGenerator
token_list = ['KW_ARRAY', 'OP_DOTDOT', 'LBRAK', 'RBRAK', 'SEMI', 'KW_TUPLE',
              'KW_LOCAL', 'KW_GLOBAL', 'KW_DEFUN', 'LPAR', 'RPAR', 'OP_COMMA',
              'KW_END', 'KW_WHILE', 'KW_DO', 'KW_IF', 'KW_THEN', 'KW_ELSIF',
              'KW_ELSE', 'KW_FOREACH', 'KW_FOR', 'KW_IN', 'OP_DOT', 'INT_LIT',
              'RETURN',
              'PRINT', 'EXCHANGE', 'OP_LESSEQUAL', 'OP_GREATEREQUAL',
              'OP_LESS', 'OP_GREATER', 'OP_EQUAL', 'OP_NOTEQUA', 'ASSIGN',
              'OP_PLUS', 'OP_MINUS', 'COMMENT', 'OP_MULT', 'OP_DIV', 'ID',
              'END-OF-LINE', 'WS', 'UNKNOWN']
precedence_list = [('left', ['OP_PLUS', 'OP_MINUS']),
                   ('left', ['OP_MULT', 'OP_DIV'])]


class ProjectParser():
    def __init__(self):
        self.pg = ParserGenerator(token_list, precedence=precedence_list)
        self.parse()
        self.built_parser = self.pg.build()

    def input(self, tokens):
        return self.built_parser.parse(tokens)

    def parse(self):
        @self.pg.production('start : input')
        def start(p):
            return Node("start", p)

        @self.pg.production('input : ')
        @self.pg.production('input : statement')
        @self.pg.production('input : declaration')
        @self.pg.production('input : definition')
        @self.pg.production('input : input statement')
        @self.pg.production('input : input declaration')
        @self.pg.production('input : input definition')
        def input(p):
            return Node("input", p)

        @self.pg.production('expression : INT_LIT')
        @self.pg.production('expression : lhs_item')
        @self.pg.production('expression : ID expression')
        @self.pg.production('expression : LPAR expression RPAR')
        @self.pg.production('expression : expression OP_MULT expression')
        @self.pg.production('expression : expression OP_DIV expression')
        @self.pg.production('expression : expression OP_PLUS expression')
        @self.pg.production('expression : expression OP_MINUS expression')
        @self.pg.production('expression : expression OP_COMMA expression')
        def expr(p):
            return Node("expr", p)

        @self.pg.production('lhs_item : ID')
        @self.pg.production('lhs_item : ID OP_DOT INT_LIT')
        @self.pg.production('lhs_item : ID LBRAK expression RBRAK')
        def lhs_item(p):
            return Node("lhs_item", p)

        @self.pg.production('lhs : lhs_item')
        @self.pg.production('lhs : lhs OP_COMMA lhs_item')
        def lhs(p):
            return Node("lhs", p)

        @self.pg.production('bool_expression : expression OP_LESS expression')
        @self.pg.production('bool_expression : expression OP_GREATER \
            expression')
        @self.pg.production('bool_expression : expression OP_EQUAL expression')
        @self.pg.production('bool_expression : expression OP_NOTEQUA \
            expression')
        @self.pg.production('bool_expression : expression OP_LESSEQUAL \
            expression')
        @self.pg.production('bool_expression : expression OP_GREATEREQUAL \
            expression')
        def bool_expr(p):
            return Node("bool_expr", p)

        @self.pg.production('range : expression OP_DOTDOT expression')
        def range(p):
            return Node("range", p)

        @self.pg.production('array_id : ID')
        def array_id(p):
            return Node("array_id", p)

        @self.pg.production('statement : lhs ASSIGN expression SEMI')
        @self.pg.production('statement : lhs EXCHANGE lhs SEMI')
        @self.pg.production('statement : KW_WHILE bool_expression KW_DO \
            statements KW_END KW_WHILE')
        @self.pg.production('statement : if_statement')
        @self.pg.production('statement : KW_FOREACH ID KW_IN range KW_DO \
            statements KW_END KW_FOR')
        @self.pg.production('statement : KW_FOREACH ID KW_IN array_id KW_DO \
            statements KW_END KW_FOR')
        @self.pg.production('statement : RETURN expression SEMI')
        @self.pg.production('statement : PRINT expression SEMI')
        def statement(p):
            return Node("stat", p)

        @self.pg.production('statements : statement')
        @self.pg.production('statements : statements statement')
        @self.pg.production('statements : ')
        def statements(p):
            return Node("stats", p)

        @self.pg.production('if_statement : KW_IF bool_expression KW_THEN statements \
            elsif_statements else_statement KW_END KW_IF')
        def if_statement(p):
            return Node("if_stat", p)

        @self.pg.production('elsif_statements : KW_ELSIF bool_expression KW_THEN \
            statements')
        @self.pg.production('elsif_statements : elsif_statements KW_ELSIF bool_expression \
            KW_THEN statements')
        @self.pg.production('elsif_statements : ')
        def elsif_statement(p):
            return Node("elsif_stat", p)

        @self.pg.production('else_statement : KW_ELSE statements')
        @self.pg.production('else_statement : ')
        def else_statement(p):
            return Node("else_stat", p)

        @self.pg.production('body : statements')
        @self.pg.production('body : declarations')
        @self.pg.production('body : body statements')
        @self.pg.production('body : body declarations')
        def body(p):
            return Node("body", p)

        @self.pg.production('definition : KW_DEFUN ID LPAR ID comma_id RPAR \
            body KW_END KW_DEFUN')
        def definition(p):
            return Node("def", p)

        @self.pg.production('comma_id : comma_id OP_COMMA ID')
        @self.pg.production('comma_id : OP_COMMA ID')
        @self.pg.production('comma_id : ')
        def comma_id(p):
            return Node("comma_id", p)

        @self.pg.production('declarations : declarations declaration')
        @self.pg.production('declarations : declaration')
        @self.pg.production('declarations : ')
        def declarations(p):
            return Node("decls", p)

        @self.pg.production('declaration : KW_ARRAY ID LBRAK expression \
            OP_DOTDOT expression RBRAK id_assign SEMI')
        @self.pg.production('declaration : KW_LOCAL ID ASSIGN expression SEMI')
        @self.pg.production('declaration : KW_GLOBAL ID ASSIGN expression \
            SEMI')
        def declaration(p):
            return Node("decl", p)

        @self.pg.production('id_assign : ID ASSIGN expression')
        @self.pg.production('id_assign : ')
        def id_assign(p):
            return Node("id_assign", p)

        @self.pg.error
        def error_handler(token):
            raise ValueError("Ran into an issue with %s at %s" %
                             (token, token.getsourcepos()))


class Node():
    def __init__(self, name, token_list):
        self.grammar_name = name
        self.token_list = token_list

    def __str__(self):
        return self.grammar_name + ": " + str(self.token_list)
