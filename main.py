# Author: Yiyang Zeng yz3622
from lexer import Lexer
from parser import ProjectParser
from codegen import CodeGen
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
    with open(os.path.join(dir, fname)) as f:
        code = f.read()

    # Lex the source code
    tokens = scanner.input(code)

    # Initialize the code generator
    codegen = CodeGen()

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
    print("--------------------Generating IR--------------------")
    ast.ir_eval(codegen.module, codegen.builder, codegen.printf)
    codegen.create_ir()
    codegen.save_ir(fname[0:-4] + ".ll")
    print("--------------------Done--------------------")


# Piazza Sample Test 0
scan_file("p4test1.txt", "Sample Test 1")

# Piazza Sample Test 0
scan_file("p4test2.txt", "Sample Test 2")

# Piazza Sample Test 1
# scan_file("p4test3.txt", "Sample Test 3")
