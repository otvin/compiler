# compiler

Goal is to eventually build a compiler for a subset of Pascal.  Compiler is written in python3 in Ubuntu.  The assembly files are written in NASM format.  You must install NASM via e.g. ```sudo apt-get install nasm``` in order for the program to compile the assembly.

### Current Status:

The program currently handles the following grammar (in a pseudo-BNF format):

```
curly braces mean zero or more repetitions
brackets mean zero or one repetition - in other words, an optional construct.
parentheses are used for grouping - exactly one of the items in the group is chosen
vertical bar means a choice of one from many
literal text is included in quotations marks
# indicates what follows on the remainder of the line is a comment

program ::= <program heading> <block> "."
program heading ::= "program" <identifier> ";"
block ::= [<declaration part>] <statement part>
declaration part ::= <variable declaration part>     # Fred note - only handling variables at this point
variable declaration part ::= "var" <variable declaration> ";" {<variable declaration> ";"}
variable declaration ::= <identifier> ":" <type>     # Fred note - only handling one identifier at a time, not a sequence
<type> ::= "integer"                                 # Fred note - only handling integers at this point
<statement part> ::= "begin" <statement sequence> "end"
<statement sequence> ::= <statement> {";" <statement>}
<statement> ::= <simple statement>                   # Fred note - not handling labels or structured statements yet
<simple statement> ::= <assignment statement> | <print statement>   # Fred note - print statement not in official BNF
<assignment statement> ::= <variable identifier> ":=" <expression>
<print statement> ::= ("write" | "writeln") "(" (<expression> | <string literal>) ")"
<expression> ::= <term> { <addition operator> <term> }    # Fred note - official BNF handles minus here, I do it in <integer>
<term> ::= <factor> { <multiplication operator> <factor> }
<factor> ::= <integer> | <variable identifier> | "(" <expression> ")"

<string literal> = "'" {<any character other than apostrophe or quote mark>} "'"
<variable identifier> ::= <identifier>
<identifier> ::= <letter> {<letter> | <digit>}
<integer> ::= ["-"] <digit> {<digit>}
<letter> ::= "A" .. "Z" || "a" .. "z"
<digit> ::= "0" .. "9"
<addition operator> ::= "+" | "-"
<multiplication operator> ::= "*" | "/"

```
 
In other words, it takes a single ```program``` statement followed by an optional set of global variable declarations.  Then, it handles one```begin...end``` block which can have one or more ```writeln()``` or ```write()``` statements or variable assignments.  Each ```writeln()``` or ```write()``` will display the result of either a string literal, or a single mathematical expression with all arguments being integers or integer-typed variables.  Addition, subtraction, multiplication, and integer division are supported.  Standard order of operations applies, and parentheses can be used.  The unary minus is also supported, so e.g. ```-2 * 2``` will evaluate to -4.  The compiler generates valid x86 assembly, then compiles and links that into an executable.  No C functions are invoked (e.g. printing to stdout uses syscalls, not a call to ```printf()```.)  

The compiler will ignore comments between open and close curly braces ```{``` and ```}```, anywhere in the code.  So ``` 4 + {random comment} 2``` will evaluate to ```6```.


Under the covers, the program first creates an Abstract Syntax Tree (AST) from the expression, then generates the assembly code from the AST.  Currently, the AST knows how to generate its own assembly code even though that overloads that class a bit, because it's easier to generate it recursively from within a single function if it's a member of that class.

### To run it:

Create a pascal file, then run ```python3 compiler.py {your file name}```.  Example: for the included ```helloworld.pas``` you would call ```python3 compiler.py helloworld.pas```.  You can then execute ```./helloworld``` 


### Known bugs:

When redirecting the output of executables to a file, string literals will pipe to the file, but integers printed to stdout will not.  This occurs even if both stdout and stderr are redirected to the file.

### References
While I have read numerous stack overflow and other posts, there are some sources that I wanted to call out.

Jack Crenshaw's Introduction to Compilers, as modified by Pascal Programming for Schools to target the x86 - http://www.pp4s.co.uk/main/tu-trans-comp-jc-01.html

Ruslan Spivak "Let's Build a Simple Interpreter" - https://ruslanspivak.com/lsbasi-part1/

x86_64 Linux Assembly Tutorials by "kupala" - https://www.youtube.com/watch?v=VQAKkuLL31g&list=PLetF-YjXm-sCH6FrTz4AQhfH6INDQvQSn

I have referenced multiple BNF for Pascal but the one I settled on is here: http://www.fit.vutbr.cz/study/courses/APR/public/ebnf.html - I used this as the starting point and modified it for my grammar.

