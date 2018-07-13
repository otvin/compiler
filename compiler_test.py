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

	f = dotest("compiler_test_files/testbyref01.pas", "compiler_test_files/testbyref01.out")
	f = dotest("compiler_test_files/testbyref02.pas", "compiler_test_files/testbyref02.out")
	f = dotest("compiler_test_files/testbyref03.pas", "compiler_test_files/testbyref03.out")
	f = dotest("compiler_test_files/testbyref04.pas", "compiler_test_files/testbyref04.out")
	f = dotest("compiler_test_files/testcomments01.pas", "compiler_test_files/testcomments01.out")
	f = dotest("compiler_test_files/testconcat01.pas", "compiler_test_files/testconcat01.out")
	f = dotest("compiler_test_files/testconcat02.pas", "compiler_test_files/testconcat02.out")
	f = dotest("compiler_test_files/testconcat03.pas", "compiler_test_files/testconcat03.out")
	f = dotest("compiler_test_files/testconcat04.pas", "compiler_test_files/testconcat04.out")
	f = dotest("compiler_test_files/testconcat05.pas", "compiler_test_files/testconcat05.out")
	f = dotest("compiler_test_files/testfunc01.pas", "compiler_test_files/testfunc01.out")
	f = dotest("compiler_test_files/testfunc02.pas", "compiler_test_files/testfunc02.out")
	f = dotest("compiler_test_files/testfunc03.pas", "compiler_test_files/testfunc03.out")
	f = dotest("compiler_test_files/testfunc04.pas", "compiler_test_files/testfunc04.out")
	f = dotest("compiler_test_files/testfunc05.pas", "compiler_test_files/testfunc05.out")
	f = dotest("compiler_test_files/testfunc06.pas", "compiler_test_files/testfunc06.out")
	f = dotest("compiler_test_files/testfunc07.pas", "compiler_test_files/testfunc07.out")
	f = dotest("compiler_test_files/testfunc08.pas", "compiler_test_files/testfunc08.out")
	f = dotest("compiler_test_files/testfunc09.pas", "compiler_test_files/testfunc09.out")
	f = dotest("compiler_test_files/testfunc10.pas", "compiler_test_files/testfunc10.out")
	f = dotest("compiler_test_files/testfunc11.pas", "compiler_test_files/testfunc11.out")
	f = dotest("compiler_test_files/testglobalvar01.pas", "compiler_test_files/testglobalvar01.out")
	f = dotest("compiler_test_files/testglobalvar02.pas", "compiler_test_files/testglobalvar02.out")
	f = dotest("compiler_test_files/testif01.pas", "compiler_test_files/testif01.out")
	f = dotest("compiler_test_files/testif02.pas", "compiler_test_files/testif02.out")
	f = dotest("compiler_test_files/testif03.pas", "compiler_test_files/testif03.out")
	f = dotest("compiler_test_files/testlocalvar01.pas", "compiler_test_files/testlocalvar01.out")
	f = dotest("compiler_test_files/testlocalvar02.pas", "compiler_test_files/testlocalvar02.out")
	f = dotest("compiler_test_files/testmath01.pas", "compiler_test_files/testmath01.out")
	f = dotest("compiler_test_files/testmath02.pas", "compiler_test_files/testmath02.out")
	f = dotest("compiler_test_files/testmath03.pas", "compiler_test_files/testmath03.out")
	f = dotest("compiler_test_files/testproc01.pas", "compiler_test_files/testproc01.out")
	f = dotest("compiler_test_files/testproc02.pas", "compiler_test_files/testproc02.out")
	f = dotest("compiler_test_files/testproc03.pas", "compiler_test_files/testproc03.out")
	f = dotest("compiler_test_files/testreal01.pas", "compiler_test_files/testreal01.out")
	f = dotest("compiler_test_files/testreal02.pas", "compiler_test_files/testreal02.out")
	f = dotest("compiler_test_files/testreal03.pas", "compiler_test_files/testreal03.out")
	f = dotest("compiler_test_files/testreal04.pas", "compiler_test_files/testreal04.out")
	f = dotest("compiler_test_files/testreal05.pas", "compiler_test_files/testreal05.out")
	f = dotest("compiler_test_files/testreal06.pas", "compiler_test_files/testreal06.out")
	f = dotest("compiler_test_files/testreal07.pas", "compiler_test_files/testreal07.out")
	f = dotest("compiler_test_files/testreal08.pas", "compiler_test_files/testreal08.out")
	f = dotest("compiler_test_files/testrecursion01.pas", "compiler_test_files/testrecursion01.out")
	f = dotest("compiler_test_files/testrelop01.pas", "compiler_test_files/testrelop01.out")
	f = dotest("compiler_test_files/testrelop02.pas", "compiler_test_files/testrelop02.out")
	f = dotest("compiler_test_files/testscope01.pas", "compiler_test_files/testscope01.out")
	f = dotest("compiler_test_files/testscope02.pas", "compiler_test_files/testscope02.out")
	f = dotest("compiler_test_files/testscope03.pas", "compiler_test_files/testscope03.out")
	f = dotest("compiler_test_files/teststring01.pas", "compiler_test_files/teststring01.out")
	f = dotest("compiler_test_files/teststring02.pas", "compiler_test_files/teststring02.out")
	f = dotest("compiler_test_files/teststring03.pas", "compiler_test_files/teststring03.out")
	f = dotest("compiler_test_files/teststring04.pas", "compiler_test_files/teststring04.out")
	f = dotest("compiler_test_files/testwhile01.pas", "compiler_test_files/testwhile01.out")
	f = dotest("compiler_test_files/testwhile02.pas", "compiler_test_files/testwhile02.out")
	f = dotest("compiler_test_files/testwrite01.pas", "compiler_test_files/testwrite01.out")
	f = dotest("compiler_test_files/testwriteln01.pas", "compiler_test_files/testwriteln01.out")
	f = dotest("compiler_test_files/testwriteln02.pas", "compiler_test_files/testwriteln02.out")
	f = dotest("compiler_test_files/testwriteln03.pas", "compiler_test_files/testwriteln03.out")


	print ("Tests Attempted: " + str(NUM_ATTEMPTS))
	print ("Tests Succeeded: " + str(NUM_SUCCESSES))

if __name__ == '__main__':  # pragma: no cover
	main()
