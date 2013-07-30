from gen import Gen
import os
import platform

class GenXilinxBuildScript(Gen):
	"""Generates the build script"""

	def __init__(self):
		return

	def gen_name(self):
		print "generates the buildscript for a Xilinx based project"

	def gen_script(self, tags = {}, buf = "", user_paths = [], debug = False):
		#determine if the user has specified the .sycamore config
		#file in the home directory

		#determine if the "build_remote" flag is set to true
		self.gen_build_script(	remote=False,
								host=None,
								tool_location=None)

		return "WINNER!"

	def gen_build_script(self, remote=False, host=None, tool_location=None):
		"""
		generate a build script that can be run on the command line
		"""
		buf = ""
		#if remote is false then we are building locally

		#if the host is not defined then find out what it is
		host = os.name
		if host != 'posix':
			#don't support anything but Linux right now
			return False

		flag_64bit = False
		arch = platform.architecture()[0]
		if '64' in arch:
			floag_64bit = True

		#find the local Xilnx distribution
		latest_version = 0.0
		base_location = "/opt"
		for root, dirs, files in os.walk(base_location):
			print "dirs: " + str(dirs)
			if "Xilinx" not in dirs:
				print "didn't find Xilinx directory"
				return
			else:
				break

		first_flag = True
		data = os.walk(base_location + "/Xilinx")
		versions = []
		for root, dirs, files in os.walk(base_location + "/Xilinx"):
			if first_flag == False:
				break
			first_flag = False
			versions = dirs

		for v in versions:
			if float(v) > latest_version:
				latest_version = float(v)


		print "On a %s Linux box, Xilinx version: %f" % (arch, latest_version)

		#if the tool_lcoation is not declared then look for the latest xilinx toolchain
		#in the default place (/opt/Xilinx/)


