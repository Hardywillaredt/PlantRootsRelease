from vecmath import * 
from spatial import Spatial
import numpy as np

class Camera(Spatial):
    def __init__(self, position=None, orient=None, fov=pi/3.0, near=1, far=1000, aspect=1.6):
        super(Camera, self).__init__(position, orient)
        
        self.isFovSet = False
        self.isNearSet = False
        self.isFarSet = False
        self.isAspectSet = False
        
        self.set_fov(fov)
        self.set_near(near)
        self.set_far(far)
        self.set_aspect(aspect)
        self.projectionMat = m44()
        self.inverseProjectionMat = m44()
        

    def set_fov(self, fov):
        self.isFovSet = True
        self._fov = float(fov)
        self._deg_fov = float(fov * 180 / pi)
        self.computeProjection()
        
    def set_fov_deg(self, fov_deg : float):
        self.isFovSet = True
        self._deg_fov = float(fov_deg)
        self._fov = float(fov_deg * pi / 180)
        self.computeProjection()

    def get_fov(self):
        return self._fov
    
    def get_fov_deg(self):
        return self._deg_fov
    
    def set_near(self, near):
        self.isNearSet = True
        self._near = float(near)
        self.computeProjection()

    def get_near(self):
        return self._near

    def set_far(self, far):
        self.isFarSet = True
        self._far = float(far)
        self.computeProjection()

    def get_far(self):
        return self._far

    def set_aspect(self, aspect):
        self.isAspectSet = True
        self._aspect = float(aspect)
        self.computeProjection()

    def get_aspect(self):
        return self._aspect

    def getProjectionMat(self):
        return self.projectionMat
    
    def getInverseProjectionMat(self):
        return self.inverseProjectionMat
#        a = self.get_aspect()
#        f = self.get_far()
#        n = self.get_near()
#        fov = self.get_fov()
#       
#        Pxx = 1.0/tan(fov/2.0)
#
#        matP = m44()
#        matP[0,0] = Pxx
#        matP[1,1] = Pxx * a 
#        matP[2,2] = (f+n)/(n-f)
#        matP[2,3] = (2*n*f)/(n-f)
#        matP[3,2] = -1.0
#
#        return matP
    
    def computeProjection(self):
        if self.isAspectSet and self.isFarSet and self.isFovSet and self.isNearSet:
            a = self.get_aspect()
            f = self.get_far()
            n = self.get_near()
            fov = self.get_fov()
           
            Pxx = 1.0/tan(fov/2.0)
    
            matP = m44()
            matP[0,0] = Pxx
            matP[1,1] = Pxx * a 
#            matP[2,2] = -(f+n)/((n-f)*n)
#            matP[2,3] = (2*f)/(f-n)
#            matP[3,2] = 1.0/n
            matP[2,2] = -f / (f - n)
            matP[3,2] = -f*n / (f - n)
            matP[2,3] = -1.0
           
    
            self.projectionMat = matP
            self.inverseProjectionMat = np.linalg.inv(matP)

    def get_camera_matrix(self):
        v = self.get_position()
        q = self.get_orientation()
        qi = q_inv(q)
        vn = q_mul_v(qi,v)
        return m44_pos_rot(vn, qi)


