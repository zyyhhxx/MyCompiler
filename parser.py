from rply import ParserGenerator
import ast_nodes

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
            return ast_nodes.Node("start", p)

        @self.pg.production('input : ')
        @self.pg.production('input : statement')
        @self.pg.production('input : declaration')
        @self.pg.production('input : definition')
        @self.pg.production('input : input statement')
        @self.pg.production('input : input declaration')
        @self.pg.production('input : input definition')
        def input(p):
            return ast_nodes.Node("input", p)

        @self.pg.production('expression : LPAR expression RPAR')
        def expr(p):
            return ast_nodes.Expression("expr", p)

        @self.pg.production('expression : expression OP_MULT expression')
        @self.pg.production('expression : expression OP_DIV expression')
        @self.pg.production('expression : expression OP_PLUS expression')
        @self.pg.production('expression : expression OP_MINUS expression')
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
        def binaryOp(p):
            return ast_nodes.BinaryOperation(p[1], p[0], p[2])

        @self.pg.production('expression : expression OP_COMMA expression')
        def commaOp(p):
            return ast_nodes.CommaOperation(p[1], p[0], p[2])

        @self.pg.production('expression : INT_LIT')
        def integer(p):
            return ast_nodes.IntegerType(p[0])

        @self.pg.production('expression : ID')
        def id(p):
            return ast_nodes.ID(p[0])

        @self.pg.production('expression : ID OP_DOT INT_LIT')
        @self.pg.production('expression : ID LBRAK expression RBRAK')
        def lhs_item(p):
            return ast_nodes.Indexed("indexes", p)

        @self.pg.production('range : expression OP_DOTDOT expression')
        def range(p):
            return ast_nodes.Range(p[1], p[0], p[2])

        @self.pg.production('declarations : declarations declaration')
        @self.pg.production('declarations : declaration')
        @self.pg.production('declarations : ')
        def declarations(p):
            return ast_nodes.Node("decls", p)

        @self.pg.production('declaration : KW_ARRAY ID LBRAK range \
            RBRAK assign SEMI')
        def array_declaration(p):
            return ast_nodes.ArrayDeclaration(p[0], p[1], p[3], p[5])

        @self.pg.production('declaration : KW_LOCAL ID assign SEMI')
        @self.pg.production('declaration : KW_GLOBAL ID assign SEMI')
        def declaration(p):
            return ast_nodes.Declaration(p[0], p[1], p[2])

        @self.pg.production('assign : ASSIGN expression')
        def assign(p):
            return ast_nodes.Assign(p[0], p[1])

        @self.pg.production('assign : ')
        def assign_empty(p):
            return ast_nodes.Node("assign", p)

        @self.pg.production('statement : expression ASSIGN expression SEMI')
        def assign_stat(p):
            return ast_nodes.AssignStatement(p[1], p[0], p[2])

        @self.pg.production('statement : expression EXCHANGE expression SEMI')
        def exchange_stat(p):
            return ast_nodes.ExchangeStatement(p[1], p[0], p[2])

        @self.pg.production('statement : PRINT expression SEMI')
        def print_stat(p):
            return ast_nodes.PrintStatement(p[0], p[1])

        @self.pg.production('statement : KW_WHILE bool_expression KW_DO \
            statements KW_END KW_WHILE')
        def while_loop(p):
            return ast_nodes.WhileLoop(p[0], p[1], p[3])

        @self.pg.production('statement : KW_FOREACH ID KW_IN range KW_DO \
            statements KW_END KW_FOR')
        @self.pg.production('statement : KW_FOREACH ID KW_IN ID KW_DO \
            statements KW_END KW_FOR')
        def foreach_loop(p):
            return ast_nodes.ForeachLoop(p[0], p[1], p[3], p[5])

        @self.pg.production('statement : KW_IF bool_expression KW_THEN statements \
            elsif_statements KW_END KW_IF')
        @self.pg.production('elsif_statements : KW_ELSIF bool_expression KW_THEN \
            statements elsif_statements')
        def statement(p):
            return ast_nodes.IfStatement(p[0], p[1], p[3], p[4])

        @self.pg.production('statements : statement')
        @self.pg.production('statements : statements statement')
        @self.pg.production('statements : ')
        def statements(p):
            return ast_nodes.Node("stats", p)

        @self.pg.production('elsif_statements : else_statement')
        def elsif_statement(p):
            return ast_nodes.Node("elsif_stats", p)

        @self.pg.production('else_statement : KW_ELSE statements')
        def else_stat(p):
            return ast_nodes.ElseStatement(p[0], p[1])

        @self.pg.production('else_statement : ')
        def else_statement(p):
            return ast_nodes.Node("else_stat", p)

        # For functions
        @self.pg.production('statement : RETURN expression SEMI')
        def return_value(p):
            return ast_nodes.ReturnValue(p[0], p[1])

        @self.pg.production('expression : ID expression')
        def unknown(p):
            return ast_nodes.FunctionCall(p[0], p[1])

        @self.pg.production('body : statements')
        @self.pg.production('body : declarations')
        @self.pg.production('body : body statements')
        @self.pg.production('body : body declarations')
        def body(p):
            return ast_nodes.Node("body", p)

        @self.pg.production('definition : KW_DEFUN ID LPAR ID comma_id RPAR \
            body KW_END KW_DEFUN')
        def definition(p):
            return ast_nodes.Function(p[0], p[1], p[3], p[4], p[6])

        @self.pg.production('comma_id : comma_id OP_COMMA ID')
        def comma_id_binary(p):
            return ast_nodes.CommaIdBinary(p[1], p[0], p[2])

        @self.pg.production('comma_id : OP_COMMA ID')
        def comma_id_single(p):
            return ast_nodes.CommaIdSingle(p[0], p[1])

        @self.pg.production('comma_id : ')
        def comma_id(p):
            return ast_nodes.Node("comma_id", p)

        @self.pg.error
        def error_handler(token):
            raise ValueError("Ran into an issue with %s at %s" %
                             (token, token.getsourcepos()))
