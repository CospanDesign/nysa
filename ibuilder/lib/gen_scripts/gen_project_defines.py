#gen_project_defines.py

from gen import Gen
import utils
from string import Template

class GenProjectDefines(Gen):
	"""Generate the top module for a project"""

	def __init__(self):
		#print "in GenProjectDefines"
		return

	def gen_script (self, tags={}, buf="", debug = False):
		"""Generate the project_defines.v"""
	
		if debug:
			print ""
			print ""
			print ""
			print ""
			print ""
			print ""
			print ""
		
		template = Template(buf) 
		vendor_string = "VENDOR_FPGA"

		board_dict = utils.get_board_config(tags["board"])
		if board_dict["build_tool"] == "xilinx":
		#if (tags["BUILD_TOOL"] == "xilinx"):
			buf = template.safe_substitute(VENDOR_FPGA = "VENDOR_XILINX")
			vendor_string = "VENDOR_XILINX"

		num_of_slaves = len(tags["SLAVES"])
		num_of_memories = 0
		if (debug):
			print "num of slaves: " + str(num_of_slaves)
			if ("MEMORY" in tags):
				print "num of memories: " + str(len(tags["MEMORY"]))
		if ("MEMORY" in tags):
			num_of_memories = len(tags["MEMORY"])	

		num_of_entities = str(num_of_slaves + num_of_memories)
		buf = template.substitute(PROJECT_NAME = tags["PROJECT_NAME"], NUMBER_OF_DEVICES=num_of_entities, VENDOR_FPGA=vendor_string, CLOCK_RATE=tags["CLOCK_RATE"])

		if debug:
			print "generating clock rate"

		

		return buf


	def get_name(self):
		print "Generate the project defines"


