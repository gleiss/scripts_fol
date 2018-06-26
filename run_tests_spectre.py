import os
import argparse

# globals
spectre_exec = "/Users/bernhard/repos/spectre/build_xcode/bin/Debug/spectre"
vampire_exec = "/Users/bernhard/repos/vampire/build_xcode/bin/Debug/vampire"
example_dir = "/Users/bernhard/repos/spectre/examples"

spectre_standard_args = ""
vampire_standard_args = "--avatar off --input_syntax smtlib2"

# test and return whether test has succeeded
def process(subdir, filename, timelimitSeconds, spectreArgs, vampireArgs):

	example_file_path = os.path.join(example_dir, subdir, filename)
	assert(os.path.exists(example_file_path)), (example_file_path + " doesn't exist!")

	spectre_out_file_path = "./spectre_out/" + subdir + "/" + filename + ".smtlib"
	vampire_out_file_path = "./vampire_out/" + subdir + "/" + filename + ".vout"

	# make sure the subdirectories exist
	if not os.path.exists("./spectre_out/" + subdir):
		os.mkdir("./spectre_out/" + subdir)	
	if not os.path.exists("./vampire_out/" + subdir):
		os.mkdir("./vampire_out/" + subdir)

	# run spectre on filepath and save result in spectre_out_file_path
	os.system(spectre_exec + " " + spectreArgs + " " + example_file_path + " > " + spectre_out_file_path)

	# run Vampire on spectre_out_file_path with given timelimit and save result in vampire_out_file_path
	os.system(vampire_exec + " " + vampireArgs + " -t " + str(timelimitSeconds) + "s " + spectre_out_file_path + " > " + vampire_out_file_path)

	# check whether proof was found and update stats
	if '% Refutation found. Thanks to Tanya!' in open(vampire_out_file_path, 'r').read():
		print("testing file " + os.path.join(subdir, filename) + ": SUCCESS")
		return True
	else:
		print("testing file " + os.path.join(subdir, filename) + ": DIDN'T WORK")
		return False

def runAllTests(timelimitSeconds, spectreArgs, vampireArgs):
	print("Running all benchmarks for " + str(timelimitSeconds) + " seconds")
	print("Spectre arguments: " + spectreArgs)
	print("Vampire arguments: " + vampireArgs)

	success = 0
	fail = 0

	# test each file in example_dir(recursively)
	for root, directories, filenames in os.walk(example_dir):
		print("\nScanning folder " + root)

		subdir = os.path.relpath(root, example_dir)
		for filename in sorted(filenames):
			if filename == ".DS_Store":
				continue

			result = process(subdir, filename, timelimitSeconds, spectreArgs, vampireArgs)
			if result == True:
				success += 1
			else:
				fail += 1

	# print stats
	print("\nSPECTRE: Overall Test results:")
	print("Running all benchmarks for " + str(timelimitSeconds) + " seconds")
	print("Spectre arguments: " + spectreArgs)
	print("Vampire arguments: " + vampireArgs)
	print("#success:" + str(success))
	print("#fail:" + str(fail))

def runSingleTest(relativePath, timelimitSeconds, spectreArgs, vampireArgs):
	print("Running benchmark at relative path " + relativePath + " for " + str(timelimitSeconds) + " seconds")
	print("Spectre arguments: " + spectreArgs)
	print("Vampire arguments: " + vampireArgs)
		
	subdir, filename = os.path.split(relativePath)
	result = process(subdir, filename, timelimitSeconds, spectreArgs, vampireArgs)

# main function
parser = argparse.ArgumentParser(description='Run spectre tests')
parser.add_argument("-f", "--single-file", required=False, default="", action="store", dest="name", help="run tests only on file from example-dir with given relative path")
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
