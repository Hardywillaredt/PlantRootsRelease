# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 16:09:02 2018

@author: Will
"""

import sys
import math

from PyQt5 import QtCore, QtGui, QtOpenGL, QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from PyQt5.QtWidgets import QMainWindow
import drawingUtil


from RootsTool import  Point3d, MetaNode3d


try:
    from OpenGL.GL import *
    import OpenGL.GL as gl
except ImportError:
    sys.exit(1)
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

def p3d2arr(p3d : Point3d):
    if isinstance(p3d, Point3d) or isinstance(p3d, MetaNode3d):
        return np.array([p3d.x, p3d.y, p3d.z])
    else:
        return p3d

# v0 and v1 are point3d endpoints
# reflectance is the color to reflect on the skeleton
# r0 and r1 are thicknesses/radii at either end
# s is the scalefactor (multiply visualization size by this much)
# cylinder may have different cap sizes at either end
def makeCylinder(v0, v1, reflectance, r0=1.0, r1=1.0, s=1.0):
    result = glGenLists(1)
    glNewList(result, GL_COMPILE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, reflectance)
#    cylLighting = (0.2, 0.025, 0.0, 1.0)
#    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, cylLighting)
#    glMaterialfv(GL_FRONT, GL_SPECULAR, reflectance)
    glShadeModel(GL_FLAT)
    
    R0 = r0 * s;
    R1 = r1 * s;
    maxR = max(R0, R1)
    numSides = max(int(maxR * 8), 8)
    V0 = v0
    V1 = v1
    if isinstance(v0, Point3d):
        V0 = p3d2arr(v0)
        V1 = p3d2arr(v1)
    else:
        V0 = v0
        V1 = v1
    normal = V0 - V1
    
    
    normal = normal / np.linalg.norm(normal)
    
    vec1 = np.array([])
    
    if normal[1] == 0 and normal[2] == 0:
        vec1 = np.cross(normal, [0, 1, 0])
    else:
        vec1 = np.cross(normal, [1, 0, 0])
    
    vec2 = np.cross(normal, vec1)
    
    vec1 = vec1 / np.linalg.norm(vec1)
    vec2 = vec2 / np.linalg.norm(vec2)
    
    p0 = V0
    p1 = V1
    stepSize = 2 * math.pi / numSides
    theta = 0.0
    glBegin(GL_TRIANGLE_STRIP)
    while theta < 2*math.pi:
        basePoint = p0 + R0*math.cos(theta)*vec1 + R0*math.sin(theta)*vec2
        capPoint = p1 + R1*math.cos(theta)*vec1 + R1*math.sin(theta)*vec2
        n = basePoint - p0
        n = n / np.linalg.norm(n)
        theta = theta + stepSize
        
        glNormal3d(n[0], n[1], n[2])
        glVertex3d(basePoint[0], basePoint[1], basePoint[2])
        glVertex3d(capPoint[0], capPoint[1], capPoint[2])
        
#    need to close the cylinder, so reissue points for theta=0
    basePoint = p0 + R0*math.cos(0)*vec1 + R0*math.sin(0)*vec2
    capPoint = p1 + R1*math.cos(0)*vec1 + R1*math.sin(0)*vec2
    n = basePoint - p0
    n = n / np.linalg.norm(n)
    
    glNormal3d(n[0], n[1], n[2])
    glVertex3d(basePoint[0], basePoint[1], basePoint[2])
    glVertex3d(capPoint[0], capPoint[1], capPoint[2])
    glEnd()
    
    
#    cylLighting = (0.4, 0.025, 0.0, 1.0)
#    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, cylLighting)
    
    glPushMatrix()
    glTranslatef(V0[0], V0[1], V0[2])
    quadric = gluNewQuadric()
    gluQuadricOrientation(quadric, GLU_OUTSIDE)
    gluSphere(quadric, r0, 15, 15)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(V1[0], V1[1], V1[2])
    quadric = gluNewQuadric()
    gluQuadricOrientation(quadric, GLU_OUTSIDE)
    gluSphere(quadric, r1, 15, 15)
    glPopMatrix()
    
    
    glEndList()
    
    return result

def computeCappedCylinderGL(v0, v1, reflectance, r0=1.0, r1=1.0, s=1.0):
    computeUncappedCylinderGL(v0, v1, reflectance, r0, r1, s)
    computeVertexGL(v0, reflectance, r0, s)
    computeVertexGL(v1, reflectance, r1, s)
    
 
    

def computeUncappedCylinderGL(v0, v1, reflectance, r0=1.0, r1=1.0, s=1.0):
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, reflectance)

    
    R0 = r0 * s;
    R1 = r1 * s;
    maxR = min(max(R0, R1), 5)
    
    if math.isnan(maxR):
        return
    
    numSides = max(int(maxR * 30), 30)
    V0 = v0
    V1 = v1
    if isinstance(v0, Point3d) or isinstance(v0, MetaNode3d):
        V0 = p3d2arr(v0)
        V1 = p3d2arr(v1)

    normal = V0 - V1
    
    normal = normal / np.linalg.norm(normal)
    
    vec1 = np.array([])
    
    if normal[1] == 0 and normal[2] == 0:
        vec1 = np.cross(normal, [0, 1, 0])
    else:
        vec1 = np.cross(normal, [1, 0, 0])
    
    vec2 = np.cross(normal, vec1)
    
    vec1 = vec1 / np.linalg.norm(vec1)
    vec2 = vec2 / np.linalg.norm(vec2)
    
    p0 = V0
    p1 = V1
    stepSize = 2 * math.pi / numSides
    theta = 0.0
    glBegin(GL_TRIANGLE_STRIP)
    while theta < 2*math.pi:
        basePoint = p0 + R0*math.cos(theta)*vec1 + R0*math.sin(theta)*vec2
        capPoint = p1 + R1*math.cos(theta)*vec1 + R1*math.sin(theta)*vec2
        n = basePoint - p0
        n = n / np.linalg.norm(n)
        theta = theta + stepSize
        
        glNormal3d(n[0], n[1], n[2])
        glVertex3d(basePoint[0], basePoint[1], basePoint[2])
        glVertex3d(capPoint[0], capPoint[1], capPoint[2])
        
#    need to close the cylinder, so reissue points for theta=0
    basePoint = p0 + R0*math.cos(0)*vec1 + R0*math.sin(0)*vec2
    capPoint = p1 + R1*math.cos(0)*vec1 + R1*math.sin(0)*vec2
    n = basePoint - p0
    n = n / np.linalg.norm(n)
    
    glNormal3d(n[0], n[1], n[2])
    glVertex3d(basePoint[0], basePoint[1], basePoint[2])
    glVertex3d(capPoint[0], capPoint[1], capPoint[2])
    glEnd()
    
    
    
def computeVertexGL(v0, reflectance, r0=1.0, s=1.0):
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, reflectance)
    glPushMatrix()
    if isinstance(v0, Point3d) or isinstance(v0, MetaNode3d):
        glTranslatef(v0.x, v0.y, v0.z)
    else:
        glTranslatef(v0[0], v0[1], v0[2])
    quadric = gluNewQuadric()
    gluQuadricOrientation(quadric, GLU_OUTSIDE)
    gluSphere(quadric, r0, 40, 40)
    glPopMatrix()
    
    
#take a set of metaNode3d vertices
#a set of metaEdge3d edges
#and the reflectance for the component and generate the call list
def makeComponent(componentEdgeMap, component, reflectance, s=1.0):
    
    result = glGenLists(1)
    glNewList(result, GL_COMPILE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, reflectance)
    glShadeModel(GL_FLAT)
    
    nodeThickness = []
    
    
    
    for edge in componentEdgeMap[component]:
        computeCylinderGL(edge.node0, edge.node1, edge.avgThickness, edge.avgThickness, s)
        nodeThickness[edge.node0] = edge.avgThickness
        nodeThickness[edge.node1] = edge.avgThickness
    
    for edge in componentEdgeMap[component]:
        nodeThickness[edge.node0] = max(nodeThickness[edge.node0], edge.avgThickness)
        nodeThickness[edge.node1] = max(nodeThickenss[edge.node1], edge.avgThickness)
        
    for node in nodeThickness:
        computeVertexGL(node, nodeThickness[node], s)
        
         
    glEndList()
    
    return result


#ColorTable =    (
#                (230, 25, 75), 
#                (60, 180, 75),
#                (255, 225, 25),
#                (0, 130, 200),	
#                (245, 130, 48),	
#                (145, 30, 180),
#                (70, 240, 240),	
#                (240, 50, 230),	
#                (210, 245, 60),	
#                (250, 190, 190),	
#                (0, 128, 128),	
#                (230, 190, 255),	
#                (170, 110, 40),	
#                (255, 250, 200),	
#                (128, 0, 0),	
#                (170, 255, 195),	
#                (128, 128, 0),	
#                (255, 215, 180),
#                (0, 0, 128),	
#                (128, 128, 128),	
#                )
ColorTable =    [
                [0.902, 0.098, 0.294, 1.0],
                [0.235, 0.706, 0.294, 1.0],
                [1.0, 0.882, 0.098, 1.0],
                [0.0, 0.51, 0.784, 1.0],
                [0.961, 0.51, 0.188, 1.0],
                [0.569, 0.118, 0.706, 1.0],
                [0.275, 0.941, 0.941, 1.0],
                [0.941, 0.196, 0.902, 1.0],
                [0.824, 0.961, 0.235, 1.0],
                [0.98, 0.745, 0.745, 1.0],
                [0.0, 0.502, 0.502, 1.0],
                [0.902, 0.745, 1.0, 1.0],
                [0.667, 0.431, 0.157, 1.0],
                [1.0, 0.98, 0.784, 1.0],
                [0.502, 0.0, 0.0, 1.0],
                [0.667, 1.0, 0.765, 1.0],
                [0.502, 0.502, 0.0, 1.0],
                [1.0, 0.843, 0.706, 1.0],
                [0.0, 0.0, 0.502, 1.0],
                [0.502, 0.502, 0.502, 1.0],
                [0.902, 0.098, 0.294, 1.0],
                [0.235, 0.706, 0.294, 1.0],
                [1.0, 0.882, 0.098, 1.0],
                [0.0, 0.51, 0.784, 1.0],
                [0.961, 0.51, 0.188, 1.0],
                [0.569, 0.118, 0.706, 1.0],
                [0.275, 0.941, 0.941, 1.0],
                [0.941, 0.196, 0.902, 1.0],
                [0.824, 0.961, 0.235, 1.0],
                [0.98, 0.745, 0.745, 1.0],
                [0.0, 0.502, 0.502, 1.0],
                [0.902, 0.745, 1.0, 1.0],
                [0.667, 0.431, 0.157, 1.0],
                [1.0, 0.98, 0.784, 1.0],
                [0.502, 0.0, 0.0, 1.0],
                [0.667, 1.0, 0.765, 1.0],
                [0.502, 0.502, 0.0, 1.0],
                [1.0, 0.843, 0.706, 1.0],
                [0.0, 0.0, 0.502, 1.0],
                [0.502, 0.502, 0.502, 1.0]
                ]
#    
#def makeGear():
#    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, reflectance)
#
#    r0 = innerRadius
#    r1 = outerRadius - toothSize / 2.0
#    r2 = outerRadius + toothSize / 2.0
#    delta = (2.0 * math.pi / toothCount) / 4.0
#    z = thickness / 2.0
#
#    glShadeModel(GL_FLAT)
#
#    for i in range(2):
#        if i == 0:
#            sign = +1.0
#        else:
#            sign = -1.0
#
#        glNormal3d(0.0, 0.0, sign)
#
#        glBegin(GL_QUAD_STRIP)
#
#        for j in range(toothCount+1):
#            angle = 2.0 * math.pi * j / toothCount
#            glVertex3d(r0 * math.cos(angle), r0 * math.sin(angle), sign * z)
#            glVertex3d(r1 * math.cos(angle), r1 * math.sin(angle), sign * z)
#            glVertex3d(r0 * math.cos(angle), r0 * math.sin(angle), sign * z)
#            glVertex3d(r1 * math.cos(angle + 3 * delta), r1 * math.sin(angle + 3 * delta), sign * z)
#
#        glEnd()
#
#        glBegin(GL_QUADS)
#
#        for j in range(toothCount):
#            angle = 2.0 * math.pi * j / toothCount                
#            glVertex3d(r1 * math.cos(angle), r1 * math.sin(angle), sign * z)
#            glVertex3d(r2 * math.cos(angle + delta), r2 * math.sin(angle + delta), sign * z)
#            glVertex3d(r2 * math.cos(angle + 2 * delta), r2 * math.sin(angle + 2 * delta), sign * z)
#            glVertex3d(r1 * math.cos(angle + 3 * delta), r1 * math.sin(angle + 3 * delta), sign * z)
#
#        glEnd()
#
#    glBegin(GL_QUAD_STRIP)
#
#    for i in range(toothCount):
#        for j in range(2):
#            angle = 2.0 * math.pi * (i + (j / 2.0)) / toothCount
#            s1 = r1
#            s2 = r2
#
#            if j == 1:
#                s1, s2 = s2, s1
#
#            glNormal3d(math.cos(angle), math.sin(angle), 0.0)
#            glVertex3d(s1 * math.cos(angle), s1 * math.sin(angle), +z)
#            glVertex3d(s1 * math.cos(angle), s1 * math.sin(angle), -z)
#
#            glNormal3d(s2 * math.sin(angle + delta) - s1 * math.sin(angle), s1 * math.cos(angle) - s2 * math.cos(angle + delta), 0.0)
#            glVertex3d(s2 * math.cos(angle + delta), s2 * math.sin(angle + delta), +z)
#            glVertex3d(s2 * math.cos(angle + delta), s2 * math.sin(angle + delta), -z)
#
#    glVertex3d(r1, 0.0, +z)
#    glVertex3d(r1, 0.0, -z)
#    glEnd()
#
#    glShadeModel(GL_SMOOTH)
#
#    glBegin(GL_QUAD_STRIP)
#
#    for i in range(toothCount+1):
#        angle = i * 2.0 * math.pi / toothCount
#        glNormal3d(-math.cos(angle), -math.sin(angle), 0.0)
#        glVertex3d(r0 * math.cos(angle), r0 * math.sin(angle), +z)
#        glVertex3d(r0 * math.cos(angle), r0 * math.sin(angle), -z)
#
#    glEnd()
