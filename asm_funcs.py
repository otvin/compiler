import os


class Assembler:
	def __init__(self, asm_filename):
		self.asm_file = open(asm_filename, 'w')
		self.string_literals = {}
		self.next_literal_index = 0
		self.variable_symbol_table = {}
		self.next_variable_index = 0
		self.next_local_label_index = 0

	def emit(self, s):
		self.asm_file.write(s)

	def emitln(self, s):
		self.emit(s + '\n')

	def emitcode(self, s):
		self.emitln('\t' + s)

	def emitsection(self,s):
		self.emitln(s)

	def emitlabel(self, s):
		self.emitln(s + ":")

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

	def setup_bss(self):
		self.emitsection("section .bss")
		self.emitcode("write_CRLF resb 2")

		for key in self.variable_symbol_table.keys():
			if self.variable_symbol_table[key][0] == "int":  #to-do use a constant instead of "int"
				self.emitcode(self.variable_symbol_table[key][1] + " resq 1\t; global variable " + key)  # 8-byte / 64-bit int


	def setup_data(self):
		if len(self.string_literals.keys()) > 0:
			self.emitsection("section .data")
			for key in self.string_literals.keys():
				self.emitcode(self.string_literals[key] + ' db "' + key + '",0')  # null-terminate everything even if nasm doesn't require
				self.emitcode(self.string_literals[key] + 'Len equ $-' + self.string_literals[key])

	def setup_text(self):
		self.emitsection("section .text")
		self.emitcode("global _start")
		self.emitcode("extern prtdec")  # imported from nasm64

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

	def emit_writeINT(self):
		self.emitlabel("_writeINT")
		self.emitcode(";int to be written must be in rax for legacy reasons.  nasm64 uses rdi")
		self.emitcode("mov rdi, rax")
		self.emitcode("call prtdec")
		self.emitcode("ret")

	def emit_writeCRLF(self):
		self.emitlabel("_writeCRLF")
		self.emitcode("mov rax, 1")
		self.emitcode("mov rdi, 1")
		self.emitcode("mov rsi, write_CRLF")
		self.emitcode("mov rdx, 1")
		self.emitcode("syscall")
		self.emitcode("ret")

	def emit_systemfunctions(self):
		self.emit_writeINT()
		self.emit_writeCRLF()


class Compiler:
	def __init__(self, asm_filename, obj_filename):
		self.asm_filename = asm_filename
		self.obj_filename = obj_filename

	def do_compile(self):
		os.system("nasm -f elf64 -o nsm64.o nsm64.asm")
		os.system("nasm -f elf64 -o " + self.obj_filename + " " + self.asm_filename)


class Linker:
	def __init__(self, obj_filename, exe_filename):
		self.obj_filename = obj_filename
		self.exe_filename = exe_filename

	def do_link(self):
		os.system("ld " + self.obj_filename + " nsm64.o -o " + self.exe_filename)



