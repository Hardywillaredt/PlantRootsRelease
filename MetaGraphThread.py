# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 15:02:40 2018

@author: Will
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from RootsTool import  Point3d, RootAttributes, Skeleton
#MetaNode3d, MetaEdge3d, MetaGraph

#import drawingUtil
import util

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

from numpy import *
import numpy as np

import math
from camera import *
#from GLObjects import MetaGraphGL

class JoinOptions():
    def __init__(self, v0id, v1id):
        self.v0id = v0id
        self.v1id = v1id


class BreakOptions():
    def __init__(self, edge):
        self.edge = edge


class SplitOptions():
    def __init__(self, splitEdge : MetaEdge3d, secondaries):
        self.splitEdge = splitEdge
        self.secondaries = secondaries

class LoadOperationThread(QThread):

    sigUpdateMetaGraph = pyqtSignal(object)

    def __init__(self, filename):
        super(LoadOperationThread, self).__init__()
        self.filename = filename

    def run(self):
        graph = MetaGraph(self.filename)
        graphGL = MetaGraphGL()
        graphGL.setMetaGraph(graph)
        self.sigUpdateMetaGraph.emit(graphGL)


class JoinOperationThread(QThread):

    sigUpdateMetaGraph = pyqtSignal(object)

    def __init__(self, graph, v0id, v1id):
        super(JoinOperationThread, self).__init__()
        self.graph = graph
        self.v0id = v0id
        self.v1id = v1id

    def run(self):
        self.graph.joinOperation(self.v0id, self.v1id)
        graphGL = MetaGraphGL()
        graphGL.setMetaGraph(self.graph)
        self.sigUpdateMetaGraph.emit(graphGL)



class BreakOperationThread(QThread):

    sigUpdateMetaGraph = pyqtSignal(object)

    def __init__(self, graph, edge):
        super(BreakOperationThread, self).__init__()
        self.graph = graph
        self.edge = edge

    def run(self):
        self.graph.breakOperation(self.edge)
        graphGL = MetaGraphGL()
        graphGL.setMetaGraph(self.graph)
        self.sigUpdateMetaGraph.emit(graphGL)

class SplitOperationThread(QThread):

    sigUpdateMetaGraph = pyqtSignal(object)

    def __init__(self, graph, splitEdge, secondaries):
        super(SplitOperationThread, self).__init__()
        self.graph = graph
        self.splitEdge = splitEdge
        self.secondaries = secondaries

    def run(self):
        self.graph.splitOperation(self.splitEdge, self.secondaries)
        graphGL = MetaGraphGL()
        graphGL.setMetaGraph(self.graph)
        self.sigUpdateMetaGraph.emit(graphGL)


class MetaGraphThread(QThread):
    
    '''vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvSIGNALSvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv'''
    '''
    Signal indicates that the underlying metagraph opengl representation has changed
    passes out the full glLists now representing the graph
    '''
    sigUpdateGL = pyqtSignal(object)
    
    '''
    too to alert notification recieved
    '''
    wasNotified = pyqtSignal()
    
    '''
    toy alert termination
    '''
    wasTerminated = pyqtSignal()
    
    '''
    sends printable object to main
    '''
    printToMain = pyqtSignal(object)
    
    '''
    sends out updated metagraphGL object
    '''
    sigUpdateMetaGraph = pyqtSignal(object)
    
    '''^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^SIGNALS^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'''
    
    
    
    '''vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvSLOTSvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv'''
    
    '''
    Slot to indicate file to load
    '''
    @pyqtSlot(str)
    def loadFileEvent(self, fileToLoad : str):
        self.fileToLoad = fileToLoad
        self.fileIsLoaded = False
        self.loadFile = True
        return
    
    @pyqtSlot(int, int)
    def acceptConnection(self, v0id, v1id):
        if self.graph != None:
            self.joinOptions = JoinOptions(v0id, v1id)
            
    @pyqtSlot(object)
    def acceptBreak(self, edge : MetaEdge3d):
        if self.graph != None:
            self.breakOptions = BreakOptions(edge)

    @pyqtSlot(object, object)
    def acceptSplit(self, splitEdge : MetaEdge3d, secondaries):
        if self.graph != None:
            self.splitOptions = SplitOptions(splitEdge, secondaries)


    
    '''^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^SLOTS^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'''
    
    
    def __init__(self):
        super(MetaGraphThread, self).__init__()
        #QThread.__init__(self)
        
        self.fileToLoad = None
        self.fileIsLoaded = False
        self.loadFile = False
        
        self.isNotified = False
        self.isTerminated = False
        self.glOutOfDate = False
        
        self.mode = 0

        self.colorTable = drawingUtil.ColorTable
        
        self.graph = None        
        self.metaGL = None
        self.geomGL = None
        
        self.edgeHighlightedMap = list()
#        self.nodeSizeMap = {}
        self.nodeHighlightedMap = list()
        self.minimizedComponentMap = {}
        
        self.rayWasPicked = False
        self.rayPicked = None
        self.originPicked = None
        
        self.joinOptions = None
        self.breakOptions = None
        self.splitOptions = None
        
        
    def __del__(self):
        self.graph = None
        self.wait()
        
        
    
    def run(self):
        while True:
            if not self.fileIsLoaded:
                if self.loadFile:
                    self.graph = MetaGraph(self.fileToLoad)
                    self.fileIsLoaded = True
                    self.loadFile = False
                    graphGL = MetaGraphGL()
                    graphGL.setMetaGraph(self.graph)
                    self.sigUpdateMetaGraph.emit(graphGL)
            
            if self.joinOptions != None:
                self.graph.joinOperation(self.joinOptions.v0id, self.joinOptions.v1id)
                graphGL = MetaGraphGL()
                graphGL.setMetaGraph(self.graph)
                self.sigUpdateMetaGraph.emit(graphGL)
                self.joinOptions = None
                
            if self.breakOptions != None:
                self.graph.breakOperation(self.breakOptions.edge)
                graphGL = MetaGraphGL()
                graphGL.setMetaGraph(self.graph)
                self.sigUpdateMetaGraph.emit(graphGL)
                self.breakOptions = None

            if self.splitOptions != None:
                self.graph.splitOperation(self.splitOptions.splitEdge, self.splitOptions.secondaries)
                graphGL = MetaGraphGL()
                graphGL.setMetaGraph(self.graph)
                self.sigUpdateMetaGraph.emit(graphGL)
                self.splitOptions = None
            
            if self.isNotified:
                self.isNotified = False
                self.wasNotified.emit()
                
            if self.isTerminated:
                self.wasTerminated.emit()
                return
            self.sleep(1000)
        
    
    
#    def updateGraphMaps(self):
##        set up the color table for the component IDs of the metagraph
#        numComponents = len(self.graph.componentNodeMap)
#        for key in self.graph.componentNodeMap.keys():
#            self.minimizedComponentMap[key] = False
                
#        self.colorTable = drawingUtil.ColorTable
#        if numComponents > len(self.colorTable):
#            for i in range(len(self.ColorTable), numComponents):
#                randColor = np.random.ranf(3)
#                self.colorTable.append([randColor[0], randColor[1], randColor[2], 1.0])
        
#        self.nodeHighlightedMap = len(self.graph.nodeLocations)*[False]
        
#        self.edgeHighlightedMap = len(self.graph.edgeConnections)*[False]
        
                
#        '''node size map manipulations shuold not be necessary
##       set the colors of the nodes based on their component ids
##       and initialize the node size map to 0 for each node
#        i = 0
#        for node in self.graph.nodeLocations:
#            self.nodeHighlightedMap[i] = False
            
##           if the connected component for this node contains only this node, then initialize the node size to 1
#            if len(self.graph.componentNodeMap[node.component]) == 1:
#                self.nodeSizeMap[i] = 1.0
#            else:
#                self.nodeSizeMap[i] = 0.0
                
#            i = i + 1
            
##       set the colors of the edges based on their component ids
##       and set the node size map to the greater of its current size or the edge thickness for each edge node
#        i = 0
#        for edge in self.graph.edgeConnections:
#            self.edgeHighlightedMap[i] = False
#            node0Size = self.nodeSizeMap[edge.node0]
#            node1Size = self.nodeSizeMap[edge.node1]
            
#            if edge.thickness > node0Size:
#                self.nodeSizeMap[edge.node0] = edge.thickness
#            if edge.thickness > node1Size:
#                self.nodeSizeMap[edge.node1] = edge.thickness
            
#            print('edge between nodes ', edge.node0, edge.node1)
            
#            i = i + 1
#            '''
        
    #def makeMetaGraphGL(self):
        
    #    self.metaGL = gl.glGenLists(1)
    #    gl.glNewList(self.metaGL, gl.GL_COMPILE)
    #    gl.glEndList()
    #    return
    #    for component in self.graph.componentEdgeMap.keys():
    #        alpha = 1.0
    #        if self.minimizedComponentMap[component]:
    #            alpha = 0.20
                
    #        for edgeId in self.graph.componentEdgeMap[component]:
    #            edge = self.graph.edgeConnections[edgeId]
    #            v0 = self.graph.nodeLocations[edge.node0]
    #            v1 = self.graph.nodeLocations[edge.node1]
    #            thickness = edge.thickness
    #            if thickness <= 0.0001:
    #                thickness = (v0.size + v1.size)/2.0
    #            if self.edgeHighlightedMap[edgeId]:
    #                color = [0.0, 0.0, 0.0, 0.0]
    #                for ci in range(0, 4):
    #                    color[ci] = min(self.colorTable[component][ci]*1.5, 1.0)
    #                color[3] = alpha
    #                drawingUtil.computeUncappedCylinderGL(v0, v1, color, thickness, thickness, 1.0)
    #            else:
    #                color = [0.0, 0.0, 0.0, 0.0]
    #                for ci in range(0, 4):
    #                    color[ci] = self.colorTable[component][ci]
    #                color[3] = alpha
    #                drawingUtil.computeUncappedCylinderGL(v0, v1, color, thickness/2.0, thickness/2.0, 1.0)
                
                
    #        for nodeId in self.graph.componentNodeMap[component]:
    #            node = self.graph.nodeLocations[nodeId]
    #            if self.nodeHighlightedMap[nodeId]:
    #                color = [0.0, 0.0, 0.0, 0.0]
    #                for ci in range(0, 4):
    #                    color[ci] = min(self.colorTable[component][ci]*1.5, 1.0)
    #                color[3] = alpha
    #                drawingUtil.computeVertexGL(node, color, node.size, 1.0)
    #            else:
    #                color = [0.0, 0.0, 0.0, 0.0]
    #                for ci in range(0, 4):
    #                    color[ci] = self.colorTable[component][ci]
    #                color[3] = alpha
    #                drawingUtil.computeVertexGL(node, color, node.size/2.0, 1.0)
                    
    #    gl.glEndList() 
    #    self.sigUpdateGL.emit(self.metaGL)
    #    return
        
    
    #def ProcessRayPicking(self, origin : np.array, ray : np.array):
        #return
#        if self.currentMode == 0:
#                (hitFound, nodeHit, nodeHitId) = self.getFirstNodeHit(origin, ray)
#                if hitFound:
#                    self.PickConnectionNode(nodeHit)
#            if self.currentMode == 1:
#                (hitFound, edgeHit, edgeHitId) = self.getFirstEdgeHit(origin, ray)
#                if hitFound:
#                    self.PickBreakEdge(edgeHit)
    
    #def getFirstEdgeHit(self, origin : np.array, ray : np.array):
    #    """
    #    determines the first edge that is hit by a picking ray
    #    returns a tuple of (hitDetected, edgeHit, edgeHitId)
    #    hitDetected : boolean indicator of hit detection
    #    edgeHit : MetaEdge3d that is hit
    #    edgeHitId : id of the edge in the skeletons edgeList
    #    """
    #    print('detecting hits')
    #    minDist = 100000000
    #    hitFound = False
    #    edgeHit = None
    #    edgeHitId = -1
    #    if not self.fileIsLoaded:
    #        return (hitFound, edgeHit, edgeHitId)
    #    i = 0
    #    for edge in self.graph.edgeConnections:
            
    #        p0 = self.graph.nodeLocations[edge.node0]
    #        p1 = self.graph.nodeLocations[edge.node1]
    #        if isinstance(p0, Point3d) or isinstance(p0, MetaNode3d):
    #            p0 = drawingUtil.p3d2arr(p0)
    #            p1 = drawingUtil.p3d2arr(p1)
                
    #        (doesIntersect, distance) = util.intersectRayCylinder(origin, ray, p0, p1, edge.thickness)
    #        if not doesIntersect:
    #            (doesIntersect, distance) = util.intersectRaySphere(origin, ray, p0, edge.thickness)
    #        if not doesIntersect:
    #            (doesIntersect, distance) = util.intersectRaySphere(origin, ray, p1, edge.thickness)
            
    #        if doesIntersect:
    #            if distance < minDist: 
    #                hitFound = True
    #                minDist = distance
    #                edgeHit = edge
    #                edgeHitId = edge.order
    #        i = i + 1
    #    return (hitFound, edgeHit, edgeHitId)
    
    #def getFirstNodeHit(self, origin : np.array, ray : np.array):
    #    self.printToMain.emit('detecting node hits')
    #    minDist = 1000000000
    #    hitFound = False
    #    nodeHit = None
    #    nodeHitId = -1
        
    #    if not self.fileIsLoaded:
    #        return(hitFound, nodeHit, nodeHitId)
        
    #    i = 0
    #    for node in self.graph.nodeLocations:
    #        p = drawingUtil.p3d2arr(node)
    #        (doesIntersect, distance) = util.intersectRaySphere(origin, ray, p, self.nodeSizeMap[i])
            
    #        if doesIntersect:
    #            if distance < minDist:
    #                hitFound = True
    #                minDist = distance
    #                nodeHit = node
    #                nodeHitId = i
    #        i = i + 1
            
    #    return(hitFound, nodeHit, nodeHitId)
    
    #def printMetaEdge(self, edge : MetaEdge3d):
    #    p0 = self.graph.nodeLocations[edge.node0]
    #    p1 = self.graph.nodeLocations[edge.node1]
        
    #    p0 = drawingUtil.p3d2arr(p0)
    #    p1 = drawingUtil.p3d2arr(p1)
    #    self.printToMain(p0)
    #    self.printToMain(p1)
        
    #def printMetaNode(self, node : MetaNode3d):
    #    p = drawingUtil.p3d2arr(node)
        
    #    self.printToMain(p)
        
    #def highlightEdge(self, edgeId : int):
    #    if edgeId > -1 and edgeId < len(self.edgeHighlightedMap):
    #        if not self.edgeHighlightedMap[edgeId]:
    #            self.edgeHighlightedMap[edgeId] = True
    #            edge = self.graph.edgeConnections[edgeId]
    #            self.nodeHighlightedMap[edge.node0] = True
    #            self.nodeHighlightedMap[edge.node1] = True
    #            self.metaGL = self.makeMetaGraphGL()
    #        else:
    #            self.unHighlightEdge(edgeId)

            
    #def unHighlightEdge(self, edgeId : int):
    #    if edgeId > -1 and edgeId < len(self.edgeHighlightedMap):
    #        if self.edgeHighlightedMap[edgeId]:
    #            self.edgeHighlightedMap[edgeId] = False
    #            edge = self.graph.edgeConnections[edgeId]
    #            self.nodeHighlightedMap[edge.node0] = False
    #            self.nodeHighlightedMap[edge.node1] = False
    #            self.metaGL = self.makeMetaGraphGL()
            
    #def highlightNode(self, nodeId : int):
    #    if nodeId > -1 and nodeId < len(self.nodeHighlightedMap):
    #        if not self.nodeHighlightedMap[nodeId]:
    #            self.nodeHighlightedMap[nodeId] = True
    #            self.metaGL = self.makeMetaGraphGL()
    #        else:
    #            self.unHighlightNode(nodeId)

    
    #def unHighlightNode(self, nodeId : int):
    #    if nodeId > -1 and nodeId < len(self.nodeHighlightedMap):
    #        if self.nodeHighlightedMap[nodeId]:
    #            self.nodeHighlightedMap[nodeId] = False
    #            self.metaGL = self.makeMetaGraphGL()
        
        
        
        