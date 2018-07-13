# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 14:26:21 2018

@author: Will
"""


import sys
import math

import numpy as np

from OpenGL.GL import *
import OpenGL.GL as gl

from OpenGL.GLU import *
from OpenGL.GLUT import *

from PyQt5 import QtCore, QtGui, QtOpenGL, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from RootsTool import  Point3d, RootAttributes, Skeleton, MetaNode3d, MetaEdge3d, MetaGraph, mgraph
import drawingUtil
import util
from ModeOptions import ConnectionModeOptions, BreakModeOptions, SplitModeOptions

import colorsys

from enum import Enum



def p3d2arr(p3d : Point3d):
    if isinstance(p3d, Point3d) or isinstance(p3d, MetaNode3d):
        return np.array([p3d.x, p3d.y, p3d.z])
    else:
        return p3d

class Colorization(Enum):
    COMPONENTS = 1
    THICKNESS = 2
    WIDTH = 3
    RATIO = 4
    DEGREE = 5


class Visualization(Enum):
    GEOMETRY = 1
    THICKNESS = 2

baseLineWidth = 3.0
highlightLineWidth = 8.0
lowlightLineWidth = 1.0



class LineGL():
    def __init__(self, v0, v1, v0id, v1id, thickness, width, idx, component, color, isBridge, isSkel = False, originalEdge = -1, v0rad=0.0, v1rad=0.0, scale=1.0):
        self.v0 = p3d2arr(v0)
        self.v1 = p3d2arr(v1)
        
        self.rad = thickness / 2.0
        self.thickness = thickness
        self.width = width
        self.id = idx
        self.component = component
        
        self.isSkel = isSkel
        self.originalEdge = originalEdge

        self.scale = scale
        self.baseScale = scale
        
        self.color = color
        self.isBridge = isBridge

        self.useVRad = False
        if v0rad != 0.0 and v1rad != 0.0:
            self.v0rad = v0rad
            self.v1rad = v1rad
            self.useVRad = True
        self.scale = scale
        
        self.isHighlight = False
        self.isLowlight = False
        self.callList = None
        
        self.baseVertices = []
        self.capVertices = []
        self.normals = []
        self.computeGeometry()
        
    def computeGeometry(self):
        if self.isSkel:
            return
        self.baseVertices = []
        self.capVertices = []
        self.normals = []
        if self.useVRad:
            R0 = self.v0rad
            R1 = self.v1rad
        else:
            R0 = self.rad
            R1 = self.rad
        
        R0 = R0 * self.scale
        R1 = R1 * self.scale
        
        maxR = max(R0, R1)
        numSides = max(int(maxR * 8), 8)
        
        for val in self.v0:
            if math.isnan(val):
                print('Point is NAN')
                return
        for val in self.v1:
            if math.isnan(val):
                print('Point is NAN')
                return
        same = True
        for val0, val1 in zip(self.v0, self.v1):
            if val0 != val1:
                same = False

        if same:
            return

        direction = self.v0 - self.v1
        
        
        direction = direction / np.linalg.norm(direction)
        
        vec1 = np.array([])
        
        if direction[1] == 0 and direction[2] == 0:
            vec1 = np.cross(direction, [0, 1, 0])
        else:
            vec1 = np.cross(direction, [1, 0, 0])
        
        vec2 = np.cross(direction, vec1)
        
        vec1 = vec1 / np.linalg.norm(vec1)
        vec2 = vec2 / np.linalg.norm(vec2)
        
        p0 = self.v0
        p1 = self.v1
        stepSize = 2 * math.pi / numSides
        theta = 0.0
#        glBegin(GL_TRIANGLE_STRIP)
        while theta < 2*math.pi:
            basePoint = p0 + R0*math.cos(theta)*vec1 + R0*math.sin(theta)*vec2
            capPoint = p1 + R1*math.cos(theta)*vec1 + R1*math.sin(theta)*vec2
            n = basePoint - p0
            n = n / np.linalg.norm(n)
            theta = theta + stepSize
            self.normals.append(n)
            self.baseVertices.append(basePoint)
            self.capVertices.append(capPoint)
    

    def generateCallList(self):
        if self.isSkel:
            return

        self.callList = gl.glGenLists(1)

        gl.glNewList(self.callList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_TRIANGLE_STRIP)

        for n, base, cap in zip(self.normals, self.baseVertices, self.capVertices):
            gl.glNormal3d(n[0], n[1], n[2])
            gl.glVertex3d(base[0], base[1], base[2])
            gl.glVertex3d(cap[0], cap[1], cap[2])

        if len(self.normals) > 0 and len(self.baseVertices) > 0 and len(self.capVertices) > 0:
            n = self.normals[0]
            base = self.baseVertices[0]
            cap = self.capVertices[0]
        
            gl.glNormal3d(n[0], n[1], n[2])
            gl.glVertex3d(base[0], base[1], base[2])
            gl.glVertex3d(cap[0], cap[1], cap[2])

        gl.glEnd()
        gl.glEndList()

    def issueGL(self, color = None):
        if color != None:
            self.color = color
        result = gl.glGenLists(1)
        
        gl.glNewList(result, gl.GL_COMPILE)
        #gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, self.color)
        gl.glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
        glShadeModel(GL_FLAT)
        gl.glBegin(gl.GL_TRIANGLE_STRIP)
        
        for n, base, cap in zip(self.normals, self.baseVertices, self.capVertices):
            gl.glNormal3d(n[0], n[1], n[2])
            gl.glVertex3d(base[0], base[1], base[2])
            gl.glVertex3d(cap[0], cap[1], cap[2])

        if len(self.normals) > 0 and len(self.baseVertices) > 0 and len(self.capVertices) > 0:
            n = self.normals[0]
            base = self.baseVertices[0]
            cap = self.capVertices[0]
        
            gl.glNormal3d(n[0], n[1], n[2])
            gl.glVertex3d(base[0], base[1], base[2])
            gl.glVertex3d(cap[0], cap[1], cap[2])

        gl.glEnd()
        gl.glEndList()
        return result

    def computeColor(self, lowColor, highColor, colorization : Colorization, percentiles):
        ratio = 0.0
        computeVal = 0.0
        if colorization == Colorization.THICKNESS:
            computeVal = self.thickness
        elif colorization == Colorization.WIDTH:
            computeVal = self.width
        elif colorization == Colorization.RATIO:
            if self.width <= 0:
                self.color = highColor
                return
            computeVal = self.thickness / self.width


        for i in range(0, len(percentiles) - 1):
            lower = percentiles[i]
            if computeVal > lower:
                upper = percentiles[i+1]
                if upper == lower:
                    break
                ratio = ratio + 0.1 * (self.thickness - lower) / (upper - lower)
                break
            else:
                ratio = ratio + 0.1

        self.color = lerpColors(lowColor, highColor, ratio)

        if self.isLowlight:
            self.color[3] = 0.6
        else:
            self.color[3] = 1.0

    #def issueGL(self, color):
    #    result = gl.glGenLists(1)
        
    #    gl.glNewList(result, gl.GL_COMPILE)
        
    #    gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, color)
        
    #    gl.glBegin(gl.GL_LINES)
        
    #    gl.glVertex3d(self.v0[0], self.v0[1], self.v0[2])
    #    gl.glVertex3d(self.v1[0], self.v1[1], self.v1[2])
    #    gl.glEnd()

    #    gl.glEndList()
    #    return result

    #def issueGLNoList(self):
    #    glShadeModel(GL_FLAT)
    #    gl.glBegin(gl.GL_TRIANGLE_STRIP)
        
    #    for n, base, cap in zip(self.normals, self.baseVertices, self.capVertices):
    #        gl.glNormal3d(n[0], n[1], n[2])
    #        gl.glVertex3d(base[0], base[1], base[2])
    #        gl.glVertex3d(cap[0], cap[1], cap[2])

    #    if len(self.normals) > 0 and len(self.baseVertices) > 0 and len(self.capVertices) > 0:
    #        n = self.normals[0]
    #        base = self.baseVertices[0]
    #        cap = self.capVertices[0]
        
    #        gl.glNormal3d(n[0], n[1], n[2])
    #        gl.glVertex3d(base[0], base[1], base[2])
    #        gl.glVertex3d(cap[0], cap[1], cap[2])

    #    gl.glEnd()
        
    def issueGLLine(self):     
        #gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, self.color)
        gl.glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
        
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3d(self.v0[0], self.v0[1], self.v0[2])
        gl.glVertex3d(self.v1[0], self.v1[1], self.v1[2])
        gl.glEnd()
        


    def display(self, colorization : Colorization, visualization : Visualization):
        if visualization == Visualization.GEOMETRY:
            gl.glLineWidth(self.scale)
            #if self.isHighlight:
            #    gl.glLineWidth(highlightLineWidth)
            #elif self.isLowlight:
            #    gl.glLineWidth(lowlightLineWidth)
            #else:
            #    gl.glLineWidth(baseLineWidth)

            self.issueGLLine()
        else:
            #gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, self.color)
            gl.glColor4f(self.color[0], self.color[2], self.color[2], self.color[3])
            drawCallList(self.callList)


    def highlight(self):
        self.isHighlight = True
        self.isLowlight = False
        self.scale = self.baseScale * 1.6
        self.computeGeometry()
        self.generateCallList()

    def unhighlight(self):
        self.isHighlight = False
        self.isLowlight = False
        self.scale = self.baseScale
        self.computeGeometry()
        self.generateCallList()

    def lowlight(self):
        self.isHighlight = False
        self.isLowlight = True
        self.scale = self.baseScale / 1.6
        self.computeGeometry()
        self.generateCallList()
            
    def setScale(self, scale):
        self.baseScale = scale
        if self.isHighlight:
            self.scale = self.baseScale * 1.6
        else:
            self.scale = self.baseScale
        
        
        
class PointGL():
    def __init__(self, v0, thickness, width, idx, component, degree, isSkel = False, scale : float = 1.0):
        self.v0 = p3d2arr(v0)
        self.radius = thickness / 2.0
        self.thickness = thickness
        self.width = width
        if self.radius <= 0:
            self.radius = 1
        if self.radius > 1:
            self.radius = 1
        self.id = idx
        self.component = component
        self.degree = degree


        self.isSkel = isSkel

        self.scale = scale
        self.baseScale = scale
        self.isHighlight = False
        
        
    def issueGL(self, color):
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, color)
        glPushMatrix()
        glTranslated(self.v0[0], self.v0[1], self.v0[2])
        quadric = gluNewQuadric()
        gluQuadricOrientation(quadric, GLU_OUTSIDE)
        if self.isSkel:
            gluSphere(quadric, self.scale, 40, 40)
        else:
            gluSphere(quadric, self.scale, 40, 40)
        glPopMatrix()
        
    def highlight(self):
        self.isHighlight = True
        self.scale = self.baseScale * 1.6
        
    def unhighlight(self):
        self.isHighlight = False
        self.scale = self.baseScale
            
    def setScale(self, scale):
        self.baseScale = scale
        if self.isHighlight:
            self.scale = self.baseScale * 1.6
        else:
            self.scale = self.baseScale



def lerpColors(lowColor, highColor, between : float):
    result = [0.0, 0.0, 0.0, 1.0]
    for i in range(0, 3):
        result[i] = lowColor[i] + (highColor[i] - lowColor[i])*between
    return result

class MetaGraphGL(QObject):
    @pyqtSlot(int)
    def unselectNode(self, nodeId):
        self.MetaNodesGL[nodeId].unhighlight()
        self.rebuildMetaNodesGLList()
        
    @pyqtSlot(int)
    def selectNode(self, nodeId):
        self.MetaNodesGL[nodeId].highlight()
        self.rebuildMetaNodesGLList()
        
    @pyqtSlot(object)
    def unselectEdges(self, edgeIds):
        for edgeId in edgeIds:
            if self.graph.edgeConnections[edgeId].isBridge:
                self.MetaEdgesGL[edgeId].setScale(1)
                #self.MetaEdgesGL[edgeId].lowlight()
                for skelEdge in self.SkelEdgesGL[edgeId]:
                    skelEdge.setScale(1)
            else:
                self.MetaEdgesGL[edgeId].unhighlight()
                self.MetaEdgesGL[edgeId].setScale(self.suggestedEdgeScale)
                for skelEdge in self.SkelEdgesGL[edgeId]:
                    skelEdge.unhighlight()
                    skelEdge.setScale(self.suggestedEdgeScale)
            self.rebuildMetaEdgeGLList(edgeId)
            self.rebuildMetaEdgeGLList(edgeId)
        
    @pyqtSlot(int)
    def selectEdge(self, edgeId):
        self.MetaEdgesGL[edgeId].highlight()
        for skelEdge in self.SkelEdgesGL[edgeId]:
            skelEdge.highlight()
        self.rebuildSkelEdgeGLList(edgeId)
        self.rebuildMetaEdgeGLList(edgeId)
    
    @pyqtSlot()
    def rebuildNodes(self):
        self.rebuildMetaNodesGLList()
        
    @pyqtSlot(object)
    def componentsChanged(self, componentMap):
        self.minimizedComponentMap = componentMap
        self.rebuildMetaNodesGLList()
        #self.rebuildGLLists()

    @pyqtSlot(object)
    def updateGraphSlot(self, graphGL):
        resolveGraphs(self, graphGL)

    @pyqtSlot(object)
    def loadGraphSlot(self, graphGL):
        resolveGraphs(self, graphGL)
        self.graph.skeleton.findBoundingSphere()
        newCenter = p3d2arr(self.graph.skeleton.center)
        for val0, val1 in zip(self.center, newCenter):
            if val0 != val1:
                self.center = newCenter
                self.centerChanged.emit(self.center)
                break

    @pyqtSlot()
    def enterGraphView(self):
        self.updateDisplayMode(0)
        self.enteringGraphView.emit(True)

    @pyqtSlot()
    def enterSkeletonView(self):
        self.updateDisplayMode(1)
        self.enteringSkeletonView.emit(True)

    @pyqtSlot()
    def enterBothView(self):
        self.updateDisplayMode(2)
        self.enteringBothView.emit(True)

    @pyqtSlot()
    def colorizeThickness(self):
        self.edgeColorization = Colorization.THICKNESS
        if self.graph == None:
            return
        
        for edgeGL in self.MetaEdgesGL:
            edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.thicknessPercentiles)
        for edgeGLList in self.SkelEdgesGL:
            for edgeGL in edgeGLList:
                edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.thicknessPercentiles)
    @pyqtSlot()
    def colorizeWidth(self):
        self.edgeColorization = Colorization.WIDTH
        if self.graph == None:
            return
        
        for edgeGL in self.MetaEdgesGL:
            edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.widthPercentiles)
        for edgeGLList in self.SkelEdgesGL:
            for edgeGL in edgeGLList:
                edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.widthPercentiles)
    @pyqtSlot()
    def colorizeRatio(self):
        self.edgeColorization = Colorization.RATIO
        if self.graph == None:
            return
        for edgeGL in self.MetaEdgesGL:
            edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.ratioPercentiles)

        for edgeGLList in self.SkelEdgesGL:
            for edgeGL in edgeGLList:
                edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.ratioPercentiles) 

    @pyqtSlot()
    def colorizeComponents(self):
        self.edgeColorization = Colorization.COMPONENTS
        if self.graph == None:
            return
        
        for edgeGL in self.MetaEdgesGL:
            edgeGL.color = self.colorTable[edgeGL.component]

        for edgeGLList in self.SkelEdgesGL:
            for edgeGL in edgeGLList:
                edgeGL.color = self.colorTable[edgeGL.component]
            
    @pyqtSlot(object, object, object)
    def highColorChanged(self, r, g, b):
        self.highColor = [r, g, b, 1.0]
        if self.edgeColorization == Colorization.RATIO:
            self.colorizeRatio()
        elif self.edgeColorization == Colorization.THICKNESS:
            self.colorizeThickness()
        elif self.edgeColorization == Colorization.WIDTH:
            self.colorizeWidth()

    @pyqtSlot(object, object, object)
    def lowColorChanged(self, r, g, b):
        self.lowColor = [r, g, b, 1.0]

        if self.edgeColorization == Colorization.RATIO:
            self.colorizeRatio()
        elif self.edgeColorization == Colorization.THICKNESS:
            self.colorizeThickness()
        elif self.edgeColorization == Colorization.WIDTH:
            self.colorizeWidth()


    @pyqtSlot(float)
    def nodeScaleChanged(self, scale):
        self.suggestedNodeScale = scale
        if self.currentMode != 0:
            return
        print(self.suggestedNodeScale)
        for nodeGL in self.MetaNodesGL:
            if nodeGL.degree == 1:
                nodeGL.setScale(self.suggestedNodeScale)
            else:
                nodeGL.setScale(self.suggestedNodeScale/5.0)
        self.rebuildMetaNodesGLList()

    @pyqtSlot(float)
    def edgeScaleChanged(self, scale):
        self.suggestedEdgeScale = scale
        if self.currentMode != 1 and self.currentMode != 2:
            return
        for edgeI in range(0, len(self.MetaEdgesGL)):
            if self.MetaEdgesGL[edgeI].isBridge:
                self.MetaEdgesGL[edgeI].setScale(1.0)
            else:
                self.MetaEdgesGL[edgeI].setScale(self.suggestedEdgeScale * 2.0)

            #self.rebuildMetaEdgeGLList(edgeI)

        for edgeI in range(0, len(self.SkelEdgesGL)):
            if self.MetaEdgesGL[edgeI].isBridge:
                for edgeGL in self.SkelEdgesGL[edgeI]:
                    edgeGL.setScale(1.0)
            else:
                for edgeGL in self.SkelEdgesGL[edgeI]:
                    edgeGL.setScale(self.suggestedEdgeScale * 2.0)

            #self.rebuildSkelEdgeGLList(edgeI)


    centerChanged = pyqtSignal(object)
    enteringGraphView = pyqtSignal(bool)
    enteringSkeletonView = pyqtSignal(bool)
    enteringBothView = pyqtSignal(bool)
    numEdgesToBreakUpdated = pyqtSignal(int)
    

    
    def __init__(self, parent = None):
        super(MetaGraphGL, self).__init__(parent)
        self.hasMetaGraph = False
        self.nodeSizeMap = {}
        self.minimizedComponentMap = {}
        self.graph = None
        
        self.modes = {-1 : 'NoMode', 0 : 'Connection Mode', 1 : 'Separation Mode', 2 : 'Spltting Mode'}
        self.currentMode = -1
        self.displayModes = {0 : 'Graph', 1 : 'Skeleton'}
        self.currentDisplayMode = 1
        self.edgeColorization = Colorization.THICKNESS
        self.nodeColorization = Colorization.THICKNESS
        self.visualization = Visualization.GEOMETRY

        if self.edgeColorization == Colorization.COMPONENTS:
            print('colorization set to none')
        
        
        self.graphGLNodesList = None
        self.MetaNodesGL = []
        self.MetaEdgesGL = []
        self.SkelEdgesGL = []
        #self.SkelNodesGL = []
        self.colorTable = drawingUtil.ColorTable
        self.highlightColorTable = []
        self.lowlightColorTable = []
        self.numComponents = 0
        center = [0.0, 0.0, 0.0]
        self.center = np.array(center)
        self.suggestedNodeScale = 2.5
        self.suggestedEdgeScale = 2.5
        
        self.connectionOptions = ConnectionModeOptions(self)
        self.connectionOptions.sigNodeUnselected.connect(self.unselectNode)
        self.connectionOptions.sigNodeSelected.connect(self.selectNode)
        self.connectionOptions.sigComponentsChanged.connect(self.componentsChanged)
        self.connectionOptions.sigSliderScaleChanged.connect(self.nodeScaleChanged)


        self.breakOptions = BreakModeOptions(self)
        self.breakOptions.sigEdgeSelected.connect(self.selectEdge)
        self.breakOptions.sigEdgeUnselected.connect(self.unselectEdges)
        self.numEdgesToBreakUpdated.connect(self.breakOptions.numEdgesToBreakUpdated)
        self.breakOptions.sigSliderScaleChanged.connect(self.edgeScaleChanged)
        
        self.splitOptions = SplitModeOptions(self)
        self.splitOptions.sigEdgeSelected.connect(self.selectEdge)
        self.splitOptions.sigEdgesUnselected.connect(self.unselectEdges)
        self.numEdgesToBreakUpdated.connect(self.splitOptions.numEdgesToBreakUpdated)
        self.splitOptions.sigSliderScaleChanged.connect(self.edgeScaleChanged)
        
    def updateDisplayMode(self, nextDisplayMode : int):
        if self.currentDisplayMode == nextDisplayMode:
            return
        else:
            #if self.currentDisplayMode == 2:
            #    for edgeGL in self.MetaEdgesGL:
            #        edgeGL.setScale(1.0)
            #    for nodeGL in self.MetaNodesGL:
            #        nodeGL.setScale(1.0)
            #    for i in range(0, len(self.MetaEdgesGL)):
            #        self.rebuildMetaEdgeGLList(i)
            #    self.rebuildMetaNodesGLList()
            #elif nextDisplayMode == 2:
            #    for edgeGL in self.MetaEdgesGL:
            #        edgeGL.setScale(1.6)
            #    for nodeGL in self.MetaNodesGL:
            #        nodeGL.setScale(1.6)
                #for i in range(0, len(self.MetaEdgesGL)):
                #    self.rebuildMetaEdgeGLList(i)
                #self.rebuildMetaNodesGLList()
            self.currentDisplayMode = nextDisplayMode
        
    def setMetaGraph(self, graph : MetaGraph):
        self.graph = graph
        self.hasMetaGraph = True
        self.numComponents = len(self.graph.componentNodeMap)
        self.minimizedComponentMap = {}

        print('setting up minimized component map with ', self.numComponents, ' elements')
        for key in self.graph.componentNodeMap.keys():
            self.minimizedComponentMap[key] = False
        self.graph.skeleton.findBoundingSphere()
        self.center = p3d2arr(self.graph.skeleton.center)
        self.MetaNodesGL = []
        self.MetaEdgesGL = []
        #self.SkelNodesGL = {}
        self.SkelEdgesGL = []
        self.fillColorTables()
                
        
        for node in self.graph.nodeLocations:
            #print('node size ', node.size, ' order ', node.order, ' component ', node.component)
            self.MetaNodesGL.append(PointGL(node, node.thickness, node.width, node.order, node.component, node.degree, False))
            
        skeleton = self.graph.skeleton
        metaEdgeI = 0
        for edge in self.graph.edgeConnections:
            v0 = self.graph.nodeLocations[edge.node0]
            v1 = self.graph.nodeLocations[edge.node1]
            if math.isnan(edge.thickness):
                print('edge thickness NAN')
            if math.isnan(edge.order):
                print('edge order NAN')
            if math.isnan(edge.component):
                print('edge component NAN')

            #print('MetaEdge v0 ', v0.order, ' v1 ', v1.order)
            self.MetaEdgesGL.append(LineGL(v0, v1, edge.node0, edge.node1, edge.thickness, edge.width, edge.order, edge.component, self.colorTable[edge.component], edge.isBridge))
            self.SkelEdgesGL.append([])
            for skelEdge in edge.edges:
                #print('skel edge v0id ', skelEdge.v0id, ' v1 id ', skelEdge.v1id, ' thickness ', skelEdge.thickness, ' component ', edge.component)
                
                #v0 = PointGL(skeleton.vertices[skelEdge.v0id], skelEdge.thickness /2.0, skelEdge.v0id, edge.component, True)
                #v1 = PointGL(skeleton.vertices[skelEdge.v1id], skelEdge.thickness /2.0, skelEdge.v1id, edge.component, True)
                line = LineGL(skeleton.vertices[skelEdge.v0id], skeleton.vertices[skelEdge.v1id], skeleton.vertices[skelEdge.v0id].id, skeleton.vertices[skelEdge.v1id], skelEdge.thickness, skelEdge.width, edge.order, edge.component, self.colorTable[edge.component], edge.isBridge, True, metaEdgeI)
                #if not edge.component in self.SkelNodesGL:
                    #self.SkelNodesGL[edge.component] = []
                #if not edge.component in self.SkelEdgesGL:
                #    self.SkelEdgesGL[edge.component] = []
                #self.SkelNodesGL[edge.component].append(v0)
                #self.SkelNodesGL[edge.component].append(v1)
                self.SkelEdgesGL[metaEdgeI].append(line)

            metaEdgeI = metaEdgeI + 1
        print('edges finished')


    
    def fillColorTables(self):
        if self.numComponents > len(self.colorTable):
            for i in range(len(self.colorTable), self.numComponents):
                randColor = np.random.ranf(3)
                self.colorTable.append([randColor[0], randColor[1], randColor[2], 1.0])
        self.highlightColorTable = []
        self.lowlightColorTable = []
        for color in self.colorTable:
            self.highlightColorTable.append([min(color[0]*1.5, 1.0), min(color[1]*1.5, 1.0), min(color[2]*1.5, 1.0), min(color[3]*1.5, 1.0)])
            self.lowlightColorTable.append([color[0], color[1], color[2], color[3]/10.0])
    
    
    def rebuildGLLists(self):
        
        return
        print('rebuilding gl lists')
        #self.graphGLEdgesLists = []
        
        #for i in range(0, len(self.MetaEdgesGL)):
        #    self.graphGLEdgesLists.append(None)
        #    self.rebuildMetaEdgeGLList(i)
        
        if self.currentMode == 0:
            for nodeGL in self.MetaNodesGL:
                if nodeGL.degree == 1:
                    nodeGL.setScale(self.suggestedNodeScale)
                else:
                    nodeGL.setScale(self.suggestedNodeScale/5.0)

        else:
            for nodeGL in self.MetaNodesGL:
                nodeGL.setScale(1.0)

        self.rebuildMetaNodesGLList()
        

        if self.edgeColorization == Colorization.THICKNESS:
            for edgeGL in self.MetaEdgesGL:
                edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.thicknessPercentiles)
            for edgeGLList in self.SkelEdgesGL:
                for edgeGL in edgeGLList:
                    edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.thicknessPercentiles)
        elif self.edgeColorization == Colorization.WIDTH:
            for edgeGL in self.MetaEdgesGL:
                edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.widthPercentiles)
            for edgeGLList in self.SkelEdgesGL:
                for edgeGL in edgeGLList:
                    edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.widthPercentiles)
        elif self.edgeColorization == Colorization.RATIO:
            for edgeGL in self.MetaEdgesGL:
                edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.ratioPercentiles)
            for edgeGLList in self.SkelEdgesGL:
                for edgeGL in edgeGLList:
                    edgeGL.computeColor(self.lowColor, self.highColor, self.edgeColorization, self.graph.skeleton.ratioPercentiles) 
        elif self.edgeColorization == Colorization.COMPONENTS:
            for edgeGL in self.MetaEdgesGL:
                edgeGL.color = self.colorTable[edgeGL.component]
            for edgeGLList in self.SkelEdgesGL:
                for edgeGL in edgeGLList:
                    edgeGL.color = self.colorTable[edgeGL.component]

        for edgeGLList in self.SkelEdgesGL:
            for edgeGL in edgeGLList:
                edgeGL.generateCallList()

        for edgeGL in self.MetaEdgesGL:
            edgeGL.generateCallList()

                    
        #self.rebuildSkelEdgesGLList()
            
        #self.rebuildSkelNodesGLList()

        print('finished rebuilding gl lists')
        
    def rebuildMetaEdgeGLList(self, idx : int):
        self.MetaEdgesGL[idx].generateCallList()

        #edgeGL = self.MetaEdgesGL[idx]
    #    color = []
    #    if self.minimizedComponentMap[edgeGL.component]:
    #        color = self.lowlightColorTable[edgeGL.component]
    #    elif edgeGL.isHighlight:
    #        color = self.highlightColorTable[edgeGL.component]
    #    else:
    #        color = self.colorTable[edgeGL.component]
        
    #    self.graphGLEdgesLists[idx] = edgeGL.issueGL(color)
        
    def rebuildMetaNodesGLList(self):
        self.graphGLNodesList = gl.glGenLists(1)
        gl.glNewList( self.graphGLNodesList, gl.GL_COMPILE)
        for pointGL in self.MetaNodesGL:
            color = []
            if self.minimizedComponentMap[pointGL.component]:
                continue
                color = self.lowlightColorTable[pointGL.component]
                #gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, self.lowlightColorTable[pointGL.component])
                #gl.glColor4f(self.lowlightColorTable[pointGL.component][0],self.lowlightColorTable[pointGL.component][1], self.lowlightColorTable[pointGL.component][2], self.lowlightColorTable[pointGL.component][3])
            if pointGL.isHighlight:
                color = self.highlightColorTable[pointGL.component]
                #gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, self.highlightColorTable[pointGL.component])
                #gl.glColor4f(self.highlightColorTable[pointGL.component][0], self.highlightColorTable[pointGL.component][1], self.highlightColorTable[pointGL.component][2], self.highlightColorTable[pointGL.component][3])
            else:
                color = self.colorTable[pointGL.component]
                if self.nodeColorization == Colorization.COMPONENTS:
                    color = self.colorTable[pointGL.component]

                #gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, self.colorTable[pointGL.component])
                #gl.glColor4f(self.colorTable[pointGL.component][0], self.colorTable[pointGL.component][1], self.colorTable[pointGL.component][2], self.colorTable[pointGL.component][3])
            
            pointGL.issueGL(color)
            
        gl.glEndList()
        
    def rebuildSkelEdgeGLList(self, idx : int):
        for edgeGL in self.SkelEdgesGL[idx]:
            edgeGL.generateCallList()
        
    #    edgeGL = self.SkelEdgesGL[idx]
    #    color = []
    #    if self.minimizedComponentMap[edgeGL.component]:
    #        color = self.lowlightColorTable[edgeGL.component]
    #    elif edgeGL.isHighlight:
    #        color = self.highlightColorTable[edgeGL.component]
    #    else:
    #        color = self.colorTable[edgeGL.component]
            
    #    self.skelGLEdgesLists[idx] = edgeGL.issueGL(color)
        
    def rebuildSkelEdgesGLList(self):
        for edgeGLList in self.SkelEdgesGL:
            for edgeGL in edgeGLList:
                edgeGL.generateCallList()
    #    for component in self.SkelEdgesGL:
    #        componentCallList = gl.glGenLists(1)
    #        gl.glNewList(componentCallList, gl.GL_COMPILE)
    #        for edgeGL in self.SkelEdgesGL[component]:
    #            if self.minimizedComponentMap[edgeGL.component]:
    #                gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE, self.lowlightColorTable[edgeGL.component])
    #            elif edgeGL.isHighlight:
    #                gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE, self.highlightColorTable[edgeGL.component])
    #            else:
    #                gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE, self.colorTable[edgeGL.component])
            
    #            edgeGL.issueGLNoList()
    #        gl.glEndList()
    #        self.skelGLEdgesLists[component] = componentCallList


    #def rebuildSkelNodesGLList(self):
    #    for component in self.SkelNodesGL:
    #        componentCallList = gl.glGenLists(1)
    #        gl.glNewList(componentCallList, gl.GL_COMPILE)
    #        for pointGL in self.SkelNodesGL[component]:
    #            if self.minimizedComponentMap[pointGL.component]:
    #                gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, self.lowlightColorTable[pointGL.component])
    #            elif pointGL.isHighlight:
    #                gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, self.highlightColorTable[pointGL.component])
    #            else:
    #                gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, self.colorTable[pointGL.component])
    #            pointGL.issueGL()

    #        gl.glEndList()
    #        self.skelGLNodesList[component] = componentCallList
                    
        
    def getFirstEdgeHit(self, origin : np.array, ray : np.array):
        minDist = 100000000
        hitFound = False
        edgeHit = None
        edgeHitId = -1
        if not self.hasMetaGraph:
            return (hitFound, edgeHit, edgeHitId) 
        if self.currentDisplayMode == 0 or self.currentDisplayMode == 2:
            for edge in self.MetaEdgesGL:
                if self.minimizedComponentMap[edge.component]:
                    continue
                p0 = edge.v0
                p1 = edge.v1
            
                
                (doesIntersect, distance) = util.intersectRayCylinder(origin, ray, p0, p1, edge.scale)
                if not doesIntersect:
                    (doesIntersect, distance) = util.intersectRaySphere(origin, ray, p0, edge.scale)
                if not doesIntersect:
                    (doesIntersect, distance) = util.intersectRaySphere(origin, ray, p1, edge.scale)
            
                if doesIntersect:
                    if distance < minDist: 
                        hitFound = True
                        minDist = distance
                        edgeHit = self.graph.edgeConnections[edge.id]
                        edgeHitId = edge.order

        if self.currentDisplayMode == 1 or self.currentDisplayMode == 2:
            metaEdgeI = -1
            for edgeList in self.SkelEdgesGL:
                metaEdgeI = metaEdgeI + 1
                for edgeGL in edgeList:
                    if self.minimizedComponentMap[edgeGL.component]:
                        continue
                    p0 = edgeGL.v0
                    p1 = edgeGL.v1
            
                
                    (doesIntersect, distance) = util.intersectRayCylinder(origin, ray, p0, p1, edgeGL.scale)
            
                    if doesIntersect:
                        if distance < minDist: 
                            hitFound = True
                            minDist = distance
                            edgeHit = self.graph.edgeConnections[metaEdgeI]
                            edgeHitId = metaEdgeI

        if hitFound:
            print('edge hit')
        return (hitFound, edgeHit, edgeHitId)
        
    def getFirstNodeHit(self, origin : np.array, ray : np.array):
        minDist = 1000000000
        hitFound = False
        nodeHit = None
        nodeHitId = -1
        
        if not self.hasMetaGraph:
            return(hitFound, nodeHit, nodeHitId)

        for node in self.MetaNodesGL:
            if self.minimizedComponentMap[node.component]:
                continue
            p = node.v0
            (doesIntersect, distance) = util.intersectRaySphere(origin, ray, p, node.scale)
            
            if doesIntersect:
                if distance < minDist:
                    hitFound = True
                    minDist = distance
                    nodeHit = self.graph.nodeLocations[node.id]
                    nodeHitId = node.id
        if hitFound:
            print('node hit')
        return(hitFound, nodeHit, nodeHitId)
        
    
    def doPicking(self, origin : np.array, ray : np.array):
        if self.currentMode == 0:
            (hitFound, nodeHit, nodeHitId) = self.getFirstNodeHit(origin, ray)
            if hitFound:
                self.connectionOptions.pickConnectionNode(nodeHit)
        elif self.currentMode == 1:
            (hitFound, edgeHit, edgeHitId) = self.getFirstEdgeHit(origin, ray)
            if hitFound:
                self.breakOptions.selectBreakEdge(edgeHit)
        elif self.currentMode == 2:
            (hitFound, edgeHit, edgeHitId) = self.getFirstEdgeHit(origin, ray)
            if hitFound:
                self.splitOptions.selectEdge(edgeHit)

    def changeEdgeSelection(self, edgeIds):
        self.unselect()
        for edgeId in edgeIds:
            if edgeId > -1 and edgeId < len(self.MetaEdgesGL):
                self.MetaEdgesGL[edgeId].highlight()
                self.rebuildMetaGLEdgeList(edgeId)
                metaEdge = self.graph.edgeConnections[edgeId]
                self.MetaNodesGL[metaEdge.node0].highlight()
                self.MetaNodesGL[metaEdge.node1].highlight()
        self.rebuildMetaNodesGLList()
    
    def updateEdgeSelection(self, edgeIds):
        for edgeId in edgeIds:
            if edgeId > -1 and edgeId < len(self.MetaEdgesGL):
                self.MetaEdgesGL[edgeId].highlight()
                self.rebuildMetaGLEdgeList(edgeId)
                metaEdge = self.graph.edgeConnections[edgeId]
                self.MetaNodesGL[metaEdge.node0].highlight()
                self.MetaNodesGL[metaEdge.node1].highlight()
        self.rebuildMetaNodesGLList()
                
    def flipEdgeSelection(self, edgeIds):
        for edgeId in edgeIds:
            if edgeId > -1 and edgeId < len(self.MetaEdgesGL):
                edgeGL = self.MetaEdgesGL[edgeId]
                metaEdge = self.graph.edgeConnections[edgeId]
                if edgeGL.isHighlight:
                    self.MetaEdgesGL[edgeId].unhighlight()
                    self.MetaNodesGL[metaEdge.node0].unhighlight()
                    self.MetaNodesGL[metaEdge.node1].unhighlight()
                else:
                    self.MetaEdgesGL[edgeId].highlight()
                    self.MetaNodesGL[metaEdge.node0].highlight()
                    self.MetaNodesGL[metaEdge.node1].highlight()
                self.rebuildMetaGLEdgeList(edgeId)
        self.rebuildMetaNodesGLList()
        
          
    def unselect(self):
        for edge in self.MetaEdgesGL:
            if edge.isHighlight:
                edge.unhighlight()
                self.rebuildMetaGLEdgeList(edge.id)
                for skelEdge in self.SkelEdgesGL[edge.id]:
                    skelEdge.unhighlight()
                self.rebuildSkelGLEdgeList(edge.id)
        
        

        for node in self.MetaNodesGL:
            node.unhighlight()
            
        self.rebuildMetaNodesGLList()
    
    def exitOtherModes(self):
        if self.connectionOptions != None:
            self.connectionOptions.exitMode()
        if self.breakOptions != None:
            self.breakOptions.exitMode()
        if self.splitOptions != None:
            self.splitOptions.exitMode()
        for nodeGL in self.MetaNodesGL:
            if nodeGL.degree == 1:
                nodeGL.setScale(1.0)

        for i in range(0, len(self.MetaEdgesGL)):
            self.MetaEdgesGL[i].unhighlight()
            self.rebuildMetaEdgeGLList(i)

        for i in range(0, len(self.SkelEdgesGL)):
            for edgeGL in self.SkelEdgesGL[i]:
                edgeGL.unhighlight()
            self.rebuildSkelEdgeGLList(i)

        self.rebuildMetaNodesGLList()
        
    def enterConnectionMode(self, widget = None):
        if self.currentMode == 0:
            return
        self.exitOtherModes()
        self.connectionOptions.enterMode(self.numComponents, widget)

        for nodeGL in self.MetaNodesGL:
            if nodeGL.degree == 1:
                nodeGL.setScale(self.suggestedNodeScale)
            else:
                nodeGL.setScale(self.suggestedNodeScale/5.0)

        self.rebuildMetaNodesGLList()

        self.currentMode = 0

    def enterBreakMode(self, widget = None):
        if self.currentMode == 1:
            return
        for key in self.minimizedComponentMap:
            self.minimizedComponentMap[key] = False
        self.exitOtherModes()
        self.breakOptions.enterMode(widget)

        self.numEdgesToBreakUpdated.emit(self.graph.numEdgesToBreak)
        for edgeI in range(0, len(self.MetaEdgesGL)):
            if self.MetaEdgesGL[edgeI].isBridge:
                self.MetaEdgesGL[edgeI].setScale(1.0)
                #self.MetaEdgesGL[edgeI].lowlight()
            else:
                #self.MetaEdgesGL[edgeI].highlight()
                self.MetaEdgesGL[edgeI].setScale(self.suggestedEdgeScale)

            self.rebuildMetaEdgeGLList(edgeI)

        for edgeI in range(0, len(self.SkelEdgesGL)):
            if self.MetaEdgesGL[edgeI].isBridge:
                for edgeGL in self.SkelEdgesGL[edgeI]:
                    edgeGL.setScale(1.0)
                    #edgeGL.lowlight()
            else:
                for edgeGL in self.SkelEdgesGL[edgeI]:
                    #edgeGL.highlight()
                    edgeGL.setScale(self.suggestedEdgeScale)

            self.rebuildSkelEdgeGLList(edgeI)

        self.currentMode = 1

    def enterSplitMode(self, widget = None):
        if self.currentMode == 2:
            return
        for key in self.minimizedComponentMap:
            self.minimizedComponentMap[key] = False
        self.exitOtherModes()
        self.splitOptions.enterMode(widget)
        self.numEdgesToBreakUpdated.emit(self.graph.numEdgesToBreak)

        for edgeI in range(0, len(self.MetaEdgesGL)):
            if self.MetaEdgesGL[edgeI].isBridge:
                self.MetaEdgesGL[edgeI].setScale(1.0)
                #self.MetaEdgesGL[edgeI].lowlight()
            else:
                #self.MetaEdgesGL[edgeI].highlight()
                self.MetaEdgesGL[edgeI].setScale(self.suggestedEdgeScale)

            self.rebuildMetaEdgeGLList(edgeI)

        for edgeI in range(0, len(self.SkelEdgesGL)):
            if self.MetaEdgesGL[edgeI].isBridge:
                for edgeGL in self.SkelEdgesGL[edgeI]:
                    edgeGL.setScale(1.0)
                    #edgeGL.lowlight()
            else:
                for edgeGL in self.SkelEdgesGL[edgeI]:
                    #edgeGL.highlight()
                    edgeGL.setScale(self.suggestedEdgeScale)

        self.currentMode = 2

    def updateModeOptions(self):
        if self.currentMode == 0:
            self.connectionOptions.setNumComponents(self.numComponents)
        elif self.currentMode == 1:
            #nothing to update for break mode
            pass
        elif self.currentMode == 2:
            #nothing to update for splitmode
            pass


    def printEdgesGL(self):
        print('printing metaGraphGL')
        for edgeGL in self.MetaEdgesGL:
            print(edgeGL.v0)
            print(edgeGL.v1)

    def display(self, zoom = 1.0):
        #graph viewing mode
        
        glEnable(GL_LIGHTING)
        if self.graphGLNodesList != None:
            drawCallList(self.graphGLNodesList)
        glDisable(GL_LIGHTING)

        if self.currentDisplayMode == 0  or self.currentDisplayMode == 2:
            for key in self.minimizedComponentMap:
                if not self.minimizedComponentMap[key]:
                    if key in self.graph.componentEdgeMap:
                        for edgeId in self.graph.componentEdgeMap[key]:
                            self.MetaEdgesGL[edgeId].display(self.edgeColorization, self.visualization)
                            #if self.visualization == Visualization.THICKNESS:
                            #    self.drawCallList(self.graphGLEdgesLists[edgeId])

        if self.currentDisplayMode == 1 or self.currentDisplayMode == 2:
            #for skelEdgeGL in self.skelGLEdgesLists:
            #    self.drawCallList(skelEdgeGL)
            for skelEdgeList in self.SkelEdgesGL:
                for skelEdge in skelEdgeList:
                    if not self.minimizedComponentMap[skelEdge.component]:
                        skelEdge.display(self.edgeColorization, self.visualization)



        #skeleton viewing mode
        
            #for key in self.minimizedComponentMap:
            #    if not self.minimizedComponentMap[key]:
            #        if key in self.skelGLEdgesLists:
            #            self.drawCallList(self.skelGLEdgesLists[key])
                    #if key in self.skelGLNodesList:
                    #    self.drawCallList(self.skelGLNodesList[key])
            #if self.skelGLEdgesLists != None:
            #    self.drawCallList(self.skelGLEdgesLists)
            #if self.skelGLNodesList != None:
            #    self.drawCallList(self.skelGLNodesList)

        #elif self.currentDisplayMode == 2:
        #    for graphEdgeGL in self.graphGLEdgesLists:
        #        self.drawCallList(graphEdgeGL)
        #    if self.graphGLNodesList != None:
        #        self.drawCallList(self.graphGLNodesList)
        #    for skelEdgeGL in self.skelGLEdgesLists:
        #        self.drawCallList(skelEdgeGL)
        #    if self.skelGLNodesList != None:
        #        self.drawCallList(self.skelGLNodesList)

def drawCallList(callList, dx : float = 0, dy : float = 0, dz : float = 0, angle : float = 0):
    glPushMatrix()
    glTranslated(dx, dy, dz)
    glRotated(angle, 0.0, 0.0, 1.0)
    glCallList(callList)
    glPopMatrix()
        
def resolveGraphs(staticGraph : MetaGraphGL, updateGraph : MetaGraphGL):
    '''
    Should only be callled by the MetaGraphGL maintained on the main thread
    '''
    print('UPDATE METAGRAPH CALLED')
    for selfNode, otherNode in zip(staticGraph.MetaNodesGL, updateGraph.MetaNodesGL):
        otherNode.isHighlight = selfNode.isHighlight
        otherNode.baseScale = selfNode.baseScale
        otherNode.scale = selfNode.scale
            
    for selfEdge, otherEdge in zip(staticGraph.MetaEdgesGL, updateGraph.MetaEdgesGL):
        otherEdge.isHighlight = selfEdge.isHighlight
        otherEdge.baseScale = selfEdge.baseScale
        otherEdge.scale = selfEdge.scale
            
    #for selfComponent, otherComponent in zip(staticGraph.SkelNodesGL, updateGraph.SkelNodesGL):
    #    otherNode.isHighlight = selfNode.isHighlight
    #    otherNode.baseScale = selfNode.baseScale
    #    otherNode.scale = selfNode.scale
            
    #for selfEdge, otherEdge in zip(staticGraph.SkelEdgesGL, updateGraph.SkelEdgesGL):
    #    otherEdge.isHighlight = selfEdge.isHighlight
    #    otherEdge.baseScale = selfEdge.baseScale
    #    otherEdge.scale = selfEdge.scale
    
    mergedComponentMap = updateGraph.minimizedComponentMap
    for i in range(0, staticGraph.numComponents):
        mergedComponentMap[i] = staticGraph.minimizedComponentMap[i]

    staticGraph.minimizedComponentMap = mergedComponentMap

    staticGraph.MetaNodesGL = updateGraph.MetaNodesGL
    staticGraph.MetaEdgesGL = updateGraph.MetaEdgesGL
    print('num edges', len(staticGraph.MetaEdgesGL))
    #staticGraph.SkelNodesGL = updateGraph.SkelNodesGL
    staticGraph.SkelEdgesGL = updateGraph.SkelEdgesGL
    staticGraph.graph = updateGraph.graph
    staticGraph.hasMetaGraph = True
    staticGraph.numComponents = updateGraph.numComponents
    print('num edges to break', staticGraph.graph.numEdgesToBreak)
    staticGraph.numEdgesToBreakUpdated.emit(staticGraph.graph.numEdgesToBreak)

    staticGraph.fillColorTables()
    staticGraph.rebuildGLLists()
    staticGraph.updateModeOptions()
    staticGraph.nodeScaleChanged(staticGraph.suggestedNodeScale)
    staticGraph.edgeScaleChanged(staticGraph.suggestedEdgeScale)
    
    
        
    