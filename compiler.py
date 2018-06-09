import sys
import asm_funcs

# constants for token types
TOKEN_INT = 0
TOKEN_PLUS = 1
TOKEN_MINUS = 2
TOKEN_MULT = 3
TOKEN_IDIV = 4
TOKEN_LPAREN = 5
TOKEN_RPAREN = 6
TOKEN_SEMICOLON = 7
TOKEN_PERIOD = 8
TOKEN_COLON = 9
TOKEN_COMMA = 10
TOKEN_ASSIGNMENT_OPERATOR = 11
TOKEN_RELOP_EQUALS = 12
TOKEN_RELOP_GREATER = 13
TOKEN_RELOP_LESS = 14
TOKEN_RELOP_GREATEREQ = 15
TOKEN_RELOP_LESSEQ = 16
TOKEN_RELOP_NOTEQ = 17

TOKEN_PROGRAM = 18
TOKEN_BEGIN = 19
TOKEN_END = 20
TOKEN_VAR = 21
TOKEN_PROCFUNC_DECLARATION_PART = 22  # This is not a real token.  I need something ASTs can hold to signify the thing that holds procedures and functions
TOKEN_FUNCTION = 23


TOKEN_WRITELN = 24
TOKEN_WRITE = 25
TOKEN_IF = 26
TOKEN_THEN = 27
TOKEN_ELSE = 28
TOKEN_WHILE = 29
TOKEN_DO = 30

TOKEN_STRING = 31
TOKEN_VARIABLE_IDENTIFIER = 32
TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT = 33
TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION = 34
TOKEN_VARIABLE_TYPE_INTEGER = 35


# hack for pretty printing
DEBUG_TOKENDISPLAY = ['INT', '+', '-', '*', '/', '(', ')', ';', '.', ':', ',', ':=', '=', '>', '<', '>=', '<=', '<>'
					  	'PROGRAM', 'BEGIN', 'END', 'VAR', '{Procedures/Functions}', 'FUNCTION',
					  	'WRITELN', 'WRITE', 'IF', 'THEN', 'ELSE', 'WHILE', 'DO',
					  	'STRING', 'VARIABLE', 'VARIABLE ASSIGNMENT', 'VARIABLE EVALUATION', 'VARIABLE TYPE Integer']


# helper functions
def isSymbol(char):
	if char in ["-", "+", "(", ")", "*", "/", ";", ".", ":", "=", "<", ">", ',']:
		return True
	else:
		return False


# grammar for now - in a pseudo BNF format
# Modified from http://www.fit.vutbr.cz/study/courses/APR/public/ebnf.html
# curly braces mean zero or more repetitions
# brackets mean zero or one repetition - in other words, an optional construct.
# parentheses are used for grouping - exactly one of the items in the group is chosen
# vertical bar means a choice of one from many
# literal text is included in quotation marks

# <program> ::= <program heading> <block> "."
# <program heading> ::= "program" <identifier> ";"
# <block> ::= [<declaration part>] <statement part>
# <declaration part> ::= [<variable declaration part>] [<procedure and function declaration part>]
# <variable declaration part> ::= "var" <variable declaration> ";" {<variable declaration> ";"}
# <variable declaration> ::= <identifier> ":" <type>     /* Fred note - only handling one identifier at a time, not a sequence */
# <type> ::= "integer"                                 /* Fred note - only handling integers at this point */
# <procedure and function declaration part> ::= {<function declaration> ";"}
# <function declaration> ::= <function heading> ";" <function body>
# <function heading> ::= "function" <identifier> [<formal parameter list>] ":" <type>
# <function body> ::= [<variable declaration part>] <statement part>
# <formal parameter list> ::= "(" <identifier> ":" <type> {";" <identifier> ":" <type>} ")"    /* Fred note - we are only allowing 6 parameters max at this time */
# <statement part> ::= "begin" <statement sequence> "end"
# <compound statement> ::= "begin" <statement sequence> "end"  /* Fred note - statement part == compound statement */
# <statement sequence> ::= <statement> {";" <statement>}
# <statement> ::= <simple statement> | <structured statement>
# <simple statement> ::= <assignment statement> | <print statement>   /* Fred note - print statement not in official BNF */
# <assignment statement> ::= <variable identifier> ":=" <simple expression>
# <print statement> ::= ("write" | "writeln") "(" (<simple expression> | <string literal>) ")"
# <structured statement> ::= <compound statement> | <while statement> | <if statement>
# <if statement> ::= "if" <expression> "then" <statement> ["else" <statement>]
# <while statement> ::= "while" <expression> "do" <statement>
# <expression> ::= <simple expression> [<relational operator> <simple expression>]
# <simple expression> ::= <term> { <addition operator> <term> }    /* Fred note - official BNF handles minus here, I do it in <integer> */
# <term> ::= <factor> { <multiplication operator> <factor> }
# <factor> ::= <integer> | <variable identifier> | <function designator> | "(" <simple expression> ")"  /* Fred note - official BNF allows <expression> here */
# <function designator> ::= <function identifier> <actual parameter list>
# <actual parameter list> ::= "(" <simple expression> {"," <simple expression>} ")"

# <string literal> = "'" {<any character other than apostrophe or quote mark>} "'"
# <variable identifier> ::= <identifier>
# <identifier> ::= <letter> {<letter> | <digit>}
# <integer> ::= ["-"] <digit> {<digit>}
# <letter> ::= "A" .. "Z" || "a" .. "z"
# <digit> ::= "0" .. "9"
# <addition operator> ::= "+" | "-"
# <multiplication operator> ::= "*" | "/"
# <relational operator> ::= "=", ">", ">=", "<", "<=", "<>"

class Token:
	def __init__(self, type, value):
		self.type = type
		self.value = value

	def isRelOp(self):
		if self.type in [TOKEN_RELOP_EQUALS, TOKEN_RELOP_GREATER, TOKEN_RELOP_LESS, TOKEN_RELOP_GREATEREQ, TOKEN_RELOP_LESSEQ, TOKEN_RELOP_NOTEQ]:
			return True
		else:
			return False

	def debugprint(self):
		return (DEBUG_TOKENDISPLAY[self.type] + ":" + str(self.value))

class ProcFuncParameter:
	def __init__(self, name, type):
		self.name = name
		self.type = type

class ProcFuncHeading:
	def __init__(self, name):
		self.name = name
		self.parameters = []  # will be a list of ProcFuncParameters
		self.localvariableAST = None
		self.localvariableSymbolTable = None
		self.returnAddress = None  # will be a string with an address offset, typically "QWORD [RBP-8]"
		self.returntype = None  # will be a token type

	def getParameterPos(self, paramName):
		ret = None
		i = 0
		while i < len(self.parameters):
			if self.parameters[i].name == paramName:
				ret = i
				break
			i += 1
		return ret

class AST():
	def __init__(self, token, comment = None):
		self.token = token
		self.comment = comment # will get put on the line emitted in the assembly code if populated.
		self.procFuncHeading = None  # only used for procs and funcs
		self.children = []

	def rpn_print(self):
		for x in self.children:
			x.rpn_print()
		print(self.token.debugprint())

	def find_string_literals(self, assembler):
		if self.token.type == TOKEN_STRING:
			if not (self.token.value in assembler.string_literals):
				assembler.string_literals[self.token.value] = assembler.generate_literal_name('string')
		else:
			for child in self.children:
				child.find_string_literals(assembler)

	def find_variable_declarations(self, assembler):
		if self.token.type == TOKEN_VARIABLE_TYPE_INTEGER:
			if self.token.value in assembler.variable_symbol_table.symbollist():
				raise ValueError ("Variable redefined: " + self.token.value)
			else:
				assembler.variable_symbol_table.insert(self.token.value, asm_funcs.SYMBOL_INTEGER, assembler.generate_variable_name('int'))
		elif self.token.type == TOKEN_FUNCTION:
			if self.procFuncHeading.name in assembler.variable_symbol_table.symbollist():
				raise ValueError("Variable redefined: " + self.procFuncHeading.name)
			else:
				assembler.variable_symbol_table.insert(self.procFuncHeading.name, asm_funcs.SYMBOL_FUNCTION, assembler.generate_variable_name("func"), self.procFuncHeading)
			# eventually - functions will have variable declarations themselves, will need to handle that here.
			# but those will be local - the procFuncHeading object will need its own symbol table.
		else:
			for child in self.children:
				child.find_variable_declarations(assembler)

	def assembleProcsAndFunctions(self, assembler):
		if self.token.type == TOKEN_FUNCTION:
			# first six integer arguments are passed in RDI, RSI, RDX, RCX, R8, and R9 in that order
			# integer return values are passed in RAX
			functionsymbol = assembler.variable_symbol_table.get(self.procFuncHeading.name)
			assembler.emitlabel(functionsymbol.label, "function: " + self.procFuncHeading.name)
			# allocate space for local variables
			# Also - if we referenced a parameter in the function as a parameter to another function,
			# that parameter could get clobbered if we did not copy it to the stack.  Example:
			# function q(r:integer):integer;
			#   begin
			#     q = f(r+2,r-9)
			#   end;
			#
			#   rdi would hold the value of r, but then when we evaluated the "r+2", we would store that value
			#   in rdi to pass it to f.  So when we went to calculate "r-9", we would go to RDI to grab r,
			#   but RDI has r+2.  So, we store all the parameters as local variables.  This is likely
			#   something we could optimize later - only store a parameter as a local variable if it is passed
			#   into another function.

			localvarbytesneeded = 0
			if self.procFuncHeading.returntype.type == TOKEN_VARIABLE_TYPE_INTEGER:
				localvarbytesneeded += 8
				self.procFuncHeading.resultAddress = 'QWORD [RBP-' + str(localvarbytesneeded) + ']'
			else:
				raise ValueError ("Invalid return type for function : " + DEBUG_TOKENDISPLAY[self.procFuncHeading.returntype.type])

			self.procFuncHeading.localvariableSymbolTable = asm_funcs.SymbolTable()
			for i in self.procFuncHeading.parameters:
				if i.type == TOKEN_VARIABLE_TYPE_INTEGER:
					localvarbytesneeded += 8
					self.procFuncHeading.localvariableSymbolTable.insert(i.name, i.type, 'QWORD [RBP-' + str(localvarbytesneeded) + ']')

				else:
					raise ValueError ("Invalid variable type : " + DEBUG_TOKENDISPLAY[i.type])

			if not (self.procFuncHeading.localvariableAST is None):
				for i in self.procFuncHeading.localvariableAST.children:  # localvariables is an AST with each var as a child
					if i.token.type == TOKEN_VARIABLE_TYPE_INTEGER:
						localvarbytesneeded += 8
						self.procFuncHeading.localvariableSymbolTable.insert(i.token.value, i.token.type, '[RBP - ' + str(localvarbytesneeded) + ']')
					else:
						raise ValueError ("Invalid variable type :" + DEBUG_TOKENDISPLAY[i.type])
			if localvarbytesneeded > 0:
				assembler.emitcode("MOV RBP, RSP", "save stack pointer")
				assembler.emitcode("SUB RSP, " + str(localvarbytesneeded), "allocate local variable storage")
				assembler.emitcode('AND RSP, QWORD -16' , '16-byte align stack pointer')
				pos = 0
				for i in self.procFuncHeading.parameters:
					assembler.emitcode("MOV " + self.procFuncHeading.localvariableSymbolTable.get(i.name).label + ', ' + asm_funcs.parameterPositionToRegister(pos), 'param: ' + i.name)
					pos += 1

			self.children[0].assemble(assembler, functionsymbol.procfuncheading)  # the code in the Begin statement will reference the parameters before global variables

			if localvarbytesneeded > 0:
				assembler.emitcode("MOV RSP, RBP", "restore stack pointer")

			# put the result in RAX
			assembler.emitcode("MOV RAX, " + self.procFuncHeading.resultAddress)
			assembler.emitcode("RET")
		else:
			for child in self.children:
				child.assembleProcsAndFunctions(assembler)

	def assemble(self, assembler, procFuncHeadingScope):
		if self.token.type == TOKEN_INT:
			assembler.emitcode("MOV RAX, " + str(self.token.value))
		elif self.token.type == TOKEN_PLUS:
			self.children[0].assemble(assembler, procFuncHeadingScope)
			# RAX now contains value of the first child
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler, procFuncHeadingScope)
			# RAX now contains value of the second child
			assembler.emitcode("POP RCX")
			# RCX now contains value of the first child
			assembler.emitcode("ADD RAX, RCX")
		elif self.token.type == TOKEN_MINUS:
			self.children[0].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("POP RCX")
			assembler.emitcode("SUB RCX, RAX")
			assembler.emitcode("MOV RAX, RCX")  # it might be quicker to sub RAX, RCX and NEG RAX.
		elif self.token.type == TOKEN_MULT:
			self.children[0].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("POP RCX")
			assembler.emitcode("IMUL RAX, RCX")
		elif self.token.type == TOKEN_IDIV:
			self.children[0].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("MOV RCX, RAX")
			assembler.emitcode("POP RAX")
			assembler.emitcode("XOR RDX, RDX")  # RDX is concatenated with RAX to do division
			assembler.emitcode("CQO") #extend RAX into RDX to handle idiv by negative numbers
			assembler.emitcode("IDIV RCX")
		elif self.token.isRelOp():
			if self.token.type == TOKEN_RELOP_EQUALS:
				jumpinstr = "JE"
			elif self.token.type == TOKEN_RELOP_NOTEQ:
				jumpinstr = "JNE"
			elif self.token.type == TOKEN_RELOP_GREATER:
				jumpinstr = "JG"
			elif self.token.type == TOKEN_RELOP_GREATEREQ:
				jumpinstr = "JGE"
			elif self.token.type == TOKEN_RELOP_LESS:
				jumpinstr = "JL"
			elif self.token.type == TOKEN_RELOP_LESSEQ:
				jumpinstr = "JLE"
			else:
				raise ValueError ("Invalid Relational Operator : " + DEBUG_TOKENDISPLAY[self.token.type])

			self.children[0].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("POP RCX")
			assembler.emitcode("CMP RCX, RAX")
			# tried using CMOVE/CMOVNE but NASM didn't like them
			labeltrue = assembler.generate_local_label()
			labeldone = assembler.generate_local_label()
			assembler.emitcode(jumpinstr + " " + labeltrue)
			assembler.emitcode("MOV RAX, 0")
			assembler.emitcode("JMP " + labeldone)
			assembler.emitlabel(labeltrue)
			assembler.emitcode("MOV RAX, -1")
			assembler.emitlabel(labeldone)
		elif self.token.type == TOKEN_IF:
			label = assembler.generate_local_label()
			assembler.emitcomment(self.comment + '...')
			self.children[0].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("CMP RAX, 0")
			assembler.emitcode("JE " + label)
			if len(self.children) == 2:
				# straight if-then
				assembler.emitcomment('... THEN ...')
				self.children[1].assemble(assembler, procFuncHeadingScope)
				assembler.emitlabel(label)
			elif len(self.children) == 3:
				# if-then-else
				assembler.emitcomment('... THEN ...')
				skipelselabel = assembler.generate_local_label()
				self.children[1].assemble(assembler, procFuncHeadingScope)
				assembler.emitcode("JMP " + skipelselabel)
				assembler.emitlabel(label)
				assembler.emitcomment('... ELSE ...')
				self.children[2].assemble(assembler, procFuncHeadingScope)
				assembler.emitlabel(skipelselabel)
			else:
				raise ValueError ("Invalid number of tokens following IF.  Expected 2 or 3, got: " + str(len(self.children)))
		elif self.token.type == TOKEN_WHILE:
			beginwhilelabel = assembler.generate_local_label()
			endwhilelabel = assembler.generate_local_label()
			assembler.emitcomment(self.comment + '...')
			assembler.emitlabel(beginwhilelabel)
			self.children[0].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("CMP RAX, 0")
			assembler.emitcode("JE " + endwhilelabel)
			assembler.emitcomment("... DO ...")
			self.children[1].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("JMP " + beginwhilelabel)
			assembler.emitlabel(endwhilelabel)
		elif self.token.type == TOKEN_WRITELN or self.token.type == TOKEN_WRITE:
			assembler.emitcomment(self.comment)
			for child in self.children:
				if child.token.type == TOKEN_STRING:
					if not (child.token.value in assembler.string_literals):
						raise ValueError ("No literal for string :" + child.token.value)
					else:
						data_name = assembler.string_literals[child.token.value]
						assembler.emitcode("push rax")
						assembler.emitcode("push rdi")
						assembler.emitcode("push rsi")
						assembler.emitcode("push rdx")
						assembler.emitcode("mov rax, 1")
						assembler.emitcode("mov rdi, 1")
						assembler.emitcode("mov rsi, " + data_name)
						assembler.emitcode("mov rdx, " + data_name + "Len")
						assembler.emitcode("syscall")
						assembler.emitcode("pop rdx")
						assembler.emitcode("pop rsi")
						assembler.emitcode("pop rdi")
						assembler.emitcode("pop rax")
				else:
					child.assemble(assembler, procFuncHeadingScope)  # the expression should be in RAX
					assembler.emitcode("push rdi")
					assembler.emitcode("mov rdi, rax") # first parameter of functions should be in RDI
					assembler.emitcode("call prtdec","imported from nsm64")
					assembler.emitcode("pop rdi")
			if self.token.type == TOKEN_WRITELN:
				assembler.emitcode("push rax")
				assembler.emitcode("push rdi")
				assembler.emitcode("push rsi")
				assembler.emitcode("push rdx")
				assembler.emitcode("call _writeCRLF")
				assembler.emitcode("pop rdx")
				assembler.emitcode("pop rsi")
				assembler.emitcode("pop rdi")
				assembler.emitcode("pop rax")
		elif self.token.type == TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT:
			assembler.emitcomment(self.comment)
			found_symbol = False
			if not (procFuncHeadingScope is None):
				parampos = procFuncHeadingScope.getParameterPos(self.token.value)
				if not (parampos is None):
					# TODO - if we have parameter types other than Integer, we need to do more logic here
					found_symbol = True
					self.children[0].assemble(assembler, procFuncHeadingScope)
					assembler.emitcode("MOV " + asm_funcs.parameterPositionToRegister(parampos) + ", RAX")
				else:
					# If this is a local variable in a function/proc we refer to it via the offset from RBP
					if not (procFuncHeadingScope.localvariableSymbolTable is None):
						if procFuncHeadingScope.localvariableSymbolTable.exists(self.token.value):
							found_symbol = True
							self.children[0].assemble(assembler, procFuncHeadingScope)
							assembler.emitcode("MOV " + procFuncHeadingScope.localvariableSymbolTable.get(self.token.value).label + ", RAX")

			if found_symbol == False:
				symbol = assembler.variable_symbol_table.get(self.token.value)
				if symbol.type == asm_funcs.SYMBOL_INTEGER:
					self.children[0].assemble(assembler, procFuncHeadingScope) # RAX has the value
					assembler.emitcode("MOV [" + symbol.label + "], RAX")
				elif symbol.type == asm_funcs.SYMBOL_FUNCTION:
					if procFuncHeadingScope is not None:
						if self.token.value == procFuncHeadingScope.name:
							self.children[0].assemble(assembler, procFuncHeadingScope)  # Sets RAX to the value we return
							assembler.emitcode("MOV " + procFuncHeadingScope.resultAddress + ", RAX")
						else:
							raise ValueError ("Cannot assign to a function inside another function: " + symbol.procfuncheading.name)
					else:
						raise ValueError ("Cannot assign to function outside of function scope: " + symbol.procfuncheading.name)
				else:
					raise ValueError ("Invalid variable type :" + asm_funcs.DEBUG_SYMBOLDISPLAY[symbol.type])
		elif self.token.type == TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION:
			# is this symbol a function parameter or local variable?
			found_symbol = False
			if not (procFuncHeadingScope is None):
				# Even though functions now copy their parameters to the stack, so there is no reason
				# to check parampos, at some point we may optimize the code by only copying parameters
				# to the stack if they are used in function invocations within the current function.
				# So, I am leaving the parampos check in this block.
				if not (procFuncHeadingScope.localvariableSymbolTable is None):
					if procFuncHeadingScope.localvariableSymbolTable.exists(self.token.value):
						found_symbol = True
						assembler.emitcode(
							"MOV RAX, " + procFuncHeadingScope.localvariableSymbolTable.get(self.token.value).label)
				if found_symbol == False:
					parampos = procFuncHeadingScope.getParameterPos(self.token.value)
					if not (parampos is None):
						found_symbol = True
						# TODO - if we take parameter types other than Integer, we need to do more logic here.
						assembler.emitcode("MOV RAX, " + asm_funcs.parameterPositionToRegister(parampos))

			if found_symbol == False:
				symbol = assembler.variable_symbol_table.get(self.token.value)
				if symbol.type == asm_funcs.SYMBOL_INTEGER:
					assembler.emitcode("MOV RAX, [" + symbol.label + "]")
				elif symbol.type == asm_funcs.SYMBOL_FUNCTION:
					# call the function - return value is in RAX
					# current limitation - 6 parameters max - to fix this, we just need to use relative
					# stack pointer address in the local symbol table to store where the others are.
					# the parameters will be the children in the AST
					# push the rdi, rsi, rdx, rcx, r8, and r9 registers onto the stack (or the ones we need)
					# put the parameters into those registers
					# call the function
					# rax has the return
					# pop all the registers back

					assembler.preserve_int_registers_for_func_call(len(symbol.procfuncheading.parameters))

					i = 0
					while i < len(self.children):
						self.children[i].assemble(assembler, procFuncHeadingScope)
						assembler.emitcode("MOV " + asm_funcs.parameterPositionToRegister(i) + ", RAX")
						i += 1
					assembler.emitcode("CALL " + symbol.label, "invoke function " + symbol.procfuncheading.name + '()')
					assembler.restore_int_registers_after_func_call(len(symbol.procfuncheading.parameters))

				else:
					raise ValueError ("Invalid variable type :" + vartuple[0])
		elif self.token.type == TOKEN_FUNCTION:
			pass # function declarations are asseembled earlier
		elif self.token.type == TOKEN_VAR:
			pass  # variable declarations are assembled earlier
		elif self.token.type in [TOKEN_BEGIN, TOKEN_PROCFUNC_DECLARATION_PART, TOKEN_PROGRAM] :
			for child in self.children:
				child.assemble(assembler, procFuncHeadingScope)
		else:
			raise ValueError("Unexpected Token :" + DEBUG_TOKENDISPLAY[self.token.type])


class Tokenizer:
	def __init__(self, text):  # todo - pull from file
		self.curPos = 0
		self.text = text
		self.length = len(text)
		self.line_number = 1
		self.line_position = 1

	def raiseTokenizeError(self, errormsg):
		errstr = "Parse Error: " + errormsg + "\n"
		errstr += "Line: " + str(self.line_number) + ", Position: " + str(self.line_position) + "\n"
		if self.peek() == "":
			errstr += "at EOF"
		else:
			errstr += "Immediately prior to: " + self.peekMulti(10)
		raise ValueError(errstr)


	def peek(self):
		if self.curPos >= self.length:
			return ""
		else:
			return self.text[self.curPos]

	def peekMulti(self, num):
		return self.text[self.curPos:self.curPos+num]

	def peekMatchStringAndSpace(self, str):
		# Looks to see if the next N characters match the string and then the N+1th character is whitespace.
		# Purpose: to see if the next block of code begins with a specific keyword or such.
		l = len(str)
		nextN = self.peekMulti(l+1).lower()
		if nextN[0:l] == str.lower() and nextN[l].isspace():
			return True
		else:
			return False


	def eat(self):
		if self.curPos >= self.length:
			raise ValueError("Length Exceeded")
		else:
			retChar = self.text[self.curPos]
			self.curPos += 1
			self.line_position += 1
			return retChar

	def getIdentifier(self):
		# <identifier> ::= <letter> {<letter> | <digit>}
		if self.peek().isalpha():
			retVal = self.eat()
			while self.peek().isalnum():
				retVal += self.eat()
			return retVal
		else:
			self.raiseTokenizeError("Identifiers must begin with alpha character")

	def getNumber(self):
		# <integer> ::= ["-"] <digit> {<digit>}
		if self.peek().isdigit():  # todo - handle floats
			retval = self.eat()
			while self.peek().isdigit():
				retval += self.eat()
			return int(retval)
		else:
			self.raiseTokenizeError("Numbers must be numeric")

	def getStringLiteral(self):
		# <string literal> = "'" {<any character other than apostrophe or quote mark>} "'"
		if self.peek() != "'":
			self.raiseTokenizeError("Strings must begin with an apostrophe.")
		self.eat()
		ret = ""
		while self.peek() != "'":
			if self.peek() == '"':
				self.raiseTokenizeError("Cannot handle quotes inside strings yet")
			elif self.peek() == "":
				self.raiseTokenizeError("End of input reached inside quoted string")
			ret += self.eat()
		self.eat()
		return ret


	def getSymbol(self):
		if isSymbol(self.peek()):
			return self.eat()
		else:
			self.raiseTokenizeError("Symbol Expected")

	def getNextToken(self, requiredtokentype=None):
		# if the next Token must be of a certain type, passing that type in
		# will lead to validation.

		if self.curPos >= self.length:
			errstr = ""
			if not (requiredtokentype is None):
				errstr = "Expected " + DEBUG_TOKENDISPLAY[requiredtokentype]
			self.raiseTokenizeError("Unexpected end of input. " + errstr)
		else:
			# get rid of comments
			if self.peek() == "{":
				while self.peek() != "}":
					if self.peek() == "\n":
						self.line_number += 1
						self.line_position += 1
					self.eat()
				self.eat() # eat the "}"
				# get rid of any white space that follows comments
				while self.peek().isspace():
					if self.peek() == "\n":
						self.line_number += 1
						self.line_position = 1
					self.eat()

			if self.peek().isalpha():
				ident = self.getIdentifier().lower()
				if ident == "begin":
					ret = Token(TOKEN_BEGIN, None)
				elif ident == "end":
					ret = Token(TOKEN_END, None)
				elif ident == "writeln":
					ret = Token(TOKEN_WRITELN, None)
				elif ident == "write":
					ret = Token(TOKEN_WRITE, None)
				elif ident == "if":
					ret = Token(TOKEN_IF, None)
				elif ident == "then":
					ret = Token(TOKEN_THEN, None)
				elif ident == "else":
					ret = Token(TOKEN_ELSE, None)
				elif ident == "while":
					ret = Token(TOKEN_WHILE, None)
				elif ident == "do":
					ret = Token(TOKEN_DO, None)
				elif ident == "program":
					ret = Token(TOKEN_PROGRAM, None)
				elif ident == "var":
					ret = Token(TOKEN_VAR, None)
				elif ident == "function":
					ret = Token(TOKEN_FUNCTION, None)
				elif ident == "integer":
					ret = Token(TOKEN_VARIABLE_TYPE_INTEGER, None)
				else:  # assume any other identifier is a variable; if inappropriate, it will throw an error later in parsing.
					ret = Token(TOKEN_VARIABLE_IDENTIFIER, ident)
			elif self.peek().isdigit():
				ret = Token(TOKEN_INT, self.getNumber())
			elif self.peek() == "'":
				ret = Token(TOKEN_STRING, self.getStringLiteral())
			elif isSymbol(self.peek()):
				sym = self.getSymbol()
				# multi-character symbols we support will be
				# := >= <= <>
				if (sym in (":", ">", "<") and self.peek() == "=") or (sym == "<" and self.peek() == ">"):
					sym += self.getSymbol()

				if sym == "+":
					ret = Token(TOKEN_PLUS, None)
				elif sym == "-":
					ret = Token(TOKEN_MINUS, None)
				elif sym == "/":
					ret = Token(TOKEN_IDIV, None)
				elif sym == "*":
					ret = Token(TOKEN_MULT, None)
				elif sym == "(":
					ret = Token(TOKEN_LPAREN, None)
				elif sym == ")":
					ret = Token(TOKEN_RPAREN, None)
				elif sym == ";":
					ret = Token(TOKEN_SEMICOLON, None)
				elif sym == ".":
					ret = Token(TOKEN_PERIOD, None)
				elif sym == ":":
					ret = Token(TOKEN_COLON, None)
				elif sym == ",":
					ret = Token(TOKEN_COMMA, None)
				elif sym == ":=":
					ret = Token(TOKEN_ASSIGNMENT_OPERATOR, None)
				elif sym == "=":
					ret = Token(TOKEN_RELOP_EQUALS, None)
				elif sym == "<>":
					ret = Token(TOKEN_RELOP_NOTEQ, None)
				elif sym == ">":
					ret = Token(TOKEN_RELOP_GREATER, None)
				elif sym == ">=":
					ret = Token(TOKEN_RELOP_GREATEREQ, None)
				elif sym == "<":
					ret = Token(TOKEN_RELOP_LESS, None)
				elif sym == "<=":
					ret = Token(TOKEN_RELOP_LESSEQ, None)
				else:
					self.raiseTokenizeError("Unrecognized Token: " + sym)

			while self.peek().isspace():
				if self.peek() == "\n":
					self.line_number += 1
					self.line_position = 1
				self.eat()

			if not (requiredtokentype is None):
				if ret.type != requiredtokentype:
					self.raiseTokenizeError(
						"Expected " + DEBUG_TOKENDISPLAY[requiredtokentype] + ", got " + DEBUG_TOKENDISPLAY[ret.type])

			return ret


class Parser:
	def __init__(self, tokenizer):
		self.tokenizer = tokenizer
		self.AST = None
		self.asssembler = None

	def raiseParseError(self, errormsg):
		errstr = "Parse Error: " + errormsg + "\n"
		errstr += "Line: " + str(self.tokenizer.line_number) + ", Position: " + str(self.tokenizer.line_position) + "\n"
		if self.tokenizer.peek() == "":
			errstr += "at EOF"
		else:
			errstr += "Immediately prior to: " + self.tokenizer.peekMulti(10)
		raise ValueError(errstr)



	def parseFactor(self):
		# <factor> ::= <integer> | <variable identifier> | <function designator> | "(" <simple expression> ")"
		# <integer> ::= ["-"] <digit> {<digit>}
		# <function designator> ::= <function identifier> <actual parameter list>
		# <actual parameter list> ::= "(" <simple expression> {"," <simple expression>} ")"

		if self.tokenizer.peek() == "(":
			# parens do not go in the AST
			lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
			ret = self.parseSimpleExpression()
			rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)
		else:
			factor = self.tokenizer.getNextToken()
			if factor.type == TOKEN_VARIABLE_IDENTIFIER:
				# we are evaluating here
				factor.type = TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION
				ret = AST(factor)

				if self.tokenizer.peek() == "(":
					# this is a function or procedure invocation
					lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
					ret.children.append(self.parseSimpleExpression())
					while self.tokenizer.peek() == ",":
						comma = self.tokenizer.getNextToken(TOKEN_COMMA)
						ret.children.append(self.parseSimpleExpression())
					rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)

			else:
				multby = 1  # will set this negative if it's a negative number
				if factor.type == TOKEN_MINUS:
					multby = -1
					factor = self.tokenizer.getNextToken()
				if factor.type != TOKEN_INT:
					self.raiseParseError("Integer expected - instead got " + DEBUG_TOKENDISPLAY[factor.type])
				factor.value = factor.value * multby
				ret = AST(factor)

		return ret

	def parseTerm(self):
		# <term> ::= <factor> { <multiplication operator> <factor> }
		ret = self.parseFactor()
		while self.tokenizer.peek() in ["*", "/"]:
			multdiv = AST(self.tokenizer.getNextToken())
			multdiv.children.append(ret)
			multdiv.children.append(self.parseFactor())
			ret = multdiv
		return ret

	def parseSimpleExpression(self):
		# <simple expression> ::= <term> { <addition operator> <term> }    # Fred note - official BNF handles minus here, I do it in <integer>
		ret = self.parseTerm()
		while self.tokenizer.peek() in ['+', '-']:
			addsub = AST(self.tokenizer.getNextToken())
			addsub.children.append(ret)
			addsub.children.append(self.parseTerm())
			ret = addsub
		return ret

	def parseExpression(self):
		# <expression> ::= <simple expression> [<relational operator> <simple expression>]
		first_simple_expression = self.parseSimpleExpression()
		if self.tokenizer.peek() in [">", "<", "="]:
			tok = self.tokenizer.getNextToken()
			if not tok.isRelOp():
				raiseParseError("Relational Operator Expected, got: " + DEBUG_TOKENDISPLAY[tok.type])
			ret = AST(tok)
			ret.children.append(first_simple_expression)
			ret.children.append(self.parseSimpleExpression())
		else:
			ret = AST(first_simple_expression)

		return ret

	def parseIfStatement(self):
		# <if statement> ::= "if" <expression> "then" <statement> ["else" <statement>]
		startpos = self.tokenizer.curPos
		ret = AST(self.tokenizer.getNextToken(TOKEN_IF))
		expression = self.parseExpression()
		endpos = self.tokenizer.curPos
		ret.comment = self.tokenizer.text[startpos:endpos]
		ret.children.append(expression)
		tok = self.tokenizer.getNextToken(TOKEN_THEN)
		statement = self.parseStatement()
		ret.children.append(statement)
		if self.tokenizer.peekMatchStringAndSpace("else"):
			tok = self.tokenizer.getNextToken(TOKEN_ELSE)
			elsestatement = self.parseStatement()
			ret.children.append(elsestatement)
		return ret

	def parseWhileStatement(self):
		# <while statement> ::= "while" <expression> "do" <statement>
		startpos = self.tokenizer.curPos
		ret = AST(self.tokenizer.getNextToken(TOKEN_WHILE))
		expression = self.parseExpression()
		endpos = self.tokenizer.curPos
		ret.comment = self.tokenizer.text[startpos:endpos]
		ret.children.append(expression)
		tok = self.tokenizer.getNextToken(TOKEN_DO)
		statement = self.parseStatement()
		ret.children.append(statement)
		return ret

	def parseStatement(self):
		# <statement> ::= <simple statement> | <structured statement>
		# <simple statement> ::= <assignment statement> | <print statement>   # Fred note - print statement not in official BNF
		# <assignment statement> ::= <variable identifier> ":=" <simple expression>
		# <print statement> ::= ("write" | "writeln") "(" (<simple expression> | <string literal>) ")"
		# <structured statement> ::= <compound statement> | <while statement> | <if statement>
		# <if statement> ::= if <expression> then <statement>
		# <while statement> ::= "while" <expression> "do" <statement>

		# if next token is begin then it is a structured => compound statement
		if self.tokenizer.peekMatchStringAndSpace("begin"):
			ret = self.parseCompoundStatement()
		# if next token is if then it is a structured => if statement
		elif self.tokenizer.peekMatchStringAndSpace("if"):
			ret = self.parseIfStatement()
		elif self.tokenizer.peekMatchStringAndSpace("while"):
			ret = self.parseWhileStatement()
		else:
			startpos = self.tokenizer.curPos
			tok = self.tokenizer.getNextToken()

			if tok.type == TOKEN_WRITELN or tok.type == TOKEN_WRITE:
				lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
				if self.tokenizer.peek() == "'":
					tobeprinted = AST(self.tokenizer.getNextToken(TOKEN_STRING))
				else:
					tobeprinted = self.parseSimpleExpression()
				rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)

				ret = AST(tok)
				ret.children.append(tobeprinted)
			elif tok.type == TOKEN_VARIABLE_IDENTIFIER:
				# we are assigning here
				tok.type = TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT
				assignment_operator = self.tokenizer.getNextToken(TOKEN_ASSIGNMENT_OPERATOR)
				ret = AST(tok)
				ret.children.append(self.parseSimpleExpression())
			else:
				self.raiseParseError("Unexpected Statement: " + DEBUG_TOKENDISPLAY[tok.type])
			endpos = self.tokenizer.curPos
			ret.comment = self.tokenizer.text[startpos:endpos]

		return ret

	def parseCompoundStatement(self):
		# <compound statement> ::= "begin" <statement sequence> "end"
		# <statement sequence> ::= <statement> {";" <statement>}
		ret = AST(self.tokenizer.getNextToken(TOKEN_BEGIN))
		statement = self.parseStatement()
		ret.children.append(statement)
		while self.tokenizer.peek() == ";":
			semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)
			statement = self.parseStatement()
			ret.children.append(statement)
		end = self.tokenizer.getNextToken(TOKEN_END)
		return ret

	def parseStatementPart(self):
		# <statement part> ::= "begin" <statement sequence> "end"
		# observation: the "Statement Part" and "Compound Statement" are identical
		return self.parseCompoundStatement()


	def parseVariableDeclarations(self):
		# variable declaration part ::= "var" <variable declaration> ";" {<variable declaration> ";"}
		# variable declaration = <identifier> ":" <type>       # Fred note - only handling one identifier at a time, not a sequence
		# <type> ::= "integer"                                 # Fred note - only handling integers at this point
		ret = AST(self.tokenizer.getNextToken(TOKEN_VAR))
		done = False
		while not done:
			# I do not know how to recognize the end of the variable section without looking ahead
			# to the next section, which is either <procedure and function declaration part> or
			# the <statement part>.  <statement part> starts with "begin".
			# <procedure and function declaration part> starts with "function" now. (procedures allowed later)
			# So, we are done when the next 6 characters are BEGIN plus whitespace.
			# There likely is a better way to do this.
			if self.tokenizer.peekMatchStringAndSpace("begin"):
				done = True
			elif self.tokenizer.peekMatchStringAndSpace("function"):
				done = True
			else:
				ident_token = self.tokenizer.getNextToken(TOKEN_VARIABLE_IDENTIFIER)
				colon_token = self.tokenizer.getNextToken(TOKEN_COLON)
				type_token = self.tokenizer.getNextToken()
				if type_token.type != TOKEN_VARIABLE_TYPE_INTEGER:
					raiseParseError ("Expected variable type, got " + DEBUG_TOKENDISPLAY[type_token.type])
				semi_token = self.tokenizer.getNextToken(TOKEN_SEMICOLON)

				type_token.value = ident_token.value
				ret.children.append(AST(type_token))

		return ret

	def parseFunctionParameter(self):
		# formal parameter list ::= "(" <identifier> ":" <type> {";" <identifier> ":" <type>} ")"    # Fred note - we are only allowing 6 parameters max at this time

		paramname = self.tokenizer.getNextToken(TOKEN_VARIABLE_IDENTIFIER).value
		colon = self.tokenizer.getNextToken(TOKEN_COLON)
		paramtypetoken = self.tokenizer.getNextToken()
		if paramtypetoken.type != TOKEN_VARIABLE_TYPE_INTEGER:
			self.raiseParseError("Expected Integer Function Parameter Type, got " + DEBUG_TOKENDISPLAY[paramtype.type])
		return ProcFuncParameter(paramname, paramtypetoken.type)

	def parseFunctionDeclaration(self):
		# <function declaration> ::= <function heading> ";" <function body>
		# <function heading> ::= "function" <identifier> [<formal parameter list>] ":" <type>
		# <function body> ::= [<variable declaration part>] <statement part>
		# <formal parameter list> ::= "(" <identifier> ":" <type> {";" <identifier> ":" <type>} ")"    # Fred note - we are only allowing 6 parameters max at this time

		functoken = self.tokenizer.getNextToken(TOKEN_FUNCTION)
		funcheading = ProcFuncHeading(self.tokenizer.getIdentifier().lower())


		if self.tokenizer.peek() == "(":
			lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
			funcheading.parameters.append(self.parseFunctionParameter())
			while self.tokenizer.peek() == ";":
				semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)
				funcheading.parameters.append(self.parseFunctionParameter())
			rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)


		colon = self.tokenizer.getNextToken(TOKEN_COLON)
		functype = self.tokenizer.getNextToken()
		if functype.type == TOKEN_VARIABLE_TYPE_INTEGER:
			funcheading.returntype = functype
		else:
			self.raiseParseError("Expected Integer Function Return Type, got " + DEBUG_TOKENDISPLAY(functype.type))
		semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)

		if self.tokenizer.peekMatchStringAndSpace("var"):
			funcheading.localvariableAST = self.parseVariableDeclarations()

		ret = AST(functoken)
		ret.procFuncHeading = funcheading
		ret.children.append(self.parseStatementPart())

		return ret

	def parseProcedureFunctionDeclarationPart(self):
		# procedure and function declaration part ::= {<function declaration> ";"}
		ret = AST(Token(TOKEN_PROCFUNC_DECLARATION_PART, None))  # this is not a real token, it just holds procs and functions
		while self.tokenizer.peekMatchStringAndSpace("function"):
			ret.children.append(self.parseFunctionDeclaration())
			semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)
		return ret


	def parseProgram(self):
		# program ::= <program heading> <block> "."
		# program heading ::= "program" <identifier> ";"
		ret = AST(self.tokenizer.getNextToken(TOKEN_PROGRAM))
		ret.token.value = self.tokenizer.getIdentifier()
		semi = self.tokenizer.getNextToken(TOKEN_SEMICOLON)

		# block ::= [<declaration part>] <statement part>
		# declaration part ::= [<variable declaration part>] [<function declaration part]
		if self.tokenizer.peekMatchStringAndSpace("var"):
			variable_declarations = self.parseVariableDeclarations()
		else:
			variable_declarations = None

		if self.tokenizer.peekMatchStringAndSpace("function"):
			function_declarations = self.parseProcedureFunctionDeclarationPart()
		else:
			function_declarations = None

		statementPart = self.parseStatementPart()
		period = self.tokenizer.getNextToken(TOKEN_PERIOD)
		if self.tokenizer.peek() != "":
			raiseParseError("Unexpected character after period " + self.tokenizer.peek())

		if not (variable_declarations is None):  # variable declarations are optional
			ret.children.append(variable_declarations)

		if not (function_declarations is None):  # function declarations are optional
			ret.children.append(function_declarations)

		ret.children.append(statementPart)

		return ret

	def parse(self):
		self.AST = self.parseProgram()

	def assembleAST(self):
		self.AST.assemble(self.assembler, None)  # None = Global Scope

	def assemble(self, filename):
		self.assembler = asm_funcs.Assembler(filename)
		self.AST.find_string_literals(self.assembler)
		self.AST.find_variable_declarations(self.assembler)

		self.assembler.setup_bss()
		self.assembler.setup_data()
		self.assembler.setup_text()

		self.AST.assembleProcsAndFunctions(self.assembler)

		self.assembler.setup_start()
		self.assembleAST()

		self.assembler.emit_terminate()
		self.assembler.emit_systemfunctions()
		self.assembler.cleanup()


def main():
	if len(sys.argv) < 2:
		print("Usage: python3 compiler.py [filename]")
		sys.exit()

	infilename = sys.argv[1]
	if infilename[-4:].lower() == ".pas":
		assemblyfilename = infilename[:-4] + ".asm"
		objectfilename = infilename[:-4] + ".o"
		exefilename = infilename[:-4]
	else:
		assemblyfilename = infilename + ".asm"
		objectfilename = infilename + ".o"
		exefilename = infilename + ".exe"


	f = open(infilename,"r")
	t = Tokenizer(f.read())
	f.close()

	print (t.text)

	p = Parser(t)

	print("Parsing...")
	p.parse()
	print("Done.\nAssembling...")
	p.assemble(assemblyfilename)
	print("Done.\nCompiling...")
	c = asm_funcs.Compiler(assemblyfilename, objectfilename)
	c.do_compile()
	print("Done.\nLinking...")
	l = asm_funcs.Linker(objectfilename, exefilename)
	l.do_link()
	print("Done.\n")


if __name__ == '__main__':
	main()
