#!/usr/bin/env python

#
# Author: Jesus Galaz  1/1/2012 (rewritten)
# Copyright (c) 2011- Baylor College of Medicine
#
# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston MA 02111-1307 USA

from sys import argv
import os
from EMAN2 import *

current = os.getcwd()
filesindir = os.listdir(current)

def main():
	progname = os.path.basename(sys.argv[0])
	usage = """prog [options] <Volume file>

	WARNING: This program still under development.
	
	Tomography 3-D particle picker and annotation tool. Still under development."""

	parser = EMArgumentParser(usage=usage,version=EMANVERSION)
	
	parser.add_argument("--ncls", type=str, help="...", default=2)
	parser.add_argument("--nbasis", type=int, help="Basis vectors to use", default=3)

	parser.add_argument("--input", type=str, help="The name of the volumes stack that HAVE BEEN ALIGNED to a common reference", default=None)
	
	parser.add_argument("--oneclass", type=int, help="Create only a single class-average. Specify the class number.",default=None)
	parser.add_argument("--verbose", "-v", dest="verbose", action="store", metavar="n", type=int, default=0, help="verbose level [0-9], higner number means higher level of verboseness")			
	parser.add_argument("--lowpass",type=int,help="Resolution (integer, in Angstroms) at which you want to apply a gaussian lowpass filter to the tomogram prior to loading it for boxing",default=0, guitype='intbox', row=3, col=2, rowspan=1, colspan=1)
	parser.add_argument("--preprocess",type=str,help="""A processor (as in e2proc3d.py) to be applied to the tomogram before opening it. \nFor example, a specific filter with specific parameters you might like. \nType 'e2proc3d.py --processors' at the commandline to see a list of the available processors and their usage""",default=None)
	
	parser.add_argument('--reverse_contrast', action="store_true", default=False, help='''This means you want the contrast to me inverted while boxing, AND for the extracted sub-volumes.\nRemember that EMAN2 **MUST** work with "white" protein. You can very easily figure out what the original color\nof the protein is in your data by looking at the gold fiducials or the edge of the carbon hole in your tomogram.\nIf they look black you MUST specify this option''')
	
	parser.add_argument('--output', type=str, default='stack.hdf', help="Specify the name of the stack file where to write the extracted sub-volumes")
	parser.add_argument('--output_format', type=str, default='stack', help='''Specify 'single' if you want the sub-volumes to be written to individual files. You MUST still provide an output name in the regular way.\nFor example, if you specify --output=myparticles.hdf\nbut also specify --output_format=single\nthen the particles will be written as individual files named myparticles_000.hdf myparticles_001.hdf...etc''')
	
	(options, args) = parser.parse_args()
		
	stack_basis = options.input.replace(".hdf","_basis.hdf")
	stack_projection = options.input.replace(".hdf","_projection.hdf")
	
	nbasis =''
	ncls = 2
	cmd1=''
	cmd2=''
	cmd3=''
	
	cmd1 = 'e2msa.py --nbasis=' +  str(nbasis) + ' ' + stack  + ' ' + stack_basis
	
	cmd2 = 'e2basis.py --mean1 project ' + stack_basis + ' ' +  stack + ' ' + stack_projection
	
	cmd3 = 'e2classifykmeans.py --ncls=' + str(ncls) + ' --average --original=' + stack + ' ' + stack_projection
	
	if cmd1 is not '':
		print "I will execute the msaer.py on stack", stack
		os.system(cmd1 + " && " + cmd2 + " && " + cmd3)
		
	return()
	
if __name__ == "__main__":
    main()
