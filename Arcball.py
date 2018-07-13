import numpy as np
import math

import OpenGL.GL as gl
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *



class arcVec:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return arcVec(self.x + other.x, self.y+other.y, self.z+other.z)
    
    def __sub__(self, other):
        return arcVec(self.x - other.x, self.y - other.y, self.z-other.z)

    def __mul__(self, val):
        if(type(self) == type(val)):
            return self.x * val.x + self.y * val.y + self.z * val.z
        else:
            return arcVec(self.x*val, self.y*val, self.z*val)

    def __truediv__(self, val):
        return arcVec(self.x / val, self.y/val, self.z/val)

    def cross(self, other):
        return arcVec(
            self.y*other.z-self.z*other.y, 
            other.x*self.z-self.x*other.z, 
            self.x*other.y-self.y*other.x)

    def mag(self):
        return math.sqrt(self * self)

    def normalized(self):
        length = self.mag()
        if length == 0:
            return arcVec(0, 0, 0)
        else:
            return self/length

    def isZero(self):
        return self.x==0 and self.y==0 and self.z==0

    def equals(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

def quaternion(q, x, y, z, w):
    x2 = x*x
    y2 = y*y
    z2 = z*z
    xy = x*y
    xz = x*z
    yz = y*z
    wx = w*x
    wy = w*y
    wz = w*z

    q[0] = 1 - 2*y2 - 2*z2
    q[1] = 2*xy + 2*wz
    q[2] = 2*xz - 2*wy
  
    q[4] = 2*xy - 2*wz
    q[5] = 1 - 2*x2 - 2*z2
    q[6] = 2*yz + 2*wx
  
    q[8] = 2*xz + 2*wy
    q[9] = 2*yz - 2*wx
    q[10]= 1 - 2*x2 - 2*y2


def quatIdentity(q):
    q[0]=1 
    q[1]=0  
    q[2]=0  
    q[3]=0
    q[4]=0  
    q[5]=1  
    q[6]=0  
    q[7]=0
    q[8]=0  
    q[9]=0  
    q[10]=1 
    q[11]=0
    q[12]=0 
    q[13]=0 
    q[14]=0 
    q[15]=1


def quatCopy(dst, src):
    dst[0]=src[0]
    dst[1]=src[1]
    dst[2]=src[2]
    dst[4]=src[4] 
    dst[5]=src[5]
    dst[6]=src[6]
    dst[8]=src[8]
    dst[9]=src[9]
    dst[10]=src[10]

def quatNext(dest, left, right):
    dest[0] = left[0]*right[0] + left[1]*right[4] + left[2] *right[8]
    dest[1] = left[0]*right[1] + left[1]*right[5] + left[2] *right[9]
    dest[2] = left[0]*right[2] + left[1]*right[6] + left[2] *right[10]
    dest[4] = left[4]*right[0] + left[5]*right[4] + left[6] *right[8]
    dest[5] = left[4]*right[1] + left[5]*right[5] + left[6] *right[9]
    dest[6] = left[4]*right[2] + left[5]*right[6] + left[6] *right[10]
    dest[8] = left[8]*right[0] + left[9]*right[4] + left[10]*right[8]
    dest[9] = left[8]*right[1] + left[9]*right[5] + left[10]*right[9]
    dest[10]= left[8]*right[2] + left[9]*right[6] + left[10]*right[10]



class ArcballCamera:
    def __init__(self):

        self.abQuat = [1.0,0.0,0.0,0.0, 
                       0.0,1.0,0.0,0.0, 
                       0.0,0.0,1.0,0.0, 
                       0.0,0.0,0.0,1.0]

        self.abLast = [1.0,0.0,0.0,0.0, 
                       0.0,1.0,0.0,0.0, 
                       0.0,0.0,1.0,0.0, 
                       0.0,0.0,0.0,1.0]

        self.abNext = [1.0,0.0,0.0,0.0, 
                       0.0,1.0,0.0,0.0, 
                       0.0,0.0,1.0,0.0, 
                       0.0,0.0,0.0,1.0]

        self.abZoom = 1.0
        self.abZoom2 = 1.0

        self.abSphere = 1.0
        self.abSphere2 = 1.0

        self.abEdge = 1.0

        self.abPlanar = False
        self.abPlaneDist = 0.5

        self.abStart = arcVec(0,0,1)
        self.abCurr = arcVec(0,0,1)
        self.abEye = arcVec(0,0,1)
        self.abEyeDir = arcVec(0,0,1)
        self.abUp = arcVec(0,1,0)
        self.abOut = arcVec(1,0,0)

        self.abGlp = [1.0,0.0,0.0,0.0, 
                       0.0,1.0,0.0,0.0, 
                       0.0,0.0,1.0,0.0, 
                       0.0,0.0,0.0,1.0]

        self.abGlm = [1.0,0.0,0.0,0.0, 
                       0.0,1.0,0.0,0.0, 
                       0.0,0.0,1.0,0.0, 
                       0.0,0.0,0.0,1.0]

        self.abGlv = [0,0,640, 480]



    def setZoom(self, radius, eye, up):
        self.abEye = eye
        self.abZoom2 = self.abEye * self.abEye
        self.abZoom = math.sqrt(self.abZoom2)

        self.abSphere = radius
        self.abSphere2 = self.abSphere * self.abSphere

        self.abEyeDir = self.abEye * (1.0/self.abZoom)
        self.abEdge = self.abSphere2 / self.abZoom

        if(self.abSphere <= 0):
            self.abPlanar = True
            self.abUp = up
            self.abOut = self.abEyeDir.cross(self.abUp)
            self.abPlaneDist = (0.0 - self.abSphere) * self.abZoom
        else:
            self.abPlanar = False

        glGetDoublev(GL_PROJECTION_MATRIX, self.abGlp)
        glGetIntegerv(GL_VIEWPORT, self.abGlv)

    def rotate(self):
        glMultMatrixf(self.abQuat)


    def edgeCoords(self, m : arcVec):
        t = (self.abEdge - self.abZoom) / (self.abEyeDir*m)
        a = self.abEye + m*t

        c = (self.abEyeDir * self.abEdge) - a

        ac = a * c
        c2 = c*c
        q = ( 0.0 - ac - math.sqrt( ac*ac - c2*((a*a)-self.abSphere2) ) ) / c2

        return (a+(c*q)).normalized()

    def sphereCoords(self, mx : float, my : float):
        aCoordinate = gluUnProject(mx, my, 0, self.abGlm, self.abGlp, self.abGlv)

        m = arcVec(aCoordinate[0], aCoordinate[1], aCoordinate[2]) - self.abEye

        a = m*m
        b = self.abEye * m
        root = b*b - a*(self.abZoom2 - self.abSphere2)
        if root <= 0:
            return self.edgeCoords(m)

        t = (0.0 - b - math.sqrt(root)) / a
        return (self.abEye + m*t).normalized()

    def planarCoords(self, mx : float, my : float):
        aCoordinate = gluUnProject(mx, my, 0, self.abGlm, self.abGlp, self.abGlv)

        m = arcVec(aCoordinate[0], aCoordinate[1], aCoordinate[2]) - self.abEye

        t = (self.abPlaneDist - self.abZoom) / (self.abEyeDir * m)
        d = self.abEye + m*t

        return arcVec(d * self.abUp, d*self.abOut, 0.0)

    def reset(self):
        quatIdentity(self.abQuat)
        quatIdentity(self.abLast)

    def start(self, mx : int, my : int):
        quatCopy(self.abLast, self.abQuat)
        if self.abPlanar:
            self.abStart = self.planarCoords(-float(mx), float(my))
        else:
            self.abStart = self.sphereCoords(-float(mx), -float(my))

    def move(self, mx : int, my : int):
        if self.abPlanar:
            self.abCurr = self.planarCoords(-float(mx), float(my))

            if(self.abCurr == self.abStart):
                return

            d = self.abCurr - self.abStart

            angle = d.mag() * 0.5
            cosa = math.cos(angle)
            sina = math.sin(angle)

            p = ((ab_out*d.x)-(ab_up*d.y)).normalized() * sina

            quaternion(self.abNext, p.x, p.y, p.z, cosa)
            quatNext(self.abQuat, self.abLast, self.abNext)

            quatCopy(self.abLast, self.abQuat)
            self.abStart = self.abCurr

        else:
            self.abCurr = self.sphereCoords(-float(mx), -float(my))

            if(self.abCurr.equals(self.abStart)):
                quatCopy(self.abQuat, self.abLast)
                return

            cos2a = self.abStart * self.abCurr
            sina = math.sqrt((1.0 - cos2a) * 0.5)
            cosa = math.sqrt((1.0 + cos2a) * 0.5)
            crossVec = (self.abStart.cross(self.abCurr)).normalized() * sina

            quaternion(self.abNext, crossVec.x,  crossVec.y, crossVec.z,  cosa)

            quatNext(self.abQuat, self.abLast, self.abNext)


   