# This script checks whether the given proof is correct.
# Use the same format for writing proofs as Vampire's output, 
# but use at the end of each line either
# 	[axiom] for all axioms of the proof
# 	[number1, ..., numberN] for all N-ary proof steps (N >= 0)
#  	
#  	Example:
# 	1. (= a 0) [axiom]
# 	3. (=> (= a 0) (= b 0)) [axiom]
#	5. (=> (= b 0)(= (f b) (f 0))) []
# 	6. (= b 0) [3,1]
# 	9. (= f(b) f(0)) [1,3,5]
# 
# furthermore declare all symbols used in any step before asserting proof axioms and steps.

vampire_exec = "/Users/bernhard/repos/vampire/build_xcode/bin/Debug/vampire"
vampire_args = "-t 5 --input_syntax smtlib2 --avatar off"
temp_file_path_smtlib = "/Users/bernhard/Desktop/test.smtlib"
temp_file_path_vout = "/Users/bernhard/Desktop/test.vout"

import os
import argparse
import re

class InferenceStep:
	def __init__(self, isAxiom, premiseIDs, conclusionID, conclusion):
		assert ((not isAxiom) or len(premiseIDs)==0)
		self.isAxiom = isAxiom
		self.premiseIDs = premiseIDs
		self.conclusionID = conclusionID
		self.conclusion = conclusion


def parseAxiom(line):
	proofAxiom = re.search(r"([0-9]+)\.(.*)\[axiom\]", line)
	proofAxiom = re.search(r"([0-9]+)\.(.*)\[axiom\]", line)
	if proofAxiom:
		return InferenceStep(True,[], proofAxiom.group(1), proofAxiom.group(2))
	else:
		return None

def constructRegexForStepOfArity(arity):
	# construct regex
	regex = r"([0-9]+)\.(.*)\["
	for argument in range(0,arity):
		regex += r"([0-9]+)"
		if argument != arity-1:
			regex += r","
	regex += r"\]"
	return regex

def parseStep(line):
	for arity in range(0,10):

		# search for regex
		regex = constructRegexForStepOfArity(arity)
		proofStep = re.search(regex, line)

		# if found, return InferenceStep
		if proofStep:
			premiseIDs = []
			for argument in range (0,arity):
				premiseID = proofStep.group(3 + argument)
				premiseIDs.append(premiseID)
			return InferenceStep(False, premiseIDs,	proofStep.group(1), proofStep.group(2))
	return None

def encodeValidityOfStep(header, step, numberToConclusion):
	string = header + "\n"
	for premiseID in step.premiseIDs:
		assert premiseID in numberToConclusion, "There is no step with ID " + str(premiseID)
		string += "(assert " + numberToConclusion[premiseID] + " )\n"
	string += "(assert-not " + step.conclusion + " )\n"
	print(string)
	return string

def prove(encoding):
	file = open(temp_file_path_smtlib,"w")
 	file.write(encoding)
 	file.close()

 	os.system(vampire_exec + " " + vampire_args + " " + temp_file_path_smtlib + " > " + temp_file_path_vout)

 	# check whether proof was found
	vampire_out_file = open(temp_file_path_vout, 'r')
	firstLine = vampire_out_file.readline()
	return (firstLine == "% Refutation found. Thanks to Tanya!\n")

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--filepath", help = "the filepath of the proof which should be checked", required=True, dest='filepath')
	filepath = parser.parse_args().filepath

	lines = open(filepath, 'r').readlines()

	numberToConclusion = {}
	linenumber = 0 # used to report the correct linenumber in assertions
	checkedInferenceCounter = 0 # used to report the number of checked inferences
	header = "" # collects the type declarations written in the proof file

	for line in lines:
		linenumber += 1

 		# if line is empty or starts with ;, ignore it
		if line == "\n" or re.match(r";.*",line):
			continue
		# try to parse line as smtlib-declaration
		if re.match(r"\(declare.*",line) or re.match(r"\(assert.*",line):
			header += line
			continue

		# try to parse line as proof axiom
		axiom = parseAxiom(line)
		if axiom != None:
			# save conclusion
			numberToConclusion[axiom.conclusionID] = axiom.conclusion
			continue
			
		# try to parse line as proof step with 0,1,...,10 premises
		step = parseStep(line)
		if step != None:

			# save conclusion
			numberToConclusion[step.conclusionID] = step.conclusion

			# encode validity of step
			encoding = encodeValidityOfStep(header, step, numberToConclusion)
		
			# prove that encoded step is sound
			success = prove(encoding)
			if success:
				checkedInferenceCounter += 1
			else:
				assert False, "Check for step " + step.conclusionID + " failed!"
			continue
		
		assert False, "Couldn't parse line " + str(linenumber) + ". Aborting"

	print("Checked " + str(checkedInferenceCounter) + " inferences, everything is fine!")

main()

