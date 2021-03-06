# Tamito KAJIYAMA <19 August 2009>

from freestyle import *
from Functions0D import CurveMaterialF0D
from logical_operators import *
from shaders import *
import bpy
import os

_HEADER = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN"
"http://www.w3.org/TR/2000/CR-SVG-20001102/DTD/svg-20001102.dtd">
<svg xml:space="default" width="%d" height="%d">
"""
_PATH = """\
<path fill="none" stroke="%s" stroke-width="%d" d="M %s" />
"""
_CLOSED_PATH = """\
<path fill="none" stroke="none" style="fill:%s" stroke-width="%d" d="M %s z" />
"""
_GROUP_START = """\
<g>
"""
_GROUP_END = """\
</g>
"""
_FOOTER = """\
</svg>
"""

class SVGWriter(StrokeShader):
	def __init__(self, f, w, h):
		StrokeShader.__init__(self)
		self.width, self.height = w, h
		self.file = f
		self.file.write(_HEADER % (w, h))
		self.groupcounter = 0

	def close(self):
		while self.groupcounter > 0:
			self.endgroup()
			self.groupcounter -= 1
		self.file.write(_FOOTER)
		self.file.close()

	def startgroup( self ):
		self.file.write( _GROUP_START )
		self.groupcounter += 1

	def endgroup( self ):
		self.file.write( _GROUP_END )
		self.groupcounter -= 1

	def shade(self, stroke):
		points = []

		stroken = len(stroke)
		fx = 0 
		fy = 0 
		lx = 1  
		ly = 1
		closed = False

		if stroken > 1:
			vi = 0
			for v in stroke:
				if vi == 0:
					fx, fy = v.point
				elif vi == stroken - 1:
					lx, ly = v.point
				vi += 1
			if fx == lx and fy == ly:
				closed = True
		
		for v in stroke:
			x, y = v.point
			points.append("%.3f,%.3f" % (x, self.height - y))

		points = " ".join(points)
		r, g, b = v.attribute.color * 255
		color = "#%02x%02x%02x" % (r, g, b)
		width = v.attribute.thickness
		width = width[0] + width[1]
		if closed:
			self.file.write(_CLOSED_PATH % (color, width, points))
		else:
			self.file.write(_PATH % (color, width, points))

import freestyle
scene = freestyle.getCurrentScene()
current_frame = scene.frame_current
output_dir = bpy.path.abspath(scene.render.filepath)
if not os.path.exists(output_dir):
	os.makedirs(output_dir)
path = os.path.join(output_dir, "output%06d.svg" % current_frame)
f = open(path, "wt")
w = scene.render.resolution_x
h = scene.render.resolution_y

upred = QuantitativeInvisibilityUP1D(0)
Operators.select(upred)
Operators.bidirectional_chain(ChainSilhouetteIterator(), NotUP1D(upred))
writer = SVGWriter(f, w, h)
writer.startgroup()
shaders_list = [
	ConstantThicknessShader(2),
	pyDepthDiscontinuityThicknessShader(1, 4),
	ConstantColorShader(0, 0, 0),
	pyMaterialColorShader(0.5),
	writer,
]
Operators.create(TrueUP1D(), shaders_list)
writer.close()
