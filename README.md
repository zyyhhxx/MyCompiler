# MyCompiler
A compiler for a custom language

## How to build and run this project
1. Install python3, llc and gcc
2. Install rply: `pip3 install rply`
3. Run main.py

## Custom Language
**UPPERCASE WORDS are terminals**

"+" etc are also some simple terminals, usually operators.  
lower-case-words are non-terminals.  
This grammar uses the EBNF notation:  
| -- means alternative.  
( ) -- means grouping.  
? after an item  means it is optional.  
\+ after an item  means "one or more of".  
\* means "zero or more of".  

### Terminals  
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

### Grammar

start symbol: input  
input = ( statement | decl | defn )*  

decl = ARRAY ID LBRAK expr DOTDOT expr RBRAK ( ID "=" expr )? SEMI  
| LOCAL ID ("=" expr)? SEMI  
| GLOBAL ID ("=" expr)? SEMI  

def = DEFUN ID LPAR ID ( COMMA ID )* RPAR body END DEFUN  

body = ( statement | decl )*  

statement = lhs "=" expr SEMI  
          | lhs "<->" lhs SEMI  
	  | WHILE bool-expr  DO statement* END WHILE  
	  | IF bool-expr THEN statement*  
	    (ELSIF bool-expr THEN statement*)*  
	    (ELSE statement*)? END IF  
	  | FOREACH ID IN (range | array-id) DO statement* END FOR  
	  | RETURN expr SEMI  
	  | PRINT expr SEMI  
	  
array-id = ID  

range = expr DOTDOT expr  

bool-expr = expr bool-op expr  

bool-op = "<" | ">" | "==" | "!=" | "<=" | ">="  

lhs =  lhs-item ( COMMA lhs-item )*  

lhs-item =  
    | ID  
    | ID DOT INT  
    | ID LBRAK expr RBRAK  
    
expr =  
    | expr COMMA expr  
    | expr ( "+" | "-" ) expr  
    | expr ( "\*" | "/" ) expr  
    | LPAR expr RPAR  
    | ID  
    | ID expr  
    | ID DOT INT  
    | ID LBRAK expr RBRAK  
    | INT
