# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 05:12:12 2018

@author: Will
"""

from RootsTool import  Point3d, RootAttributes, Skeleton, MetaNode3d, MetaEdge3d, MetaGraph
from ConnectionTabWidget import Ui_ConnectionTabWidget

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
import numpy as np

import drawingUtil
import util


class SkelGL():
    
    def __init__(self, parent=None):
        self.hasSkeleton = False
        self.hasMetaGraph = False
        self.edgeHighlightedMap = {}
        self.nodeSizeMap = {}
        self.nodeHighlightedMap = {}
        self.minimizedComponentMap = {}
        self.metaGraphGL = None
        self.skeletonGL = None
        self.highlightedEdge = -1
        self.highlightedNode = -1
        
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        
        self.modes = {-1 : 'NoMode', 0 : 'Connection Mode', 1 : 'Separation Mode', 2 : 'Spltting Mode'}
        
        self.currentMode = -1
    
    def setSkeleton(self, skeleton : Skeleton):
        self.skeleton = skeleton
#        self.skeletonGL = self.makeSkeletonGL()
        self.hasSkeleton = True
        
        c = self.skeleton.center
        diam = self.skeleton.radius
        
        self.skeletonViewBasePoint = v3(c.x, c.y, c.z + diam * 2)
        self.skeletonCenter = v3(c.x, c.y, c.z)
        
        
        
    def setMetaGraph(self, metaGraph : MetaGraph):
        self.metaGraph = metaGraph
        self.updateGraphMaps()
       
        
        self.setSkeleton(self.metaGraph.skeleton)
        self.timer.start(50)
    
    def updateGraphMaps(self):
#        set up the color table for the component IDs of the metagraph
        numComponents = len(self.metaGraph.componentNodeMap)
        for key in self.metaGraph.componentNodeMap.keys():
            print('printing component ', key)
            print(self.metaGraph.componentNodeMap[key])
            self.minimizedComponentMap[key] = False
                
        self.colorTable = drawingUtil.ColorTable
        if numComponents > len(drawingUtil.ColorTable):
            for i in range(len(drawingUtil.ColorTable), numComponents):
                randColor = np.random.ranf(3)
                self.colorTable.append([randColor[0], randColor[1], randColor[2], 1.0])
#       set the colors of the nodes based on their component ids
#       and initialize the node size map to 0 for each node
        i = 0
        for node in self.metaGraph.nodeLocations:
            self.nodeHighlightedMap[i] = False
            
#           if the connected component for this node contains only this node, then initialize the node size to 1
            if len(self.metaGraph.componentNodeMap[node.component]) == 1:
                self.nodeSizeMap[i] = 1.0
            else:
                self.nodeSizeMap[i] = 0.0
                
            i = i + 1
            
#       set the colors of the edges based on their component ids
#       and set the node size map to the greater of its current size or the edge thickness for each edge node
        i = 0
        for edge in self.metaGraph.edgeConnections:
            self.edgeHighlightedMap[i] = False
            node0Size = self.nodeSizeMap[edge.node0]
            node1Size = self.nodeSizeMap[edge.node1]
            
            if edge.thickness > node0Size:
                self.nodeSizeMap[edge.node0] = edge.thickness
            if edge.thickness > node1Size:
                self.nodeSizeMap[edge.node1] = edge.thickness
            
            print('edge between nodes ', edge.node0, edge.node1)
            
            i = i + 1
            
        self.hasMetaGraph = True
        self.metaGraphGL = self.makeMetaGraphGL()
    
    
    def makeMetaGraphGL(self):
        if not self.hasMetaGraph:
            return None
        result = gl.glGenLists(1)
        gl.glNewList(result, gl.GL_COMPILE)
        
        for component in self.metaGraph.componentEdgeMap.keys():
            alpha = 1.0
            if self.minimizedComponentMap[component]:
                alpha = 0.20
                
            for edgeId in self.metaGraph.componentEdgeMap[component]:
                edge = self.metaGraph.edgeConnections[edgeId]
                v0 = self.metaGraph.nodeLocations[edge.node0]
                v1 = self.metaGraph.nodeLocations[edge.node1]
                thickness = edge.thickness
                if thickness <= 0.01:
                    thickness = (self.nodeSizeMap[v0.order] + self.nodeSizeMap[v1.order])/2.0
                if self.edgeHighlightedMap[edgeId]:
                    color = [0.0, 0.0, 0.0, 0.0]
                    for ci in range(0, 4):
                        color[ci] = min(self.colorTable[component][ci]*1.5, 1.0)
                    color[3] = alpha
                    drawingUtil.computeUncappedCylinderGL(v0, v1, color, thickness, thickness, 1.0)
                else:
                    color = [0.0, 0.0, 0.0, 0.0]
                    for ci in range(0, 4):
                        color[ci] = self.colorTable[component][ci]
                    color[3] = alpha
                    drawingUtil.computeUncappedCylinderGL(v0, v1, color, thickness/2.0, thickness/2.0, 1.0)
                
                
            for nodeId in self.metaGraph.componentNodeMap[component]:
                node = self.metaGraph.nodeLocations[nodeId]
                if self.nodeHighlightedMap[nodeId]:
                    color = [0.0, 0.0, 0.0, 0.0]
                    for ci in range(0, 4):
                        color[ci] = min(self.colorTable[component][ci]*1.5, 1.0)
                    color[3] = alpha
                    drawingUtil.computeVertexGL(node, color, self.nodeSizeMap[nodeId], 1.0)
                else:
                    color = [0.0, 0.0, 0.0, 0.0]
                    for ci in range(0, 4):
                        color[ci] = self.colorTable[component][ci]
                    color[3] = alpha
                    drawingUtil.computeVertexGL(node, color, self.nodeSizeMap[nodeId]/2.0, 1.0)
                    
        gl.glEndList()
        return result
    
    
    def getFirstEdgeHit(self, origin : np.array, ray : np.array):
        """
        determines the first edge that is hit by a picking ray
        returns a tuple of (hitDetected, edgeHit, edgeHitId)
        hitDetected : boolean indicator of hit detection
        edgeHit : MetaEdge3d that is hit
        edgeHitId : id of the edge in the skeletons edgeList
        """
        print('detecting hits')
        minDist = 100000000
        hitFound = False
        edgeHit = None
        edgeHitId = -1
        if not self.hasMetaGraph:
            return (hitFound, edgeHit, edgeHitId)
        i = 0
        for edge in self.metaGraph.edgeConnections:
            
            p0 = self.metaGraph.nodeLocations[edge.node0]
            p1 = self.metaGraph.nodeLocations[edge.node1]
            if isinstance(p0, Point3d) or isinstance(p0, MetaNode3d):
                p0 = drawingUtil.p3d2arr(p0)
                p1 = drawingUtil.p3d2arr(p1)
                
            (doesIntersect, distance) = util.intersectRayCylinder(origin, ray, p0, p1, edge.thickness)
            if not doesIntersect:
                (doesIntersect, distance) = util.intersectRaySphere(origin, ray, p0, edge.thickness)
            if not doesIntersect:
                (doesIntersect, distance) = util.intersectRaySphere(origin, ray, p1, edge.thickness)
            
            if doesIntersect:
                if distance < minDist: 
                    hitFound = True
                    minDist = distance
                    edgeHit = edge
                    edgeHitId = edge.order
            i = i + 1
        
        if hitFound:
            print('hit detected')
            self.printMetaEdge(edgeHit)
        else:
            print('no hit detected')
        return (hitFound, edgeHit, edgeHitId)
    
    def getFirstNodeHit(self, origin : np.array, ray : np.array):
        print('detecting node hits')
        minDist = 1000000000
        hitFound = False
        nodeHit = None
        nodeHitId = -1
        
        if not self.hasMetaGraph:
            return(hitFound, nodeHit, nodeHitId)
        
        i = 0
        for node in self.metaGraph.nodeLocations:
            p = drawingUtil.p3d2arr(node)
            (doesIntersect, distance) = util.intersectRaySphere(origin, ray, p, self.nodeSizeMap[i])
            
            if doesIntersect:
                if distance < minDist:
                    hitFound = True
                    minDist = distance
                    nodeHit = node
                    nodeHitId = i
            i = i + 1
            
        if hitFound:
            print('hit detected')
            self.printMetaNode(nodeHit)
        else:
            print('no hit detected')
            
        return(hitFound, nodeHit, nodeHitId)
    
    def printMetaEdge(self, edge : MetaEdge3d):
        p0 = self.metaGraph.nodeLocations[edge.node0]
        p1 = self.metaGraph.nodeLocations[edge.node1]
        
        p0 = drawingUtil.p3d2arr(p0)
        p1 = drawingUtil.p3d2arr(p1)
        print(p0, p1)
        
    def printMetaNode(self, node : MetaNode3d):
        p = drawingUtil.p3d2arr(node)
        print(p)
        
    def highlightEdge(self, edgeId : int):
        if edgeId > -1 and not self.edgeHighlightedMap[edgeId]:
            self.edgeHighlightedMap[edgeId] = True
            edge = self.metaGraph.edgeConnections[edgeId]
            self.nodeHighlightedMap[edge.node0] = True
            self.nodeHighlightedMap[edge.node1] = True
            self.metaGraphGL = self.makeMetaGraphGL()
            
        if edgeId > -1 and self.edgeHighlightedMap[edgeId]:
            self.unHighlightEdge(edgeId)

            
    def unHighlightEdge(self, edgeId : int):
        if edgeId > -1 and self.edgeHighlightedMap[edgeId]:
            self.edgeHighlightedMap[edgeId] = False
            edge = self.metaGraph.edgeConnections[edgeId]
            self.nodeHighlightedMap[edge.node0] = False
            self.nodeHighlightedMap[edge.node1] = False
            self.metaGraphGL = self.makeMetaGraphGL()
            
    def highlightNode(self, nodeId : int):
        
        if nodeId > -1 and not self.nodeHighlightedMap[nodeId]:
            self.nodeHighlightedMap[nodeId] = True
            self.metaGraphGL = self.makeMetaGraphGL()
        elif nodeId > -1 and self.nodeHighlightedMap[nodeId]:
            self.unHighlightNode(nodeId)

    
    def unHighlightNode(self, nodeId : int):
        
        if nodeId > -1 and self.nodeHighlightedMap[nodeId]:
            self.nodeHighlightedMap[nodeId] = False
            self.metaGraphGL = self.makeMetaGraphGL()
            
    def enterConnectionMode(self, ConnectionWidget : Ui_ConnectionTabWidget):
        self.componentOfInterest1 = 0
        self.componentOfInterest2 = 1
        self.minimizedComponentMap = {}
        self.connectionWidget = ConnectionWidget
        self.currentMode = 0
        self.node1 = None
        self.node2 = None
        if self.hasMetaGraph:
            for i in range(0, len(self.metaGraph.componentNodeMap)):
                self.minimizedComponentMap[i] = True
                self.connectionWidget.ComponentOne.addItem(str(i))
                self.connectionWidget.ComponentTwo.addItem(str(i))
            self.minimizedComponentMap[self.componentOfInterest1] = False
            self.minimizedComponentMap[self.componentOfInterest2] = False
            self.metaGraphGL = self.makeMetaGraphGL()
            
    def updateConnectionWidget(self, ConnectionWidget : Ui_ConnectionTabWidget):
        print('updating connection widget')
        ConnectionWidget.ComponentOne.clear()
        ConnectionWidget.ComponentTwo.clear()
        if self.hasMetaGraph:
            for i in range(0, len(self.metaGraph.componentNodeMap)):
                self.minimizedComponentMap[i] = True
                ConnectionWidget.ComponentOne.addItem(str(i))
                ConnectionWidget.ComponentTwo.addItem(str(i))
            if self.componentOfInterest1 > -1 and self.componentOfInterest1 < len(self.metaGraph.componentNodeMap):
                ConnectionWidget.ComponentOne.setCurrentIndex(self.componentOfInterest1)
            if self.componentOfInterest2 > -1 and self.componentOfInterest2 < len(self.metaGraph.componentNodeMap):
                ConnectionWidget.ComponentTwo.setCurrentIndex(self.componentOfIterest2)
        print('completed connection widget update')
        self.metaGraphGL = self.makeMetaGraphGL()
            
        
    def ChangeComponentOne(self, val):
        print('component of interest changed to ', val)
        if self.componentOfInterest2 != self.componentOfInterest1:
            self.minimizedComponentMap[self.componentOfInterest1] = True
        self.componentOfInterest1 = int(val)
        self.minimizedComponentMap[self.componentOfInterest1] = False
        self.metaGraphGL = self.makeMetaGraphGL()
            
    def ChangeComponentTwo(self, val):
        print('component of interest changed to ', val)
        if self.componentOfInterest2 != self.componentOfInterest1:
            self.minimizedComponentMap[self.componentOfInterest2] = True
            
        self.componentOfInterest2 = int(val)
        self.minimizedComponentMap[self.componentOfInterest2] = False
        self.metaGraphGL = self.makeMetaGraphGL()
    
    def PickConnectionNode(self, node : MetaNode3d):
#        if we are not in connection mode do nothing
        if self.currentMode != 0:
            return
#        if the component of the selected node is neither of the components of interest then ignore it
        if node.component != self.componentOfInterest1 and node.component != self.componentOfInterest2:
            return
        
        if self.node1 == None:
            self.node1 = node
            self.highlightNode(node.order)
        elif self.node2 == None:
            if node.component != self.node1.component:
                self.node2 = node
            else:
                self.unHighlightNode(self.node1.order)
                self.node1 = node
            self.highlightNode(node.order)
        else:
            if node.component == self.node1.component:
                self.unHighlightNode(self.node1.order)
                self.node1 = node
            else:
                self.unHighlightNode(self.node2.order)
                self.node2 = node
            self.highlightNode(node.order)
            
            
    def AcceptConnection(self):
#        if we are not in connection mode do nothing
        if self.currentMode != 0:
            return
#        if both node are selected create the connection and update the graph
        if self.node1 != None and self.node2 != None:
            self.metaGraph.joinOperation(self.node1.id, self.node2.id)
            self.node1 = None
            self.node2 = None
            self.updateGraphMaps()
            
    def enterBreakMode(self):
        self.currentMode = 1
        self.breakEdge = None
        
    def PickBreakEdge(self, edge : MetaEdge3d):
#        if we are not breaking mode do nothing
        if self.currentMode != 1:
            return
        if self.breakEdge != None:
            self.unHighlightEdge(self.breakEdge.order)
        self.breakEdge = edge
        self.highlightEdge(self.breakEdge.order)
        
    def AcceptBreak(self):
        if self.currentMode != 1:
            return
        if self.breakEdge != None:
            self.metaGraph.breakOperation(self.breakEdge)
            self.breakEdge = None
            self.updateGraphMaps()
        

        
        



    
    
    
    
    
    
    
    