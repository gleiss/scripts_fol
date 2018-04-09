# This script checks whether the given proof is correct.
# Use the same format for writing proofs as Vampire's output, 
# but use at the end
# 	[axiom] for all proof steps without parents
# 	[number] for all unary proof steps
# 	[number, number] for all binary proof steps
# 	(no other steps are allowed)
#  	
#  	Example:
# 	1. a=0 [axiom]
# 	3. a=0 => b=0 [axiom]
# 	6. b=0 [3,1]
# 	9. $greatereq(b,0) [6]
# 
# furthermore declare all symbols used in any step in the header variable in this file

import re
import os

proofFilepath = "/Users/bernhard/Desktop/proof.vout"
vampire_exec = "/Users/bernhard/repos/vampire/build_xcode/bin/Debug/vampire"
temp_file_path_tptp = "/Users/bernhard/Desktop/test.tptp"
temp_file_path_vout = "/Users/bernhard/Desktop/test.vout"
header = """tff(a_type, type, a : $int).
tff(b_type, type, b : $int).\n
"""

def dumpUnaryProofStep(premise, conclusion):
	string = "tff(premise, axiom," + premise + ").\n"
	string += "tff(conclusion, conjecture," + conclusion + ").\n"
	return string

def dumpBinaryProofStep(premise1, premise2, conclusion):
	string = "tff(premise, axiom," + premise1 + ").\n"
	string += "tff(premise, axiom," + premise2 + ").\n"
	string += "tff(conclusion, conjecture," + conclusion + ").\n"
	return string

def doProving(encoding):
	file = open(temp_file_path_tptp,"w") 
 	file.write(header + encoding)
 	file.close()

 	os.system(vampire_exec + " " + temp_file_path_tptp + " > " + temp_file_path_vout)

 	# check whether proof was found and update stats
	vampire_out_file = open(temp_file_path_vout, 'r')
	firstLine = vampire_out_file.readline()
	return (firstLine == "% Refutation found. Thanks to Tanya!\n")

lines = open(proofFilepath, 'r').readlines()

numberToConclusion = {}
linenumber = 0
checkedInferenceCounter = 0

for line in lines:
	linenumber += 1
	sanityCounter = 0
	proofAxiom = re.search(r"([0-9]+)\.(.*)\[axiom\]", line)
	proofStepUnary = re.search(r"([0-9]+)\.(.*)\[([0-9]+)\]", line)
	proofStepBinary = re.search(r"([0-9]+)\.(.*)\[([0-9]+),([0-9]+)\]", line)

	if proofAxiom:
		sanityCounter += 1
		conclusionID = proofAxiom.group(1)
		conclusion = proofAxiom.group(2)
		numberToConclusion[conclusionID] = conclusion	

	if proofStepUnary:
		sanityCounter += 1
		conclusionID = proofStepUnary.group(1)
		conclusion = proofStepUnary.group(2)
		premiseID = proofStepUnary.group(3)
		numberToConclusion[conclusionID] = conclusion
		
		assert premiseID in numberToConclusion, "There is no step with ID " + str(premiseID)
		encoding = dumpUnaryProofStep(numberToConclusion[premiseID], conclusion)
		success = doProving(encoding)
		if success:
			checkedInferenceCounter += 1
		else:
			assert False, "Check for step " + conclusionID + " failed!"


	if proofStepBinary:
		sanityCounter += 1
		conclusionID = proofStepBinary.group(1)
		conclusion = proofStepBinary.group(2)
		premise1ID = proofStepBinary.group(3)
		premise2ID = proofStepBinary.group(4)
		numberToConclusion[conclusionID] = conclusion
		
		assert premise1ID in numberToConclusion, "There is no step with ID " + str(premise1ID)
		assert premise2ID in numberToConclusion, "There is no step with ID " + str(premise2ID)
		encoding = dumpBinaryProofStep(numberToConclusion[premise1ID], numberToConclusion[premise2ID], conclusion)
		success = doProving(encoding)
		if success:
			checkedInferenceCounter += 1
		else:
			assert False, "Check for step " + conclusionID + " failed!"

	assert sanityCounter == 1, "Line " + str(linenumber) + " doesn't represent a valid inference. Aborting"

print("Checked " + str(checkedInferenceCounter) + " inferences, everything is fine!")


