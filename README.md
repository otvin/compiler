# compiler

This program is a compiler for a subset of Pascal.  Compiler is written in python3 in Ubuntu.  The assembly files are written in NASM format.  You must install NASM via e.g. ```sudo apt-get install nasm``` in order for the program to compile the assembly.

### Current Status:

The program currently handles the following grammar (in a pseudo-BNF format):

```
curly braces mean zero or more repetitions
brackets mean zero or one repetition - in other words, an optional construct.
parentheses are used for grouping - exactly one of the items in the group is chosen
vertical bar means a choice of one from many
literal text is included in quotation marks
Text in /* */ is a comment

<program> ::= <program heading> <block> "."
<program heading> ::= "program" <identifier> ";"
<block> ::= [<declaration part>] <statement part>
<declaration part> ::= [<variable declaration part>] [<procedure and function declaration part>]
<variable declaration part> ::= "var" <variable declaration> ";" {<variable declaration> ";"}
<variable declaration> ::= <identifier> ":" <type>     /* Fred note - only handling one identifier at a time, not a sequence */
<type> ::= "integer"                                 /* Fred note - only handling integers at this point */
<procedure and function declaration part> ::= {<function declaration> ";"}
<function declaration> ::= <function heading> ";" <function body>
<function heading> ::= "function" <identifier> [<formal parameter list>] ":" <type>
<function body> ::= [<variable declaration part>] <statement part>
<formal parameter list> ::= "(" <identifier> ":" <type> {";" <identifier> ":" <type>} ")"    /* Fred note - we are only allowing 6 parameters max at this time */
<statement part> ::= "begin" <statement sequence> "end"
<compound statement> ::= "begin" <statement sequence> "end"  /* Fred note - statement part == compound statement */
<statement sequence> ::= <statement> {";" <statement>}
<statement> ::= <simple statement> | <structured statement>
<simple statement> ::= <assignment statement> | <print statement>   /* Fred note - print statement not in official BNF */
<assignment statement> ::= <variable identifier> ":=" <simple expression>
<print statement> ::= ("write" | "writeln") "(" (<simple expression> | <string literal>) ")"
<structured statement> ::= <compound statement> | <while statement> | <if statement>
<if statement> ::= "if" <expression> "then" <statement> ["else" <statement>]
<while statement> ::= "while" <expression> "do" <statement>
<expression> ::= <simple expression> [<relational operator> <simple expression>]
<simple expression> ::= <term> { <addition operator> <term> }    /* Fred note - official BNF handles minus here, I do it in <integer> */
<term> ::= <factor> { <multiplication operator> <factor> }
<factor> ::= <integer> | <variable identifier> | <function designator> | "(" <simple expression> ")"  /* Fred note - official BNF allows <expression> here */
<function designator> ::= <function identifier> <actual parameter list>
<actual parameter list> ::= "(" <simple expression> {"," <simple expression>} ")"

<string literal> = "'" {<any character>} "'"  # note - apostrophes in string literals have to be escaped by using two apostrophes
<variable identifier> ::= <identifier>
<identifier> ::= <letter> {<letter> | <digit>}
<integer> ::= ["-"] <digit> {<digit>}
<letter> ::= "A" .. "Z" || "a" .. "z"
<digit> ::= "0" .. "9"
<addition operator> ::= "+" | "-"
<multiplication operator> ::= "*" | "DIV"
<relational operator> ::= "=", ">", ">=", "<", "<=", "<>"
```
 
In other words, it takes a single ```program``` statement followed by an optional set of global variable declarations and an optional set of function declarations.  Then, it handles one```begin...end``` block which can have one or more ```writeln()``` or ```write()``` statements, variable assignments, function invocations, ```while/do``` blocks, or ```if/then/else``` statements.  The valid conditional tests for an ```if``` or ```while``` statement are equality, inequality, greater, greater or equal, less than, and less than or equal.  After the ```then``` and ```else```, or after the ```do```, there may be a single statement or another ```begin...end``` block. Each ```writeln()``` or ```write()``` will display the result of either a string literal, or a single mathematical expression with all arguments being integers or integer-typed variables.  Addition, subtraction, multiplication, and integer division are supported.  Standard order of operations applies, and parentheses can be used.  The unary minus is also supported, so e.g. ```-2 * 2``` will evaluate to -4.  The compiler generates valid x86 assembly, then compiles and links that into an executable.  No C functions are invoked (e.g. printing to stdout uses syscalls, not a call to ```printf()```.)  

The compiler will ignore comments between open and close curly braces ```{``` and ```}```, anywhere in the code.  So ``` 4 + {random comment} 2``` will evaluate to ```6```.

Recursive functions are supported.  See ```test_recursion.pas``` in the test suite for the Fibonacci sequence.  Functions can have local variables, but the main ```begin..end``` for the program cannot.  The main can only reference global variables.

Under the covers, the program first creates an Abstract Syntax Tree (AST) from the expression, then generates the assembly code from the AST.  Currently, the AST knows how to generate its own assembly code even though that overloads that class a bit, because it's easier to generate it recursively from within a single function if it's a member of that class.

All Integers are 64-bit.  All Reals are 64-bit

### To run it:

Create a pascal file, then run ```python3 compiler.py {your file name}```.  Example: for the included ```helloworld.pas``` you would call ```python3 compiler.py helloworld.pas```.  You can then execute ```./helloworld``` 

### To run the test suite:

Execute ```python3 compiler_test.py```


### Known bugs:

When executing a program, both ```write()``` and ```writeln()``` display properly.  When piping the output to a file, if a ```write``` is called on either a string or number, that value will make it to stdout.  However, the next ```write``` or ```writeln``` statement will not, until a ```writeln``` is called.  That will flush something and subsequent strings will make it to the file.  This is truly bizarre.  Thus, the files in the compiler test suite do not exercise ```write```.  Note I have tested to see if ```write()``` is piping to stderr and that is not the case.  I have no clue.


### References
While I have read numerous stack overflow and other posts, there are some sources that I wanted to call out.

Jack Crenshaw's Introduction to Compilers, as modified by Pascal Programming for Schools to target the x86 - http://www.pp4s.co.uk/main/tu-trans-comp-jc-01.html

Ruslan Spivak "Let's Build a Simple Interpreter" - https://ruslanspivak.com/lsbasi-part1/

I have referenced multiple BNF for Pascal but the one I settled on is here: http://www.fit.vutbr.cz/study/courses/APR/public/ebnf.html - I used this as the starting point and modified it for my grammar.

The nasm64.asm file that I included was found here: https://forum.nasm.us/index.php?topic=2062.0 - the GPL license information is left intact in that file.