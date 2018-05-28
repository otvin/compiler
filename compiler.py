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
TOKEN_ASSIGNMENT_OPERATOR = 10

TOKEN_PROGRAM = 11
TOKEN_BEGIN = 12
TOKEN_END = 13
TOKEN_VAR = 14
TOKEN_WRITELN = 15
TOKEN_WRITE = 16

TOKEN_STRING = 17
TOKEN_VARIABLE_IDENTIFIER = 18
TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT = 19
TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION = 20
TOKEN_VARIABLE_TYPE_INTEGER = 21


# hack for pretty printing
DEBUG_TOKENDISPLAY = ['INT', '+', '-', '*', '/', '(', ')', ';', '.', ':', ':=', 'PROGRAM', 'BEGIN', 'END', 'VAR', 'WRITELN', 'WRITE', 'STRING', 'VARIABLE', 'VARIABLE ASSIGNMENT',
					  	'VARIABLE EVALUATION', 'VARIABLE TYPE Integer']


# helper functions
def isSymbol(char):
	if char in ["-", "+", "(", ")", "*", "/", ";", ".", ":", "="]:
		return True
	else:
		return False


# grammar for now - in a pseudo BNF format

# program ::= program <identifier>; <variable declarations> <compound statement>.
# compound statement ::= begin <statement> [; <statement>]* end
# statement ::= <printstatement> | <variable assignment>
# printstatement ::= [write | writeln]  (<expression> | <stringliteral>)
# expression ::= <term> [ <addop> <term>]*
# term ::= <factor> [ <multop> <factor>]*
# factor ::= <0 or 1 minus signs> <integer> | <variable identifier> | <lparen> <expression> <rparen>
# addop ::= + | -
# multop ::= * | /
# stringliteral ::= '<string>'      ; NOTE - cannot handle " inside a string yet.  Cannot escape apostrophes yet.
# variable declarations ::= <empty> | [var <identifier> : <variable type>;]*
# variable type ::= Integer
# variable assigment ::= <variable identifier> := <expression>

class Token:
	def __init__(self, type, value):
		self.type = type
		self.value = value

	def debugprint(self):
		return (DEBUG_TOKENDISPLAY[self.type] + ":" + str(self.value))


class AST():
	def __init__(self, token):
		self.token = token
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
			if self.token.value in assembler.variable_symbol_table:
				raise ValueError ("Variable redefined: " + self.token.value)
			else:
				assembler.variable_symbol_table[self.token.value] = ("int", assembler.generate_variable_name('int'))  #todo - use a constant instead of "int"
		else:
			for child in self.children:
				child.find_variable_declarations(assembler)

	def assemble(self, assembler):
		if self.token.type == TOKEN_INT:
			assembler.emitcode("MOV RAX, " + str(self.token.value))
		elif self.token.type == TOKEN_PLUS:
			self.children[0].assemble(assembler)
			# RAX now contains value of the first child
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler)
			# RAX now contains value of the second child
			assembler.emitcode("POP RCX")
			# RCX now contains value of the first child
			assembler.emitcode("ADD RAX, RCX")
		elif self.token.type == TOKEN_MINUS:
			self.children[0].assemble(assembler)
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler)
			assembler.emitcode("POP RCX")
			assembler.emitcode("SUB RCX, RAX")
			assembler.emitcode("MOV RAX, RCX")  # it might be quicker to sub RAX, RCX and NEG RAX.
		elif self.token.type == TOKEN_MULT:
			self.children[0].assemble(assembler)
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler)
			assembler.emitcode("POP RCX")
			assembler.emitcode("IMUL RAX, RCX")
		elif self.token.type == TOKEN_IDIV:
			self.children[0].assemble(assembler)
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler)
			assembler.emitcode("MOV RCX, RAX")
			assembler.emitcode("POP RAX")
			assembler.emitcode("XOR RDX, RDX")  # RDX is concatenated with RAX to do division
			assembler.emitcode("IDIV RCX")
		elif self.token.type == TOKEN_WRITELN or self.token.type == TOKEN_WRITE:
			for child in self.children:
				if child.token.type == TOKEN_STRING:
					if not (child.token.value in assembler.string_literals):
						raise ValueError ("No literal for string :" + child.token.value)
					else:
						data_name = assembler.string_literals[child.token.value]
						assembler.emitcode("mov rax, 1")
						assembler.emitcode("mov rdi, 1")
						assembler.emitcode("mov rsi, " + data_name)
						assembler.emitcode("mov rdx, " + data_name + "Len")
						assembler.emitcode("syscall")
				else:
					child.assemble(assembler)  # the expression should be in RAX
					assembler.emitcode("call _writeINT")
			if self.token.type == TOKEN_WRITELN:
				assembler.emitcode("call _writeCRLF")
		elif self.token.type == TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT:
			vartuple = assembler.variable_symbol_table[self.token.value]
			if vartuple[0] == "int": #to-do use a constant instead of "int"
				self.children[0].assemble(assembler) # RAX has the value
				assembler.emitcode("MOV [" + vartuple[1] + "], RAX")
			else:
				raise ValueError ("Invalid variable type :" + vartuple[0])
		elif self.token.type == TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION:
			vartuple = assembler.variable_symbol_table[self.token.value]
			if vartuple[0] == "int":  # to-do use a constant instead of "int"
				assembler.emitcode("MOV RAX, [" + vartuple[1] + "]")
			else:
				raise ValueError ("Invalid variable type :" + vartuple[0])
		elif self.token.type == TOKEN_BEGIN:
			for child in self.children:
				child.assemble(assembler)
		elif self.token.type == TOKEN_VAR:
			pass  # variable declarations are assembled earlier
		elif self.token.type == TOKEN_PROGRAM:
			for child in self.children:
				child.assemble(assembler)
		else:
			raise ValueError("Unexpected Token :" + DEBUG_TOKENDISPLAY[self.token.type])


class Tokenizer:
	def __init__(self, text):  # todo - pull from file
		self.curPos = 0
		self.text = text
		self.length = len(text)
		self.line_number = 1
		self.line_position = 1

	def raiseTokenizeError(selfself, errormsg):
		errstr = "Parse Error: " + errormsg + "\n"
		errstr += "Line: " + str(self.line_number) + ", Position: " + str(self.line_position) + "\n"
		if self.peek() == "":
			errstr += "at EOF"
		else:
			errstr += "Immediately prior to: " + self.peekMulti(10)
		raise ValueError(str)


	def peek(self):
		if self.curPos >= self.length:
			return ""
		else:
			return self.text[self.curPos]

	def peekMulti(self, num):
		return self.text[self.curPos:self.curPos+num]

	def eat(self):
		if self.curPos >= self.length:
			raise ValueError("Length Exceeded")
		else:
			retChar = self.text[self.curPos]
			self.curPos += 1
			self.line_position += 1
			return retChar

	def getIdentifier(self):
		if self.peek().isalpha():
			retVal = self.eat()
			while self.peek().isalnum():
				retVal += self.eat()
			return retVal
		else:
			self.raiseTokenizeError("Identifiers must begin with alpha character")

	def getNumber(self):
		if self.peek().isdigit():  # todo - handle floats
			retval = self.eat()
			while self.peek().isdigit():
				retval += self.eat()
			return int(retval)
		else:
			self.raiseTokenizeError("Numbers must be numeric")

	def getQuotedString(self):
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
				elif ident == "program":
					ret = Token(TOKEN_PROGRAM, None)
				elif ident == "var":
					ret = Token(TOKEN_VAR, None)
				elif ident == "integer":
					ret = Token(TOKEN_VARIABLE_TYPE_INTEGER, None)
				else:  # assume any other identifier is a variable; if inappropriate, it will throw an error later in parsing.
					ret = Token(TOKEN_VARIABLE_IDENTIFIER, ident)
			elif self.peek().isdigit():
				ret = Token(TOKEN_INT, self.getNumber())
			elif self.peek() == "'":
				ret = Token(TOKEN_STRING, self.getQuotedString())
			elif isSymbol(self.peek()):
				sym = self.getSymbol()
				# multi-character symbols we support will be
				# := >= <= <>
				if (sym in (":", ">", "<") and self.peek() == "=") or (sym == "<" and self.peek == ">"):
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
				elif sym == ":=":
					ret = Token(TOKEN_ASSIGNMENT_OPERATOR, None)
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
		# factor ::= <0 or 1 minus signs> <integer> | <variable identifier> | <lparen> <expression> <rparen>
		if self.tokenizer.peek() == "(":
			# parens do not go in the AST
			lparen = self.tokenizer.getNextToken()
			ret = self.parseExpression()
			if self.tokenizer.peek() != ")":
				self.raiseParseError("Right Paren expected")
			rparen = self.tokenizer.getNextToken()
			return (ret)
		else:
			factor = self.tokenizer.getNextToken()
			if factor.type == TOKEN_VARIABLE_IDENTIFIER:
				# we are evaluating here
				factor.type = TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION
			else:
				multby = 1  # will set this negative if it's a negative number
				if factor.type == TOKEN_MINUS:
					multby = -1
					factor = self.tokenizer.getNextToken()
				if factor.type != TOKEN_INT:
					self.raiseParseError("Integer expected - instead got " + DEBUG_TOKENDISPLAY[factor.type])
				factor.value = factor.value * multby


			return AST(factor)

	def parseTerm(self):
		# term ::= <factor> [ <multop> <factor>]*
		ret = self.parseFactor()
		while self.tokenizer.peek() in ["*", "/"]:
			multdiv = AST(self.tokenizer.getNextToken())
			multdiv.children.append(ret)
			multdiv.children.append(self.parseFactor())
			ret = multdiv
		return ret

	def parseExpression(self):
		# expression ::= <term> [ <addop> <term>]*
		ret = self.parseTerm()
		while self.tokenizer.peek() in ['+', '-']:
			addsub = AST(self.tokenizer.getNextToken())
			addsub.children.append(ret)
			addsub.children.append(self.parseTerm())
			ret = addsub
		return ret

	def parseStatement(self):
		# statement ::= <printstatement> | <variable assignment>
		# printstatement ::= [write | writeln]  (<expression> | <stringliteral>)
		# variable assigment ::= <variable identifier> := <expression>

		tok = self.tokenizer.getNextToken()

		if tok.type == TOKEN_WRITELN or tok.type == TOKEN_WRITE:
			lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
			if self.tokenizer.peek() == "'":
				tobeprinted = AST(self.tokenizer.getNextToken(TOKEN_STRING))
			else:
				tobeprinted = self.parseExpression()
			rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)

			ret = AST(tok)
			ret.children.append(tobeprinted)
		elif tok.type == TOKEN_VARIABLE_IDENTIFIER:
			# we are assigning here
			tok.type = TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT
			assignment_operator = self.tokenizer.getNextToken(TOKEN_ASSIGNMENT_OPERATOR)
			ret = AST(tok)
			ret.children.append(self.parseExpression())
		else:
			raiseParseError("Unexpected Statement: " + DEBUG_TOKENDISPLAY[tok.type])

		return ret

	def parseCompoundStatement(self):
		# compound statement ::= begin <statement> [; <statement>]* end
		ret = AST(self.tokenizer.getNextToken(TOKEN_BEGIN))
		statement = self.parseStatement()
		ret.children.append(statement)
		while self.tokenizer.peek() == ";":
			semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)
			statement = self.parseStatement()
			ret.children.append(statement)
		end = self.tokenizer.getNextToken(TOKEN_END)
		return ret

	def parseVariableDeclarations(self):
		# variable declarations = <empty> | [var <identifier> : <variable type>;]*
		# variable type = Integer
		if self.tokenizer.peekMulti(3).lower() == 'var':
			ret = AST(self.tokenizer.getNextToken(TOKEN_VAR))
			done = False
			while not done:
				# we are done when the next 6 characters are BEGIN plus whitespace.
				# there likely is a better way to do this
				nextsix = self.tokenizer.peekMulti(6).lower()
				if nextsix[0:5].lower() == 'begin' and nextsix[5].isspace():
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
		else:
			ret = None

		return ret

	def parseProgram(self):
		# program ::= program <identifier>; <variable declarations> <compound statement>.
		ret = AST(self.tokenizer.getNextToken(TOKEN_PROGRAM))
		ret.token.value = self.tokenizer.getIdentifier()
		semi = self.tokenizer.getNextToken(TOKEN_SEMICOLON)

		variable_declarations = self.parseVariableDeclarations()

		compound_statement = self.parseCompoundStatement()
		period = self.tokenizer.getNextToken(TOKEN_PERIOD)
		if self.tokenizer.peek() != "":
			raiseParseError("Unexpected character after period " + self.tokenizer.peek())

		if not (variable_declarations is None):  # variable declarations are optional
			ret.children.append(variable_declarations)

		ret.children.append(compound_statement)

		return ret

	def parse(self):
		self.AST = self.parseProgram()

	def assembleAST(self):
		self.AST.assemble(self.assembler)

	def assemble(self, filename):
		self.assembler = asm_funcs.Assembler(filename)
		self.AST.find_string_literals(self.assembler)
		self.AST.find_variable_declarations(self.assembler)

		self.assembler.setup_bss()
		self.assembler.setup_data()
		self.assembler.setup_text()
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
