import compiler
import asm_funcs
import os

NUM_ATTEMPTS = 0
NUM_SUCCESSES = 0

def dotest(infilename, resultfilename):
	global NUM_ATTEMPTS
	global NUM_SUCCESSES

	assemblyfilename = infilename[:-4] + ".asm"
	objectfilename = infilename[:-4] + ".o"
	exefilename = infilename[:-4]
	testoutputfilename = exefilename + ".testoutput"

	f = open(infilename, "r")
	t = compiler.Tokenizer(f.read())
	f.close()

	p = compiler.Parser(t)
	p.parse()
	p.assemble(assemblyfilename)
	c = asm_funcs.Compiler(assemblyfilename, objectfilename)
	c.do_compile()
	l = asm_funcs.Linker(objectfilename, exefilename)
	l.do_link()

	os.system("./" + exefilename + " > " + testoutputfilename)

	testfile = open(testoutputfilename, "r")
	testvalue = testfile.read()
	testfile.close()

	resultfile = open(resultfilename, "r")
	resultvalue = resultfile.read()
	resultfile.close()

	NUM_ATTEMPTS += 1

	if resultvalue == testvalue:
		print("PASS: " + infilename)
		NUM_SUCCESSES += 1

		# remove the files from passed tests; we will leave the files from failed tests so we can debug
		os.system("rm " + assemblyfilename)
		os.system("rm " + objectfilename)
		os.system("rm " + exefilename)
		os.system("rm " + testoutputfilename)

		return True
	else:
		print("FAIL: " + infilename)
		return False



def main():
	global NUM_ATTEMPTS
	global NUM_SUCCESSES

	f = dotest("compiler_test_files/test1.pas", "compiler_test_files/test1.out")
	f = dotest("compiler_test_files/test2.pas", "compiler_test_files/test2.out")
	f = dotest("compiler_test_files/test3.pas", "compiler_test_files/test3.out")
	f = dotest("compiler_test_files/test4.pas", "compiler_test_files/test4.out")
	f = dotest("compiler_test_files/test5.pas", "compiler_test_files/test5.out")
	f = dotest("compiler_test_files/test6.pas", "compiler_test_files/test6.out")
	f = dotest("compiler_test_files/test7.pas", "compiler_test_files/test7.out")
	f = dotest("compiler_test_files/test8.pas", "compiler_test_files/test8.out")
	f = dotest("compiler_test_files/test9.pas", "compiler_test_files/test9.out")

	print ("Tests Attempted: " + str(NUM_ATTEMPTS))
	print ("Tests Succeeded: " + str(NUM_SUCCESSES))

if __name__ == '__main__':
	main()
