import os
import argparse

spectre_exec = "/Users/bernhard/repos/spectre/build_xcode/bin/Debug/spectre"
vampire_exec = "/Users/bernhard/repos/vampire/build_xcode/bin/Debug/vampire"
example_dir = "/Users/bernhard/repos/spectre/examples"

# test function and return whether test has succeeded
def process(filename, timelimitSeconds, spectreArgs, vampireArgs):
	filepath = example_dir + "/" + filename

	spectre_out_file_path = "./spectre_out/" + filename + ".tptp"
	vampire_out_file_path = "./vampire_out/" + filename + ".vout"

	# run spectre on filepath and save result in spectre_out_file_path
	os.system(spectre_exec + " " + spectreArgs + " " + filepath + " > " + spectre_out_file_path)

	# run Vampire on spectre_out_file_path with given timelimit and save result in vampire_out_file_path
	os.system(vampire_exec + " --avatar off --input_syntax smtlib2 " + vampireArgs + " -t " + str(timelimitSeconds) + "s " + spectre_out_file_path + " > " + vampire_out_file_path)

	# check whether proof was found and update stats
	if '% Refutation found. Thanks to Tanya!' in open(vampire_out_file_path, 'r').read():
		print("testing file " + filename + ": SUCCESS")
		return True
	else:
		print("testing file " + filename + ": DIDN'T WORK")
		return False

def runAllTests(timelimitSeconds, spectreArgs, vampireArgs):
	print("Running all benchmarks for " + str(timelimitSeconds) + " seconds")
	if spectreArgs != "":
		print("Additional Spectre arguments: " + spectreArgs)
	if vampireArgs != "":
		print("Additional Vampire arguments: " + vampireArgs)

	success = 0
	fail = 0

	# test each file in example_dir and print stats
	for filename in sorted(os.listdir(example_dir)):
	    result = process(filename, timelimitSeconds, spectreArgs, vampireArgs)
	    if result == True:
	    	success += 1
	    else:
	    	fail += 1

	print("\nSPECTRE: Test results:")
	print("#success:" + str(success))
	print("#fail:" + str(fail))

def runSingleTest(filename, timelimitSeconds, spectreArgs, vampireArgs):
	print("Running benchmark " + filename + " for " + str(timelimitSeconds) + " seconds")
	if spectreArgs != "":
		print("Additional Spectre arguments: " + spectreArgs)
	if vampireArgs != "":
		print("Additional Vampire arguments: " + vampireArgs)
		
	result = process(filename, timelimitSeconds, spectreArgs, vampireArgs)

	print("\nSPECTRE: Test result for file " + filename + " :")
	if result == True:
		print("success!")
	else:
		print("failed!")

parser = argparse.ArgumentParser(description='Run spectre tests')
parser.add_argument("-f", "--single-file", required=False, default="", action="store", dest="name", help="run tests only on file from example-dir with given name")
parser.add_argument("-t", "--time", required=False, default=5, action="store", dest="time", help="set time-limit (seconds) for Vampire (default: 5)")
parser.add_argument("-sargs", "--spectre-args", required=False, default="", action="store", dest="sargs", help="additional arguments for Spectre")
parser.add_argument("-vargs", "--vampire-args", required=False, default="", action="store", dest="vargs", help="additional arguments for Vampire")
args = parser.parse_args()

if args.name != "":
	runSingleTest(args.name,args.time,args.sargs,args.vargs)
else:
	runAllTests(args.time,args.sargs,args.vargs)
