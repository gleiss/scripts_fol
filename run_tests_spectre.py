import os
import argparse

spectre_exec = "/Users/bernhard/repos/spectre/build_xcode/bin/Debug/spectre"
vampire_exec = "/Users/bernhard/repos/vampire/build_xcode/bin/Debug/vampire"
example_dir = "/Users/bernhard/repos/spectre/examples"

spectre_standard_args = ""
vampire_standard_args = "--avatar off --input_syntax smtlib2"

# test function and return whether test has succeeded
def process(filepath, filename, timelimitSeconds, spectreArgs, vampireArgs):

	spectre_out_file_path = "./spectre_out/" + filename + ".tptp"
	vampire_out_file_path = "./vampire_out/" + filename + ".vout"

	# run spectre on filepath and save result in spectre_out_file_path
	os.system(spectre_exec + " " + spectreArgs + " " + filepath + " > " + spectre_out_file_path)

	# run Vampire on spectre_out_file_path with given timelimit and save result in vampire_out_file_path
	os.system(vampire_exec + " " + vampireArgs + " -t " + str(timelimitSeconds) + "s " + spectre_out_file_path + " > " + vampire_out_file_path)

	# check whether proof was found and update stats
	if '% Refutation found. Thanks to Tanya!' in open(vampire_out_file_path, 'r').read():
		print("testing file " + filename + ": SUCCESS")
		return True
	else:
		print("testing file " + filename + ": DIDN'T WORK")
		return False

def runAllTests(timelimitSeconds, spectreArgs, vampireArgs):
	print("Running all benchmarks for " + str(timelimitSeconds) + " seconds")
	print("Spectre arguments: " + spectreArgs)
	print("Vampire arguments: " + vampireArgs)

	success = 0
	fail = 0

	# test each file in example_dir(recursively) and print stats
	for root, directories, filenames in os.walk(example_dir):
		print("\nScanning folder " + root)

		for filename in sorted(filenames):
			if filename == ".DS_Store":
				continue
			filepath = os.path.join(root,filename)

			result = process(filepath, filename, timelimitSeconds, spectreArgs, vampireArgs)
			if result == True:
				success += 1
			else:
				fail += 1

	print("\nSPECTRE: Overall Test results:")
	print("Running all benchmarks for " + str(timelimitSeconds) + " seconds")
	print("Spectre arguments: " + spectreArgs)
	print("Vampire arguments: " + vampireArgs)
	print("#success:" + str(success))
	print("#fail:" + str(fail))

def runSingleTest(filename, timelimitSeconds, spectreArgs, vampireArgs):
	print("Running benchmark " + filename + " for " + str(timelimitSeconds) + " seconds")
	print("Spectre arguments: " + spectreArgs)
	print("Vampire arguments: " + vampireArgs)
		
	filepath = os.path.join(example_dir, filename)
	print(filepath)
	result = process(filepath, filename, timelimitSeconds, spectreArgs, vampireArgs)

parser = argparse.ArgumentParser(description='Run spectre tests')
parser.add_argument("-f", "--single-file", required=False, default="", action="store", dest="name", help="run tests only on file from example-dir with given name")
parser.add_argument("-t", "--time", required=False, default=5, action="store", dest="time", help="set time-limit (seconds) for Vampire (default: 5)")
parser.add_argument("-sargs", "--spectre-args", required=False, default="", action="store", dest="additionalSpectreArgs", help="additional arguments for Spectre")
parser.add_argument("-vargs", "--vampire-args", required=False, default="", action="store", dest="additionalVampireArgs", help="additional arguments for Vampire")
args = parser.parse_args()

spectreArgs = " " + spectre_standard_args + " " + args.additionalSpectreArgs + " "
vampireArgs = " " + vampire_standard_args + " " + args.additionalVampireArgs + " "

if args.name != "":
	runSingleTest(args.name,args.time,spectreArgs, vampireArgs)
else:
	runAllTests(args.time, spectreArgs, vampireArgs)
