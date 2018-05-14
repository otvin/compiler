# compiler

Goal is to eventually build a compiler for a subset of Pascal.  Compiler is written in python3 in Ubuntu.  The assembly files are written in NASM format.  You must install NASM via e.g. ```sudo apt-get install nasm``` in order for the program to compile the assembly.

### Current Status:

The program currently generates x86 assembly to compute the result of a single mathematical expression with all arguments being integers.  Addition, subtraction, multiplication, and integer division are supported.  Standard order of operations applies, and parentheses can be used.  The unary minus is also supported, so e.g. ```-2 * 2``` will evaluate to -4.  The generated x86 assembly wthen displays the result of the evaluation of the expression to stdout.  

Under the covers, the program first creates an Abstract Syntax Tree (AST) from the expression, then generates the assembly code from the AST.  Currently, the AST knows how to generate its own assembly code.  I plan to create a new class that will accept an AST and generate the assembly.

### To run it:

Currently the expression is hard-coded into compiler.py.  Edit the ```t=Tokenizer(...)``` line to pass, as a string parameter, the math expression you would like to evaluate.  From command line, run ```python3 compiler.py```.  It will then generate a file named test.asm in your current directory, as well as the object file test.o and an executable named test.  From command line, run ```./test``` and the result of the math expression will be displayed on screen.

### References
While I have read numerous stack overflow and other posts, there are some sources that I wanted to call out.

Jack Crenshaw's Introduction to Compilers, as modified by Pascal Programming for Schools to target the x86 - http://www.pp4s.co.uk/main/tu-trans-comp-jc-01.html

Ruslan Spivak "Let's Build a Simple Interpreter" - https://ruslanspivak.com/lsbasi-part1/

x86_64 Linux Assembly Tutorials by "kupala" - https://www.youtube.com/watch?v=VQAKkuLL31g&list=PLetF-YjXm-sCH6FrTz4AQhfH6INDQvQSn

