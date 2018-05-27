# compiler

Goal is to eventually build a compiler for a subset of Pascal.  Compiler is written in python3 in Ubuntu.  The assembly files are written in NASM format.  You must install NASM via e.g. ```sudo apt-get install nasm``` in order for the program to compile the assembly.

### Current Status:

The program currently handles the following grammar:

```
# program ::= program <identifier>; <compound statement>.
# compound statement ::= begin <statement> [; <statement>]* end
# statement ::= writeln(<expression>) | write(<expression>)
# expression ::= <term> [ <addop> <term>]*
# term ::= <factor> [ <multop> <factor>]*
# factor ::== <integer> | <lparen> <expression> <rparen>
# addop = + | -
# multop = * | /
```

In other words, it takes a single ```program``` statement followed by a```begin...end``` block which can have one or more ```writeln()``` statements.  Each ```writeln()``` will display the result of a single mathematical expression with all arguments being integers.  Addition, subtraction, multiplication, and integer division are supported.  Standard order of operations applies, and parentheses can be used.  The unary minus is also supported, so e.g. ```-2 * 2``` will evaluate to -4.  The compiler generates valid x86 assembly, then compiles and links that into an executable.  No C functions are invoked (e.g. printing to stdout uses syscalls, not a call to ```printf()```.)  

Under the covers, the program first creates an Abstract Syntax Tree (AST) from the expression, then generates the assembly code from the AST.  Currently, the AST knows how to generate its own assembly code even though that overloads that class a bit, because it's easier to generate it recursively from within a single function.

### To run it:

Create a pascal file, then run ```python3 compiler.py {your file name}```.  Example: for a file ```test1.pas``` you would call ```python3 compiler.py test1.pas```. 

### Known bugs:

None

### References
While I have read numerous stack overflow and other posts, there are some sources that I wanted to call out.

Jack Crenshaw's Introduction to Compilers, as modified by Pascal Programming for Schools to target the x86 - http://www.pp4s.co.uk/main/tu-trans-comp-jc-01.html

Ruslan Spivak "Let's Build a Simple Interpreter" - https://ruslanspivak.com/lsbasi-part1/

x86_64 Linux Assembly Tutorials by "kupala" - https://www.youtube.com/watch?v=VQAKkuLL31g&list=PLetF-YjXm-sCH6FrTz4AQhfH6INDQvQSn

