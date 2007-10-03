#!/usr/bin/env python

#
# Author: Steven Ludtke, 04/10/2003 (sludtke@bcm.edu)
# Copyright (c) 2000-2006 Baylor College of Medicine
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
#
#

import PyQt4
from PyQt4 import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt
from OpenGL import GL,GLU,GLUT
from valslider import ValSlider
from math import *
from EMAN2 import *
import EMAN2
import sys
import numpy
from emimageutil import ImgHistogram
from weakref import WeakKeyDictionary
from pickle import dumps,loads

class EMPlot2D(QtOpenGL.QGLWidget):
	"""A QT widget for drawing 2-D plots using matplotlib
	"""
	def __init__(self, parent=None):
		fmt=QtOpenGL.QGLFormat()
		fmt.setDoubleBuffer(True);
		QtOpenGL.QGLWidget.__init__(self,fmt, parent)
		self.axes=(0,1,-1)

		self.data={}				# List of Lists to plot 
			
	def setData(self,key,data):
		"""Set a keyed data set. The key should generally be a string describing the data.
		'data' is a tuple/list of tuples/list representing all values for a particular
		axis. eg - the points: 1,5; 2,7; 3,9 would be represented as ((1,2,3),(5,7,9)).
		Multiple axes may be set, and which axis represents which axis in the plot can be
		selected by the user."""
		
		if data : self.data[key]=data
		else : del self.data[key]
		
		self.data=data
		if data==None:
			self.updateGL()
			return
		
		self.updateGL()
		
	def initializeGL(self):
		GL.glClearColor(0,0,0,0)
	
	def paintGL(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
#		GL.glLoadIdentity()
#		GL.glTranslated(0.0, 0.0, -10.0)
		
		if not self.data : return
				
		
		GL.glRasterPos(0,0)
		GL.glPixelZoom(1.0,1.0)
		GL.glDrawPixels(self.width(),self.height(),GL.GL_LUMINANCE,GL.GL_UNSIGNED_BYTE,a)

	def resizeGL(self, width, height):
		side = min(width, height)
		GL.glViewport(0,0,self.width(),self.height())
	
		GL.glMatrixMode(GL.GL_PROJECTION)
		GL.glLoadIdentity()
		GLU.gluOrtho2D(0.0,self.width(),0.0,self.height())
		GL.glMatrixMode(GL.GL_MODELVIEW)
		GL.glLoadIdentity()
		
	
	def showInspector(self,force=0):
		if not force and self.inspector==None : return
		
		if not self.inspector : self.inspector=EMImageInspector2D(self)
		self.inspector.show()
	
	def closeEvent(self,event) :
		if self.inspector: self.inspector.close()
	
	def setAxes(self,key,xa,ya,za):
		self.axes=(0,1,-1)
		self.updateGL()
	
	#def dragEnterEvent(self,event):
		
		#if event.provides("application/x-eman"):
			#event.setDropAction(Qt.CopyAction)
			#event.accept()

	
	#def dropEvent(self,event):
#=		if EMAN2.GUIbeingdragged:
			#self.setData(EMAN2.GUIbeingdragged)
			#EMAN2.GUIbeingdragged=None
		#elif event.provides("application/x-eman"):
			#x=loads(event.mimeData().data("application/x-eman"))
			#self.setData(x)
			#event.acceptProposedAction()

	
	def mousePressEvent(self, event):
		if event.button()==Qt.MidButton:
			self.showInspector(1)
		#elif event.button()==Qt.RightButton:
			#self.rmousedrag=(event.x(),event.y())
		#elif event.button()==Qt.LeftButton:
			#if self.mmode==0:
				#self.emit(QtCore.SIGNAL("mousedown"), event)
				#return
			#elif self.mmode==1 :
				#try: 
					#del self.shapes["MEASL"]
				#except: pass
				#self.addShape("MEAS",("line",.5,.1,.5,lc[0],lc[1],lc[0]+1,lc[1],2))
	
	def mouseMoveEvent(self, event):
		pass
		#if self.rmousedrag and event.buttons()&Qt.RightButton:
			#self.origin=(self.origin[0]+self.rmousedrag[0]-event.x(),self.origin[1]-self.rmousedrag[1]+event.y())
			#self.rmousedrag=(event.x(),event.y())
			#self.update()
		#elif event.buttons()&Qt.LeftButton:
			#if self.mmode==0:
				#self.emit(QtCore.SIGNAL("mousedrag"), event)
				#return
			#elif self.mmode==1 :
				#self.addShape("MEAS",("line",.5,.1,.5,self.shapes["MEAS"][4],self.shapes["MEAS"][5],lc[0],lc[1],2))
				#dx=lc[0]-self.shapes["MEAS"][4]
				#dy=lc[1]-self.shapes["MEAS"][5]
				#self.addShape("MEASL",("label",.5,.1,.5,lc[0]+2,lc[1]+2,"%d,%d - %d,%d\n%1.1f,%1.1f (%1.2f)"%(self.shapes["MEAS"][4],self.shapes["MEAS"][5],lc[0],lc[1],dx,dy,hypot(dx,dy)),10,-1))
	
	def mouseReleaseEvent(self, event):
		pass
		#lc=self.scrtoimg((event.x(),event.y()))
		#if event.button()==Qt.RightButton:
			#self.rmousedrag=None
		#elif event.button()==Qt.LeftButton:
			#if self.mmode==0:
				#self.emit(QtCore.SIGNAL("mouseup"), event)
				#return
			#elif self.mmode==1 :
				#self.addShape("MEAS",("line",.5,.1,.5,self.shapes["MEAS"][4],self.shapes["MEAS"][5],lc[0],lc[1],2))

	def wheelEvent(self, event):
		pass
		#if event.delta() > 0:
			#self.setScale(self.scale + MAG_INC)	
		#elif event.delta() < 0:
			#if ( self.scale - MAG_INC > 0 ):
				#self.setScale(self.scale - MAG_INC)
		## The self.scale variable is updated now, so just update with that
		#if self.inspector: self.inspector.setScale(self.scale)

class EMPlot2DInspector(QtGui.QWidget):
	def __init__(self,target) :
		QtGui.QWidget.__init__(self,None)
		self.target=target
		
		self.vbl = QtGui.QVBoxLayout(self)
		self.vbl.setMargin(0)
		self.vbl.setSpacing(6)
		self.vbl.setObjectName("vbl")
		
		self.tabbar=QtGui.QTabBar()
		self.tabbar.addTab("Default")
		self.vbl.addWidget(self.tabbar)
		
		
		self.slidex=ValSlider(None,(0,1),"X col:",0)
		self.slidex.setIntonly(1)
		self.vbl.addWidget(self.slidex)
		
		self.slidey=ValSlider(None,(0,1),"Y col:",1)
		self.slidey.setIntonly(1)
		self.vbl.addWidget(self.slidey)
		
		self.slidec=ValSlider(None,(-1,1),"C col:",-1)
		self.slidec.setIntonly(1)
		self.vbl.addWidget(self.slidec)
		
		#self.hbl = QtGui.QHBoxLayout()
		#self.hbl.setMargin(0)
		#self.hbl.setSpacing(6)
		#self.hbl.setObjectName("hbl")
		#self.vbl.addLayout(self.hbl)
		
		#self.hist = ImgHistogram(self)
		#self.hist.setObjectName("hist")
		#self.hbl.addWidget(self.hist)
		
		#self.vbl2 = QtGui.QVBoxLayout()
		#self.vbl2.setMargin(0)
		#self.vbl2.setSpacing(6)
		#self.vbl2.setObjectName("vbl2")
		#self.hbl.addLayout(self.vbl2)
		
		#self.invtog = QtGui.QPushButton("Invert")
		#self.invtog.setCheckable(1)
		#self.vbl2.addWidget(self.invtog)
		
		#self.ffttog = QtGui.QPushButton("FFT")
		#self.ffttog.setCheckable(1)
		#self.vbl2.addWidget(self.ffttog)

		#self.hbl2 = QtGui.QHBoxLayout()
		#self.hbl2.setMargin(0)
		#self.hbl2.setSpacing(6)
		#self.hbl2.setObjectName("hboxlayout")
		#self.vbl.addLayout(self.hbl2)
		
		#self.mapp = QtGui.QPushButton("App")
		#self.mapp.setCheckable(1)
		#self.hbl2.addWidget(self.mapp)

		#self.mmeas = QtGui.QPushButton("Meas")
		#self.mmeas.setCheckable(1)
		#self.hbl2.addWidget(self.mmeas)

		#self.mmode=QtGui.QButtonGroup()
		#self.mmode.setExclusive(1)
		#self.mmode.addButton(self.mapp,0)
		#self.mmode.addButton(self.mmeas,1)
		
		#self.scale = ValSlider(self,(0.1,5.0),"Mag:")
		#self.scale.setObjectName("scale")
		#self.scale.setValue(1.0)
		#self.vbl.addWidget(self.scale)
		
		#self.mins = ValSlider(self,label="Min:")
		#self.mins.setObjectName("mins")
		#self.vbl.addWidget(self.mins)
		
		#self.maxs = ValSlider(self,label="Max:")
		#self.maxs.setObjectName("maxs")
		#self.vbl.addWidget(self.maxs)
		
		#self.brts = ValSlider(self,(-1.0,1.0),"Brt:")
		#self.brts.setObjectName("brts")
		#self.vbl.addWidget(self.brts)
		
		#self.conts = ValSlider(self,(0.0,1.0),"Cont:")
		#self.conts.setObjectName("conts")
		#self.vbl.addWidget(self.conts)
		
		#self.gammas = ValSlider(self,(.1,5.0),"Gam:")
		#self.gammas.setObjectName("gamma")
		#self.gammas.setValue(1.0)
		#self.vbl.addWidget(self.gammas)

		#self.lowlim=0
		#self.highlim=1.0
		#self.busy=0
		
		QtCore.QObject.connect(self.slidex, QtCore.SIGNAL("valueChanged"), self.newCols)
		QtCore.QObject.connect(self.slidey, QtCore.SIGNAL("valueChanged"), self.newCols)
		QtCore.QObject.connect(self.slidez, QtCore.SIGNAL("valueChanged"), self.newCols)
		
		
		#QtCore.QObject.connect(self.gammas, QtCore.SIGNAL("valueChanged"), self.newGamma)
		#QtCore.QObject.connect(self.invtog, QtCore.SIGNAL("toggled(bool)"), target.setInvert)
		#QtCore.QObject.connect(self.mmode, QtCore.SIGNAL("buttonClicked(int)"), target.setMMode)

	def newCols(self,val):
		if target: target.setAxes(self.slidex.value,self.slidey.value,self.slidec.value)
	


# This is just for testing, of course
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	window = EMPlot2D()
	if len(sys.argv)==1 : 
		window.setData("test",[[1,2,3,4],[2,3,4,3],[3,4,5,2]])

	window.show()
		
	sys.exit(app.exec_())
	
