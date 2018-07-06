import compiler
import asm_funcs
import os

NUM_ATTEMPTS = 0
NUM_SUCCESSES = 0

def dotest(infilename, resultfilename):
	global NUM_ATTEMPTS
	global NUM_SUCCESSES

	NUM_ATTEMPTS += 1

	try:
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



		if resultvalue == testvalue:
			print("PASS: " + infilename)
			NUM_SUCCESSES += 1

			# remove the files from passed tests; we will leave the files from failed tests so we can debug
			os.system("rm " + assemblyfilename)
			os.system("rm " + objectfilename)
			os.system("rm " + exefilename)
			os.system("rm " + testoutputfilename)

			return True
		else: # pragma: no cover
			print("FAIL: " + infilename)
			return False
	except Exception as e: # pragma: no cover
		print("FAIL: " + infilename)
		print(e)
		return False


def main():
	global NUM_ATTEMPTS
	global NUM_SUCCESSES

	f = dotest("compiler_test_files/test1.pas", "compiler_test_files/test1.out")
	f = dotest("compiler_test_files/test1a.pas", "compiler_test_files/test1a.out")
	f = dotest("compiler_test_files/test1b.pas", "compiler_test_files/test1b.out")
	f = dotest("compiler_test_files/test2.pas", "compiler_test_files/test2.out")
	f = dotest("compiler_test_files/test3.pas", "compiler_test_files/test3.out")
	f = dotest("compiler_test_files/test4.pas", "compiler_test_files/test4.out")
	f = dotest("compiler_test_files/test5.pas", "compiler_test_files/test5.out")
	f = dotest("compiler_test_files/test6.pas", "compiler_test_files/test6.out")
	f = dotest("compiler_test_files/test7.pas", "compiler_test_files/test7.out")
	f = dotest("compiler_test_files/test8.pas", "compiler_test_files/test8.out")
	f = dotest("compiler_test_files/test9.pas", "compiler_test_files/test9.out")
	f = dotest("compiler_test_files/test10.pas", "compiler_test_files/test10.out")
	f = dotest("compiler_test_files/test11.pas", "compiler_test_files/test11.out")
	f = dotest("compiler_test_files/test_recursion.pas", "compiler_test_files/test_recursion.out")
	f = dotest("compiler_test_files/test11a.pas", "compiler_test_files/test11a.out")
	f = dotest("compiler_test_files/test12a.pas", "compiler_test_files/test12a.out")
	f = dotest("compiler_test_files/test12b.pas", "compiler_test_files/test12b.out")
	f = dotest("compiler_test_files/test12c.pas", "compiler_test_files/test12c.out")
	f = dotest("compiler_test_files/test12d.pas", "compiler_test_files/test12d.out")
	f = dotest("compiler_test_files/test13.pas", "compiler_test_files/test13.out")
	f = dotest("compiler_test_files/test14.pas", "compiler_test_files/test14.out")
	f = dotest("compiler_test_files/variablescope.pas", "compiler_test_files/variablescope.out")
	f = dotest("compiler_test_files/test15.pas", "compiler_test_files/test15.out")
	f = dotest("compiler_test_files/test16.pas", "compiler_test_files/test16.out")
	f = dotest("compiler_test_files/test17.pas", "compiler_test_files/test17.out")
	f = dotest("compiler_test_files/test18.pas", "compiler_test_files/test18.out")
	f = dotest("compiler_test_files/testwrite.pas", "compiler_test_files/testwrite.out")
	f = dotest("compiler_test_files/test19.pas", "compiler_test_files/test19.out")
	f = dotest("compiler_test_files/test20.pas", "compiler_test_files/test20.out")
	f = dotest("compiler_test_files/test20a.pas", "compiler_test_files/test20a.out")
	f = dotest("compiler_test_files/test20b.pas", "compiler_test_files/test20b.out")
	f = dotest("compiler_test_files/test20c.pas", "compiler_test_files/test20c.out")
	f = dotest("compiler_test_files/test20d.pas", "compiler_test_files/test20d.out")
	f = dotest("compiler_test_files/test20e.pas", "compiler_test_files/test20e.out")
	f = dotest("compiler_test_files/test20e2.pas", "compiler_test_files/test20e2.out")
	f = dotest("compiler_test_files/test20f.pas", "compiler_test_files/test20f.out")
	f = dotest("compiler_test_files/test20g.pas", "compiler_test_files/test20g.out")
	f = dotest("compiler_test_files/test20h.pas", "compiler_test_files/test20h.out")
	f = dotest("compiler_test_files/test20i.pas", "compiler_test_files/test20i.out")
	f = dotest("compiler_test_files/test21.pas", "compiler_test_files/test21.out")
	f = dotest("compiler_test_files/test21a.pas", "compiler_test_files/test21a.out")
	f = dotest("compiler_test_files/test21b.pas", "compiler_test_files/test21b.out")
	f = dotest("compiler_test_files/test21d.pas", "compiler_test_files/test21d.out")
	f = dotest("compiler_test_files/test21e.pas", "compiler_test_files/test21e.out")
	f = dotest("compiler_test_files/test21fa.pas", "compiler_test_files/test21fa.out")
	f = dotest("compiler_test_files/test22.pas", "compiler_test_files/test22.out")
	f = dotest("compiler_test_files/test23.pas", "compiler_test_files/test23.out")
	f = dotest("compiler_test_files/test24.pas", "compiler_test_files/test24.out")
	f = dotest("compiler_test_files/test24a.pas", "compiler_test_files/test24a.out")
	f = dotest("compiler_test_files/test24b.pas", "compiler_test_files/test24b.out")
	f = dotest("compiler_test_files/test24c.pas", "compiler_test_files/test24c.out")
	f = dotest("compiler_test_files/test24d.pas", "compiler_test_files/test24d.out")
	f = dotest("compiler_test_files/test24e.pas", "compiler_test_files/test24e.out")
	f = dotest("compiler_test_files/test24f2.pas", "compiler_test_files/test24f2.out")
	print ("Tests Attempted: " + str(NUM_ATTEMPTS))
	print ("Tests Succeeded: " + str(NUM_SUCCESSES))

if __name__ == '__main__':  # pragma: no cover
	main()
