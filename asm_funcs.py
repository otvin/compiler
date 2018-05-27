import os


class Assembler:
	def __init__(self, asm_filename):
		self.asm_file = open(asm_filename, 'w')
		self.string_literals = {}
		self.next_data_name = 0
		self.next_label = 0

	def emit(self, s):
		self.asm_file.write(s)

	def emitln(self, s):
		self.emit(s + '\n')

	def emitcode(self, s):
		self.emitln('\t' + s)

	def emitlabel(self, s):
		self.emitln(s)

	def cleanup(self):
		self.asm_file.close()

	def generate_data_name(self, prefix):
		ret = 'fredpascal' + prefix + str(self.next_data_name)
		self.next_data_name += 1
		return ret


	def setup_bss(self):
		self.emitlabel("section .bss")
		self.emitcode("write_intDigitSpace resb 100")
		self.emitcode("write_intDigitSpacePos resb 8")
		self.emitcode("write_minusSign resb 2")
		self.emitcode("write_CRLF resb 2")

	def setup_data(self):
		if len(self.string_literals.keys()) > 0:
			self.emitlabel("section .data")
			for key in self.string_literals.keys():
				self.emitcode(self.string_literals[key] + ' db "' + key + '",0')  # null-terminate everything even if nasm doesn't require
				self.emitcode(self.string_literals[key] + 'Len equ $-' + self.string_literals[key])

	def setup_text(self):
		self.emitlabel("section .text")
		self.emitcode("global _start")

	def setup_start(self):
		self.emitlabel("_start:")
		# need to set these constants.  When I used section .data, the issue was that they would somehow
		# get overwritten
		self.emitcode("; define minus sign - ascii 45 + ascii 0")
		self.emitcode("mov rcx, write_minusSign")
		self.emitcode("mov rbx, 45")
		self.emitcode("mov [rcx], rbx")
		self.emitcode("inc rcx")
		self.emitcode("mov rbx, 0")
		self.emitcode("mov [rcx], rbx")
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
		self.emitlabel("_writeINT:\t\t;int to be written must be in rax. rax is clobbered")
		self.emitlabel("\t; source = https://www.youtube.com/watch?v=XuUD0WQ9kaE - modified to do negatives")
		self.emitcode("cmp rax, 0")
		self.emitcode("jge .doneSigned")
		self.emitcode("; need to print the minus sign and negate RAX")
		self.emitcode("push rax")
		self.emitcode("mov rax, 1")
		self.emitcode("mov rdi, 1")
		self.emitcode("mov rsi, write_minusSign")
		self.emitcode("mov rdx, 1")
		self.emitcode("syscall")
		self.emitcode("pop rax")
		self.emitcode("neg rax")

		self.emitlabel(".doneSigned:")
		self.emitcode("mov rcx, write_intDigitSpace")
		self.emitcode("xor rbx, rbx")  # put a zero here - null-terminate the string
		self.emitcode("mov [rcx], rbx")
		self.emitcode("inc rcx")
		self.emitcode("mov [write_intDigitSpacePos], rcx")
		self.emitlabel(".writeINTLoop:")
		self.emitcode("mov rdx, 0\t\t;because rdx gets concatenated onto rax when calling div")
		self.emitcode("mov rbx, 10")
		self.emitcode("div rbx")
		self.emitcode("push rax")
		self.emitcode("add rdx, 48")
		self.emitcode("mov rcx, [write_intDigitSpacePos]")
		self.emitcode("mov [rcx], dl")
		self.emitcode("inc rcx")
		self.emitcode("mov [write_intDigitSpacePos], rcx")
		self.emitcode("pop rax")
		self.emitcode("cmp rax, 0")
		self.emitcode("jne .writeINTLoop")
		self.emitlabel(".writeINTLoop2:")
		self.emitcode("mov rcx, [write_intDigitSpacePos]")
		self.emitcode("mov rax, 1")
		self.emitcode("mov rdi, 1")
		self.emitcode("mov rsi, rcx")
		self.emitcode("mov rdx, 1")
		self.emitcode("syscall")
		self.emitcode("mov rcx, [write_intDigitSpacePos]")
		self.emitcode("dec rcx")
		self.emitcode("mov [write_intDigitSpacePos], rcx")
		self.emitcode("cmp rcx, write_intDigitSpace")
		self.emitcode("jge .writeINTLoop2")
		self.emitcode("ret")

	def emit_writeCRLF(self):
		self.emitlabel("_writeCRLF:")
		self.emitcode("mov rax, 1")
		self.emitcode("mov rdi, 1")
		self.emitcode("mov rsi, write_CRLF")
		self.emitcode("mov rdx, 1")
		self.emitcode("syscall")
		self.emitcode("ret")

	def emit_writeSTR(self):
		pass

	def emit_systemfunctions(self):
		self.emit_writeINT()
		self.emit_writeSTR()
		self.emit_writeCRLF()


class Compiler:
	def __init__(self, asm_filename, obj_filename):
		self.asm_filename = asm_filename
		self.obj_filename = obj_filename

	def do_compile(self):
		os.system("nasm -f elf64 -o " + self.obj_filename + " " + self.asm_filename)


class Linker:
	def __init__(self, obj_filename, exe_filename):
		self.obj_filename = obj_filename
		self.exe_filename = exe_filename

	def do_link(self):
		os.system("ld " + self.obj_filename + " -o " + self.exe_filename)


def DEBUG_helloworld_test():
	a = Assembler("mytest.asm")

	a.emitlabel('section .data')
	a.emitcode('text db "Hello, World!", 10')
	a.emitln("")

	a.emitlabel('section .text')
	a.emitcode('global _start')
	a.emitln("")

	a.emitlabel('_start:')
	a.emitlabel('mov rax, 1')
	a.emitlabel('mov rdi, 1')
	a.emitlabel('mov rsi, text')
	a.emitlabel('mov rdx, 14')
	a.emitlabel('syscall')
	a.emitln("")

	a.emitlabel('mov rax, 60')
	a.emitlabel('mov rdi, 0')
	a.emitlabel('syscall')

	a.cleanup()

	c = Compiler("mytest.asm", "mytest.o")
	c.do_compile()

	l = Linker("mytest.o", "mytest")
	l.do_link()
