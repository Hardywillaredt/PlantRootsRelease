# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 02:48:14 2017

@author: Will
"""

from RootsTool import  Point3d, RootAttributes, Skeleton, mgraph
#MetaNode3d, MetaEdge3d, MetaGraph,

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5 import QtGui

from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
#from SkeletonViewer import *

import sys
from RootsUI import Ui_RootsUI
from EditingTabWidget import Ui_EditingTabWidget
from VisualizationTabWidget import Ui_VisualizationTabWidget
#from ConnectionTabWidget import Ui_ConnectionTabWidget
#from BreakTabWidget import Ui_BreakTabWidget
#from SplitTabWidget import Ui_SplitTabWidget
#from AddNodeTabWidget import Ui_AddNodeTabWidget

import matplotlib.cm as cm
import matplotlib.pyplot as plt

import test_glviewer as tgl
#from GLObjects import MetaGraphGL, Colorization

#from MetaGraphThread import MetaGraphThread
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import types

#class RootsGUI(Ui_RootsUI):
#    def __init__(self, dialog):
#        Ui_RootsUI.__init__(self)
#        self.setupUi(dialog)
#        self.dlg = dialog
#        self.LoadFile.clicked.connect(self.PickFile)
##        layout = self.GLWidgetHolder.layout
#        layout = QVBoxLayout(self.GLWidgetHolder)
#        layout.addStretch(1)
#        self.GLView = tgl.GLWidget()
##        self.GLView = SkeletonViewer()
#        layout.addChildWidget(self.GLView)
#        
#        self.GLWidgetHolder.setLayout(layout)
#        self.GLWidgetHolder.show()
#        #self.GLView = SkeletonViewer(self.GLWidgetHolder)
#        
#    def PickFile(self):
#        options = QFileDialog.Options()
#        
#        options |= QFileDialog.DontUseNativeDialog
#        self.loadFileName = QFileDialog.getOpenFileName(self.dlg, 'Open File', "")
#        qDebug(str(self.loadFileName[0]))
#        self.LoadSkeleton(str(self.loadFileName[0]))
#        
#    def LoadSkeleton(self, filename):
#        self.skeleton = Skeleton(filename)
#        self.GLView.setSkeleton(self.skeleton)

NoMode = 0
ConnectionMode = 1
BreakMode = 2
SplitMode = 3


        

def getColorList(size, colormap):
    colorList = []
    minval = 0
    maxval = 1
    for i in range(0, size):
        colorList.append(i)
        maxval = i

    norm = plt.Normalize(minval, maxval)
    listFormat = colormap(norm(colorList))

    return listFormat.tolist()


from math import log10, floor
def round_to_2(x):
  return round(x, -int(floor(log10(abs(x)))) + 1)

class VisualizationTabWidget(Ui_VisualizationTabWidget, QObject):

    viewSkeleton = pyqtSignal(bool)
    viewGraph = pyqtSignal(bool)
    viewBoth = pyqtSignal(bool)

    backgroundColorChanged = pyqtSignal(float, float, float)
    loadMeshSig = pyqtSignal()

    def getHeatmap(self, idx : int):
        if idx == 0:
            return [[1.0, 0.0, 0.0, 1.0]]
        else:
            return getColorList(1000, cm.get_cmap(self.heatmapOptions[idx]))

    @pyqtSlot(int)
    def edgeColorizationChanged(self, optionId : int):
        if optionId == 0: #thickness
            self.graph.colorizeEdgesByThickness()
            pass
        elif optionId == 1: #width
            self.graph.colorizeEdgesByWidth()
            pass
        elif optionId == 2: #thickness / width
            self.graph.colorizeEdgesByRatio()
            pass
        elif optionId ==3 : #component
            self.graph.colorizeEdgesByComponent()
            pass


    @pyqtSlot(int)
    def nodeColorizationChanged(self, optionId : int):
        if optionId == 0: #thickness
            self.graph.colorizeNodesByThickness()
            #self.graph.nodeColorization = Colorization.THICKNESS
            pass
        elif optionId == 1: #width
            self.graph.colorizeNodesByWidth()
            #self.graph.nodeColorization = Colorization.WIDTH
            pass
        elif optionId == 2: #degree
            self.graph.colorizeNodesByDegree()
            #self.graph.nodeColorization = Colorization.DEGREE
            pass
        elif optionId == 3: #component
            self.graph.colorizeNodesByComponent()
            #self.graph.nodeColorization = Colorization.COMPONENTS
            pass
        elif optionId == 4: #flat node color
            self.graph.colorizeNodesByConstantColor()
    @pyqtSlot(int)
    def nodeHeatmapChanged(self, optionId : int):
        heatmap = self.getHeatmap(optionId)
        self.graph.assignNodeHeatmap(heatmap)

    @pyqtSlot(int)
    def edgeHeatmapChanged(self, optionId : int):
        heatmap = self.getHeatmap(optionId)
        self.graph.assignEdgeHeatmap(heatmap)

    @pyqtSlot(int)
    def junctionScaleChanged(self, sliderVal):
        scale = 1.0 * sliderVal / 10.0
        self.graph.setJunctionScale(scale)

    @pyqtSlot(int)
    def endpointScaleChanged(self, sliderVal):
        scale = 1.0 * sliderVal / 10.0
        self.graph.setEndpointScale(scale)

    @pyqtSlot(int)
    def edgeScaleChanged(self, sliderVal):
        scale = 1.0 * sliderVal / 10.0
        scale = max(scale, 1.0)
        self.graph.setEdgeScale(scale)


    @pyqtSlot()
    def edgeColorFloorChanged(self):
        sliderVal = self.edgeColorFloor.value()
        floor = 1.0 * sliderVal / 100.0
        if not self.edgeColorFloor.isSliderDown():
            self.graph.setEdgeColorFloor(floor)

    @pyqtSlot()
    def edgeColorCeilingChanged(self):
        sliderVal = self.edgeColorCeiling.value()
        ceiling = 1.0 * sliderVal / 100.0
        self.graph.setEdgeColorCeiling(ceiling)

    @pyqtSlot()
    def nodeColorFloorChanged(self):
        sliderVal = self.nodeColorFloor.value()
        floor = 1.0 * sliderVal / 100.0
        self.graph.setNodeColorFloor(floor)

    @pyqtSlot()
    def nodeColorCeilingChanged(self):
        sliderVal = self.nodeColorCeiling.value()
        ceiling = 1.0 * sliderVal / 100.0
        self.graph.setNodeColorCeiling(ceiling)

    @pyqtSlot(bool)
    def showJunctionsPressed(self, showJunctions : bool):
        self.graph.showJunctions(showJunctions)

    @pyqtSlot(bool)
    def showEndpointsPressed(self, showEndpoints : bool):
        self.graph.showEndpoints(showEndpoints)

    @pyqtSlot(bool)
    def showEdgesPressed(self, showEdges : bool):
        self.graph.showEdges(showEdges)

    @pyqtSlot(bool)
    def magnifyNonBridgesPressed(self, magnifyNonBridges : bool):
        self.graph.magnifyNonBridges(magnifyNonBridges)

    @pyqtSlot(bool)
    def showOnlyNonBridgesPressed(self, showOnly : bool):
        self.graph.showOnlyNonBridges(showOnly)

    @pyqtSlot(bool)
    def backgroundColorClicked(self, active):
        pickedColor = QtWidgets.QColorDialog.getColor(self.currentBackground, self.widget)
        self.backgroundColorChanged.emit(pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentBackground = pickedColor

    @pyqtSlot(bool)
    def constantNodeColorClicked(self, active):
        pickedColor = QtWidgets.QColorDialog.getColor(self.currentNodeColor, self.widget)
        self.graph.setConstantNodeColor(pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentNodeColor = pickedColor

    @pyqtSlot(bool)
    def edgeSelectionColorClicked(self, active):
        pickedColor = QtWidgets.QColorDialog.getColor(self.currentEdgeSelectionColor, self.widget)
        self.graph.setEdgeSelectionColor(pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentEdgeSelectionColor = pickedColor

    @pyqtSlot(bool)
    def loadMeshClicked(self, active : bool):
        self.loadMeshSig.emit()

    @pyqtSlot(bool)
    def meshColorClicked(self, active : bool):
        pickedColor = QtWidgets.QColorDialog.getColor(self.currentMeshColor, self.widget)
        self.graph.setMeshColor(pickedColor.redF(), pickedColor.greenF(), pickedColor.blueF())
        self.currentMeshColor = pickedColor

    @pyqtSlot(bool)
    def displayMeshClicked(self, doShow : bool):
        self.graph.showMesh(doShow)

    @pyqtSlot()
    def meshAlphaChanged(self):
        alphaInt = self.meshAlpha.value()
        alpha = 1.0 * alphaInt / 100.0
        self.graph.setMeshAlpha(alpha)

    def __init__(self, widget, graphObject : mgraph, viewSkeletonButton, viewGraphButton, viewBothButton):
        Ui_VisualizationTabWidget.__init__(self)
        QObject.__init__(self)
        self.setupUi(widget)
        self.widget = widget
        self.graph = graphObject
        self.currentBackground = QColor(255, 255, 255)
        self.currentNodeColor = QColor(0, 0, 0)
        self.currentEdgeSelectionColor = QColor(255, 255, 255)
        self.currentMeshColor = QColor(0, 0, 255)

        self.graph.setConstantNodeColor(self.currentNodeColor.redF(), self.currentNodeColor.greenF(), self.currentNodeColor.blueF())
        self.graph.setEdgeSelectionColor(self.currentEdgeSelectionColor.redF(), self.currentEdgeSelectionColor.greenF(), self.currentEdgeSelectionColor.blueF())
        
        self.graph.setMeshColor(self.currentMeshColor.redF(), self.currentMeshColor.greenF(), self.currentMeshColor.blueF())
        

        self.edgeColorizationOptions = {}
        self.edgeColorizationOptions[0] = "Thickness"
        self.edgeColorizationOptions[1] = "Width"
        self.edgeColorizationOptions[2] = "Thick/Width"
        self.edgeColorizationOptions[3] = "Component"

        self.nodeColorizationOptions = {}
        self.nodeColorizationOptions[0] = "Thickness"
        self.nodeColorizationOptions[1] = "Width"
        self.nodeColorizationOptions[2] = "Degree"
        self.nodeColorizationOptions[3] = "Component"
        self.nodeColorizationOptions[4] = "Flat Color"
        self.heatmapOptions = {}
        self.heatmapOptions[0] = "None"
        self.heatmapOptions[1] = "viridis"
        self.heatmapOptions[2] = "plasma"
        self.heatmapOptions[3] = "inferno"
        self.heatmapOptions[4] = "magma"
        self.heatmapOptions[5] = "hot"
        self.heatmapOptions[6] = "cool"
        self.heatmapOptions[7] = "gist_heat"
        self.heatmapOptions[8] = "BuGn"
        self.heatmapOptions[9] = "jet"



        for key in self.edgeColorizationOptions:
            self.edgeColorization.addItem(self.edgeColorizationOptions[key])

        for key in self.nodeColorizationOptions:
            self.nodeColorization.addItem(self.nodeColorizationOptions[key])

        for key in self.heatmapOptions:
            self.edgeHeatmapType.addItem(self.heatmapOptions[key])
            self.nodeHeatmapType.addItem(self.heatmapOptions[key])
        



        self.edgeColorization.currentIndexChanged.connect(self.edgeColorizationChanged)
        self.nodeColorization.currentIndexChanged.connect(self.nodeColorizationChanged)
        self.edgeHeatmapType.currentIndexChanged.connect(self.edgeHeatmapChanged)
        self.nodeHeatmapType.currentIndexChanged.connect(self.nodeHeatmapChanged)

        self.edgeColorization.setCurrentIndex(1)
        self.nodeColorization.setCurrentIndex(1)
        self.edgeColorization.setCurrentIndex(0)
        self.nodeColorization.setCurrentIndex(0)

        self.showEndpoints.toggled.connect(self.showEndpointsPressed)
        self.showJunctions.toggled.connect(self.showJunctionsPressed)
        self.showEdges.toggled.connect(self.showEdgesPressed)
        self.magnifyNonBridges.toggled.connect(self.magnifyNonBridgesPressed)
        self.displayOnlyNonBridges.toggled.connect(self.showOnlyNonBridgesPressed)

        self.backgroundColor.clicked.connect(self.backgroundColorClicked)
        self.constantNodeColor.clicked.connect(self.constantNodeColorClicked)
        self.edgeSelectionColor.clicked.connect(self.edgeSelectionColorClicked)


        self.showEndpoints.setChecked(True)
        self.showJunctions.setChecked(True)
        self.showEdges.setChecked(True)
        self.magnifyNonBridges.setChecked(False)
        

        self.loadMeshButton.clicked.connect(self.loadMeshClicked)
        self.meshColorButton.clicked.connect(self.meshColorClicked)
        self.displayMesh.toggled.connect(self.displayMeshClicked)

        self.displayMesh.setChecked(False)


        #setting slider callbacks and values
        self.edgeScale.valueChanged.connect(self.edgeScaleChanged)
        self.junctionScale.valueChanged.connect(self.junctionScaleChanged)
        self.endpointScale.valueChanged.connect(self.endpointScaleChanged)
        self.edgeColorFloor.sliderReleased.connect(self.edgeColorFloorChanged)
        self.edgeColorCeiling.sliderReleased.connect(self.edgeColorCeilingChanged)
        self.nodeColorFloor.sliderReleased.connect(self.nodeColorFloorChanged)
        self.nodeColorCeiling.sliderReleased.connect(self.nodeColorCeilingChanged)       
        self.meshAlpha.sliderReleased.connect(self.meshAlphaChanged)



        self.edgeColorFloor.setSliderDown(True)
        self.edgeColorCeiling.setSliderDown(True)
        self.nodeColorFloor.setSliderDown(True)
        self.nodeColorCeiling.setSliderDown(True)
        self.meshAlpha.setSliderDown(True)
        self.edgeScale.setValue(20)
        self.junctionScale.setValue(5)
        self.endpointScale.setValue(5)
        self.edgeColorFloor.setValue(0)
        self.edgeColorCeiling.setValue(100)
        self.nodeColorFloor.setValue(0)
        self.nodeColorCeiling.setValue(100)
        self.meshAlpha.setValue(30)
        self.edgeColorFloor.setSliderDown(False)
        self.edgeColorCeiling.setSliderDown(False)
        self.nodeColorFloor.setSliderDown(False)
        self.nodeColorCeiling.setSliderDown(False)
        self.meshAlpha.setSliderDown(False)



        

        
        
        

        self.viewSkeleton.emit(True)

        #self.geometryVisualization.currentIndexChanged.connect(self.geometryVisualizationChanged)

        #self.viewGraph.connect(viewGraphButton.trigger)
        #graphObject.enteringGraphView.connect(self.enteringGraphView)

        #self.viewSkeleton.connect(viewSkeletonButton.trigger)
        #graphObject.enteringSkeletonView.connect(self.enteringSkelView)

        #self.viewBoth.connect(viewBothButton.trigger)
        #graphObject.enteringBothView.connect(self.enteringBothView)


        #self.lowColor = QColor(Qt.blue)
        #self.highColor = QColor(Qt.red)

        #self.lowColorButton.setAutoFillBackground(True)
        #self.highColorButton.setAutoFillBackground(True)

        #self.setLowColor(self.lowColor)
        #self.setHighColor(self.highColor)

        #self.lowColorButton.clicked.connect(self.pickLowColor)
        #self.highColorButton.clicked.connect(self.pickHighColor)
       
        #self.lowColorChanged.connect(graphObject.lowColorChanged)
        #self.highColorChanged.connect(graphObject.highColorChanged)

        #self.lowColorChanged.emit(self.lowColor.redF(), self.lowColor.greenF(), self.lowColor.blueF())
        #self.highColorChanged.emit(self.highColor.redF(), self.highColor.greenF(), self.highColor.blueF())
        #self.geometryVisualizationOptions = {}
        #self.geometryVisualizationOptions[0] = "View Skeleton"
        #self.geometryVisualizationOptions[1] = "View MetaGraph"
        #self.geometryVisualizationOptions[2] = "View Both"
        #for key in self.geometryVisualizationOptions:
        #    self.geometryVisualization.addItem(self.geometryVisualizationOptions[key])


    #@pyqtSlot(bool)
    #def pickLowColor(self, someBool):
    #    pickedColor = QColorDialog.getColor(self.lowColor, self.widget)
    #    self.setLowColor(pickedColor)
    #@pyqtSlot(bool)
    #def pickHighColor(self, someBool):
    #    pickedColor = QColorDialog.getColor(self.highColor, self.widget)
    #    self.setHighColor(pickedColor)
    #@pyqtSlot(QColor)
    #def setLowColor(self, lowColor : QColor):
    #    self.lowColor = lowColor
    #    lowColorHSL = self.lowColor.toHsl()
    #    lowLightness = lowColorHSL.lightnessF()
    #    lowTextColor = QColor(Qt.black)
    #    if lowLightness < 0.1791:
    #        lowTextColor = QColor(Qt.white)
    #    self.lowColorButton.setStyleSheet( "background-color: " + self.lowColor.name() + "; color:" + lowTextColor.name())
    #    self.lowColorButton.update()
    #    self.lowColorChanged.emit(self.lowColor.redF(), self.lowColor.greenF(), self.lowColor.blueF())

    #@pyqtSlot(QColor)
    #def setHighColor(self, highColor : QColor):
    #    self.highColor = highColor

    #    highColorHSL = self.highColor.toHsl()
    #    highLightness = highColorHSL.lightnessF()
    #    highTextColor = QColor(Qt.black)
    #    if highLightness < 0.1791:
    #        highTextColor = QColor(Qt.white)
    #    self.highColorButton.setStyleSheet( "background-color: " + self.highColor.name() + "; color:" + highTextColor.name())
    #    self.highColorButton.update()

    #    self.highColorChanged.emit(self.highColor.redF(), self.highColor.greenF(), self.highColor.blueF())
            #@pyqtSlot(int)
    #def geometryVisualizationChanged(self, optionId : int):
    #    if optionId == 0: #skeleton
    #        self.viewSkeleton.emit(True)
    #        pass
    #    elif optionId == 1: #graph
    #        self.viewGraph.emit(True)
    #        pass
    #    elif optionId == 2: #both
    #        self.viewBoth.emit(True)
    #        pass
    #@pyqtSlot(bool)
    #def enteringSkelView(self, val : bool):
    #    self.geometryVisualization.currentIndexChanged.disconnect(self.geometryVisualizationChanged)
    #    self.geometryVisualization.setCurrentIndex(0)
    #    self.geometryVisualization.currentIndexChanged.connect(self.geometryVisualizationChanged)
    #@pyqtSlot(bool)
    #def enteringGraphView(self, val : bool):
    #    self.geometryVisualization.currentIndexChanged.disconnect(self.geometryVisualizationChanged)
    #    self.geometryVisualization.setCurrentIndex(1)
    #    self.geometryVisualization.currentIndexChanged.connect(self.geometryVisualizationChanged)
    #@pyqtSlot(bool)
    #def enteringBothView(self, val : bool):
    #    self.geometryVisualization.currentIndexChanged.disconnect(self.geometryVisualizationChanged)
    #    self.geometryVisualization.setCurrentIndex(2)
    #    self.geometryVisualization.currentIndexChanged.connect(self.geometryVisualizationChanged)

class EditingTabWidget(Ui_EditingTabWidget, QObject):

    modeChangeSig = pyqtSignal(int)


    @pyqtSlot(bool)
    def showOnlySelected(self, doShow : bool):
        self.showSelected = doShow
        if self.mode == ConnectionMode:
            if self.graph != None:
                self.graph.setDisplayOnlySelectedComponents(self.showSelected)

    @pyqtSlot(int)
    def componentOneChanged(self, component : int):
        self.component1 = component
        if self.mode == ConnectionMode:
            if self.graph != None:
                self.graph.setComponent1(component)

    @pyqtSlot(int)
    def componentTwoChanged(self, component : int):
        self.component2 = component
        if self.mode == ConnectionMode:
            if self.graph != None:
                self.graph.setComponent2(component)

    @pyqtSlot(bool)
    def showBoundingBoxes(self, doShow : bool):
        self.showBoxes = doShow
        if self.mode == ConnectionMode:
            if self.graph != None:
                self.graph.setShowBoundingBoxes(self.showBoxes)

    @pyqtSlot(bool)
    def connectionModePressed(self, pressed : bool):
        self.changeMode(ConnectionMode)
        #self.exitCurrentMode()
        #if self.mode != ConnectionMode:
        #    self.mode = ConnectionMode
        #    if self.graph != None:
        #        self.graph.unselectAll()
        #        self.updateWidget()
        #    self.modeChangeSig.emit(self.mode)

    @pyqtSlot(bool)
    def acceptConnectionPressed(self, pressed : bool):
        if self.mode == ConnectionMode:
            self.graph.joinOperation()
            self.updateWidget()

    @pyqtSlot(bool)
    def breakModePressed(self, pressed : bool):
        self.changeMode(BreakMode)
        #self.exitCurrentMode()
        #if self.mode != BreakMode:
        #    self.mode = BreakMode
        #    if self.graph != None:
        #        self.graph.unselectAll()
        #        self.updateWidget()
        #    self.modeChangeSig.emit(self.mode)

    @pyqtSlot(bool)
    def splitModePressed(self, pressed : bool):
        self.changeMode(SplitMode)
        #self.exitCurrentMode()
        #if self.mode != SplitMode:
        #    self.mode = SplitMode
        #    if self.graph != None:
        #        self.graph.unselectAll()
        #        self.updateWidget()
        #    self.modeChangeSig.emit(self.mode)

    @pyqtSlot(bool)
    def acceptRemovalPressed(self, pressed : bool):
        if self.mode == BreakMode:
            if self.graph != None:
                self.graph.breakOperation()
                self.updateWidget()
        if self.mode == SplitMode:
            if self.graph != None:
                self.graph.splitOperation()
                self.updateWidget()

    def __init__(self, graphObject : mgraph, widget=None):
        Ui_EditingTabWidget.__init__(self)
        QObject.__init__(self)
        self.setupUi(widget)
        self.widget = widget
        self.graph = graphObject
        self.showSelected = False
        self.showBoxes = False
        self.mode = NoMode
        self.component1 = 0
        self.component2 = 0

        self.showOnlySelectedButton.toggled.connect(self.showOnlySelected)
        self.showBoundingBoxesButton.toggled.connect(self.showBoundingBoxes)
        self.ComponentOne.currentIndexChanged.connect(self.componentOneChanged)
        self.ComponentTwo.currentIndexChanged.connect(self.componentTwoChanged)
        self.ConnectionModeButton.clicked.connect(self.connectionModePressed)
        self.AcceptConnectionButton.clicked.connect(self.acceptConnectionPressed)
        self.BreakModeButton.clicked.connect(self.breakModePressed)
        self.SplitModeButton.clicked.connect(self.splitModePressed)
        self.AcceptRemovalButton.clicked.connect(self.acceptRemovalPressed)

        
    def changeMode(self, mode : int):
        if self.mode != mode:
            self.mode = mode
            print("changing mode")
            if self.graph != None:
                self.graph.unselectAll()
                self.updateWidget()
                if mode != ConnectionMode:
                    self.graph.setDisplayOnlySelectedComponents(False)
                    self.graph.setShowBoundingBoxes(False)
                if mode == ConnectionMode:
                    self.graph.setDisplayOnlySelectedComponents(self.showSelected)
                    self.graph.setShowBoundingBoxes(self.showBoxes)
            self.modeChangeSig.emit(self.mode)

    def exitCurrentMode(self):
        pass

    def setGraph(self, graph : mgraph):
        print("setting graph")
        self.graph = graph
        self.updateWidget()
        if self.mode == ConnectionMode and self.graph != None:
            self.graph.setDisplayOnlySelectedComponents(self.showSelected)
            self.graph.setShowBoundingBoxes(self.showBoxes)

    def updateWidget(self):
        if self.graph != None:
            edgesString = str(self.graph.getNumEdgesToBreak())
            self.edgesToBreak.setText(edgesString)

            self.ComponentOne.currentIndexChanged.disconnect(self.componentOneChanged)
            self.ComponentTwo.currentIndexChanged.disconnect(self.componentTwoChanged)

            self.ComponentOne.clear()
            self.ComponentTwo.clear()
        
            componentSizes = self.graph.getComponentSizes()
            numComponents = self.graph.getNumComponents()
            for i in range(0, numComponents):
                descriptor = str(i) + ' - ' + str(round_to_2(componentSizes[i]))
                self.ComponentOne.addItem(descriptor)
                self.ComponentTwo.addItem(descriptor)

            self.component1 = max(self.component1, 0)
            self.component2 = max(self.component2, 0)
            self.component1 = min(self.component1, numComponents - 1)
            self.component2 = min(self.component2, numComponents - 1)

            self.ComponentOne.setCurrentIndex(self.component1)
            self.ComponentTwo.setCurrentIndex(self.component2)
            self.graph.setComponent1(self.component1)
            self.graph.setComponent2(self.component2)
        
            self.ComponentOne.currentIndexChanged.connect(self.componentOneChanged)
            self.ComponentTwo.currentIndexChanged.connect(self.componentTwoChanged)
        else:
            self.edgesToBreak.setText("")
            self.ComponentOne.clear()
            self.ComponentTwo.clear()

#class ConnectionTabWidget(Ui_ConnectionTabWidget):
#    def __init__(self, widget=None):
#        Ui_ConnectionTabWidget.__init__(self)
#        self.setupUi(widget)
#class BreakTabWidget(Ui_BreakTabWidget, QObject):
#    def __init__(self, widget=None):
#        Ui_BreakTabWidget.__init__(self)
#        QObject.__init__(self)
#        self.setupUi(widget)
#        self.widget = widget

#class SplitTabWidget(Ui_SplitTabWidget, QObject):
#    def __init__(self, widget=None):
#        Ui_SplitTabWidget.__init__(self)
#        QObject.__init__(self)
#        self.setupUi(widget)

#        self.widget = widget

#class AddNodeTabWidget(Ui_AddNodeTabWidget, QObject):
#    def __init__(self, widget = None):
#        Ui_AddNodeTabWidget.__init__(self)
#        QObject.__init__(self)
#        self.setupUi(widget)

#        self.widget = widget
        

class RootsTabbedProgram(QMainWindow):
    
    @pyqtSlot()
    def notifyConfirmed(self):
        print('Notify confirmed')
        
    @pyqtSlot()
    def terminateConfirmed(self):
        print('Terminate confirmed')
        
    @pyqtSlot()
    def mainPrint(self, toPrint : object):
        print(toPrint)
        
    @pyqtSlot()
    def acceptPressed(self):
        print('accept pressed')

    

    @pyqtSlot(int)
    def tabChanged(self, tabPos):
        if tabPos == 0:
            pass
        if tabPos == 1:
            self.enterConnectionMode()
            pass
        if tabPos == 2:
            self.enterBreakMode()
            pass
        if tabPos == 3:
            self.enterSplitMode()
            pass

    def __init__(self, parent = None):
        super(RootsTabbedProgram, self).__init__(parent)
        
        self.currentMode = -2
        self.glwidget = tgl.GLWidget(self)
        self.dockedWidget = None
        self.__setUI()
        
        
    def __setUI(self, title="RootsEditor"):
        self.mainMenu = self.menuBar()
        
        self.mainMenu.setNativeMenuBar(False)
        self.fileMenu = self.mainMenu.addMenu('File')
        
        loadButton = QAction('Load rootfile', self)
        loadButton.setShortcut('Ctrl+L')
        loadButton.setShortcutContext(Qt.ApplicationShortcut)
        loadButton.setStatusTip('Load rootfile or skeleton')
        loadButton.triggered.connect(self.loadFile)
        self.fileMenu.addAction(loadButton)

        loadMeshButton = QAction('Load mesh file', self)
        loadMeshButton.setShortcut('Ctrl+M')
        loadMeshButton.setShortcutContext(Qt.ApplicationShortcut)
        loadMeshButton.setStatusTip('Load root mesh')
        loadMeshButton.triggered.connect(self.loadMesh)
        self.fileMenu.addAction(loadMeshButton)

        saveButton = QAction('Save rootfile', self)
        saveButton.setShortcut('Ctrl+S')
        saveButton.setShortcutContext(Qt.ApplicationShortcut)
        saveButton.setStatusTip('Save rootfile')
        saveButton.triggered.connect(self.saveFile)
        self.fileMenu.addAction(saveButton)
        
        
        exitButton = QAction('Exit', self)
        exitButton.setShortcut('Ctrl+E')
        exitButton.setShortcutContext(Qt.ApplicationShortcut)
        exitButton.setStatusTip('Exit RootsEditor')
        exitButton.triggered.connect(self.close)
        self.fileMenu.addAction(exitButton)
        
        self.modeMenu = self.mainMenu.addMenu('Mode')
        
        connectionModeButton = QAction('Connection', self)
        connectionModeButton.setShortcut('Ctrl+C')
        connectionModeButton.setShortcutContext(Qt.ApplicationShortcut)
        connectionModeButton.setStatusTip('Connect broken components')
        connectionModeButton.triggered.connect(self.enterConnectionMode)
        self.modeMenu.addAction(connectionModeButton)
        
        breakModeButton = QAction('Break', self)
        breakModeButton.setShortcut('Ctrl+B')
        breakModeButton.setShortcutContext(Qt.ApplicationShortcut)
        breakModeButton.setStatusTip('Break invalid edges')
        breakModeButton.triggered.connect(self.enterBreakMode)
        self.modeMenu.addAction(breakModeButton)
        
        
        splitModeButton = QAction('Split', self)
        splitModeButton.setShortcut('Ctrl+X')
        splitModeButton.setShortcutContext(Qt.ApplicationShortcut)
        splitModeButton.setStatusTip('Split edges between two branches that have merged')
        splitModeButton.triggered.connect(self.enterSplitMode)
        self.modeMenu.addAction(splitModeButton)


        self.viewMenu = self.mainMenu.addMenu('View Mode')

        viewGraphButton = QAction('MetaGraph', self)
        viewGraphButton.setShortcut('Ctrl+G')
        viewGraphButton.setShortcutContext(Qt.ApplicationShortcut)
        viewGraphButton.setStatusTip('View the metagpraph only')
        self.viewMenu.addAction(viewGraphButton)

        viewSkeletonButton = QAction('Skeleton', self)
        viewSkeletonButton.setShortcut('Ctrl+R')
        viewSkeletonButton.setShortcutContext(Qt.ApplicationShortcut)
        viewSkeletonButton.setStatusTip('View the skeleton only')
        self.viewMenu.addAction(viewSkeletonButton)

        viewBothButton = QAction('Both', self)
        viewBothButton.setShortcut('Ctrl+D')
        viewBothButton.setShortcutContext(Qt.ApplicationShortcut)
        viewBothButton.setStatusTip('View metagraph and skeleton simultaneously')
        self.viewMenu.addAction(viewBothButton)


        recenterButton = QAction('Recenter', self)
        recenterButton.setShortcut('Ctrl+F')
        recenterButton.setShortcutContext(Qt.ApplicationShortcut)
        recenterButton.setStatusTip('Recenter view on skeleton')
        recenterButton.triggered.connect(self.glwidget.recenter)
        self.viewMenu.addAction(recenterButton)


        acceptShortcut = QAction('Accept Operation', self)
        acceptShortcut.setShortcut('Ctrl+A')
        acceptShortcut.setShortcutContext(Qt.ApplicationShortcut)
        acceptShortcut.triggered.connect(self.acceptPressed)
        self.addAction(acceptShortcut)
        

        centralWidget = QtWidgets.QWidget()

        self.setCentralWidget(centralWidget)
        centralLayout = QtWidgets.QGridLayout()
        centralLayout.addWidget(self.glwidget, 1, 1)
        centralWidget.setLayout(centralLayout)
        centralWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.glwidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.glwidget.setMinimumSize(200, 200)
        
        
        w = 1800
        h = 1000
        self.resize(w, h)
        self.installEventFilter(self)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle('Skeleton Viewer')
        self.dockedWidget = None
        self.viewWidget = None
        
        self.createTabWidget(viewSkeletonButton, viewGraphButton, viewBothButton)
        
    def createTabWidget(self, viewSkeletonButton, viewGraphButton, viewBothButton):
        rightDock = QDockWidget('Editing', self)
        rightDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.tabWidget = QTabWidget(rightDock)
        
        widget = QtWidgets.QWidget(self.tabWidget)
        self.EditingTab = EditingTabWidget(self.glwidget.graph, widget)
        self.tabWidget.addTab(widget, 'Editing')
        self.EditingTab.modeChangeSig.connect(self.switchModes)

        #widget = QtWidgets.QWidget(self.tabWidget)
        #self.ConnectionTab = ConnectionTabWidget(widget)
        #self.tabWidget.addTab(widget, 'Connection')
        
        #widget = QtWidgets.QWidget(self.tabWidget)
        #self.BreakTab = BreakTabWidget(widget)
        #self.tabWidget.addTab(widget, 'Break')

        #widget = QtWidgets.QWidget(self.tabWidget)
        #self.SplitTab = SplitTabWidget(widget)
        #self.tabWidget.addTab(widget, 'Split')

        rightDock.setWidget(self.tabWidget)
        label = QtWidgets.QLabel('', rightDock)
        rightDock.setTitleBarWidget(label)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, rightDock)
        self.dockWidget = rightDock

        self.tabWidget.currentChanged.connect(self.tabChanged)

        leftDock = QDockWidget('Visualization', self)
        leftDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        widget = QtWidgets.QWidget(leftDock)
        self.VisualizationTab = VisualizationTabWidget(widget, self.glwidget.graph, viewSkeletonButton, viewGraphButton, viewBothButton)
        self.VisualizationTab.backgroundColorChanged.connect(self.glwidget.backgroundColorChanged)

        self.VisualizationTab.loadMeshSig.connect(self.loadMesh)

        leftDock.setWidget(widget)
        label = QtWidgets.QLabel('', leftDock)
        leftDock.setTitleBarWidget(label)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, leftDock)
        self.leftDockWidget = leftDock

    @pyqtSlot(int)
    def switchModes(self, mode : int):
        if self.currentMode != mode:
            self.currentMode = mode
            self.glwidget.currentMode = mode

    def enterConnectionMode(self):
        if self.currentMode == ConnectionMode or self.currentMode == -2:
            return
        self.currentMode = ConnectionMode
        self.tabWidget.setCurrentIndex(1)
        self.glwidget.enterConnectionMode(self.ConnectionTab)

    
    def enterBreakMode(self):
        if self.currentMode == BreakMode or self.currentMode == -2:
            return
        self.currentMode = BreakMode
        self.tabWidget.setCurrentIndex(2)
        self.glwidget.enterBreakMode(self.BreakTab)
        
    def enterSplitMode(self):
        if self.currentMode == SplitMode or self.currentMode == -2:
            return
        self.currentMode = SplitMode
        self.tabWidget.setCurrentIndex(3)
        self.glwidget.enterSplitMode(self.SplitTab)

    def enterAddNodeMode(self):
        if self.currentMode == 3:
            return
        self.closeDockWidget()
        self.currentMode = 3

        self.closeDockWidget()

        dock = QDockWidget('Add Node Tab', self)
        dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        dockWidget = QWidget()
        AddTab = AddNodeTabWidget(dockWidget)

        dock.setWidget(dockWidget)
        label = QtWidgets.QLabel('', dock)
        dock.setTitleBarWidget(label)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        self.glwidget.enterAddNodeMode(AddTab)
        self.dockedWidget = dock

    
    def eventFilter(self, obj, event):
        return False

    def closeDockWidget(self):
        print('closing dock widget')
        if self.dockedWidget != None:
            print('dock widget is not none')
            self.dockedWidget.hide()
            self.dockedWidget.destroy()

    
    
        
    def loadFile(self):
        options = QFileDialog.Options()
        
        options |= QFileDialog.DontUseNativeDialog
        self.loadFileName = QFileDialog.getOpenFileName(self, 'Open File', "")
#        qDebug(str(self.loadFileName[0]))
        
        if self.loadFileName[0] != "":
            self.glwidget.loadFileEvent(str(self.loadFileName[0]))
            self.EditingTab.setGraph(self.glwidget.graph)
            #self.currentMode = -1
            #self.metaThread.loadFileEvent(str(self.loadFileName[0]))
    def loadMesh(self):
        options = QFileDialog.Options()

        options |= QFileDialog.DontUseNativeDialog
        meshFileName = QFileDialog.getOpenFileName(self, 'Open Mesh', "")

        if meshFileName != "":
            self.glwidget.graph.loadMeshFromFile(meshFileName[0])

    def saveFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.saveFileName = QFileDialog.getSaveFileName(self, 'Save File', filter="ply(*.ply)")

        if self.saveFileName[0] != "":
            self.glwidget.graph.saveToFile(self.saveFileName[0])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RootsTabbedProgram()
    window.show()
#    dialog = QDialog()
#    prog = RootsGUI(dialog)
    
#    dialog.show()
    sys.exit(app.exec_())
