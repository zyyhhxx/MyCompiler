# Author: Yiyang Zeng yz3622
from lexer import Lexer
from parser import ProjectParser, Node
import os

dir = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
scanner = Lexer()
parser = ProjectParser()


def scan_file(fname, test_name):
    print("-----------------------------Running " + test_name +
          "-----------------------------")

    # Read the file
    with open(fname) as f:
        code = f.read()

    # lex the source code
    tokens = scanner.input(code)
    parser = ProjectParser()
    ast = parser.input(tokens)
    print_tree_preorder(ast)


def print_tree(node, dot_num=0):
    has_token = False
    for token in node.token_list:
        if not isinstance(token, Node):
            has_token = True
    for token in node.token_list:
        if isinstance(token, Node):
            if has_token:
                print_tree(token, dot_num+1)
            else:
                print_tree(token, dot_num)
        else:
            # Indentation
            for i in range(dot_num*2):
                print('.', end='')
            print(token.name + ":" + token.value)


pre_tokens = ['KW_ARRAY', 'OP_DOTDOT', 'KW_TUPLE',
              'KW_LOCAL', 'KW_GLOBAL', 'KW_DEFUN', 'LPAR', 'OP_COMMA',
              'KW_ELSIF',
              'KW_ELSE', 'KW_IN', 'OP_DOT',
              'RETURN',
              'PRINT', 'EXCHANGE', 'OP_LESSEQUAL', 'OP_GREATEREQUAL',
              'OP_LESS', 'OP_GREATER', 'OP_EQUAL', 'OP_NOTEQUA', 'ASSIGN',
              'OP_PLUS', 'OP_MINUS', 'OP_MULT', 'OP_DIV']


def print_tree_preorder(node, dot_num=0):
    has_token = False
    pre_token_list = []
    for token in node.token_list:
        if not isinstance(token, Node):
            has_token = True
            if token.name in pre_tokens:
                pre_token_list.append(token)
    for token in pre_token_list:
        # Indentation
        for i in range(dot_num*2):
            print('.', end='')
        print(token.name + ":" + token.value)
    for token in node.token_list:
        if isinstance(token, Node):
            if has_token:
                print_tree_preorder(token, dot_num+1)
            else:
                print_tree_preorder(token, dot_num)
        else:
            if token not in pre_token_list:
                # Indentation
                for i in range(dot_num*2):
                    print('.', end='')
                print(token.name + ":" + token.value)


# Piazza Sample Test 0
scan_file(os.path.join(dir, "p2test0.txt"), "Piazza Sample Test 0")

# Piazza Sample Test 1
scan_file(os.path.join(dir, "p2test1.txt"), "Piazza Sample Test 1")

# Piazza Sample Test 2
scan_file(os.path.join(dir, "p2test2.txt"), "Piazza Sample Test 2")

# Piazza Sample Test 3
scan_file(os.path.join(dir, "p2test3.txt"), "Piazza Sample Test 3")

# Piazza Sample Test 4
scan_file(os.path.join(dir, "p2test4.txt"), "Piazza Sample Test 4")

# Piazza Sample Test 5
scan_file(os.path.join(dir, "p2test5.txt"), "Piazza Sample Test 5")

# Piazza Sample Test 6
scan_file(os.path.join(dir, "p2test10.txt"), "Piazza Sample Test 10")
