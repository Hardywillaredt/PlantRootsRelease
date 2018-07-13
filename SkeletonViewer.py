# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 05:46:58 2017

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

from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from numpy import *

class SkeletonViewer(QOpenGLWidget):
    def __init__(self, parent=None):
        super(SkeletonViewer, self).__init__(parent)
#        fmt = QtOpenGL.QGLFormat()
#        fmt.setVersion(3,3)
#        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
#        fmt.setSampleBuffers(True)
  #      super(SkeletonViewer, self).__init__(fmt, None)
        self.viewingMode = 0
        self.bgColor = QColor.fromRgb(0, 0, 0)
        self.isSkeletonSet = False
        self.isGraphSet = False
        self.turnf = 0.0
        self.camera = Camera()
        self.camera.set_position(v3(0, 0, 10))
        self.camera.look_at(v3(0, 0, 0))
        self.camera.set_near(1)
        self.camera.set_far(1000)
        self.camera.set_fov(math.pi / 2)
        self.installEventFilter(self)
        self.setFocus()
        w = 300
        h = 300
        self.resize(w, h)
        
        
    def initializeGL(self):
        print(self.getOpenglInfo())

        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClearDepth(1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)
#        glu.gluLookAt(0, 1, -300, 0, 0, 0, 0, 1, 0)
#        gl.glTranslated(0.0, 0.0, -10.0)
    
    def getOpenglInfo(self):
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
        """.format(
            gl.glGetString(gl.GL_VENDOR),
            gl.glGetString(gl.GL_RENDERER),
            gl.glGetString(gl.GL_VERSION),
            gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        )
        return info
        
    def setSkeleton(self, skel):
        self.skeleton = skel
        self.skeleton.moveCenterTo(0.0, 0.0, 0.0)
        self.displaySkeleton = self.makeDisplaySkeleton()
        self.isSkeletonSet = True;
        c = self.skeleton.sphereCenter
        diam = self.skeleton.sphereR
        
        self.camera.set_position(v3(c.x, c.y, c.z + diam))
        self.camera.look_at(v3(c.x-diam, c.y-diam, c.z-diam))

        
    def setMetaGraph(self, graph):
        self.graph = graph
        self.displayGraph = self.makeDisplayGraph()
        self.displaySkeleton = self.makeDisplaySkeleton()
       
        self.graph.skeleton.findBoundingSphere()
        self.graph.skeleton.reload()
        
        
       
        
        self.center = self.graph.skeleton.center
        self.radius = self.graph.skeleton.radius

        self.isGraphSet = True
        
        
    def makeDisplayGraph(self):
        glList = gl.glGenLists(1)
        
        gl.glNewList(glList, gl.GL_COMPILE)
        gl.glLineWidth(2)
        gl.glColor3f(0.0, 0.9, 1.0)
        gl.glBegin(gl.GL_LINES)
        for i in range(0, int(len(self.graph.edgeConnections))):
            vert1Index = self.graph.edgeConnections[i].node0
            vert2Index = self.graph.edgeConnections[i].node1
            point1 = self.graph.nodeLocations[vert1Index]
            point2 = self.graph.nodeLocations[vert2Index]
            gl.glVertex3f(point1.x, point1.y, point1.z)
            gl.glVertex3f(point2.x, point2.y, point2.z)
        gl.glEnd()
        gl.glEndList()
        return glList
    
    def makeDisplaySkeleton(self):
        glList = gl.glGenLists(1)
        
        gl.glNewList(glList, gl.GL_COMPILE)
        gl.glLineWidth(2)
        gl.glColor3f(0.0, 0.9, 1.0)
        gl.glBegin(gl.GL_LINES)
        for i in range(0, int(len(self.graph.skeleton.edges))):
            vert1Index = self.graph.skeleton.edges.v0id
            vert2Index = self.graph.skeleton.edges.v1id
#            vert1Index = self.skeleton.edges[2*i]
#            vert2Index = self.skeleton.edges[2*i + 1]
            point1 = self.graph.skeleton.vertices[vert1Index]
            point2 = self.graph.skeleton.vertices[vert2Index]
            gl.glVertex3f(point1.x, point1.y, point1.z)
            gl.glVertex3f(point2.x, point2.y, point2.z)
        gl.glEnd()
        gl.glEndList()
        return glList
        
    def setViewingSkeleton(self):
        self.viewingMode = 1
    
    def setViewingMetaGraph(self):
        self.viewingMode = 2
        
    def paintGL(self):
#        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
#        glu.gluLookAt(0, 1, -300, 0, 0, 0, 0, 1, 0)

#        self.turnf = self.turnf + 0.01
#        gl.glRotatef(self.turnf, 0, 1, 0)
       
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_MODELVIEW)
 
 
        gl.glLoadIdentity()
        gl.glTranslatef(1.5, 0.0, -7.0)
 
        gl.glBegin(gl.GL_QUADS)
        gl.glColor3f(0.0, 1.0, 0.0);     # Green
        gl.glVertex3f( 1.0, 1.0, -1.0);
        gl.glVertex3f(-1.0, 1.0, -1.0);
        gl.glVertex3f(-1.0, 1.0,  1.0);
        gl.glVertex3f( 1.0, 1.0,  1.0);
 
        # Bottom face (y = -1.0)
        gl.glColor3f(1.0, 0.5, 0.0);     # Orange
        gl.glVertex3f( 1.0, -1.0,  1.0);
        gl.glVertex3f(-1.0, -1.0,  1.0);
        gl.glVertex3f(-1.0, -1.0, -1.0);
        gl.glVertex3f( 1.0, -1.0, -1.0);
 
        # Front face  (z = 1.0)
        gl.glColor3f(1.0, 0.0, 0.0);     # Red
        gl.glVertex3f( 1.0,  1.0, 1.0);
        gl.glVertex3f(-1.0,  1.0, 1.0);
        gl.glVertex3f(-1.0, -1.0, 1.0);
        gl.glVertex3f( 1.0, -1.0, 1.0);
 
        # Back face (z = -1.0)
        gl.glColor3f(1.0, 1.0, 0.0);     # Yellow
        gl.glVertex3f( 1.0, -1.0, -1.0);
        gl.glVertex3f(-1.0, -1.0, -1.0);
        gl.glVertex3f(-1.0,  1.0, -1.0);
        gl.glVertex3f( 1.0,  1.0, -1.0);
 
        # Left face (x = -1.0)
        gl.glColor3f(0.0, 0.0, 1.0);     # Blue
        gl.glVertex3f(-1.0,  1.0,  1.0);
        gl.glVertex3f(-1.0,  1.0, -1.0);
        gl.glVertex3f(-1.0, -1.0, -1.0);
        gl.glVertex3f(-1.0, -1.0,  1.0);
      
        # Right face (x = 1.0)
        gl.glColor3f(1.0, 0.0, 1.0);     # Magenta
        gl.glVertex3f(1.0,  1.0, -1.0);
        gl.glVertex3f(1.0,  1.0,  1.0);
        gl.glVertex3f(1.0, -1.0,  1.0);
        gl.glVertex3f(1.0, -1.0, -1.0);
        gl.glEnd();  # End of drawing color-cube

        
        
        
    def PickFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.loadFileName = QFileDialog.getOpenFileName(self.dlg, 'Open File', "")
        qDebug(str(self.loadFileName[0]))
        self.LoadSkeleton(str(self.loadFileName[0]))
        
    def LoadSkeleton(self, filename):
        self.skeleton = Skeleton(filename)
        
    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())
    
    def keyPressed(self, key):
        if key == QtCore.Qt.Key_A:
            a =1
#            move te camera left
        elif key == QtCore.Qt.Key_W:
            a =1
#            move the camera in
        elif key == QtCore.Qt.Key_S:
            a =1
#            move the camera out
        elif key == QtCore.Qt.Key_E:
            a =1
#            move the camera up
        elif key == QtCore.Qt.Key_D:
            a =1
#            move the camera down
        elif key == QtCore.Qt.Key_F:
            a =1
#            move the camera right
            


        
    