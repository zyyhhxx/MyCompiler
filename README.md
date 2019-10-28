# MyCompiler
A compiler for a custom language

# How to build and run this project
1. Install python3
2. Install rply: pip3 install rply
3. Run main.py

# Custom Language
**UPPERCASE WORDS are terminals**

"+" etc are also some simple terminals, usually operators.  
lower-case-words are non-terminals.  
This grammar uses the EBNF notation:  
| -- means alternative.  
( ) -- means grouping.  
? after an item  means it is optional.  
+ after an item  means "one or more of".  
* means "zero or more of".  

# Terminals  
ARRAY: "array"  
ID: identifier  
DOTDOT: ".."  
LBRAK: "["  
RBRAK: "]"  
SEMI: ";"  
TUPLE: "tuple"  
LOCAL: "local"  
GLOBAL: "global"  
DEFUN: "defun"  
LPAR: "("  
RPAR: ")"  
COMMA: ","  
END: "end"  
WHILE: "while"  
DO: "do"  
IF: "if"  
THEN: "then"  
ELSIF: "elsif"  
ELSE: "else"  
FOREACH: "foreach"  
FOR: "for"  
IN: "in"  
DOT: "."  
INT: integer literal  
RETURN: "return"  
PRINT: "print"  

# Grammar

start symbol: input

input = ( statement | decl | defn )*

decl = ARRAY ID LBRAK expr DOTDOT expr RBRAK ( ID "=" expr )? SEMI //XXX
     // XXX no more "tuple declarations", this is gone: | TUPLE ID "=" expr ( COMMA expr)+ SEMI
     | LOCAL ID ("=" expr)? SEMI //XXX init ALSO optional
     | GLOBAL ID ("=" expr)? SEMI //XXX init optional

// function definition; no way to specify types of parameters
def = DEFUN ID LPAR ID ( COMMA ID )* RPAR body END DEFUN

body = ( statement | decl )* // no nested function definitions

statement = lhs "=" expr SEMI  // assignment
          | lhs "<->" lhs SEMI // exchange
	  | WHILE bool-expr  DO statement* END WHILE
	  | IF bool-expr THEN statement*
	    (ELSIF bool-expr THEN statement*)*  // XXX any number of statements allowed
	    (ELSE statement*)? END IF  // XXX any number of statements allowed
	  | FOREACH ID IN (range | array-id) DO statement* END FOR
	  | RETURN expr SEMI
	  | PRINT expr SEMI

array-id = ID 

range = expr DOTDOT expr // XXX

bool-expr = expr bool-op expr 

bool-op = "<" | ">" | "==" | "!=" | "<=" | ">="

// left hand side of an assignment
lhs =  lhs-item ( COMMA lhs-item )*

lhs-item =
    | ID // variable
    | ID DOT INT  // tuple component reference
    | ID LBRAK expr RBRAK // array element reference

expr = // XXX *ascending* order of precedence: from least important to most important
    | expr COMMA expr // tuple constuctor
    | expr ( "+" | "-" ) expr
    | expr ( "*" | "/" ) expr
    // XXX there is no more unary minus!!
    | LPAR expr RPAR
    | ID
    | ID expr // function call, right-associative
    | ID DOT INT // tuple reference
    | ID LBRAK expr RBRAK // array element reference
    // XXX this was missing!
    | INT
