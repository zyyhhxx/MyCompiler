# Author: Yiyang Zeng yz3622
from lexer import Lexer
from parser import ProjectParser
from ast_nodes import errors, declarations, usage, print_queue
import os

dir = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
scanner = Lexer()
global ast
ast = None


def scan_file(fname, test_name):
    print("-----------------------------Running " + test_name +
          "-----------------------------")

    # Read the file
    with open(fname) as f:
        code = f.read()

    # lex the source code
    tokens = scanner.input(code)
    parser = ProjectParser()
    global ast
    ast = parser.input(tokens)
    ast.eval()
    print("--------------------Declarations--------------------")
    for scope, item, line, item_type in declarations:
        print("%s: declare \"%s\", %s %s" % (line, item, scope,
                                             str(item_type)))
    print("--------------------Variable Usage--------------------")
    for scope, item, use_line, item_type, declared_line in usage:
        print("%s: use \"%s\", %s %s declared on %s" %
              (use_line, item, scope, str(item_type), declared_line))
    print("--------------------Errors--------------------")
    for item in errors:
        print(item)
    print("--------------------Standard Output--------------------")
    for item in print_queue:
        print(item)
    print("--------------------Done--------------------")


# Piazza Sample Test 0
scan_file(os.path.join(dir, "p3longtypecheck.txt"), "Piazza Sample Test 0")

# Piazza Sample Test 1
# scan_file(os.path.join(dir, "p3simplefunctionstypecheck.txt"),
#           "Piazza Sample Test 1")
