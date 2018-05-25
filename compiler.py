import asm_funcs

# constants for token types
TOKEN_INT = 0
TOKEN_PLUS = 1
TOKEN_MINUS = 2
TOKEN_MULT = 3
TOKEN_IDIV = 4
TOKEN_LPAREN = 5
TOKEN_RPAREN = 6
TOKEN_WRITELN = 7
TOKEN_BEGIN = 8
TOKEN_END = 9
TOKEN_SEMICOLON = 10

# hack for pretty printing
DEBUG_TOKENDISPLAY = ['INT', '+', '-', '*', '/', '(', ')', 'WRITELN', 'BEGIN', 'END', ';']


# helper functions
def isSymbol(char):
	if char in ["-", "+", "(", ")", "*", "/", ";"]:
		return True
	else:
		return False


# grammar for now

# compound statement ::= begin <statement> [; <statement>]*
# statement ::= writeln(<expression>
# expression ::= <term> [ <addop> <term>]*
# term ::= <factor> [ <multop> <factor>]*
# factor ::== <integer> | <lparen> <expression> <rparen>
# addop = + | -
# multop = * | /

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

	def interpret(self):
		if self.token.type == TOKEN_INT:
			return self.token.value
		elif self.token.type == TOKEN_PLUS:
			return self.children[0].interpret() + self.children[1].interpret()
		elif self.token.type == TOKEN_MINUS:
			return self.children[0].interpret() - self.children[1].interpret()
		elif self.token.type == TOKEN_MULT:
			return self.children[0].interpret() * self.children[1].interpret()
		elif self.token.type == TOKEN_IDIV:
			return self.children[0].interpret() // self.children[1].interpret()
		else:
			raise ValueError("Unexpected Token")

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
		elif self.token.type == TOKEN_WRITELN:
			self.children[0].assemble(assembler)  # the expression should be in RAX
			assembler.emitcode("call _writeINT")
			assembler.emitcode("call _writeCRLF")
		elif self.token.type == TOKEN_BEGIN:
			for child in self.children:
				child.assemble(assembler)

		else:
			raise ValueError("Unexpected Token")


class Tokenizer:
	def __init__(self, text):  # todo - pull from file
		self.curPos = 0
		self.text = text
		self.length = len(text)

	def peek(self):
		if self.curPos >= self.length:
			return ""
		else:
			return self.text[self.curPos]

	def eat(self):
		if self.curPos >= self.length:
			raise ValueError("Length Exceeded")
		else:
			retChar = self.text[self.curPos]
			self.curPos += 1
			return retChar

	def getIdentifier(self):
		if self.peek().isalpha():
			retVal = self.eat()
			while self.peek().isalnum():
				retVal += self.eat()
			return retVal
		else:
			raise ValueError(
				"Identifiers must begin with alpha character")  # todo - error should indicate what was seen

	def getNumber(self):
		if self.peek().isdigit():  # todo - handle floats
			retval = self.eat()
			while self.peek().isdigit():
				retval += self.eat()
			return int(retval)
		else:
			raise ValueError("Numbers must be numeric")

	def getSymbol(self):
		if isSymbol(self.peek()):  # todo - handle multi-character symbols
			return self.eat()
		else:
			raise ValueError("Symbol Expected")

	def getNextToken(self, requiredtokentype=None):
		# if the next Token must be of a certain type, passing that type in
		# will lead to validation.

		if self.curPos > self.length:
			return None
		else:
			if self.peek().isalpha():
				ident = self.getIdentifier().lower()
				if ident == "begin":
					ret = Token(TOKEN_BEGIN, None)
				elif ident == "end":
					ret = Token(TOKEN_END, None)
				elif ident == "writeln":
					ret = Token(TOKEN_WRITELN, None)
				else:
					raise ValueError("Unrecognized Token: " + ident)
			elif self.peek().isdigit():
				ret = Token(TOKEN_INT, self.getNumber())
			elif isSymbol(self.peek()):
				sym = self.getSymbol()
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
				else:
					raise ValueError("Unrecognized Token: " + sym)

			while self.peek().isspace():
				self.eat()

			if not (requiredtokentype is None):
				if ret.type != requiredtokentype:
					raise ValueError(
						"Expected " + DEBUG_TOKENDISPLAY[requiredtokentype] + ", got " + DEBUG_TOKENDISPLAY[ret.type])

			return ret


class Parser:
	def __init__(self, tokenizer):
		self.tokenizer = tokenizer
		self.AST = None
		self.asssembler = None

	def parseFactor(self):
		# factor ::== <0 or 1 minus signs> <integer> | <lparen> <expression> <rparen>
		# just do integer for now
		if self.tokenizer.peek() == "(":
			# parens do not go in the AST
			lparen = self.tokenizer.getNextToken()
			ret = self.parseExpression()
			if self.tokenizer.peek() != ")":
				raise ValueError("Right Paren expected")
			rparen = self.tokenizer.getNextToken()
			return (ret)
		else:
			multby = 1  # will set this negative if it's a negative number
			factor = self.tokenizer.getNextToken()
			if factor.type == TOKEN_MINUS:
				multby = -1
				factor = self.tokenizer.getNextToken()
			if factor.type != TOKEN_INT:
				raise ValueError("Integer expected")
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
		# statement ::= writeln(<expression>)
		writeln = self.tokenizer.getNextToken(TOKEN_WRITELN)
		lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
		expression = self.parseExpression()
		rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)
		ret = AST(writeln)
		ret.children.append(expression)
		return ret

	def parseCompoundStatement(self):
		# compound statement ::= begin <statement> [; <statement>]*
		ret = AST(self.tokenizer.getNextToken(TOKEN_BEGIN))
		statement = self.parseStatement()
		ret.children.append(statement)
		while self.tokenizer.peek() == ";":
			semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)
			statement = self.parseStatement()
			ret.children.append(statement)
		return ret


	def parse(self):
		self.AST = self.parseCompoundStatement()

	def assembleAST(self):
		self.AST.assemble(self.assembler)

	def assemble(self, filename):
		self.assembler = asm_funcs.Assembler(filename)
		self.assembler.setup_bss()
		self.assembler.setup_data()
		self.assembler.setup_text()
		self.assembler.setup_start()

		self.assembleAST()

		self.assembler.emit_terminate()
		self.assembler.emit_systemfunctions()
		self.assembler.cleanup()


def main():
	t = Tokenizer("begin writeln(18+7);writeln(8*(7+1));writeln(45-3);writeln(5-9) end")
	p = Parser(t)

	print("Parsing...")
	p.parse()
	print("Done.\nAssembling...")
	p.assemble("test.asm")
	print("Done.\nCompiling...")
	c = asm_funcs.Compiler("test.asm", "test.o")
	c.do_compile()
	print("Done.\nLinking...")
	l = asm_funcs.Linker("test.o", "test")
	l.do_link()
	print("Done.\n")


if __name__ == '__main__':
	main()
