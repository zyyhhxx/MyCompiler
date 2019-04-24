# Author: Yiyang Zeng yz3622
from lexer import Lexer
import os


def scan_file(fname, scanner, test_name):
    print("-----------------------------Running " + test_name +
          "-----------------------------")

    # Read the file
    with open(fname) as f:
        code = f.read()

    # lex the source code
    scanner.input(code)
    token = scanner.next()
    while token:
        print(token)
        token = scanner.next()
    print("I am done")


dir = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
scanner = Lexer()

# Piazza Sample Test 1
scan_file(os.path.join(dir, "p1test1.txt"), scanner, "Piazza Sample Test 1")

# Piazza Sample Test 2
scan_file(os.path.join(dir, "p1test2.txt"), scanner, "Piazza Sample Test 2")

# Piazza Sample Test 3
scan_file(os.path.join(dir, "p1test3.txt"), scanner, "Piazza Sample Test 3")

# Custom Sample Test 1
scan_file(os.path.join(dir, "mytest1.txt"), scanner, "Custom Sample Test 1")

# Custom Sample Test 2
scan_file(os.path.join(dir, "mytest2.txt"), scanner, "Custom Sample Test 2")
