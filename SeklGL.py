# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 05:12:12 2018

@author: Will
"""

from RootsTool import  Point3d, RootAttributes, Skeleton, MetaNode3d, MetaEdge3d, MetaGraph

import OpenGL.GL as gl
import OpenGL.GLU as glu
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QInputDialog, QLineEdit, QFileDialog, QOpenGLWidget
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import qDebug
from PyQt5 import QtCore
from PyQt5 import QtGui

import PyQt5.QtOpenGL
import math
from camera import *

try:
    from OpenGL.GL import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL grabber",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)

from OpenGL.GLU import *
from OpenGL.GLUT import *

from numpy import *

import drawingUtil

class SkelGL():
    
    def __init__(self, parent=None):
        self.hasSkeleton = False
        self.hasMetaGraph = False
        self.colorMap = {}
        self.baseColor = (0.8, 0.2, 0.2, 1.0)
        
    
    def setSkeleton(self, skeleton : Skeleton):
        self.skeleton = skeleton
#        self.skeletonGL = self.makeSkeletonGL()
        self.hasSkeleton = True
        
        c = self.skeleton.sphereCenter
        diam = self.skeleton.sphereR
        
        self.skeletonViewBasePoint = v3(c.x, c.y, c.z - diam)
        self.skeletonCenter = v3(c.x, c.y, c.z)
        
    def setMetaGraph(self, metaGraph : MetaGraph):
        self.metaGraph = metaGraph
        self.metaGraphGL = self.makeMetaGraphGL()
        self.hasMetaGraph = True
        
        self.setSkeleton(self.metaGraph.skeleton)
        
    
    
    def makeMetaGraphGL(self):
        result = glGenLists(1)
        glNewList(result, GL_COMPILE)
        for edge in self.metaGraph.edgeConnections:
            v0 = self.metaGraph.nodeLocations[edge.node0]
            v1 = self.metaGraph.nodeLocations[edge.node1]
            thickness = edge.thickness
            drawingUtil.computeCylinderGL(v0, v1, self.baseColor, thickness, thickness)
            
        glEndList()
        return result
            
            
        for i in range(0, int(len(self.graph.edgeConnections))):
            edge = self
            vert1Index = self.metaGraph.edgeConnections[i].node0
            vert2Index = self.metaGraph.edgeConnections[i].node1
            point1 = self.metaGraph.nodeLocations[vert1Index]
            point2 = self.metaGraph.nodeLocations[vert2Index]
            
#            print(' ' + str(point1.x) + ' ' + str(point1.y) + ' ' + str(point1.z))
            gl.glVertex3f(point1.x, point1.y, point1.z)
            gl.glVertex3f(point2.x, point2.y, point2.z)
    
    
    
    
    
    
    
    
    
    
    
    
    
    