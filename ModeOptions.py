# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 21:07:56 2018

@author: Will
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ConnectionTabWidget import Ui_ConnectionTabWidget
from BreakTabWidget import Ui_BreakTabWidget
from SplitTabWidget import Ui_SplitTabWidget
from AddNodeTabWidget import Ui_AddNodeTabWidget

from RootsTool import  Point3d, RootAttributes, Skeleton, mgraph
#MetaNode3d, MetaEdge3d, MetaGraph

from math import log10, floor
def round_to_2(x):
  return round(x, -int(floor(log10(abs(x)))) + 1)

class ConnectionModeOptions(QObject):
    
    @pyqtSlot(int)
    def ComponentOneChanged(self, val):
        self.graph.setComponent1(val)
        if self.allowAllComponents:
            return
        if self.component1 == val:
            self.sigComponentsChanged.emit(self.minimizedComponents)
            return
        self.unselectNode1()
        self.minimizedComponents[val] = False
        self.minimizedComponents[self.component1] = True
        self.minimizedComponents[self.component2] = False
        self.component1 = val
        self.sigComponentsChanged.emit(self.minimizedComponents)
    
    @pyqtSlot(int)
    def ComponentTwoChanged(self, val):
        self.graph.setComponent2(val)
        if self.allowAllComponents:
            return
        if self.component2 == val:
            self.sigComponentsChanged.emit(self.minimizedComponents)
            return
        self.unselectNode2()       
        self.minimizedComponents[val] = False
        self.minimizedComponents[self.component2] = True
        self.minimizedComponents[self.component1] = False
        self.component2 = val
        self.sigComponentsChanged.emit(self.minimizedComponents)
                
    @pyqtSlot(bool)
    def showSelected(self, showOnlySelected):
        self.graph.setDisplayOnlySelectedComponents(showOnlySelected)
        if showOnlySelected:
            self.allowAllComponents = False
            self.sigComponentsChanged.emit(self.minimizedComponents)
        else:
            self.allowAllComponents = True
            newMap = {}
            for key in self.minimizedComponents:
                newMap[key] = False
            self.sigComponentsChanged.emit(newMap)

    @pyqtSlot(bool)
    def showBoundingBoxes(self, doShow):
        self.graph.setShowBoundingBoxes(doShow)

    sigNodeSelected = pyqtSignal(int) #nodeId
    
    sigNodeUnselected = pyqtSignal(int) #nodeId
    
    sigComponentsChanged = pyqtSignal(object) #MinimizedComponentsMap

    sigConnectionAccepted = pyqtSignal(int, int) #nodeId, nodeId

    sigSliderScaleChanged = pyqtSignal(float)

    @pyqtSlot(int)
    def sliderUpdated(self, sliderVal):
        scale = 1.0 * sliderVal / 10.0
        self.sigSliderScaleChanged.emit(scale)

    
    def __init__(self, parent = None, graph = None):
        super(ConnectionModeOptions, self).__init__(parent)
        self.component1 = 0
        self.component2 = 0
        self.minimizedComponents = {}
        self.node1 = None
        self.node2 = None
        self.numComponents = 0
        self.widget = None
        self.allowAllComponents = True
        self.graph = graph
        for i in range(0, self.numComponents):
            if i == self.component1 or i == self.component2:
                self.minimizedComponents[i] = False
            else:
                self.minimizedComponents[i] = True

        self.isActive = False

    def pickNode(self, eyeX, eyeY, eyeZ, rayX, rayY, rayZ):
        if self.isActive:
            self.graph.selectConnectionNode(eyeX, eyeY, eyeZ, rayX, rayY, rayZ)
                
    def setWidget(self, widget : Ui_ConnectionTabWidget):
        if widget != None:
            self.widget = widget
        if self.widget != None:
            self.widget.ComponentOne.currentIndexChanged.connect(self.ComponentOneChanged)
            self.widget.ComponentTwo.currentIndexChanged.connect(self.ComponentTwoChanged)
            self.widget.AcceptConnection.clicked.connect(self.acceptConnection)
            self.widget.showSelected.toggled.connect(self.showSelected)
            self.widget.showBoundingBoxes.toggled.connect(self.showBoundingBoxes)
            #self.widget.scaleSlider.sliderMoved.connect(self.sliderUpdated)
            self.updateConnectionWidget()

        
    
    def setNumComponents(self, numComponents : int):
        self.numComponents = self.graph.getNumComponents()
        self.updateConnectionWidget()
        return
        for i in range(self.numComponents, numComponents):
            self.minimizedComponents[i] = True
        self.numComponents = numComponents
        if numComponents <= self.component1:
            self.minimizedComponents[self.component1] = True
            self.component1 = numComponents - 1
            self.unselectNode1()
        if numComponents <= self.component2:
            self.minimizedComponents[self.component2] = True
            self.component2 = numComponents - 1
            self.unselectNode2()
        if self.numComponents > 1:
            if self.component1 == self.component2:
                if self.component1 == 0:
                    self.component2 = 1
                else:
                    self.component1 = 0
        if self.node1 != None:
            if self.node1.component != self.component1:
                self.unselectNode1()
        if self.node2 != None:
            if self.node2.component != self.component2:
                self.unselectNode2()
        self.updateConnectionWidget()
        self.graph.setComponent1(self.component1)
        self.graph.setComponent2(self.component2)
        self.minimizedComponents[self.component1] = False
        self.minimizedComponents[self.component2] = False
        self.sigComponentsChanged.emit(self.minimizedComponents)
    
    def updateConnectionWidget(self):
        print('updating connection widget')
        componentSizes = self.graph.getComponentSizes()
        self.numComponents = self.graph.getNumComponents()
        if self.widget == None:
            return
        self.widget.ComponentOne.currentIndexChanged.disconnect(self.ComponentOneChanged)
        self.widget.ComponentTwo.currentIndexChanged.disconnect(self.ComponentTwoChanged)

        self.widget.ComponentOne.clear()
        self.widget.ComponentTwo.clear()
        
        componentSizes = self.graph.getComponentSizes()
        self.numComponents = self.graph.getNumComponents()
        for i in range(0, self.numComponents):
            #TODO truncate size string to 2 sigfigs
            descriptor = str(i) + ' - ' + str(round_to_2(componentSizes[i]))
            self.widget.ComponentOne.addItem(descriptor)
            self.widget.ComponentTwo.addItem(descriptor)
            
        self.widget.ComponentOne.setCurrentIndex(self.component1)
        self.widget.ComponentTwo.setCurrentIndex(self.component2)
        self.graph.setComponent1(max(self.component1, 0))
        self.graph.setComponent2(max(self.component2, 0))
        self.widget.ComponentOne.currentIndexChanged.connect(self.ComponentOneChanged)
        self.widget.ComponentTwo.currentIndexChanged.connect(self.ComponentTwoChanged)

    def pickConnectionNode(self, node):
        pass
        #if self.component1 == self.component2 and node.component == self.component1 or self.allowAllComponents:
        #    if self.node1 != None:
        #        if self.node1.order == node.order:
        #            self.unselectNode1()
        #            return
        #    if self.node2 != None:
        #        if self.node2.order == node.order:
        #            self.unselectNode2()
        #            return
        #    if self.node1 == None:
        #        self.node1 = node
        #        self.sigNodeSelected.emit(self.node1.order)
        #    elif self.node2 == None:
        #        self.node2 = node
        #        self.sigNodeSelected.emit(self.node2.order)
        #    else:
        #        self.node2 = self.node1
        #        self.node1 = node                    

        #elif node.component == self.component1:
        #    if self.node1 != None:
        #        if self.node1.order == node.order:
        #            self.unselectNode1()
        #            return
        #    self.unselectNode1()
        #    self.node1 = node
        #    self.sigNodeSelected.emit(self.node1.order)
            
        #elif node.component == self.component2:
        #    if self.node2 != None:
        #        if self.node2.order == node.order:
        #            self.unselectNode2()
        #            return
        #    self.unselectNode2()
        #    self.node2 = node
        #    self.sigNodeSelected.emit(self.node2.order)

        #else:
        #    if self.node1 != None:
        #        if self.node1.order == node.order:
        #            self.unselectNode1()
        #            return
        #    if self.node2 != None:
        #        if self.node2.order == node.order:
        #            self.unselectNode2()
        #            return
        #    if self.node1 == None:
        #        self.node1 = node
        #        #self.sigNodeSelected.emit(self.node1.order)
        #    elif self.node2 == None:
        #        self.node2 = node
        #        #self.sigNodeSelected.emit(self.node2.order)
        #    else:
        #        self.node2 = self.node1
        #        self.node1 = node     
        
    def unselectNode1(self):
        if self.node1 != None:
            #self.sigNodeUnselected.emit(self.node1.order)
            self.node1 = None
        
    def unselectNode2(self):
        if self.node2 != None:
            #self.sigNodeUnselected.emit(self.node2.order)
            self.node2 = None
            
    def acceptConnection(self):
        if not self.isActive:
            return
        self.graph.joinOperation()
        self.graph.unselectAll()
        #if self.node1 != None and self.node2 != None:
        #    node1id = self.node1.id
        #    node2id = self.node2.id
        #    self.unselectNode1()
        #    self.unselectNode2()
        #    self.sigConnectionAccepted.emit(node1id, node2id)
        #else:
        #    print('No Connection Made ->')
        #    if self.node1 == None:
        #        print('No node on component 2 is selected')
        #    if self.node2 == None:
        #        print('No node on component 2 is selected')
        self.updateConnectionWidget()
            
    def enterMode(self, numComponents : int, widget : Ui_ConnectionTabWidget):
        self.graph.unselectAll()
        self.unselectNode1()
        self.unselectNode2()
        self.setNumComponents(numComponents)
        self.setWidget(widget)
        self.setNumComponents(numComponents)
        self.isActive = True
        if self.widget != None:
            pass

    def exitMode(self):
        self.graph.unselectAll()
        self.graph.setDisplayOnlySelectedComponents(False)
        self.graph.setShowBoundingBoxes(False)
        self.unselectNode1()
        self.unselectNode2()
        self.isActive = False
        if self.widget != None:
            pass
        #self.disconnect()
    
    
    

class BreakModeOptions(QObject):
    
    sigEdgeSelected = pyqtSignal(int)  #edge id

    sigEdgeUnselected = pyqtSignal(object)  #list(edge id)
    
    sigBreakAccepted = pyqtSignal(object) #MetaEdge3d
    
    sigSliderScaleChanged = pyqtSignal(float)

    @pyqtSlot(int)
    def sliderUpdated(self, sliderVal):
        scale = 1.0 * sliderVal / 10.0
        self.sigSliderScaleChanged.emit(scale)

    def __init__(self, parent = None, graph = None):
        super(BreakModeOptions, self).__init__(parent)
        self.breakEdge = None
        self.widget = None
        self.isActive = False
        self.numEdgesToBreak = 0
        self.graph = graph
        
    def pickEdge(self, eyeX, eyeY, eyeZ, rayX, rayY, rayZ):
        if self.isActive:
            self.graph.selectBreakEdge(eyeX, eyeY, eyeZ, rayX, rayY, rayZ)

    def setWidget(self, widget):
        if widget != None:
            self.widget = widget
            #self.widget.scaleSlider.sliderMoved.connect(self.sliderUpdated)
            self.widget.AcceptBreak.clicked.connect(self.acceptBreak)
        if self.widget != None:
            self.updateWidget()
        
    def updateWidget(self):
        if self.widget == None:
            return
        edgesString = str(self.graph.getNumEdgesToBreak())
        self.widget.edgesToBreak.setText(edgesString)
        
    def selectBreakEdge(self, edge):
        pass
        if self.breakEdge != None:
            if self.breakEdge.order == edge.order:
                self.unselectBreakEdge()
                return
        self.unselectBreakEdge()
        self.breakEdge = edge
        self.sigEdgeSelected.emit(self.breakEdge.order)
        
        
    def unselectBreakEdge(self):
        pass
        if self.breakEdge != None:
            self.sigEdgeUnselected.emit([self.breakEdge.order])
            self.breakEdge = None
                                     
    def acceptBreak(self):
        print('breaking')
        if not self.isActive:
            return
        self.graph.breakOperation()
        self.graph.unselectAll()
        self.updateWidget()
        pass
        if self.breakEdge != None:
            edgeToBreak = self.breakEdge
            self.unselectBreakEdge()
            self.sigBreakAccepted.emit(edgeToBreak)
        else:
            print('No Break Performed -> ')
            print('no edge selected to break')
        

    def enterMode(self, widget = None):
        self.graph.unselectAll()
        self.graph.setDisplayOnlySelectedComponents(False)
        self.unselectBreakEdge()
        self.setWidget(widget)
        self.isActive = True
        if self.widget != None:
            self.setWidget(widget)

    def exitMode(self):
        self.graph.unselectAll()
        self.unselectBreakEdge()
        self.isActive = False
        if self.widget != None:
            pass

    @pyqtSlot(int)
    def numEdgesToBreakUpdated(self, numedges):
        self.numEdgesToBreak = numedges
        self.updateWidget()
        #self.disconnect()
    
class SplitModeOptions(QObject):
    
    
    sigEdgesUnselected = pyqtSignal(object)  #list(edgeIds)

    sigEdgeSelected = pyqtSignal(int)  #edgeId

    sigSplitAccepted = pyqtSignal(object, object)  #MetaEdge3d primary, list(MetaEdge3d) accompanying

    sigSliderScaleChanged = pyqtSignal(float)

    @pyqtSlot(int)
    def sliderUpdated(self, sliderVal):
        scale = 1.0 * sliderVal / 10.0
        self.sigSliderScaleChanged.emit(scale)

    def __init__(self, parent = None, graph = None):
        super(SplitModeOptions, self).__init__(parent)
        self.primaryEdge = None
        self.widget = None
        self.secondaryEdges = []
        self.isActive = False
        self.numEdgesToBreak = 0
        self.graph = graph

    def pickEdge(self, eyeX, eyeY, eyeZ, rayX, rayY, rayZ):
        if self.isActive:
            self.graph.selectSplitEdge(eyeX, eyeY, eyeZ, rayX, rayY, rayZ)

    def setWidget(self, widget):
        if widget != None:
            self.widget = widget
            #self.widget.scaleSlider.sliderMoved.connect(self.sliderUpdated)
            self.widget.AcceptSplit.clicked.connect(self.acceptSplit)
        if self.widget != None:
            self.updateWidget()

    def updateWidget(self):
        if self.widget == None:
            return
        edgesString = str(self.graph.getNumEdgesToBreak())
        #edgesString = str(self.numEdgesToBreak)
        self.widget.edgesToBreak.setText(edgesString)

    def selectEdge(self, edge):
        pass
        if self.primaryEdge != None:
            #If the selected edge is the same as the primary edge, unselect everything
            if self.primaryEdge.order == edge.order:
                self.unselectAll()
                return
            
            if (self.primaryEdge.node0 == edge.node0 or self.primaryEdge.node1 == edge.node0 or 
                self.primaryEdge.node0 == edge.node1 or self.primaryEdge.node1 == edge.node1):

                #If the selected edge is one of the secondary edges already, unselect that secondary edge
                for secondaryEdge in self.secondaryEdges:
                    if edge.order == secondaryEdge.order:
                        self.sigEdgesUnselected.emit([secondaryEdge.order])
                        self.secondaryEdges.remove(secondaryEdge)
                        return
                #If the selected edge is neighbors with the primary, and not already selected, select it
                self.secondaryEdges.append(edge)

            else:
                #If this edge isn't a neighbor to the primary edge, then make this the primary edge, dump others
                self.unselectAll()
                self.primaryEdge = edge
        else:
            #If there is no primary edge selected, make this the primary and announce it
            self.primaryEdge = edge

        self.sigEdgeSelected.emit(edge.order)


    def unselectAll(self):
        self.graph.unselectAll()
        pass
        if self.primaryEdge != None:
            self.secondaryEdges.append(self.primaryEdge)
            edgeIds = []
            for edge in self.secondaryEdges:
                edgeIds.append(edge.order)
            self.sigEdgesUnselected.emit(edgeIds)
            self.secondaryEdges = []
            self.primaryEdge = None
        self.graph.unselectAll()

    def checkPrimaryConnectivity(self):
        pass
        node0Good = False
        node1Good = False
        if self.primaryEdge != None:
            p = self.primaryEdge
            for s in self.secondaryEdges:
                if s.node0 == p.node0 or s.node1 == p.node0:
                    node0Good = True
                if s.node0 == p.node1 or s.node1 == p.node1:
                    node1Good = True
        return (node0Good and node1Good)

    def acceptSplit(self):
        if not self.isActive:
            return
        self.graph.splitOperation()
        #if self.checkPrimaryConnectivity():
        #    primaryEdge = self.primaryEdge
        #    secondaryEdges = self.secondaryEdges
        #    self.unselectAll()
        #    self.sigSplitAccepted.emit(primaryEdge, secondaryEdges)
        #else:
        #    print('No Split Performed -> ')
        #    if self.primaryEdge == None:
        #        print('No center edge selected to split on')
        #    else:
        #        print('Edges on either side of the edge to split are not selected')

        self.graph.unselectAll()
        self.updateWidget()



    def enterMode(self, widget = None):
        self.unselectAll()
        self.setWidget(widget)
        self.isActive = True
        if self.widget != None:
            self.setWidget(widget)
        self.graph.unselectAll()

    def exitMode(self):
        self.graph.unselectAll()
        self.unselectAll()
        self.isActive = False
        if self.widget != None:
            pass
        
        #self.disconnect()

    @pyqtSlot(int)
    def numEdgesToBreakUpdated(self, numEdges):
        self.numEdgesToBreak = numEdges
        self.updateWidget()


class AddNodeOptions(QObject):

    def __init__(self, parent = None, graph = None):
        super(AddNodeOptions, self).__init__(parent)
        self.widget = None
        self.isActive = False
        self.graph = graph
        
    def pickNode(self, eyeX, eyeY, eyeZ, rayX, rayY, rayZ):
        if self.isActive:
            self.graph.selectPromotionNode(eyeX, eyeY, eyeZ, rayX, rayY, rayZ)

    def setWidget(self, widget):
        if widget != None:
            self.widget = widget
            #self.widget.scaleSlider.sliderMoved.connect(self.sliderUpdated)
            self.widget.AcceptNode.clicked.connect(self.acceptNode)
        
                                     
    def acceptNode(self):
        print('breaking')
        if not self.isActive:
            return
        self.graph.promoteOperation()
        self.graph.unselectAll()

    def enterMode(self, widget = None):
        self.isActive = True
        self.graph.unselectAll()
        self.setWidget(widget)
        if self.widget != None:
            self.setWidget(widget)

    def exitMode(self):
        self.graph.unselectAll()
        self.isActive = False
        if self.widget != None:
            pass