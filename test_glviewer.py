import sys
import math

from Arcball import ArcballCamera, arcVec

from RootsTool import IssuesGL, VBOSphere
from ConnectionTabWidget import Ui_ConnectionTabWidget
from BreakTabWidget import Ui_BreakTabWidget
from SplitTabWidget import Ui_SplitTabWidget
from AddNodeTabWidget import Ui_AddNodeTabWidget

from PyQt5 import QtCore, QtGui, QtOpenGL, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from PyQt5.QtWidgets import QMainWindow


from camera import *
from vecmath import *
import numpy as np

from typing import Union
import random

try:
    from OpenGL.GL import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL grabber",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)
import OpenGL.GL as gl
from OpenGL.GLU import *
from OpenGL.GLUT import *

from ModeOptions import ConnectionModeOptions, BreakModeOptions, SplitModeOptions, AddNodeOptions


from RootsTool import  Point3d, RootAttributes, Skeleton, mgraph



NoMode = 0
ConnectionMode = 1
BreakMode = 2
SplitMode = 3
useArcball = True


def p3d2arr(p3d : Point3d):
    if isinstance(p3d, Point3d) or isinstance(p3d, MetaNode3d):
        return np.array([p3d.x(), p3d.y(), p3d.z()])
    else:
        return p3d

class GLWidget(QtOpenGL.QGLWidget):
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    @pyqtSlot(str)
    def loadFileEvent(self, filename : str):
        self.graph.loadFromFile(filename)
        self.recenter()
    
    @pyqtSlot(int, int)
    def acceptConnection(self, v0id, v1id):
        pass
            
    @pyqtSlot(object)
    def acceptBreak(self, edge):
        pass

    @pyqtSlot(object, object)
    def acceptSplit(self, splitEdge, secondaries):
        pass

    @pyqtSlot(object)
    def viewCenterChanged(self, center):
        self.camera.look_at(center)
        self.camera.viewCenter = center
        self.camera.standoff = np.linalg.norm(self.camera.viewCenter - self.camera.get_position())
        self.camera.increment_phi(0.01)
        self.camera.increment_theta(0.01)
        if not useArcball:
            self.camera.resolveAngularPosition()

    @pyqtSlot()
    def recenter(self):
        self.camera.viewCenter = p3d2arr(self.graph.skeleton.center)
        self.camera.standoff = self.graph.skeleton.radius*4
        self.arcball.setZoom(self.arcballRadius, arcVec(0, 0, -self.camera.standoff), arcVec(0, 1, 0))
        self.camera.resolveAngularPosition()
        self.graph.setZoom(math.log10(self.graph.skeleton.radius) / 2, 0.0, 0.0, self.camera.standoff, 0, 0, 1)

    @pyqtSlot(float, float, float)
    def backgroundColorChanged(self, r, g, b):
        self.backgroundColor = [r, g, b, 1.0]

    

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        
        self.setupInteraction()
        self.setupVis()
        self.cyls = list()

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.timeOut)
        self.timer.start(10)
        
        self.graph = mgraph()

        self.connectionOptions = ConnectionModeOptions(self, self.graph)
        self.breakOptions = BreakModeOptions(self, self.graph)
        self.splitOptions = SplitModeOptions(self, self.graph)
        self.addNodeOptions = AddNodeOptions(self, self.graph)

        self.modes = {-1 : 'NoMode', 0 : 'Connection Mode', 1 : 'Separation Mode', 2 : 'Spltting Mode'}
        
        self.currentMode = -1
    
    @pyqtSlot()
    def timeOut(self):
        if self.isWDown:
            self.camera.goForward(self.speed)
        elif self.isSDown:
            self.camera.goForward(-self.speed)
            
        if self.isADown:
            self.camera.goRight(-self.speed)
        elif self.isDDown:
            self.camera.goRight(self.speed)
        
        if self.isQDown:
            self.camera.roll(-0.01 * 5)
        elif self.isEDown:
            self.camera.roll(0.01 * 5)
        self.update()
        
        
    @pyqtSlot()
    def updateCurrentGL(self, modelGL : object):
        self.modelGL = modelGL
        self.hasModelGL = True

    def setupInteraction(self):
        self.isMouseLeftDown = False
        self.isMouseRightDown = False
        self.isMouseMiddleDown = False
        self.zoom = 1.0
        self.zoomDegrees = 0.0
        self.lastMouseX = 0.0
        self.lastMouseY = 0.0
        self.mousePressX = 0.0
        self.mousePressY = 0.0


        self.isWDown = False
        self.isADown = False
        self.isSDown = False
        self.isDDown = False
        self.isQDown = False
        self.isEDown = False

        self.baseSpeed = 0.15 * 5
        self.speed = self.baseSpeed
        self.installEventFilter(self)
        self.setFocusPolicy(Qt.StrongFocus)
        
    def setupVis(self):
        self.camera = Camera()
        initialPosition = v3(0, 0, -40)
        self.camera.set_position(initialPosition)
        self.viewCenter = v3()
        self.camera.look_at(self.viewCenter)
        self.camera.set_near(1.0)
        self.camera.set_far(5000.0)
        self.baseFov = (60.0 / 180.0) * np.pi
        self.maxFov = (90.0 / 180.0) * np.pi
        self.camera.set_fov(self.baseFov)
        w = float(self.width())
        h = float(self.height())
        self.camera.set_aspect(w/h)
        p = self.camera.get_model_matrix()
        self.imageCenterX = w / 2.0
        self.imageCenterY = h / 2.0
        self.backgroundColor = [0.3, 0.3, 0.3, 1.0]

        #self.graph.setZoom(self.graph.skeleton.radius, 0.0, 0.0, self.camera.standoff, 0, 0, 1)

        self.arcball = ArcballCamera()
        



        self.doStopRotation = False

        
    def __del__(self):
        self.makeCurrent()
        

    def initializeGL(self):
        lightPos = (1000.0, 1000.0, 1000.0, 1.0)
        lightPos2 = (-1000.0, -1000.0, 0, 1.0)

        lightpos0 = (1000.0, 0, 0, 1.0)
        lightpos1 = (0.0, 1000.0, 0, 1.0)
        lightpos2 = (0.0, 0.0, 1000.0, 1.0)
        lightpos3 = (750, 750, 750, 1.0)
        ambientLight = (1.0, 1.0, 1.0, 1.0)
        ref = (0.5, 0.0, 0.0, 1.0)
        ref2 = (1.0, 0.0, 0.0, 1.0)
        reflectance1 = (0.8, 0.1, 0.0, 0.7)
        reflectance2 = (0.0, 0.8, 0.2, 1.0)
        reflectance3 = (0.2, 0.2, 1.0, 1.0)
        
        
        glEnable(GL_LIGHT0)
        #glEnable(GL_LIGHT1)
        #glEnable(GL_LIGHT2)
        #glEnable(GL_LIGHT3)
        glLightfv(GL_LIGHT0, GL_POSITION, lightpos0)
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, (-1, 0, 0, 1.0))
        #glLightfv(GL_LIGHT1, GL_POSITION, lightpos1)
        #glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, (0, -1, 0, 1.0))
        #glLightfv(GL_LIGHT2, GL_POSITION, lightpos2)
        #glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, (0, 0, -1, 1.0))
        #glLightfv(GL_LIGHT3, GL_POSITION, lightpos3)
        #glLightfv(GL_LIGHT3, GL_SPOT_DIRECTION, (-1, -1, -1, 1.0))
        glDisable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.cx = 0
        self.cy = 0
        self.cz = 0
        self.rad = 10
        rad = self.rad

        self.rotX = 0.0
        self.rotY = 0.0

        glEnable(GL_NORMALIZE)
        glClearColor(self.backgroundColor[0], self.backgroundColor[1], self.backgroundColor[2], self.backgroundColor[3])
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera.get_fov_deg(), self.camera.get_aspect(), self.camera.get_near(), self.camera.get_far())
        
        glMatrixMode(GL_MODELVIEW)
        self.issuesGL = IssuesGL()
        self.sphere = VBOSphere()
        
        self.arcballRadius = 5.0
        self.arcball.setZoom(self.arcballRadius, arcVec(0, 0, -40), arcVec(0, 1, 0))
        

        random.seed(0)
        self.randvals = []
        for row in range(0, 201):
            self.randvals.append([])
            for col in range(0, 201):
                self.randvals[row].append(random.uniform(0.25, 1.0))


    def paintGL(self):
        glClearColor(self.backgroundColor[0], self.backgroundColor[1], self.backgroundColor[2], self.backgroundColor[3])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        

        
        pos = self.camera.get_position()
        up = self.camera.get_world_up()
        self.camera.look_at(self.camera.viewCenter)
        lpos = self.camera.viewCenter
        ldir = lpos - pos


        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera.get_fov_deg(), self.camera.get_aspect(), self.camera.get_near(), self.camera.get_far())

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        #gluLookAt(pos[0], pos[1], pos[2], lpos[0], lpos[1], lpos[2], up[0], up[1], up[2])
        #self.arcball.rotate()



        lightpos = pos
        color = (1.0, 0.0, 1.0, 1.0)

        
        if not useArcball:
            gluLookAt(pos[0], pos[1], pos[2], lpos[0], lpos[1], lpos[2], up[0], up[1], up[2])
        

        
        
        glPushMatrix();
        
        self.graph.draw()
        
        ldir /= np.linalg.norm(ldir)
       
        glPopMatrix()
        glPopMatrix()

        
 
        
    def resizeGL(self, width : int, height : int):
        side = min(width, height)
        
        w = float(self.width())
        h = float(self.height())
        self.camera.set_aspect(w/h)
        
        
        glViewport(0, 0, width, height)

        self.imageCenterX = float(width) / 2.0
        self.imageCenterY = float(height) / 2.0
        pos = self.camera.get_position()
        up = self.camera.get_world_up()
        self.camera.look_at(self.camera.viewCenter)
        lpos = self.camera.viewCenter
        ldir = lpos - pos
        gluLookAt(pos[0], pos[1], pos[2], lpos[0], lpos[1], lpos[2], up[0], up[1], up[2])


    def normalizeAngle(self, angle : float):
        while (angle < 0):
            angle += 360 * 16

        while (angle > 360 * 16):
            angle -= 360 * 16
    
    
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if self.underMouse() and modifiers == Qt.NoModifier:
            if key == Qt.Key_W:
                self.isWDown = True
            elif key == Qt.Key_S:
                self.isSDown = True
                
            elif key == Qt.Key_A:
                self.isADown = True
            elif key == Qt.Key_D:
                self.isDDown = True
                
            elif key == Qt.Key_Q:
                self.isQDown = True
            elif key == Qt.Key_E:
                self.isEDown = True
        

        QtOpenGL.QGLWidget.keyPressEvent(self, event)
        
    
    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()
        if key == Qt.Key_W:
            self.isWDown = False
        elif key == Qt.Key_S:
            self.isSDown = False
                
        elif key == Qt.Key_A:
            self.isADown = False
        elif key == Qt.Key_D:
            self.isDDown = False
                
        elif key == Qt.Key_Q:
            self.isQDown = False
        elif key == Qt.Key_E:
            self.isEDown = False
                
        elif key == Qt.Key_Return:
            if self.currentMode == 0:
                t = 1
            elif self.currentMode == 1:
                g = 3
                
        QtOpenGL.QGLWidget.keyReleaseEvent(self, event)

    def wheelEvent(self, QWheelEvent : QtGui.QWheelEvent):
        numDegrees = (QWheelEvent.angleDelta() / 8.0).y()

        if self.zoom < self.baseFov / self.maxFov:
            if numDegrees < 0:
                return super().wheelEvent(QWheelEvent)
        self.zoomDegrees += numDegrees

        halfRotations = self.zoomDegrees / 180

        self.zoom = pow(2.0, halfRotations)


        fov = self.baseFov / self.zoom
        fov = min(fov, self.maxFov)

        self.camera.set_fov(fov)

        self.speed = self.baseSpeed / self.zoom

        return super().wheelEvent(QWheelEvent)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        
        if event.button() == Qt.RightButton and not self.isMouseLeftDown:
            self.isMouseRightDown = True
            self.lastMouseX = event.x()
            self.lastMouseY = event.y()

        elif event.button() == Qt.LeftButton and not self.isMouseRightDown:
            self.isMouseLeftDown = True
            self.startRotation = True
            self.lastMouseX = event.x()
            self.lastMouseY = event.y()

            self.mousePressX = event.x()
            self.mousePressY = event.y()

            invertY = (self.imageCenterY * 2 - event.y()) - 1
            self.arcball.start(event.x(), event.y())

        elif event.button() == Qt.MiddleButton:
            self.isMouseMiddleDown = True
            self.lastMouseX = event.x()
            self.lastMouseY = event.y()
        
        
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):

        if self.isMouseMiddleDown:
            difX = event.x() - self.lastMouseX
            difY = event.y() - self.lastMouseY

            shifty = self.speed * difY * 0.0022 / (math.log2(2 + self.zoom))
            shiftx = -self.speed * difX * 0.0022 / (math.log2(2 + self.zoom))

            self.camera.goUp(shifty * self.camera.standoff)
            self.camera.goRight(shiftx * self.camera.standoff)

            

            self.lastMouseX = event.x()
            self.lastMouseY = event.y()
            self.graph.shiftEye(-shiftx, -shifty)

        if self.isMouseLeftDown:
            difX = event.x() - self.lastMouseX
            difY = event.y() - self.lastMouseY

            if self.startRotation:
                self.startRotation = False
                self.graph.startRotation(self.lastMouseX, self.height() - self.lastMouseY - 1)
            
            self.graph.mouseMoved(event.x(), self.height() - event.y() - 1, self.zoom)
            
            if not useArcball:
                self.camera.increment_phi(0.01*difX * self.speed)
                self.camera.increment_theta(0.01*difY * self.speed)
                self.camera.resolveAngularPosition()

            #self.arcball.move(event.x(), event.y())
            
            self.lastMouseX = event.x()
            self.lastMouseY = event.y()
            
        elif self.isMouseRightDown:
            difX = event.x() - self.lastMouseX
            difY = event.y() - self.lastMouseY

            self.camera.yaw(0.001 * difX)
            self.camera.pitch(0.001*difY)
            self.camera.resolveAngularPosition()

            
            self.lastMouseX = event.x()
            self.lastMouseY = event.y()
            
        #if self.isMouseLeftDown or self.isMouseRightDown or self.isMouseMiddleDown:
        #    if event.x() > self.width():
        #        self.lastMouseX = 0
        #        newPoint = self.mapToGlobal(QtCore.QPoint(0, event.y()))
        #        QtGui.QCursor.setPos(newPoint.x(), newPoint.y())
        #    elif event.x() < 0:
        #        self.lastMouseX = self.width()
        #        newPoint = self.mapToGlobal(QtCore.QPoint(self.width(), event.y()))
        #        QtGui.QCursor.setPos(newPoint.x(), newPoint.y())
                
        #    if event.y() > self.height():
        #        self.lastMouseY = 0
        #        newPoint = self.mapToGlobal(QtCore.QPoint(event.x(), 0))
        #        QtGui.QCursor.setPos(newPoint.x(), newPoint.y())
        #    if event.y() < 0:
        #        self.lastMouseY = self.height()
        #        newPoint = self.mapToGlobal(QtCore.QPoint(event.x(), self.height()))
        #        QtGui.QCursor.setPos(newPoint.x(), newPoint.y())
        
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == Qt.RightButton:
            self.isMouseRightDown = False
        elif event.button() == Qt.LeftButton:

            if(abs(event.x() - self.mousePressX) < 5 and abs(event.y() - self.mousePressY) < 5):
                #ray = self.getRay(event.x(), event.y())
                #origin = self.camera.getNpPosition()
                
                #if self.currentMode == ConnectionMode:
                #    self.graph.selectConnectionNode(origin[0].item(), origin[1].item(), origin[2].item(), ray[0].item(), ray[1].item(), ray[2].item())
                #elif self.currentMode == BreakMode:
                #    self.graph.selectBreakEdge(origin[0].item(), origin[1].item(), origin[2].item(), ray[0].item(), ray[1].item(), ray[2].item())
                #elif self.currentMode == SplitMode:
                #    self.graph.selectSplitEdge(origin[0].item(), origin[1].item(), origin[2].item(), ray[0].item(), ray[1].item(), ray[2].item())
                if self.currentMode == ConnectionMode:
                    self.graph.selectConnectionNode(event.x(), self.height() - event.y())
                elif self.currentMode == BreakMode:
                    self.graph.selectBreakEdge(event.x(), self.height() - event.y())
                elif self.currentMode == SplitMode:
                    self.graph.selectSplitEdge(event.x(), self.height() - event.y())

            self.isMouseLeftDown = False
            self.doStopRotation = True

        elif event.button() == Qt.MiddleButton:
            self.isMouseMiddleDown = False
            
    def getRay(self, windowX : float, windowY : float):
        projectedX = (windowX - self.imageCenterX) / self.imageCenterX
        projectedY = (self.imageCenterY - windowY) / self.imageCenterY
        
        view = self.camera.get_world_forward()
        view = view / np.linalg.norm(view)
        
        h = np.cross(view, self.camera.get_world_up())
        h = h / np.linalg.norm(h)
        
        v = np.cross(h, view)
        v = v / np.linalg.norm(v)
        
        vLength = np.tan(self.camera.get_fov() / 2) * self.camera.get_near()
        hLength = vLength * self.camera.get_aspect()
        
        v = v * vLength
        h = h * hLength
        
        dirVec = view * self.camera.get_near() + h*projectedX + v*projectedY
        dirVec = dirVec / np.linalg.norm(dirVec)

        #pos = self.camera.getNpPosition() + view * self.camera.get_near() + h*projectedX + v*projectedY
        
        #dirVec = pos - self.camera.getNpPosition()
        
        #dirVec = dirVec/ np.linalg.norm(dirVec)
        
        return dirVec
            
    
    def enterConnectionMode(self, ConnectionWidget : Ui_ConnectionTabWidget):
        self.currentMode = 0
        self.connectionWidget = ConnectionWidget
        self.connectionOptions.exitMode()
        self.breakOptions.exitMode()
        self.splitOptions.exitMode()
        self.addNodeOptions.exitMode()
        self.connectionOptions.enterMode(self.graph.getNumComponents(), ConnectionWidget)


    def enterBreakMode(self, BreakWidget : Ui_BreakTabWidget):
        self.currentMode = 1
        self.connectionOptions.exitMode()
        self.breakOptions.exitMode()
        self.splitOptions.exitMode()
        self.addNodeOptions.exitMode()
        self.breakOptions.enterMode(BreakWidget)

        
    def enterSplitMode(self, SplitWidget : Ui_SplitTabWidget):
        self.currentMode = 2
        self.connectionOptions.exitMode()
        self.breakOptions.exitMode()
        self.splitOptions.exitMode()
        self.addNodeOptions.exitMode()
        self.splitOptions.enterMode(SplitWidget)

    def enterAddNodeMode(self, AddNodeWidget : Ui_AddNodeTabWidget):
        self.currentMode = 3
        self.connectionOptions.exitMode()
        self.breakOptions.exitMode()
        self.splitOptions.exitMode()
        self.addNodeOptions.exitMode()
        self.addNodeOptions.enterMode(AddNodeWidget)
        