# compiler

This program is a compiler for a subset of Pascal.  Compiler is written in python3 in Ubuntu.  The assembly files are written in NASM format.  You must install NASM via e.g. ```sudo apt-get install nasm``` in order for the program to compile the assembly.  The resulting binaries are 64-bit.

The compiler supports the following Pascal language features:
* Signed Real and Integer variables and literals (64-bit)
* String literals
* if - then [- else]
* while - do
* Math operations: addition, subtraction, multiplication, and floating point/integer division
  * When Real and Integer combined in an operation, result is a Real
* Logical operators: equal to, not equal, less than, less than or equal, greater than, greater than or equal
  * both Real and Integer
* Procedures and Functions
  *  Parameters passed by value or by reference
  *  Up to 8 Real parameters by value, up to a combined 6 Integer + by reference parameters
  *  Integers passed in byval to Real parameters get converted to Real
  *  Recursion
* Write() and Writeln() to stdout
* Comments

Originally, I intended to develop the language strictly using Assembly, leveraging an open-source library to handle printing Integers and Reals to stdout vs. rolling my own.  However, doing dynamic memory allocation without malloc() seemed too difficult.  So, for now, I am linking libc for access to malloc() and free().    

    

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
<type> ::= "integer" | "real"   
<procedure and function declaration part> ::= {(<procedure declaration> | <function declaration>) ";"}
<function declaration> ::= <function heading> ";" <procedure or function body>
<procedure declaration> ::= <procedure heading> ";" <procedure or function body>
<function heading> ::= "function" <identifier> [<formal parameter list>] ":" <type>
<procedure heading> ::= "procedure" <identifier> [<formal parameter list>]
<procedure or function body> ::= [<variable declaration part>] <statement part>
<formal parameter list> ::= "(" ["var"] <identifier> ":" <type> {";" ["var"] <identifier> ":" <type>} ")"    /* Fred note - we are only allowing 6 Integer and 8 Real parameters */
<statement part> ::= "begin" <statement sequence> "end"
<compound statement> ::= "begin" <statement sequence> "end"  /* Fred note - statement part == compound statement */
<statement sequence> ::= <statement> {";" <statement>}
<statement> ::= <simple statement> | <structured statement>
<simple statement> ::= <assignment statement> | <write statement>   /* Fred note - print statement not in official BNF */
<assignment statement> ::= <variable identifier> ":=" <simple expression>
<write statement> ::= ("write" | "writeln") "(" <write parameter> {"," <write parameter>} ")"
<write parameter> ::= <simple expression> | <string literal>
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
<real> ::= ["-"]<digit>{digit}["."<digit>{digit}]
<letter> ::= "A" .. "Z" || "a" .. "z"
<digit> ::= "0" .. "9"
<addition operator> ::= "+" | "-"
<multiplication operator> ::= "*" | "/", "DIV"
<relational operator> ::= "=", ">", ">=", "<", "<=", "<>"
```
 
In other words, it takes a single ```program``` statement followed by an optional set of global variable declarations and an optional set of procedure and function declarations.  Then, it handles one```begin...end``` block which can have one or more ```writeln()``` or ```write()``` statements, variable assignments, function invocations, ```while/do``` blocks, or ```if/then/else``` statements.  The valid conditional tests for an ```if``` or ```while``` statement are equality, inequality, greater, greater or equal, less than, and less than or equal.  After the ```then``` and ```else```, or after the ```do```, there may be a single statement or another ```begin...end``` block. Each ```writeln()``` or ```write()``` will display string literals, variables, mathematical expressions.  Addition, subtraction, multiplication, and both floating-point and integer division are supported.  Standard order of operations applies, and parentheses can be used.  The unary minus is also supported, so e.g. ```-2 * 2``` will evaluate to -4.  The compiler generates valid x86-64 assembly, then compiles and links that into an executable.  No C functions are invoked (e.g. printing to stdout uses syscalls, not a call to ```printf()```.)  

The compiler will ignore comments between open and close curly braces ```{``` and ```}```, anywhere in the code.  So ``` 4 + {random comment} 2``` will evaluate to ```6```.

Recursive functions are supported.  See ```test_recursion.pas``` in the test suite for the Fibonacci sequence.  Functions can have local variables, but the main ```begin..end``` for the program cannot.  The main can only reference global variables.

Under the covers, the program first creates an Abstract Syntax Tree (AST) from the expression, then generates the assembly code from the AST.  Currently, the AST knows how to generate its own assembly code even though that overloads that class a bit, because it's easier to generate it recursively from within a single function if it's a member of that class.

All Integers are 64-bit.  All Reals are 64-bit.  If an Integer is passed into a function for a Real parameter it will be converted to Real on the fly.  Similarly, arithmetic between an Integer and a Real will convert to a Real.  Trying to pass a Real into an Integer parameter however will result in a compile error.

### To run it:

Create a pascal file, then run ```python3 compiler.py {your file name}```.  Example: for the included ```helloworld.pas``` you would call ```python3 compiler.py helloworld.pas```.  You can then execute ```./helloworld``` 

### To run the test suite:

Execute ```python3 compiler_test.py```


### Known bugs:

If a function takes a byRef integer and real parameters, and it is invoked from another function (not main) and the real parameter is updated, then the integer paramter value is wiped out.  See: ```compiler_test_files/known_bug1.pas```.  It should display 8 then 5, and actually displays 8 then 0.

Compiler does not provide a good error message when invoking a procedure as a parameter to a procedure or function, instead giving an error that "vartuple is not defined"

Compiler does not error when invoking a function and ignoring the return value (basically treating a function like a procedure call).  This is not valid Pascal.  

## Design limitation:

Many symbols are generated with the word 'fred' plus additional prefix.  It is quite possible to generate a symbol collision and get an unexpected "variable redefined" error if you use lots of variables that begin with 'fred.'  So, don't do that.

### Not yet tested:

Have not tested ByRef parameters with Procedures


### Code Coverage:

Running ```compiler_test.py```, with all debug and error condition code excluded via ```# pragma: no cover```

Code coverage:
    
    asm_funcs.py: 99%
    
    compiler.py: 98%
    
All the code missed is expected
    
Branch coverage:

    asm_funcs.py: 97%
    
    compiler.py: 97%

### References
While I have read numerous stack overflow and other posts, there are some sources that I wanted to call out.

Jack Crenshaw's Introduction to Compilers, as modified by Pascal Programming for Schools to target the x86 - http://www.pp4s.co.uk/main/tu-trans-comp-jc-01.html

Ruslan Spivak "Let's Build a Simple Interpreter" - https://ruslanspivak.com/lsbasi-part1/

I have referenced multiple BNF for Pascal but the one I settled on is here: http://www.fit.vutbr.cz/study/courses/APR/public/ebnf.html - I used this as the starting point and modified it for my grammar.

The nsm64.asm file that I included was found here: https://forum.nasm.us/index.php?topic=2062.0 - the GPL license information is left intact in that file.