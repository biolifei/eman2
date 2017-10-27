#!/usr/bin/env python
from __future__ import print_function
# Muyuan Chen 2016-10
from EMAN2 import *
import numpy as np

def main():
	
	usage="""[prog] <json file from spt folder> <output hdf file>
	Read particle_parms_??.json file generated by e2spt_align.py and bin the orientaions. Output a class average like hdf file as e2eulerxplor.py input.
	"""
	parser = EMArgumentParser(usage=usage,version=EMANVERSION)
	parser.add_argument("--sym", type=str,help="symmetry", default="c1")
	parser.add_argument("--delta", type=int,help="angular step", default=5)
	(options, args) = parser.parse_args()
	logid=E2init(sys.argv)
	
	filein=args[0]
	fileout=args[1]
	sym=parsesym(options.sym)
	oris=sym.gen_orientations("eman",{"delta":options.delta})
	
	#### load transforms from json file
	jss=js_open_dict(filein)
	trans=[v["xform.align3d"] for v in list(jss.values())]
	
	k=0
	adiffs=[]
	cls=[0]*len(oris)
	for t in trans:
		tr=t.get_params("eman")
		t0=Transform({"type":"eman", "alt":tr["alt"], "az":tr["az"]})
		adiff=[ang_diff(t0, o) for o in oris]
		adiffs.append(np.min(adiff))
		cls[np.argmin(adiff)]+=1
	print("min err: {}, max err: {}".format(np.min(adiffs), np.max(adiffs)))
	print("std of orientations: {}".format(np.std(cls)))
	try: os.remove(fileout)
	except: pass
	e=EMData(1,1)
	for i,o in enumerate(oris):
		e["xform.projection"]=o
		e["ptcl_repr"]=cls[i]
		e.write_image(fileout,i)
	
	
	E2end(logid)
	
def run(cmd):
	print(cmd)
	launch_childprocess(cmd)
	
def ang_diff(a0,a1):
	a=a0*a1.inverse()
	rot=a.get_rotation("spin")
	o=rot["omega"]
	if o>90.:
		o=180.-o
	return o
	
if __name__ == '__main__':
	main()
	
