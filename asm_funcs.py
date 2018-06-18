import os

SYMBOL_FUNCTION = 0
SYMBOL_INTEGER = 1
SYMBOL_INTEGER_PTR = 2
SYMBOL_REAL = 3
SYMBOL_REAL_PTR = 4

DEBUG_SYMBOLDISPLAY = ["FUNCTION", "INT", "REAL"]

def intParameterPositionToRegister(pos):
	# First six integer parameters to functions are stored in registers.
	# This function converts the position in the function parameter list to a register
	# once we get > 6 parameters it will be stack pointer offsets
	if pos == 1:
		ret = "RDI"
	elif pos == 2:
		ret = "RSI"
	elif pos == 3:
		ret = "RDX"
	elif pos == 4:
		ret = "RCX"
	elif pos == 5:
		ret = "R8"
	elif pos == 6:
		ret = "R9"
	else: # pragma: no cover
		raise ValueError ("Invalid Parameter Position " + str(pos))
	return ret

def realParameterPositionToRegister(pos):
	# First eight float parameters are passed in XMM0..XMM7.  After that, it would be stack pointer
	# offsets.
	if pos >=1 and pos <=8:
		ret = "XMM" + str(pos-1)
	else: # pragma: no cover
		raise ValueError ("Invalid Parameter Position " + str(pos))
	return ret

def codeToASMComment(code):
	# takes a block of code and converts it to a comment that can be added to the line in the assembly
	# remove newlines
	c = code.replace('\n','')
	c = c.replace('\t','')
	# remove comments
	i = 0
	c2 = ''
	while i < len(c):
		while c[i] != '{':
			c2 += c[i]
			i += 1
			if i >= len(c):
				return c2
		while c[i] != '}':
			i += 1
			if i >= len(c):
				return c2
		if c[i] == '}':
			i += 1
			if i >= len(c):
				return c2
	return c2

class SymbolData:
	def __init__(self, type, label, procFuncHeading = None):
		self.type = type
		self.label = label
		self.procfuncheading = procFuncHeading

	def isPointer(self):
		if self.type in [SYMBOL_INTEGER_PTR, SYMBOL_REAL_PTR]:
			return True
		else:
			return False

class SymbolTable:
	def __init__ (self):
		self.symbols = {}

	def exists(self, symbolname):
		if symbolname in self.symbols:
			return True
		else:
			return False

	def insert(self, symbolname, symboltype, symbollabel, procFuncHeading = None):
		if self.exists(symbolname): # pragma: no cover
			raise ValueError ("Duplicate symbol inserted :" + symbolname)
		if symboltype not in [SYMBOL_FUNCTION, SYMBOL_REAL, SYMBOL_INTEGER, SYMBOL_REAL_PTR, SYMBOL_INTEGER_PTR]: # pragma: no cover
			raise ValueError ("Invalid symbol type")
		self.symbols[symbolname] = SymbolData(symboltype, symbollabel, procFuncHeading)

	def get(self, symbolname):
		if symbolname not in self.symbols: # pragma: no cover
			if self.symbols is None:
				symbolstr = "None"
			else:
				symbolstr = str(self.symbols)
			raise KeyError ("Symbol " + symbolname + " not present\n" + symbolstr)
		return self.symbols[symbolname]

	def symbollist(self):
		return self.symbols.keys()

class Assembler:
	def __init__(self, asm_filename):
		self.asm_file = open(asm_filename, 'w')
		self.string_literals = {}
		self.real_literals = {}
		self.next_literal_index = 0
		self.variable_symbol_table = SymbolTable()
		self.next_variable_index = 0
		self.next_local_label_index = 0

	def emit(self, s):
		self.asm_file.write(s)

	def emitln(self, s):
		self.emit(s + '\n')

	def emitcode(self, s, comment = None):
		if comment is None:
			self.emitln('\t' + s)
		else:
			self.emitln('\t' + s + '\t\t;' + codeToASMComment(comment))

	def emitpushxmmreg(self, reg):
		self.emitcode("SUB RSP, 16")
		self.emitcode("MOVDQU [RSP], " + reg)

	def emitpopxmmreg(self, reg):
		self.emitcode("MOVDQU " + reg + ", [RSP]")
		self.emitcode("ADD RSP, 16")

	def emitsection(self,s):
		self.emitln(s)

	def emitlabel(self, s, comment = None):
		if comment is None:
			self.emitln(s + ":")
		else:
			self.emitln(s + ":\t\t\t;" + codeToASMComment(comment))

	def emitcomment(self, comment):
		if comment is not None:
			self.emitln('\t\t\t\t;' + codeToASMComment(comment))

	def cleanup(self):
		self.asm_file.close()

	def generate_literal_name(self, prefix):
		ret = 'fredliteral' + prefix + str(self.next_literal_index)
		self.next_literal_index += 1
		return ret

	def generate_variable_name(self, prefix):
		ret = 'fredvar' + prefix + str(self.next_variable_index)
		self.next_variable_index += 1
		return ret

	def generate_local_label(self):
		ret = ".L" + str(self.next_local_label_index)
		self.next_local_label_index += 1
		return ret

	def preserve_xmm_registers_for_func_call(self, num_registers):
		if num_registers > 8: # pragma: no cover
			raise ValueError ("Cannot preserve more than 8 XMM registers")
		i = 0
		while i < num_registers:
			if i==0:
				pass # can't preserve XMM0 as it will be used for the return value
			else:
				self.emitpushxmmreg("XMM" + str(i))
			i += 1

	def restore_xmm_registers_after_func_call(self, num_registers):
		if num_registers > 8: # pragma: no cover
			raise ValueError ("Cannot restore more than 8 XMM registers")
		i = num_registers - 1;
		while i >= 0:
			if i==0:
				pass # don't restore XMM0 as it will have the return value if it is a real function
			else:
				self.emitpopxmmreg("XMM" + str(i))
			i -= 1

	def preserve_int_registers_for_func_call(self, num_registers):
		# push the rdi, rsi, rdx, rcx, r8, and r9
		if num_registers >= 1:
			self.emitcode("PUSH RDI")
			if num_registers >= 2:
				self.emitcode("PUSH RSI")
				if num_registers >= 3:
					self.emitcode("PUSH RDX")
					if num_registers >= 4:
						self.emitcode("PUSH RCX")
						if num_registers >= 5:
							self.emitcode("PUSH R8")
							if num_registers >= 6:
								self.emitcode("PUSH R9")

		# always preserve RBP
		self.emitcode("PUSH RBP")

	def restore_int_registers_after_func_call(self, num_registers):
		self.emitcode("POP RBP")

		if num_registers >=6:
			self.emitcode("POP R9")
		if num_registers >=5:
			self.emitcode("POP R8")
		if num_registers >=4:
			self.emitcode("POP RCX")
		if num_registers >=3:
			self.emitcode("POP RDX")
		if num_registers >=2:
			self.emitcode("POP RSI")
		if num_registers >=1:
			self.emitcode("POP RDI")


	def setup_bss(self):
		self.emitsection("section .bss")
		self.emitcode("write_CRLF resb 2")

		for key in self.variable_symbol_table.symbollist():
			symbol = self.variable_symbol_table.get(key)
			if symbol.type in [SYMBOL_INTEGER, SYMBOL_REAL]:
				self.emitcode(symbol.label + " resq 1\t; global variable " + key)  # 8-byte / 64-bit int or float



	def setup_data(self):
		if len(self.string_literals.keys()) > 0 or len(self.real_literals.keys()) > 0:
			self.emitsection("section .data")
			for key in self.string_literals.keys():
				self.emitcode(self.string_literals[key] + ' db `' + key.replace('`','\\`') + '`')
				self.emitcode(self.string_literals[key] + 'Len equ $-' + self.string_literals[key])
			for key in self.real_literals.keys():
				self.emitcode(self.real_literals[key] + ' dq ' + str(key))

	def setup_text(self):
		self.emitsection("section .text")
		self.emitcode("global _start")
		self.emitcode("extern prtdec")  # imported from nasm64
		self.emitcode("extern prtdbl")  # imported from nasm64

	def setup_start(self):
		self.emitlabel("_start")
		# need to set these constants.  When I used section .data, the issue was that they would somehow
		# get overwritten
		self.emitcode("; define CRLF - ascii 10 + ascii 0")
		self.emitcode("mov rcx, write_CRLF")
		self.emitcode("mov rbx, 10")
		self.emitcode("mov [rcx], rbx")
		self.emitcode("inc rcx")
		self.emitcode("mov rbx, 0")
		self.emitcode("mov [rcx], rbx")

	def emit_terminate(self):
		self.emitcode("mov rax,60")
		self.emitcode("mov rdi,0")
		self.emitcode("syscall")

	def emit_writeCRLF(self):
		self.emitlabel("_writeCRLF")
		self.emitcode("mov rax, 1")
		self.emitcode("mov rdi, 1")
		self.emitcode("mov rsi, write_CRLF")
		self.emitcode("mov rdx, 1")
		self.emitcode("syscall")
		self.emitcode("ret")

	def emit_systemfunctions(self):
		self.emit_writeCRLF()


class Compiler:
	def __init__(self, asm_filename, obj_filename):
		self.asm_filename = asm_filename
		self.obj_filename = obj_filename

	def do_compile(self):
		# os.system("nasm -f elf64 -o nsm64.o nsm64.asm")
		# os.system("nasm -f elf64 -o " + self.obj_filename + " " + self.asm_filename)

		# Need to make debug symbols a flag but for now this will work
		os.system("nasm -f elf64 -F dwarf -g -o nsm64.o nsm64.asm")
		os.system("nasm -f elf64 -F dwarf -g -o " + self.obj_filename + " " + self.asm_filename)

class Linker:
	def __init__(self, obj_filename, exe_filename):
		self.obj_filename = obj_filename
		self.exe_filename = exe_filename

	def do_link(self):
		os.system("ld " + self.obj_filename + " nsm64.o -o " + self.exe_filename)



