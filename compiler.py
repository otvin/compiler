import sys
import asm_funcs

TOKENID = 0
VALID_TOKEN_LIST = []
def NEXT_TOKENID():
	global TOKENID
	TOKENID += 1
	return TOKENID
def TokDef(display_string):
	global VALID_TOKEN_LIST
	a = (NEXT_TOKENID(), display_string)
	VALID_TOKEN_LIST.append(a)
	return a

# constants for token types - give each token type unique id and a string to print when debugging.
# we could extend to using namedtuples later if we want to use this for pattern matching
TOKEN_INT = TokDef("INT")
TOKEN_REAL = TokDef("REAL")
TOKEN_STRING = TokDef("STRING")
TOKEN_PLUS = TokDef("+")
TOKEN_MINUS = TokDef("-")
TOKEN_MULT = TokDef("*")
TOKEN_IDIV = TokDef("DIV")
TOKEN_MOD = TokDef("MOD")
TOKEN_DIV = TokDef("/")
TOKEN_LPAREN = TokDef("(")
TOKEN_RPAREN = TokDef(")")
TOKEN_SEMICOLON = TokDef(";")
TOKEN_PERIOD = TokDef(".")
TOKEN_COLON = TokDef(":")
TOKEN_COMMA = TokDef(",")
TOKEN_ASSIGNMENT_OPERATOR = TokDef(":=")
TOKEN_RELOP_EQUALS = TokDef("=")
TOKEN_RELOP_GREATER = TokDef(">")
TOKEN_RELOP_LESS = TokDef("<")
TOKEN_RELOP_GREATEREQ = TokDef(">=")
TOKEN_RELOP_LESSEQ = TokDef("<=")
TOKEN_RELOP_NOTEQ = TokDef("<>")

TOKEN_PROGRAM = TokDef("PROGRAM")
TOKEN_BEGIN = TokDef("BEGIN")
TOKEN_END = TokDef("END")
TOKEN_VAR = TokDef("VAR")
TOKEN_PROCFUNC_DECLARATION_PART = TokDef("{Procedures/Functions}")  # This is not a real token.  I need something ASTs can hold to signify the thing that holds procedures and functions
TOKEN_FUNCTION = TokDef("FUNCTION")
TOKEN_PROCEDURE = TokDef("PROCEDURE")

TOKEN_IF = TokDef("IF")
TOKEN_THEN = TokDef("THEN")
TOKEN_ELSE = TokDef("ELSE")
TOKEN_WHILE = TokDef("WHILE")
TOKEN_DO = TokDef("DO")

TOKEN_WRITELN = TokDef("WRITELN")
TOKEN_WRITE = TokDef("WRITE")
TOKEN_CONCAT = TokDef("CONCAT")


TOKEN_STRING_LITERAL = TokDef("String Literal")
TOKEN_IDENTIFIER = TokDef("Undetermined Identifier")
TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT = TokDef("VARIABLE ASSIGNMENT")
TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION = TokDef("VARIABLE EVALUATION")
TOKEN_VARIABLE_TYPE_INTEGER = TokDef("VARIABLE TYPE: Integer")
TOKEN_VARIABLE_TYPE_REAL = TokDef("VARIABLE TYPE: Real")
TOKEN_VARIABLE_TYPE_STRING = TokDef("VARIABLE TYPE: String")
TOKEN_PROCEDURE_CALL = TokDef("Procedure Call")

TOKEN_NOOP = TokDef("NO-OP")

def DEBUG_TOKENDISPLAY(tokentype): # pragma: no cover
	return tokentype[1]


EXPRESSIONID = 0
VALID_EXPRESSIONTYPE_LIST = []
def NEXT_EXPRESSIONID():
	global EXPRESSIONID
	EXPRESSIONID += 1
	return EXPRESSIONID
def ExpressionDef(display_string):
	global VALID_EXPRESSION_LIST
	a = (NEXT_EXPRESSIONID(), display_string)
	VALID_EXPRESSIONTYPE_LIST.append(a)
	return a

EXPRESSIONTYPE_NONE = ExpressionDef("")
EXPRESSIONTYPE_INT = ExpressionDef("Expressiontype: Integer")
EXPRESSIONTYPE_REAL = ExpressionDef("Expressiontype: Real")
EXPRESSIONTYPE_STRING = ExpressionDef("Expressiontype: String")

def DEBUG_EXPRESSIONTYPEDISPLAY(expressiontype): # pragma: no cover
	return expressiontype[1]




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
# <variable declaration> ::= <identifier list> ":" <type>
# <identifier list> ::= <identifier> {"," <identifier>}
# <type> ::= "integer" | "real" | "string"
# <procedure and function declaration part> ::= {(<procedure declaration> | <function declaration>) ";"}
# <function declaration> ::= <function heading> ";" <procedure or function body>
# <procedure declaration> ::= <procedure heading> ";" <procedure or function body>
# <function heading> ::= "function" <identifier> [<formal parameter list>] ":" <type>
# <procedure heading> ::= "procedure" <identifier> [<formal parameter list>]
# <procedure or function body> ::= [<variable declaration part>] <statement part>
# <formal parameter list> ::= "(" ["var"] <identifier> ":" <type> {";" ["var"] <identifier> ":" <type>} ")"    /* Fred note - we are only allowing 6 Integer and 8 Real parameters */
# <statement part> ::= "begin" <statement sequence> "end"
# <compound statement> ::= "begin" <statement sequence> "end"  /* Fred note - statement part == compound statement */
# <statement sequence> ::= <statement> | <statement> ';' <statement sequence>
# <statement> ::= <simple statement> | <structured statement> | <empty statement>
# <simple statement> ::= <assignment statement> | <procedure statement>
# <procedure statement> ::= <procedure identifier> [<actual parameter list>]
# <assignment statement> ::= <variable identifier> ":=" <simple expression>
# <structured statement> ::= <compound statement> | <while statement> | <if statement>
# <if statement> ::= "if" <expression> "then" <statement> ["else" <statement>]
# <while statement> ::= "while" <expression> "do" <statement>
# <expression> ::= <simple expression> [<relational operator> <simple expression>]
# <simple expression> ::= <term> { <addition operator> <term> }    /* Fred note - official BNF handles minus here, I do it in <integer> and <real>*/
# <term> ::= <factor> { <multiplication operator> <factor> }
# <factor> ::= <integer> | <real> | <string> | <variable identifier> | <function designator> | "(" <simple expression> ")"  /* Fred note - official BNF allows <expression> here */
# <function designator> ::= <function identifier> [<actual parameter list>]
# <actual parameter list> ::= "(" <simple expression> {"," <simple expression>} ")"

# <string literal> = "'" {<any character>} "'"  # note - apostrophes in string literals have to be escaped by using two apostrophes
# <variable identifier> ::= <identifier>
# <identifier> ::= <letter> {<letter> | <digit>}
# <integer> ::= ["-"] <digit> {<digit>}
# <real> ::= ["-"]<digit>{digit}["."<digit>{digit}]
# <letter> ::= "A" .. "Z" || "a" .. "z"
# <digit> ::= "0" .. "9"
# <addition operator> ::= "+" | "-"
# <multiplication operator> ::= "*" | "/", "DIV", "MOD"
# <relational operator> ::= "=", ">", ">=", "<", "<=", "<>"

# These aren't technically in the BNF.  Write/Writeln are just procedures.  Concat is just a function.  So these
# aren't needed because the BNF covers them, however I wrote them out for my own benefit.
# <write statement> ::= ("write" | "writeln") "(" <write parameter> {"," <write parameter>} ")"
# <write parameter> ::= <simple expression> | <string literal>
# <concat statement> ::= "concat" "(" <string parameter> "," <string parameter> {"," <string parameter>} ")"
# <string parameter> :: <simple expression> | <string literal>  /* simple expression here must be of string type */


class Token:
	def __init__(self, type, value):
		self.type = type
		self.value = value

	@property
	def type(self):
		return self.__type

	@type.setter
	def type(self, t):
		if t in VALID_TOKEN_LIST:
			self.__type = t
		else: # pragma: no cover
			raise ValueError("Invalid Token Type")

	def isRelOp(self):
		if self.type in [TOKEN_RELOP_EQUALS, TOKEN_RELOP_GREATER, TOKEN_RELOP_LESS, TOKEN_RELOP_GREATEREQ, TOKEN_RELOP_LESSEQ, TOKEN_RELOP_NOTEQ]:
			return True
		else:
			return False

	def isReservedFunction(self):
		if self.type == TOKEN_CONCAT:
			return True
		else:
			return False

	def debugprint(self): # pragma: no cover
		ret = DEBUG_TOKENDISPLAY(self.type)
		if not (self.value is None):
			ret += ":" + str(self.value)
		return (ret)

class ProcFuncParameter:
	def __init__(self, name, type, byref):
		self.name = name
		self.type = type  # will be a token variable type e.g. TOKEN_VARIABLE_TYPE_INTEGER
		self.byref = byref # will be a boolean

	@property
	def type(self):
		return self.__type

	@type.setter
	def type(self, t):
		if t in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_STRING, TOKEN_VARIABLE_TYPE_REAL]:
			self.__type = t
		elif type(t) is Token: # pragma: no cover
			raise ValueError("Invalid Parameter Type: " + t.debugprint())
		else: # pragma: no cover
			raise ValueError("Invalid Parameter Type: " + t)

	def isIntegerParameterType(self):
		# Section 3.2.3 of the ABI - defines the types of registers used to pass parameters
		# Note: our implementation of ByVal Strings involves passing a reference and then copying
		# it locally, vs. passing the String on the stack.
		if self.byref or self.type in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_STRING]:
			return True
		else:
			return False

class ProcFuncHeading:
	def __init__(self, name):
		self.name = name
		self.parameters = []  # will be a list of ProcFuncParameters
		self.localvariableAST = None
		self.localvariableSymbolTable = None
		self.returnAddress = None  # will be a string with an address offset, typically "[RBP-8]"
		self.returntype = None  # will be a token variable type e.g. TOKEN_VARIABLE_TYPE_INTEGER

	@property
	def returntype(self):
		return self.__returntype

	@returntype.setter
	def returntype(self, rt):
		if rt is None:
			self.__returntype = None
		elif rt in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_REAL]:
			self.__returntype = rt
		elif type(rt) is Token: # pragma: no cover
			raise ValueError("Invalid Return Type: " + rt.debugprint())
		else: # pragma: no cover
			raise ValueError("Invalid Return Type: " + rt)



	def getParameterPos(self, paramName):
		ret = None
		i = 0
		while i < len(self.parameters):
			if self.parameters[i].name == paramName:
				ret = i
				break
			i += 1
		return ret


	def getRegisterForParameterName(self, paramName):
		ret = None
		intargs = 0
		realargs = 0
		i = 0
		while i < len(self.parameters):
			sp = self.parameters[i]
			if sp.isIntegerParameterType():
				intargs += 1
				if sp.name == paramName:
					ret = asm_funcs.intParameterPositionToRegister(intargs)
					break
			else:
				realargs += 1
				if sp.name == paramName:
					ret = asm_funcs.realParameterPositionToRegister(realargs)
					break
			i += 1
		return ret

	def getIntegerParameterCount(self):
		return self.getParameterCountByType(TOKEN_VARIABLE_TYPE_INTEGER)

	def getRealParameterCount(self):
		return self.getParameterCountByType(TOKEN_VARIABLE_TYPE_REAL)

	def getParameterCountByType(self, type):
		ret = 0
		i = 0
		while i < len(self.parameters):
			if self.parameters[i].type == type:
				ret += 1
			elif self.parameters[i].type != TOKEN_VARIABLE_TYPE_INTEGER and type == TOKEN_VARIABLE_TYPE_INTEGER and self.parameters[i].byref == True:
				# byref parameters count as integer type
				ret += 1
			i += 1
		return ret

	def getParameterByPos(self, pos):
		if pos < 0 or pos >= len(self.parameters): # pragma: no cover
			raise ValueError("Invlalid parameter number: " + str(pos))
		return self.parameters[pos]

class AST():
	def __init__(self, token, comment = None):
		self.token = token
		self.comment = comment # will get put on the line emitted in the assembly code if populated.
		self.procFuncHeading = None  # only used for procs and funcs
		self.expressiontype = EXPRESSIONTYPE_NONE # will be set during static type checking
		self.children = []

	@property
	def expressiontype(self):
		return self.__expressiontype

	@expressiontype.setter
	def expressiontype(self, et):
		if et in VALID_EXPRESSIONTYPE_LIST:
			self.__expressiontype = et
		else: # pragma: no cover
			raise ValueError("Invalid Expressiontype")


	def rpn_print(self, level = 0): # pragma: no cover
		for x in self.children:
			x.rpn_print(level + 1)
		typestr = level * " "
		if self.expressiontype != EXPRESSIONTYPE_NONE:
			typestr += DEBUG_EXPRESSIONTYPEDISPLAY(self.expressiontype) + "|"
		print(typestr + self.token.debugprint())

	def find_literals(self,assembler):
		if self.token.type == TOKEN_STRING_LITERAL:
			if not (self.token.value in assembler.string_literals):
				assembler.string_literals[self.token.value] = assembler.generate_literal_name('string')
		elif self.token.type == TOKEN_REAL:
			if not (self.token.value in assembler.real_literals):
				assembler.real_literals[self.token.value] = assembler.generate_literal_name('real')
		else:
			for child in self.children:
				child.find_literals(assembler)

	def find_main_begin(self):
		if self.token.type == TOKEN_BEGIN and self.token.value == True:
			return self
		else:
			for child in self.children:
				ret = child.find_main_begin()
				if not ret is None:
					if ret.token.type == TOKEN_BEGIN and ret.token.value == True:
						return ret
			return None

	def find_procfunc_concats(self, localvarbytesneeded, procFuncHeading):
		if self.token.type == TOKEN_CONCAT:
			localvarbytesneeded += 8
			# concats do not have brackets around value the way local variables do, because
			# sometimes we use same assemble() code when it is a global var,
			# so we always add the brackets when assembling.
			self.token.value = 'fredconcat' + str(localvarbytesneeded)  # just needs to be unique
			procFuncHeading.localvariableSymbolTable.insert(self.token.value, asm_funcs.SYMBOL_CONCAT, symbol_rbp_offset = (-1 * localvarbytesneeded))
		for child in self.children:
			localvarbytesneeded = child.find_procfunc_concats(localvarbytesneeded, procFuncHeading)

		return localvarbytesneeded


	def find_concats(self, assembler):
		# concat needs stack space allocated for each invocation.  If we add other reserved
		# functions with same requirements, we can rename this method.
		if self.token.type == TOKEN_CONCAT:
			concat_label = assembler.generate_variable_name("concat")
			self.token.value = concat_label
			assembler.variable_symbol_table.insert(concat_label, asm_funcs.SYMBOL_CONCAT, symbol_global_label = concat_label)

		# concat can take the results of a concat as a parameter, so we have to look within the
		# children of the concat as well.  Thus, cannot do an "else" here.
		for child in self.children:
			child.find_concats(assembler)

	def find_global_variable_declarations(self, assembler):
		# local variables are not part of the main AST.  They are attached to the procFuncHeading
		# as the localVariableAST.
		if self.token.type == TOKEN_VARIABLE_TYPE_INTEGER:
			if self.token.value in assembler.variable_symbol_table.symbollist(): # pragma: no cover
				raise ValueError ("Variable redefined: " + self.token.value)
			else:
				assembler.variable_symbol_table.insert(self.token.value, asm_funcs.SYMBOL_INTEGER, symbol_global_label = assembler.generate_variable_name('int'))
		elif self.token.type == TOKEN_VARIABLE_TYPE_REAL:
			if self.token.value in assembler.variable_symbol_table.symbollist(): # pragma: no cover
				raise ValueError ("Variable redefined: " + self.token.value)
			else:
				assembler.variable_symbol_table.insert(self.token.value, asm_funcs.SYMBOL_REAL, symbol_global_label = assembler.generate_variable_name('real'))
		elif self.token.type == TOKEN_VARIABLE_TYPE_STRING:
			if self.token.value in assembler.variable_symbol_table.symbollist(): # pragma: no cover
				raise ValueError ("Variable redefined: " + self.token.value)
			else:
				assembler.variable_symbol_table.insert(self.token.value, asm_funcs.SYMBOL_STRING, symbol_global_label = assembler.generate_variable_name('string'))
		elif self.token.type == TOKEN_FUNCTION:
			if self.procFuncHeading.name in assembler.variable_symbol_table.symbollist(): # pragma: no cover
				raise ValueError("Variable redefined: " + self.procFuncHeading.name)
			else:
				assembler.variable_symbol_table.insert(self.procFuncHeading.name, asm_funcs.SYMBOL_FUNCTION, symbol_global_label = assembler.generate_variable_name("func"), procFuncHeading = self.procFuncHeading)
		elif self.token.type == TOKEN_PROCEDURE:
			if self.procFuncHeading.name in assembler.variable_symbol_table.symbollist():  # pragma: no cover
				raise ValueError("Variable redefined: " + self.procFuncHeading.name)
			else:
				assembler.variable_symbol_table.insert(self.procFuncHeading.name, asm_funcs.SYMBOL_PROCEDURE, symbol_global_label = assembler.generate_variable_name("proc"), procFuncHeading = self.procFuncHeading)
		else:
			for child in self.children:
				child.find_global_variable_declarations(assembler)

	def static_type_check(self, assembler, parentProcFuncHeading = None):
		for child in self.children:
			if not self.procFuncHeading is None:
				child.static_type_check(assembler, self.procFuncHeading)
			else:
				child.static_type_check(assembler, parentProcFuncHeading)

		# Just to save some typing
		etype0 = None
		etype1 = None
		if len(self.children) >= 2:
			etype1 = self.children[1].expressiontype
		if len(self.children) >= 1:
			etype0 = self.children[0].expressiontype

		if self.token.type == TOKEN_INT:
			self.expressiontype = EXPRESSIONTYPE_INT
		elif self.token.type == TOKEN_REAL:
			self.expressiontype = EXPRESSIONTYPE_REAL
		elif self.token.type in [TOKEN_STRING, TOKEN_STRING_LITERAL, TOKEN_CONCAT]:
			self.expressiontype = EXPRESSIONTYPE_STRING
		elif self.token.type == TOKEN_PLUS:
			# validation check
			if etype0 not in [EXPRESSIONTYPE_INT, EXPRESSIONTYPE_REAL, EXPRESSIONTYPE_STRING]:  # pragma: no cover
				raise ValueError("Invalid type for first operand")
			if etype1 not in [EXPRESSIONTYPE_INT, EXPRESSIONTYPE_REAL, EXPRESSIONTYPE_STRING]:  # pragma: no cover
				raise ValueError("Invalid type for second operand")
			if (etype0 == EXPRESSIONTYPE_STRING or etype1 == EXPRESSIONTYPE_STRING) and etype0 != etype1:  # pragma: no cover
				raise ValueError("Cannot mix String and numeric types for this operator")
			if etype0 == EXPRESSIONTYPE_STRING and etype1 == EXPRESSIONTYPE_STRING:
				self.expressiontype = EXPRESSIONTYPE_STRING
			elif etype0 == EXPRESSIONTYPE_INT and etype1 == EXPRESSIONTYPE_INT:
				self.expressiontype = EXPRESSIONTYPE_INT
			else:
				self.expressiontype = EXPRESSIONTYPE_REAL
		elif self.token.type in [TOKEN_MINUS, TOKEN_MULT]:
			# validation check
			if etype0 not in [EXPRESSIONTYPE_INT, EXPRESSIONTYPE_REAL]: # pragma: no cover
				raise ValueError ("Invalid type for first operand")
			if etype1 not in [EXPRESSIONTYPE_INT, EXPRESSIONTYPE_REAL]: # pragma: no cover
				raise ValueError ("Invalid type for second operand")
			if etype0 == EXPRESSIONTYPE_INT and etype1 == EXPRESSIONTYPE_INT:
				self.expressiontype = EXPRESSIONTYPE_INT
			else:
				self.expressiontype = EXPRESSIONTYPE_REAL
		elif self.token.type in [TOKEN_IDIV, TOKEN_MOD]:
			if etype0 != EXPRESSIONTYPE_INT: # pragma: no cover
				raise ValueError ("First operand of DIV or MOD must be an Integer.")
			if etype1 != EXPRESSIONTYPE_INT: # pragma: no cover
				raise ValueError ("Second operand of DIV or MOD must be an Integer.")
			self.expressiontype = EXPRESSIONTYPE_INT
		elif self.token.type == TOKEN_DIV:
			self.expressiontype = EXPRESSIONTYPE_REAL
		elif self.token.type in [TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT, TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION]:
			foundit = False
			if not parentProcFuncHeading is None:
				for param in parentProcFuncHeading.parameters:
					if param.name == self.token.value:
						if param.type == TOKEN_VARIABLE_TYPE_INTEGER:
							self.expressiontype = EXPRESSIONTYPE_INT
							foundit = True
							break
						elif param.type == TOKEN_VARIABLE_TYPE_REAL:
							self.expressiontype = EXPRESSIONTYPE_REAL
							foundit = True
							break
						elif param.type == TOKEN_VARIABLE_TYPE_STRING:
							self.expressiontype = EXPRESSIONTYPE_STRING
							foundit = True
							break
			if not foundit:
				if not parentProcFuncHeading is None:
					if self.token.type == TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT:
						if self.token.value == parentProcFuncHeading.name:
							foundit = True
							if parentProcFuncHeading.returntype == TOKEN_VARIABLE_TYPE_INTEGER:
								self.expressiontype = EXPRESSIONTYPE_INT
								for child in self.children:
									if child.expressiontype == EXPRESSIONTYPE_REAL: # pragma: no cover
										raise ValueError("Cannot assign real value as return type to function " + parentProcFuncHeading.name)
							elif parentProcFuncHeading.returntype == TOKEN_VARIABLE_TYPE_REAL:
								self.expressiontype = EXPRESSIONTYPE_REAL
							elif parentProcFuncHeading.returntype == TOKEN_VARIABLE_TYPE_STRING:
								self.expressiontype = EXPRESSIONTYPE_STRING
							else: # pragma: no cover
								raise ValueError("Invalid return type from function + " + parentProcFuncHeading.name)

			if foundit == False:
				if not parentProcFuncHeading is None:
					# Note - parentProcFuncHeading.localvariableSymbolTable is not yet built when this code is running.
					# So, we need to look at parentProcFuncHeading.localvariableAST to get the information we need.
					if not parentProcFuncHeading.localvariableAST is None:
						for localvar in parentProcFuncHeading.localvariableAST.children:
							if localvar.token.value == self.token.value:
								foundit = True
								if localvar.token.type == TOKEN_VARIABLE_TYPE_INTEGER:
									self.expressiontype = EXPRESSIONTYPE_INT
								elif localvar.token.type == TOKEN_VARIABLE_TYPE_REAL:
									self.expressiontype = EXPRESSIONTYPE_REAL
								elif localvar.token.type == TOKEN_VARIABLE_TYPE_STRING:
									self.expressiontype = EXPRESSIONTYPE_STRING
								break

			if foundit == False:
				myvar = None
				if myvar is None:
					myvar = assembler.variable_symbol_table.get(self.token.value)
				if myvar.type == asm_funcs.SYMBOL_INTEGER:
					self.expressiontype = EXPRESSIONTYPE_INT
				elif myvar.type == asm_funcs.SYMBOL_REAL:
					self.expressiontype = EXPRESSIONTYPE_REAL
				elif myvar.type == asm_funcs.SYMBOL_STRING:
					self.expressiontype = EXPRESSIONTYPE_STRING
				elif myvar.type == asm_funcs.SYMBOL_FUNCTION:
					if myvar.procfuncheading.returntype == TOKEN_VARIABLE_TYPE_INTEGER:
						self.expressiontype = EXPRESSIONTYPE_INT
					elif myvar.procfuncheading.returntype == TOKEN_VARIABLE_TYPE_REAL:
						self.expressiontype = EXPRESSIONTYPE_REAL
					elif myvar.procfuncheading.returntype == TOKEN_VARIABLE_TYPE_STRING:
						self.expressiontype = EXPRESSIONTYPE_STRING
					else: # pragma: no cover
						raise ValueError ("Invalid Expression Type")
		elif self.token.isRelOp():
			if etype0 not in [EXPRESSIONTYPE_INT, EXPRESSIONTYPE_REAL]: # pragma: no cover
				raise ValueError ("Invalid type left of relational op")
			if etype1 not in [EXPRESSIONTYPE_INT, EXPRESSIONTYPE_REAL]: # pragma: no cover
				raise ValueError ("Invalid type right of relational op")
			if etype0 != etype1: # pragma: no cover
				errstr = "Left of " + DEBUG_TOKENDISPLAY(self.token.type) + " type "
				errstr += DEBUG_EXPRESSIONTYPEDISPLAY(etype0)
				errstr += ", right has type " + DEBUG_EXPRESSIONTYPEDISPLAY(etype1)
				raise ValueError (errstr)
			self.expressiontype = etype0

	def assembleProcsAndFunctions(self, assembler):
		if self.token.type in (TOKEN_FUNCTION, TOKEN_PROCEDURE):
			# first six integer arguments are passed in RDI, RSI, RDX, RCX, R8, and R9 in that order
			# first eight real arguments are passed in XMM0..XMM7
			# integer return values are passed in RAX
			# real return values are passed in XMM0

			if self.token.type == TOKEN_FUNCTION:
				s = "function"
			else:
				s = "procedure"

			procfuncsymbol = assembler.variable_symbol_table.get(self.procFuncHeading.name)
			assembler.emitlabel(procfuncsymbol.global_label, s + ": " + self.procFuncHeading.name)

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

			if self.token.type == TOKEN_FUNCTION:
				# We need to allocate space on the stack for the return value, as a given function may
				# set and reset the return value multiple times, invoking other code that may clobber
				# rax/xmm0 in betweeen, and can set it before the function ends.


				if self.procFuncHeading.returntype in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_REAL]:
					localvarbytesneeded += 8
					self.procFuncHeading.resultAddress = '[RBP-' + str(localvarbytesneeded) + ']'
				elif self.procFuncHeading.returntype == TOKEN_VARIABLE_TYPE_STRING:
					# Per ABI - if a type has return class MEMORY, then the caller provides space for the return value and
					# passes this address in RDI as if it were the first argument to the function.  Strings are greater than
					# 4 eightbytes, so have return class MEMORY.
					raise ValueError ("String return types not yet supported")
				else: # pragma: no cover
					raise ValueError ("Unhandled return type for function")

			self.procFuncHeading.localvariableSymbolTable = asm_funcs.SymbolTable()
			for i in self.procFuncHeading.parameters:
				if i.type in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_REAL, TOKEN_VARIABLE_TYPE_STRING]:
					localvarbytesneeded += 8
					if i.type == TOKEN_VARIABLE_TYPE_INTEGER:
						if i.byref:
							symboltype = asm_funcs.SYMBOL_INTEGER_PTR
						else:
							symboltype = asm_funcs.SYMBOL_INTEGER
					elif i.type == TOKEN_VARIABLE_TYPE_REAL:
						if i.byref:
							symboltype = asm_funcs.SYMBOL_REAL_PTR
						else:
							symboltype = asm_funcs.SYMBOL_REAL
					else:
						if i.byref:
							symboltype = asm_funcs.SYMBOL_STRING_PTR
						else:
							symboltype = asm_funcs.SYMBOL_STRING

					self.procFuncHeading.localvariableSymbolTable.insert(i.name, symboltype, symbol_rbp_offset = (-1 * localvarbytesneeded))
					assembler.emitcomment("Parameter: " + i.name + " = [RBP-" + str(localvarbytesneeded) + "]")
				else: # pragma: no cover
					raise ValueError ("Invalid variable type : " + DEBUG_TOKENDISPLAY(i.type))

			if not (self.procFuncHeading.localvariableAST is None):
				for i in self.procFuncHeading.localvariableAST.children:  # localvariables is an AST with each var as a child
					if i.token.type in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_REAL]:
						localvarbytesneeded += 8
						if i.token.type == TOKEN_VARIABLE_TYPE_INTEGER:
							symboltype = asm_funcs.SYMBOL_INTEGER
						else:
							symboltype = asm_funcs.SYMBOL_REAL
					elif i.token.type == TOKEN_VARIABLE_TYPE_STRING:
						localvarbytesneeded += 256
						symboltype = asm_funcs.SYMBOL_STRING

					else: # pragma: no cover
						raise ValueError ("Invalid variable type :" + DEBUG_TOKENDISPLAY(i.token.type))
					self.procFuncHeading.localvariableSymbolTable.insert(i.token.value, symboltype, symbol_rbp_offset = (-1 * localvarbytesneeded))
					assembler.emitcomment("Variable: " + i.token.value + " = [RBP-" + str(localvarbytesneeded) + "]")

			localvarbytesneeded = self.find_procfunc_concats(localvarbytesneeded, self.procFuncHeading)

			if localvarbytesneeded > 0:
				assembler.emitcode("PUSH RBP")  # ABI requires callee to preserve RBP
				assembler.emitcode("MOV RBP, RSP", "save stack pointer")
				assembler.emitcode("SUB RSP, " + str(localvarbytesneeded), "allocate local storage")
				numbyvalstringparameters = 0
				for i in self.procFuncHeading.parameters:
					param_address = self.procFuncHeading.localvariableSymbolTable.get(i.name).as_address()
					register = self.procFuncHeading.getRegisterForParameterName(i.name)
					if i.type == TOKEN_VARIABLE_TYPE_INTEGER or i.byref:
						assembler.emitcode("MOV " + param_address + ', ' + register, 'param: ' + i.name)
					elif i.type == TOKEN_VARIABLE_TYPE_REAL:
						assembler.emitcode("MOVSD " + param_address + ', ' + register, 'param: ' + i.name)
					elif i.type == TOKEN_VARIABLE_TYPE_STRING:
						if not i.byref:
							numbyvalstringparameters += 1
							assembler.emitcode("NEWSTACKSTRING","Allocate stack space for param " + i.name)
							assembler.emitcode("MOV " + param_address + ", rax")

				# setup the concats
				for key in self.procFuncHeading.localvariableSymbolTable.symbollist():
					symbol = self.procFuncHeading.localvariableSymbolTable.get(key)
					if symbol.type == asm_funcs.SYMBOL_CONCAT:
						assembler.emitcode("NEWSTACKSTRING")
						assembler.emitcode("mov " + symbol.as_address() + ", rax")

				assembler.emitcode('AND RSP, QWORD -16', '16-byte align stack pointer')

				if numbyvalstringparameters > 0:
					# copy byval string parameters - need to do this after all the stack space for the proc/func is
					# allocated, else we end up creating a new stack frame in the middle of the stack frame we're
					# trying to create.

					# this is a bit hacky but here is the situation:
					# Normally above we preserve the value of a register into local storage.  For
					# strings that are byval, we do NOT do this, because we were given a pointer and
					# we want to copy the string so we do not edit the original.  The problem: copystring
					# uses RDI and RSI.  So if we have a byval string passed in RDI or RSI then we can step on
					# it by doing something like:
					#	mov rdi, [rbp-16]
					#	mov rsi, rdi  # BUG - this rdi is because the string passed in was in first parameter

					assembler.emitcode("PUSH R12","Cache RDI and RSI")
					assembler.emitcode("PUSH R13")
					assembler.emitcode("MOV R12, RDI")
					assembler.emitcode("MOV R13, RSI")

					for i in self.procFuncHeading.parameters:
						if i.type == TOKEN_VARIABLE_TYPE_STRING:
							if not i.byref:
								param_address = self.procFuncHeading.localvariableSymbolTable.get(i.name).as_address()
								register = self.procFuncHeading.getRegisterForParameterName(i.name)
								if register.lower() == "rdi":
									register = "R12"
								elif register.lower() == "rsi":
									register = "R13"
								assembler.emit_copystring(param_address, register)

					assembler.emitcode("POP R13")
					assembler.emitcode("POP R12")

			self.children[0].assemble(assembler, procfuncsymbol.procfuncheading)  # the code in the Begin statement will reference the parameters before global variables

			if self.token.type == TOKEN_FUNCTION:
				# put the result in correct register
				if self.procFuncHeading.returntype == TOKEN_VARIABLE_TYPE_INTEGER:
					assembler.emitcode("MOV RAX, " + self.procFuncHeading.resultAddress)
				else:
					assembler.emitcode("MOVSD XMM0, " + self.procFuncHeading.resultAddress)

			if localvarbytesneeded > 0:
				assembler.emitcode("MOV RSP, RBP", "restore stack pointer")
				assembler.emitcode("POP RBP")

			assembler.emitcode("RET")
		else:
			for child in self.children:
				child.assembleProcsAndFunctions(assembler)

	def assembleTwoChildrenForMathEvaluation(self, assembler, procFuncHeadingScope):
		# used for math and relational operators
		# for integer operations, the first child is in RAX and the second child is in RCX
		# for floating point operations, the first child is in XMM0 and the second child is in XMM8
		if self.expressiontype == EXPRESSIONTYPE_INT:
			# all children must be ints
			self.children[0].assemble(assembler, procFuncHeadingScope)
			# RAX now contains value of the first child
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler, procFuncHeadingScope)
			# RAX now contains value of the second child
			assembler.emitcode("POP RCX")
		elif self.expressiontype == EXPRESSIONTYPE_REAL:
			# integer children will be in RAX and have to be moved to XMM0
			# real children will already be in XMM0
			self.children[0].assemble(assembler, procFuncHeadingScope)
			if self.children[0].expressiontype == EXPRESSIONTYPE_INT:
				assembler.emitcode("CVTSI2SD XMM0, RAX")
			assembler.emitpushxmmreg("XMM0")
			self.children[1].assemble(assembler, procFuncHeadingScope)
			if self.children[1].expressiontype == EXPRESSIONTYPE_INT:
				assembler.emitcode("CVTSI2SD XMM0, RAX")
			assembler.emitpopxmmreg("XMM8")
		else:  # pragma: no cover
			raise valueError ("Invalid ExpressionType")

	def assembleProcFuncInvocation(self, assembler, procFuncHeadingScope, symbol):
		# procFuncHeadingScope = the scope of the caller
		# symbol = contains the procFuncHeading of the function being called
		#
		# only difference between procedures and functions at invocation is that the function assembly
		# will set up the return values in RAX or XMM0, plus allocate the memory needed if the function
		# returns a Memory type, such as String.
		#
		# current limitation - 6 int + 8 real parameters max - to increase this later, we just need to use relative
		# stack pointer address in the local symbol table to store where the others are.  Note: if a function
		# has a "memory" return type (e.g. String), then the return type consumes one of the registers for int
		# parameters so current limitation would be 5 int parameters in that case.
		#
		# the parameters will be the children in the AST
		# any register (except XMM0) used to pass a parameter gets pushed onto the stack
		# put the parameters into those registers, with special handling for XMM0
		# call the proc/function
		# rax or XMM0 has the return
		# pop all the registers back except XMM0

		assembler.preserve_xmm_registers_for_procfunc_call(symbol.procfuncheading.getRealParameterCount())
		assembler.preserve_int_registers_for_procfunc_call(symbol.procfuncheading.getIntegerParameterCount())

		i = 0
		intparams = 0
		realparams = 0
		while i < len(self.children):

			curparam = symbol.procfuncheading.getParameterByPos(i)
			if curparam.byref:
				# If we are passing into a proc/function a param that itself is not a pointer, then we need
				# to pass its address if it is being passed byref.  A param that is a pointer itself we can just
				# pass the value of the pointer, because that is a reference to the original variable.
				curchild = self.children[i]
				childtoken = curchild.token

				# In general, arguments to procs/functions can be variables, literals, or other functions.  However,
				# when passing a value byref, the only of those three that is acceptable is a variable.
				if childtoken.type != TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION:  # pragma: no cover
					raise ValueError("Variable identifier expected calling " + symbol.procfuncheading.name + '()')

				intparams += 1  # all pointers are ints

				# The assemble() method of the child will place the current value of the variable into RAX/XMM0.
				# So we do not assemble() the child.  Instead, we go through the symbol table itself.  If the child
				# is a pointer itself, that means that it was passed byref into the caller, so the actual value
				# of the child can be passed to the callee.  If the child is not a pointer, then we need to get the
				# effective address of the child (i.e. a pointer to the child) and then pass that into the callee.
				found_symbol = False
				if not (procFuncHeadingScope is None):
					if not (procFuncHeadingScope.localvariableSymbolTable is None):
						if procFuncHeadingScope.localvariableSymbolTable.exists(childtoken.value):
							found_symbol = True
							childsymbol = procFuncHeadingScope.localvariableSymbolTable.get(childtoken.value)
							if childsymbol.isPointer():
								assembler.emitcode("MOV " + asm_funcs.intParameterPositionToRegister(intparams) + "," + childsymbol.as_address())
							else:
								assembler.emitcode("LEA " + asm_funcs.intParameterPositionToRegister(intparams) + "," + childsymbol.as_address())
				if not found_symbol:
					# must be a global variable
					childsymbol = assembler.variable_symbol_table.get(childtoken.value)
					assembler.emitcode("MOV " + asm_funcs.intParameterPositionToRegister(intparams) + "," + childsymbol.as_value())
			else:
				# If we are passing into a proc/function a value that itself is a pointer, then we
				# need to dereference the pointer if it is being passed byval.  The assemble()
				# method does that automatically because it moves the result of the computation
				# into RAX / XMM0

				paramtype = curparam.type
				self.children[i].assemble(assembler, procFuncHeadingScope)
				if paramtype in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_STRING]:
					intparams += 1
					if self.children[i].expressiontype == EXPRESSIONTYPE_REAL:  # pragma: no cover
						raise ValueError("Cannot pass real into integer-typed parameter into " + symbol.procfuncheading.name + '()')
					assembler.emitcode("MOV " + asm_funcs.intParameterPositionToRegister(intparams) + ", RAX")
				elif paramtype == TOKEN_VARIABLE_TYPE_REAL:
					realparams += 1
					if self.children[i].expressiontype == EXPRESSIONTYPE_INT:
						assembler.emitcode("CVTSI2SD XMM0, RAX")
					# If a proc/function takes more than one Real parameter, the first parameter will be overwritten with the value of the last.
					# unless we do this.  Reason: all floating point calculations put their result into XMM0.  First parameter to proc/function
					# gets its value put in XMM0, then when system goes to calculate the second Real parameter, it first stores the
					# value in XMM0 (when it is evaluated) and then pushes it to XMM1 since XMM1 holds the second parameter.
					# Fix is to calculate the first parameter, stash it, then grab it back.
					if realparams == 1:
						# XMM0 contains the value after the self.children[i].assemble() from above
						assembler.emitpushxmmreg("XMM0")
					else:
						assembler.emitcode("MOVSD " + asm_funcs.realParameterPositionToRegister(realparams) + ", XMM0")
				else:  # pragma: no cover
					raise ValueError("Invalid expressiontype")


			i += 1

		if realparams > 0:
			assembler.emitpopxmmreg("XMM0")

		assembler.emitcode("CALL " + symbol.as_value(), "invoke " + symbol.procfuncheading.name + '()')
		assembler.restore_int_registers_after_procfunc_call(symbol.procfuncheading.getIntegerParameterCount())
		assembler.restore_xmm_registers_after_procfunc_call(symbol.procfuncheading.getRealParameterCount())


	def assemble(self, assembler, procFuncHeadingScope):
		if self.token.type == TOKEN_INT:
			assembler.emitcode("MOV RAX, " + str(self.token.value))
		elif self.token.type == TOKEN_REAL:
			assembler.emitcode("MOVSD XMM0, [" + assembler.real_literals[self.token.value] + "]")
		elif self.token.type == TOKEN_STRING_LITERAL:
			data_name = assembler.string_literals[self.token.value]
			assembler.emitcode("mov rax, " + data_name)
		elif self.token.type in [TOKEN_PLUS, TOKEN_MINUS, TOKEN_MULT, TOKEN_DIV]:
			self.assembleTwoChildrenForMathEvaluation(assembler, procFuncHeadingScope)
			if self.expressiontype == EXPRESSIONTYPE_INT:
				if self.token.type == TOKEN_PLUS:
					assembler.emitcode("ADD RAX, RCX")
				elif self.token.type == TOKEN_MINUS:
					assembler.emitcode("SUB RCX, RAX")
					assembler.emitcode("MOV RAX, RCX")  # it might be quicker to sub RAX, RCX and NEG RAX
				elif self.token.type == TOKEN_MULT:
					assembler.emitcode("IMUL RAX, RCX")
				else: # pragma: no cover
					raise ValueError ("Floating point division has integer type - error")
			else:
				if self.token.type == TOKEN_PLUS:
					assembler.emitcode("ADDSD XMM0, XMM8")
				elif self.token.type == TOKEN_MINUS:
					assembler.emitcode("SUBSD XMM8, XMM0")
					assembler.emitcode("MOVSD XMM0, XMM8")
				elif self.token.type == TOKEN_MULT:
					assembler.emitcode("MULSD XMM0, XMM8")
				elif self.token.type == TOKEN_DIV:
					assembler.emitcode("DIVSD XMM8, XMM0")
					assembler.emitcode("MOVSD XMM0, XMM8")

		elif self.token.type in [TOKEN_IDIV, TOKEN_MOD]:
			self.children[0].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("PUSH RAX")
			self.children[1].assemble(assembler, procFuncHeadingScope)
			assembler.emitcode("MOV RCX, RAX")
			assembler.emitcode("POP RAX")
			assembler.emitcode("XOR RDX, RDX")  # RDX is concatenated with RAX to do division
			assembler.emitcode("CQO") #extend RAX into RDX to handle idiv by negative numbers
			assembler.emitcode("IDIV RCX")
			if self.token.type == TOKEN_MOD:
				assembler.emitcode("MOV RAX, RDX") # Remainder of IDIV is in RDX.
		elif self.token.isRelOp():

			self.assembleTwoChildrenForMathEvaluation(assembler, procFuncHeadingScope)

			if self.expressiontype == EXPRESSIONTYPE_INT:
				assembler.emitcode("CMP RCX, RAX")
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
				else: # pragma: no cover
					raise ValueError ("Invalid Relational Operator : " + DEBUG_TOKENDISPLAY(self.token.type))

			elif self.expressiontype == EXPRESSIONTYPE_REAL:
				assembler.emitcode("UCOMISD XMM8, XMM0")
				if self.token.type == TOKEN_RELOP_EQUALS:
					jumpinstr = "JE"
				elif self.token.type == TOKEN_RELOP_NOTEQ:
					jumpinstr = "JNE"
				elif self.token.type == TOKEN_RELOP_GREATER:
					jumpinstr = "JA"
				elif self.token.type == TOKEN_RELOP_GREATEREQ:
					jumpinstr = "JAE"
				elif self.token.type == TOKEN_RELOP_LESS:
					jumpinstr = "JB"
				elif self.token.type == TOKEN_RELOP_LESSEQ:
					jumpinstr = "JBE"
				else: # pragma: no cover
					raise ValueError ("Invalid Relational Operator : " + DEBUG_TOKENDISPLAY(self.token.type))


			labeltrue = assembler.generate_local_label()
			labeldone = assembler.generate_local_label()
			assembler.emitcode(jumpinstr + " " + labeltrue)
			assembler.emitcode("MOV RAX, 0")
			assembler.emitcode("JMP " + labeldone)
			assembler.emitlabel(labeltrue)
			assembler.emitcode("MOV RAX, -1")  # we may need to move to using 1 for True per the x86-64 manuals
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
			else: # pragma: no cover
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
				if child.token.type == TOKEN_STRING_LITERAL:
					if not (child.token.value in assembler.string_literals): # pragma: no cover
						raise ValueError ("No literal for string :" + child.token.value)
					else:
						data_name = assembler.string_literals[child.token.value]
						assembler.emitcode("push rdi")
						assembler.emitcode("mov rdi, " + data_name)
						assembler.emitcode("call printstring", "imported from fredstringfunc")
						assembler.emitcode("pop rdi")
				elif child.expressiontype == EXPRESSIONTYPE_STRING:
					child.assemble(assembler, procFuncHeadingScope)  # the string result should be in RAX
					assembler.emitcode("push rdi")
					assembler.emitcode("mov rdi, rax")
					assembler.emitcode("call printstring", "imported from fredstringfunc")
					assembler.emitcode("pop rdi")
				elif child.expressiontype == EXPRESSIONTYPE_INT:
					child.assemble(assembler, procFuncHeadingScope)  # the expression should be in RAX
					assembler.emitcode("push rdi")
					assembler.emitcode("mov rdi, rax") # first parameter of functions should be in RDI
					assembler.emitcode("call prtdec","imported from nsm64")
					assembler.emitcode("pop rdi")
				elif child.expressiontype == EXPRESSIONTYPE_REAL:
					child.assemble(assembler, procFuncHeadingScope)  # the expression should be in XMM0
					assembler.emitcode("call prtdbl")
				else: # pragma: no cover
					raise ValueError ("Do not know how to write this type.")
			if self.token.type == TOKEN_WRITELN:
				assembler.emitcode("push rdi")
				assembler.emitcode("call newline", "imported from nsm64")
				assembler.emitcode("pop rdi")
		elif self.token.type == TOKEN_CONCAT:
			assembler.emitcomment(self.comment)
			if len(self.children) < 2: # pragma: no cover
				raise ValueError("Concat() requires 2 or more arguments.")
			else:
				if not(procFuncHeadingScope is None):
					# concats are ALWAYS local variables, never parameters, nor are they ever global variables if
					# encountered inside a function/procedure.  So if there is a ProcFuncHeadingScope, then the concat IS
					# a local variable, period, so we do not have to track that we found it and then back out to the global scope
					# in case we did not find it locally and then search for it globally.
					if not(procFuncHeadingScope.localvariableSymbolTable is None):
						address = procFuncHeadingScope.localvariableSymbolTable.get(self.token.value).as_address()
					else: # pragma: no cover
						raise ValueError("Error: Concat not properly found/allocated")
				else:
					address = "[" + self.token.value + "]"

				assembler.emitcode("mov rax, " + address)
				assembler.emitcode("push rax")
				child = self.children[0]
				if child.token.type == TOKEN_STRING_LITERAL:
					assembler.emit_copyliteraltostring("rax", child.token.value)
				else:
					child.assemble(assembler, procFuncHeadingScope)  # rax points to result
					assembler.emitcode("pop r11")  # now r11 conains the temp string
					assembler.emitcode("push r11")  # preserve it
					assembler.emit_copystring("r11", "rax")
				assembler.emitcode("pop rax")
				assembler.emitcode("push rax")

				for child in self.children[1:]:
					# always make sure that at the start of each iteration of the loop, rax
					# contains the address of the temp string
					if child.token.type == TOKEN_STRING_LITERAL:
						assembler.emit_stringconcatliteral("rax", child.token.value)
					else:
						child.assemble(assembler, procFuncHeadingScope)  # rax points to result
						assembler.emitcode("pop r11")  # now r11 conains the temp string
						assembler.emitcode("push r11")  # preserve it
						assembler.emit_stringconcatstring("r11", "rax")
					assembler.emitcode("pop rax")
					assembler.emitcode("push rax")
				assembler.emitcode("pop rax") # now rax has the string that is returned from the Concat
		elif self.token.type == TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT:
			assembler.emitcomment(self.comment)
			found_symbol = False
			if not (procFuncHeadingScope is None):
				# If this is a param or local variable in a function/proc we refer to it via the offset from RBP
				if not (procFuncHeadingScope.localvariableSymbolTable is None):
					if procFuncHeadingScope.localvariableSymbolTable.exists(self.token.value):
						child = self.children[0]
						symbol = procFuncHeadingScope.localvariableSymbolTable.get(self.token.value)
						found_symbol = True

						if symbol.type not in [asm_funcs.SYMBOL_STRING, asm_funcs.SYMBOL_STRING_PTR]:
							child.assemble(assembler, procFuncHeadingScope)

							if not symbol.isPointer():
								if child.expressiontype == EXPRESSIONTYPE_INT:
									assembler.emitcode("MOV " + symbol.as_address() + ", RAX")
								elif child.expressiontype == EXPRESSIONTYPE_REAL:
									assembler.emitcode("MOVSD " + symbol.as_address() + ", XMM0")
								else: # pragma: no cover
									raise ValueError("Invalid expressiontype")
							else:
								if child.expressiontype == EXPRESSIONTYPE_INT:
									assembler.emitcode("MOV R11, " + symbol.as_address())
									assembler.emitcode("MOV [R11], RAX")
								elif child.expressiontype == EXPRESSIONTYPE_REAL:
									assembler.emitcode("MOV R11, " + symbol.as_address())
									assembler.emitcode("MOVDQU [R11], XMM0")
								else: # pragma: no cover
									raise ValueError("Invalid expressiontype")
						else:
							# two options - first, we are assigning from a string literal.
							# second, we are assigning from some other string expression.
							if not symbol.isPointer():
								if child.token.type == TOKEN_STRING_LITERAL:
									assembler.emit_copyliteraltostring(symbol.as_address(), child.token.value)
								else:
									child.assemble(assembler, procFuncHeadingScope) # RAX has the address of the resulting String
									assembler.emit_copystring(symbol.as_address(), "RAX")
							else:
								child.assemble(assembler, procFuncHeadingScope)
								assembler.emitcode("MOV R11, " + symbol.as_address())
								assembler.emit_copystring("[R11]", "RAX")

			if found_symbol == False:
				# Must be a global variable or a function
				symbol = assembler.variable_symbol_table.get(self.token.value)
				if symbol.type == asm_funcs.SYMBOL_INTEGER:
					self.children[0].assemble(assembler, procFuncHeadingScope) # RAX has the value
					assembler.emitcode("MOV " + symbol.as_address() + ", RAX")
				elif symbol.type == asm_funcs.SYMBOL_REAL:
					self.children[0].assemble(assembler, procFuncHeadingScope) # XMM0 has the value
					assembler.emitcode("MOVSD " + symbol.as_address() + ", XMM0")
				elif symbol.type == asm_funcs.SYMBOL_STRING:
					# two options - first, we are assigning from a string literal.
					# second, we are assigning from some other string expression.
					child = self.children[0]
					if child.token.type == TOKEN_STRING_LITERAL:
						assembler.emit_copyliteraltostring(symbol.as_address(), child.token.value)
					else:
						child.assemble(assembler, procFuncHeadingScope)  # Sets RAX pointing to the result
						assembler.emit_copystring(symbol.as_address(), "rax")
				elif symbol.type == asm_funcs.SYMBOL_FUNCTION:
					if procFuncHeadingScope is not None:
						if self.token.value == procFuncHeadingScope.name:
							self.children[0].assemble(assembler, procFuncHeadingScope)  # Sets RAX or XMM0 to the value we return
							if procFuncHeadingScope.returntype == TOKEN_VARIABLE_TYPE_INTEGER:
								assembler.emitcode("MOV " + procFuncHeadingScope.resultAddress + ", RAX")
							else:
								assembler.emitcode("MOVSD " + procFuncHeadingScope.resultAddress + ", XMM0")
						else: # pragma: no cover
							raise ValueError ("Cannot assign to a function inside another function: " + symbol.procfuncheading.name)
					else: # pragma: no cover
						raise ValueError ("Cannot assign to function outside of function scope: " + symbol.procfuncheading.name)
				else: # pragma: no cover
					raise ValueError ("Invalid variable type :" + asm_funcs.DEBUG_SYMBOLDISPLAY(symbol.type))
		elif self.token.type == TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION:
			# is this symbol a function parameter or local variable?
			found_symbol = False
			if not (procFuncHeadingScope is None):
				if not (procFuncHeadingScope.localvariableSymbolTable is None):
					if procFuncHeadingScope.localvariableSymbolTable.exists(self.token.value):
						found_symbol = True
						symbol = procFuncHeadingScope.localvariableSymbolTable.get(self.token.value)
						if symbol.type in [asm_funcs.SYMBOL_INTEGER, asm_funcs.SYMBOL_STRING]:
							assembler.emitcode("MOV RAX, " + symbol.as_address())
						elif symbol.type == asm_funcs.SYMBOL_REAL:
							assembler.emitcode("MOVSD XMM0, " + symbol.as_address())
						elif symbol.type in [asm_funcs.SYMBOL_INTEGER_PTR, asm_funcs.SYMBOL_STRING_PTR]:
							assembler.emitcode("MOV R11, " + symbol.as_address())
							assembler.emitcode("MOV RAX, [R11]")
						elif symbol.type == asm_funcs.SYMBOL_REAL_PTR:
							assembler.emitcode("MOV R11, " + symbol.as_address())
							assembler.emitcode("MOVDQU XMM0, [R11]")
						else: # pragma: no cover
							raise ValueError ("Unhandled Symbol Type")
				if found_symbol == False:
					# Even though functions now copy their parameters to the stack, so there is no reason
					# to check the parameter list, at some point we may optimize the code by only copying parameters
					# to the stack if they are passed byRef or used in function invocations within the current function.
					# So, I am leaving the parameter list check here.
					reg = procFuncHeadingScope.getRegisterForParameterName(self.token.value)
					if not (reg is None):
						found_symbol = True
						paramtype = procFuncHeadingScope.parameters[procFuncHeadingScope.getParameterPos[self.token.value]].type
						if paramtype == TOKEN_VARIABLE_TYPE_INTEGER:
							assembler.emitcode("MOV RAX, " + reg)
						elif paramtype == TOKEN_VARIABLE_TYPE_REAL:
							assembler.emitcode("MOVSD XMM0, " + reg)
						else: # pragma: no cover
							raise ValueError("Invalid Parameter Type")

			if found_symbol == False:
				# Check to see if it is a global variable
				symbol = assembler.variable_symbol_table.get(self.token.value)
				if symbol.type in [asm_funcs.SYMBOL_INTEGER, asm_funcs.SYMBOL_STRING]:
					assembler.emitcode("MOV RAX, " + symbol.as_address())
				elif symbol.type == asm_funcs.SYMBOL_REAL:
					assembler.emitcode("MOVSD XMM0, " + symbol.as_address())
				elif symbol.type == asm_funcs.SYMBOL_FUNCTION:
					# call the function - return value is in RAX or XMM0
					self.assembleProcFuncInvocation(assembler, procFuncHeadingScope, symbol)
				else: # pragma: no cover
					raise ValueError ("Invalid variable type :" + vartuple[0])
		elif self.token.type == TOKEN_PROCEDURE_CALL:
			if not assembler.variable_symbol_table.exists(self.token.value): # pragma: no cover
				raise ValueError("Invalid procedure name: " + self.token.value)
			symbol = assembler.variable_symbol_table.get(self.token.value)
			self.assembleProcFuncInvocation(assembler, procFuncHeadingScope, symbol)
		elif self.token.type in (TOKEN_FUNCTION, TOKEN_PROCEDURE) :
			pass # proc/function declarations are asseembled earlier
		elif self.token.type == TOKEN_VAR:
			pass  # variable declarations are assembled earlier
		elif self.token.type == TOKEN_NOOP:
			pass  # nothing to do for a noop.
		elif self.token.type in [TOKEN_BEGIN, TOKEN_PROCFUNC_DECLARATION_PART, TOKEN_PROGRAM] :
			for child in self.children:
				child.assemble(assembler, procFuncHeadingScope)
		else: # pragma: no cover
			raise ValueError("Unexpected Token :" + DEBUG_TOKENDISPLAY(self.token.type))


class Tokenizer:
	def __init__(self, text):
		self.curPos = 0
		self.text = text
		self.length = len(text)
		self.line_number = 1
		self.line_position = 1

	def raiseTokenizeError(self, errormsg): # pragma: no cover
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
		if self.curPos >= self.length: # pragma: no cover
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
		else: # pragma: no cover
			self.raiseTokenizeError("Identifiers must begin with alpha character")

	def getNumber(self):
		# <integer> ::= ["-"] <digit> {<digit>}
		# <real> ::= ["-"]<digit>{digit}["."<digit>{digit}]
		if self.peek().isdigit():
			retval = self.eat()
			while self.peek().isdigit():
				retval += self.eat()
			if self.peek() == "." and self.peekMulti(2)[1].isdigit():
				retval += self.eat() # eat the period
				while self.peek().isdigit():
					retval += self.eat()
				return float(retval)
			else:
				return int(retval)

		else: # pragma: no cover
			self.raiseTokenizeError("Numbers must be numeric")

	def getStringLiteral(self):
		# <string literal> = "'" {<any character>} "'"  # note - apostrophes in string literals have to be escaped by using two apostrophes
		if self.peek() != "'": # pragma: no cover
			self.raiseTokenizeError("Strings must begin with an apostrophe.")
		self.eat()
		ret = ""
		done = False
		while not done:
			if self.peek() == "'" and self.peekMulti(2) != "''":
				done = True
			elif self.peekMulti(2) == "''":
				ret += "'"
				self.eat() #eat first apostrophe
				self.eat() #eat second apostrophe
			elif self.peek() == "": # pragma: no cover
				self.raiseTokenizeError("End of input reached inside quoted string")
			else:
				ret += self.eat()
		self.eat() # eat closing apostrophe
		return ret


	def getSymbol(self):
		if isSymbol(self.peek()):
			return self.eat()
		else: # pragma: no cover
			self.raiseTokenizeError("Symbol Expected")

	def eatComments(self):
		while self.peek() == "{":
			while self.peek() != "}":
				if self.peek() == "\n":
					self.line_number += 1
					self.line_position += 1
				self.eat()
			self.eat()  # eat the "}"
			# get rid of any white space that follows comments
			while self.peek().isspace():
				if self.peek() == "\n":
					self.line_number += 1
					self.line_position = 1
				self.eat()


	def getNextToken(self, requiredtokentype=None):
		# if the next Token must be of a certain type, passing that type in
		# will lead to validation.

		if self.curPos >= self.length:
			errstr = "" # pragma: no cover
			if not (requiredtokentype is None): # pragma: no cover
				errstr = "Expected " + DEBUG_TOKENDISPLAY(requiredtokentype) # pragma: no cover
			self.raiseTokenizeError("Unexpected end of input. " + errstr) # pragma: no cover
		else:
			if self.peek().isalpha():
				ident = self.getIdentifier().lower()
				if ident == "begin":
					ret = Token(TOKEN_BEGIN, False)  # The value of a "BEGIN" token is True/False whether or not it is "main."
				elif ident == "end":
					ret = Token(TOKEN_END, None)
				elif ident == "writeln":
					ret = Token(TOKEN_WRITELN, None)
				elif ident == "write":
					ret = Token(TOKEN_WRITE, None)
				elif ident == "concat":
					ret = Token(TOKEN_CONCAT, None)
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
				elif ident == "procedure":
					ret = Token(TOKEN_PROCEDURE, None)
				elif ident == "integer":
					ret = Token(TOKEN_VARIABLE_TYPE_INTEGER, None)
				elif ident == "real":
					ret = Token(TOKEN_VARIABLE_TYPE_REAL, None)
				elif ident == "string":
					ret = Token(TOKEN_VARIABLE_TYPE_STRING, None)
				elif ident == "div":
					ret = Token(TOKEN_IDIV, None)
				elif ident == "mod":
					ret = Token(TOKEN_MOD, None)
				else:  # assume any other identifier is a variable; if inappropriate, it will throw an error later in parsing.
					ret = Token(TOKEN_IDENTIFIER, ident)
			elif self.peek().isdigit():
				num = self.getNumber()
				if isinstance(num, int):
					ret = Token(TOKEN_INT, num)
				else:
					ret = Token(TOKEN_REAL, num)
			elif self.peek() == "'":
				ret = Token(TOKEN_STRING_LITERAL, self.getStringLiteral())
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
					ret = Token(TOKEN_DIV, None)
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
				else: # pragma: no cover
					self.raiseTokenizeError("Unrecognized Token: " + sym)
			else:  # pragma: no cover
				self.raiseTokenizeError("Unrecognized Token: " + self.peek())

			while self.peek().isspace():
				if self.peek() == "\n":
					self.line_number += 1
					self.line_position = 1
				self.eat()

			if not (requiredtokentype is None):
				if ret.type != requiredtokentype: # pragma: no cover
					self.raiseTokenizeError("Expected " + DEBUG_TOKENDISPLAY(requiredtokentype) + ", got " + DEBUG_TOKENDISPLAY(ret.type))

			self.eatComments()

			return ret


class Parser:
	def __init__(self, tokenizer):
		self.tokenizer = tokenizer
		self.AST = None
		self.asssembler = None

	def raiseParseError(self, errormsg): # pragma: no cover
		errstr = "Parse Error: " + errormsg + "\n"
		errstr += "Line: " + str(self.tokenizer.line_number) + ", Position: " + str(self.tokenizer.line_position) + "\n"
		if self.tokenizer.peek() == "":
			errstr += "at EOF"
		else:
			errstr += "Immediately prior to: " + self.tokenizer.peekMulti(10)
		raise ValueError(errstr)

	def parseReservedFunction(self, functoken):
		# Concat is a function, so is covered in the <function designator> BNF, however I have it here for my benefit.
		# <concat statement> ::= "concat" "(" <string parameter> "," <string parameter> {"," <string parameter>} ")"
		# <string parameter> :: <string literal> | <variable identifier>
		if functoken.type == TOKEN_CONCAT:
			ret = AST(functoken)
			lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
			# Need to have at least two children
			ret.children.append(self.parseStringParameter())
			comma = self.tokenizer.getNextToken(TOKEN_COMMA)
			done = False
			while not done:
				ret.children.append(self.parseStringParameter())
				if self.tokenizer.peek() == ")":
					done = True
				else:
					comma = self.tokenizer.getNextToken(TOKEN_COMMA)
			rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)
		else: # pragma: no cover
			raise ValueError("Invalid Reserved Function " + DEBUG_TOKENDISPLAY(functoken))
		return ret

	def parseFactor(self):
		# <factor> ::= <integer> | <real> | <string> | <variable identifier> | <function designator> | "(" <simple expression> ")"  /* Fred note - official BNF allows <expression> here */
		# <integer> ::= ["-"] <digit> {<digit>}
		# <real> ::= ["-"]<digit>{digit}["."<digit>{digit}]
		# <function designator> ::= <function identifier> <actual parameter list>
		# <actual parameter list> ::= "(" <simple expression> {"," <simple expression>} ")"


		if self.tokenizer.peek() == "(":
			# parens do not go in the AST
			lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
			ret = self.parseSimpleExpression()
			rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)
		else:
			factor = self.tokenizer.getNextToken()
			if factor.isReservedFunction():
				ret = self.parseReservedFunction(factor)
			elif factor.type == TOKEN_IDENTIFIER:
				# we are evaluating here
				factor.type = TOKEN_VARIABLE_IDENTIFIER_FOR_EVALUATION
				ret = AST(factor)

				if self.tokenizer.peek() == "(":
					# this is a function invocation - but at this point we cannot tell if it is
					# a valid function.  Invalid invocations will error later.
					lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
					ret.children.append(self.parseSimpleExpression())
					while self.tokenizer.peek() == ",":
						comma = self.tokenizer.getNextToken(TOKEN_COMMA)
						ret.children.append(self.parseSimpleExpression())
					rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)

			else:
				if factor.type == TOKEN_MINUS:
					factor = self.tokenizer.getNextToken()
					factor.value = -1 * factor.value
				ret = AST(factor)

				if isinstance(factor.value, int):
					ret.expressiontype = EXPRESSIONTYPE_INT
				elif isinstance(factor.value, float):
					ret.expressiontype = EXPRESSIONTYPE_REAL
				else:
					ret.expressiontype = EXPRESSIONTYPE_STRING

		return ret

	def parseTerm(self):
		# <term> ::= <factor> { <multiplication operator> <factor> }
		ret = self.parseFactor()
		while self.tokenizer.peek() in ["*","/"] or self.tokenizer.peekMatchStringAndSpace("div") or self.tokenizer.peekMatchStringAndSpace("mod"):
			multdiv = AST(self.tokenizer.getNextToken())
			multdiv.children.append(ret)
			nextchild = self.parseFactor()
			multdiv.children.append(nextchild)
			ret = multdiv


		return ret

	def parseSimpleExpression(self):
		# <simple expression> ::= <term> { <addition operator> <term> }    # Fred note - official BNF handles minus here, I do it in <integer>
		ret = self.parseTerm()
		while self.tokenizer.peek() in ['+', '-']:
			addsub = AST(self.tokenizer.getNextToken())
			addsub.children.append(ret)
			nextchild = self.parseTerm()
			addsub.children.append(nextchild)
			ret = addsub
		return ret

	def parseExpression(self):
		# <expression> ::= <simple expression> [<relational operator> <simple expression>]
		first_simple_expression = self.parseSimpleExpression()
		if self.tokenizer.peek() in [">", "<", "="]:
			tok = self.tokenizer.getNextToken()
			if not tok.isRelOp(): # pragma: no cover
				raiseParseError("Relational Operator Expected, got: " + DEBUG_TOKENDISPLAY(tok.type))
			ret = AST(tok)
			next_simple_expression = self.parseSimpleExpression()
			ret.children.append(first_simple_expression)
			ret.children.append(next_simple_expression)
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

	def parseStringParameter(self):
		# <string parameter> :: <simple expression> | <string literal>
		# <string literal> = "'" {<any character>} "'"  # note - apostrophes in string literals have to be escaped by using two apostrophes
		# <variable identifier> ::= <identifier>
		if self.tokenizer.peek() == "'":
			ret = AST(self.tokenizer.getNextToken(TOKEN_STRING_LITERAL))
		else:
			ret = self.parseSimpleExpression()
		return ret

	def parseStatement(self):
		# <statement> ::= <simple statement> | <structured statement> | <empty statement>
		# <simple statement> ::= <assignment statement> | <procedure statement>
		# <assignment statement> ::= <variable identifier> ":=" <simple expression>
		# <procedure statement> ::= <procedure identifier> [<actual parameter list>]
		# <actual parameter list> ::= "(" <simple expression> {"," <simple expression>} ")"
		# <structured statement> ::= <compound statement> | <while statement> | <if statement>
		# <if statement> ::= if <expression> then <statement>
		# <while statement> ::= "while" <expression> "do" <statement>

		# write/writeln are just system-defined procedures, so the BNF above defines them, but I find this helpful
		# <write statement> ::= ("write" | "writeln") "(" <write parameter> {"," <write parameter>} ")"
		# <write parameter> ::= <simple expression> | <string literal>

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
				ret = AST(tok)
				lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
				done = False
				while not done:
					if self.tokenizer.peek() == "'":
						tobeprinted = AST(self.tokenizer.getNextToken(TOKEN_STRING_LITERAL))
					else:
						tobeprinted = self.parseSimpleExpression()
					ret.children.append(tobeprinted)
					if self.tokenizer.peek() == ")":
						done = True
					else:
						comma = self.tokenizer.getNextToken(TOKEN_COMMA)
				rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)
			elif tok.type == TOKEN_IDENTIFIER:
				if self.tokenizer.peekMulti(2) == ":=":
					# we are assigning here
					tok.type = TOKEN_VARIABLE_IDENTIFIER_FOR_ASSIGNMENT
					assignment_operator = self.tokenizer.getNextToken(TOKEN_ASSIGNMENT_OPERATOR)
					ret = AST(tok)
					ret.children.append(self.parseSimpleExpression())
				else:
					# procedure invocation - note that Pascal does not allow invoking a function
					# and ignoring the result, so this cannot be a function invocation.
					tok.type = TOKEN_PROCEDURE_CALL
					ret = AST(tok)
					if self.tokenizer.peek() == "(":
						# this is a procedure invocation (or
						lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
						ret.children.append(self.parseSimpleExpression())
						while self.tokenizer.peek() == ",":
							comma = self.tokenizer.getNextToken(TOKEN_COMMA)
							ret.children.append(self.parseSimpleExpression())
						rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)
			else:
				self.tokenizer.curPos = startpos
				ret = AST(Token(TOKEN_NOOP, None))

			endpos = self.tokenizer.curPos
			ret.comment = self.tokenizer.text[startpos:endpos]

		return ret

	def parseCompoundStatement(self):
		# <compound statement> ::= "begin" <statement sequence> "end"
		# <statement sequence> ::= <statement> | <statement> ';' <statement sequence>
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
		# <variable declaration part> ::= "var" <variable declaration> ";" {<variable declaration> ";"}
		# <variable declaration> ::= <identifier list> ":" <type>
		# <identifier list> ::= <identifier> {"," <identifier>}
		# <type> ::= "integer" | "real" | "string"
		ret = AST(self.tokenizer.getNextToken(TOKEN_VAR))
		done = False
		while not done:
			# I do not know how to recognize the end of the variable section without looking ahead
			# to the next section, which is either <procedure and function declaration part> or
			# the <statement part>.  <statement part> starts with "begin".
			# <procedure and function declaration part> starts with "function" or "procedure."
			# So, we are done when the next N characters are BEGIN/FUNCTION/PROCEDURE plus whitespace.
			if self.tokenizer.peekMatchStringAndSpace("begin"):
				done = True
			elif self.tokenizer.peekMatchStringAndSpace("function"):
				done = True
			elif self.tokenizer.peekMatchStringAndSpace("procedure"):
				done = True
			else:
				ident_token_list = []
				ident_token_list.append(self.tokenizer.getNextToken(TOKEN_IDENTIFIER))
				while self.tokenizer.peek() == ",":
					comma = self.tokenizer.getNextToken(TOKEN_COMMA)
					ident_token_list.append(self.tokenizer.getNextToken(TOKEN_IDENTIFIER))
				colon_token = self.tokenizer.getNextToken(TOKEN_COLON)
				type_token = self.tokenizer.getNextToken()
				if type_token.type not in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_REAL, TOKEN_VARIABLE_TYPE_STRING]: # pragma: no cover
					self.raiseParseError ("Expected variable type, got " + DEBUG_TOKENDISPLAY(type_token.type))
				semi_token = self.tokenizer.getNextToken(TOKEN_SEMICOLON)

				for ident_token in ident_token_list:
					variable_token = Token(type_token.type, ident_token.value )
					ret.children.append(AST(variable_token))

		return ret

	def parseProcFuncParameter(self):
		# <formal parameter list> ::= "(" ["var"] <identifier> ":" <type> {";" ["var"] <identifier> ":" <type>} ")"    /* Fred note - we are only allowing 6 Integer and 8 Real parameters */

		if self.tokenizer.peekMatchStringAndSpace("var"):
			vartoken = self.tokenizer.getNextToken(TOKEN_VAR)
			byref = True
		else:
			byref = False
		paramname = self.tokenizer.getNextToken(TOKEN_IDENTIFIER).value
		colon = self.tokenizer.getNextToken(TOKEN_COLON)
		paramtypetoken = self.tokenizer.getNextToken()
		if not paramtypetoken.type in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_REAL, TOKEN_VARIABLE_TYPE_STRING]: # pragma: no cover
			self.raiseParseError("Expected Integer, Real, or String Procedure/Function Parameter Type, got " + DEBUG_TOKENDISPLAY(paramtypetoken.type))
		return ProcFuncParameter(paramname, paramtypetoken.type, byref)

	def parseFormalParameterList(self, procfuncheading):
		# <formal parameter list> ::= "(" ["var"] <identifier> ":" <type> {";" ["var"] <identifier> ":" <type>} ")"    /* Fred note - we are only allowing 6 Integer and 8 Real parameters */
		lparen = self.tokenizer.getNextToken(TOKEN_LPAREN)
		procfuncheading.parameters.append(self.parseProcFuncParameter())
		while self.tokenizer.peek() == ";":
			semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)
			procfuncheading.parameters.append(self.parseProcFuncParameter())
		rparen = self.tokenizer.getNextToken(TOKEN_RPAREN)

	def parseFunctionDeclaration(self):
		# <function declaration> ::= <function heading> ";" <procedure or function body>
		# <function heading> ::= "function" <identifier> [<formal parameter list>] ":" <type>
		# <procedure or function body> ::= [<variable declaration part>] <statement part>

		functoken = self.tokenizer.getNextToken(TOKEN_FUNCTION)
		funcheading = ProcFuncHeading(self.tokenizer.getIdentifier().lower())


		if self.tokenizer.peek() == "(":
			self.parseFormalParameterList(funcheading)


		colon = self.tokenizer.getNextToken(TOKEN_COLON)
		functype = self.tokenizer.getNextToken()
		if functype.type in [TOKEN_VARIABLE_TYPE_INTEGER, TOKEN_VARIABLE_TYPE_REAL]:
			funcheading.returntype = functype.type
		else:
			self.raiseParseError("Expected Integer Function Return Type, got " + DEBUG_TOKENDISPLAY(functype.type)) # pragma: no cover
		semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)

		if self.tokenizer.peekMatchStringAndSpace("var"):
			funcheading.localvariableAST = self.parseVariableDeclarations()

		ret = AST(functoken)
		ret.procFuncHeading = funcheading
		ret.children.append(self.parseStatementPart())

		return ret

	def parseProcedureDeclaration(self):
		# <procedure declaration> ::= <procedure heading> ";" <procedure or function body>
		# <procedure heading> ::= "procedure" <identifier> [<formal parameter list>]
		# <procedure or function body> ::= [<variable declaration part>] <statement part>

		proctoken = self.tokenizer.getNextToken(TOKEN_PROCEDURE)
		procheading = ProcFuncHeading(self.tokenizer.getIdentifier().lower())

		if self.tokenizer.peek() == "(":
			self.parseFormalParameterList(procheading)
		semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)
		if self.tokenizer.peekMatchStringAndSpace("var"):
			procheading.localvariableAST = self.parseVariableDeclarations()

		ret = AST(proctoken)
		ret.procFuncHeading = procheading
		ret.children.append(self.parseStatementPart())

		return ret

	def parseProcedureFunctionDeclarationPart(self):
		# <procedure and function declaration part> ::= {(<procedure declaration> | <function declaration>) ";"}
		ret = AST(Token(TOKEN_PROCFUNC_DECLARATION_PART, None))  # this is not a real token, it just holds procs and functions
		done = False
		while not done:
			if self.tokenizer.peekMatchStringAndSpace("function"):
				ret.children.append(self.parseFunctionDeclaration())
				semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)
			elif self.tokenizer.peekMatchStringAndSpace("procedure"):
				ret.children.append(self.parseProcedureDeclaration())
				semicolon = self.tokenizer.getNextToken(TOKEN_SEMICOLON)
			else:
				done = True
		return ret


	def parseProgram(self):
		# program ::= <program heading> <block> "."
		# program heading ::= "program" <identifier> ";"

		# eat any leading comments
		self.tokenizer.eatComments()

		ret = AST(self.tokenizer.getNextToken(TOKEN_PROGRAM))
		ret.token.value = self.tokenizer.getIdentifier()
		semi = self.tokenizer.getNextToken(TOKEN_SEMICOLON)

		# block ::= [<declaration part>] <statement part>
		# <declaration part> ::= [<variable declaration part>] [<procedure and function declaration part>]
		if self.tokenizer.peekMatchStringAndSpace("var"):
			variable_declarations = self.parseVariableDeclarations()
		else:
			variable_declarations = None

		if self.tokenizer.peekMatchStringAndSpace("function") or self.tokenizer.peekMatchStringAndSpace("procedure"):
			procfunc_declarations = self.parseProcedureFunctionDeclarationPart()
		else:
			procfunc_declarations = None

		statementPart = self.parseStatementPart()
		if statementPart.token.type == TOKEN_BEGIN:
			statementPart.token.value = True  # set the "main" begin to have True as its value
		else: # pragma: no cover
			raiseParseError("Unexpected token to begin main block, expected BEGIN, received " + DEBUG_TOKENDISPLAY(statementpart.token.type))
		period = self.tokenizer.getNextToken(TOKEN_PERIOD)
		if self.tokenizer.peek() != "": # pragma: no cover
			raiseParseError("Unexpected character after period " + self.tokenizer.peek())

		if not (variable_declarations is None):  # variable declarations are optional
			ret.children.append(variable_declarations)

		if not (procfunc_declarations is None):  # procedure and function declarations are optional
			ret.children.append(procfunc_declarations)

		ret.children.append(statementPart)

		return ret

	def parse(self):
		self.AST = self.parseProgram()

	def assembleAST(self):
		self.AST.assemble(self.assembler, None)  # None = Global Scope

	def assemble(self, filename):
		self.assembler = asm_funcs.Assembler(filename)
		self.AST.find_literals(self.assembler)
		self.AST.find_global_variable_declarations(self.assembler)
		# concat needs stack space allocated for each invocation.  If we add other reserved
		# functions with same requirements, we can rename this method.
		mainbegin = self.AST.find_main_begin()
		mainbegin.find_concats(self.assembler)
		self.AST.static_type_check(self.assembler)

		self.assembler.setup_macros()
		self.assembler.setup_bss()
		self.assembler.setup_data()
		self.assembler.setup_text()

		self.AST.assembleProcsAndFunctions(self.assembler)

		self.assembler.setup_start()
		self.assembleAST()

		self.assembler.emit_terminate()
		self.assembler.cleanup()


def main(): # pragma: no cover
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


if __name__ == '__main__': # pragma: no cover
	main()
