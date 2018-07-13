from vecmath import *
import numpy as np

class Spatial(object):
    origin = v3()
    def __init__(self, position=None, orientation=None):
        self._pos = v3(0,0,0)
        self._ori = quat(0,0,0,1)
        self.viewCenter = v3()
        self.theta = np.pi / 2.0
        self.phi = 0.0
        self.standoff = 100.0
        if position is not None:
            self.set_position(position)

        if orientation is not None:
            self.set_orientation(orientation)

    def get_position(self):
        return self._pos[:]
    
    def getNpPosition(self):
        return v3(self._pos[0], self._pos[1], self._pos[2])
#        return np.array([[self._pos[0]],
#                         [self._pos[1]],
#                         [self._pos[2]]])

    def increment_phi(self, deltaPhi):
        self.phi += deltaPhi
        while self.phi < 0:
            self.phi += 2.0*np.pi
        while self.phi > 2.0 * np.pi:
            self.phi -= 2.0*np.pi
        

    def increment_theta(self, deltaTheta):
        if self.theta + deltaTheta > np.pi-0.0001:
            self.theta = np.pi-0.0001
        elif self.theta + deltaTheta < 0.0001:
            self.theta = 0.0001
        else:
            self.theta += deltaTheta

    def resolveAngularPosition(self):
        eyex = self.viewCenter[0] + self.standoff*np.cos(self.phi)*np.sin(self.theta)
        eyez = self.viewCenter[2] + self.standoff*np.sin(self.phi)*np.sin(self.theta)
        eyey = self.viewCenter[1] + self.standoff*np.cos(self.theta)
        self._pos = [eyex, eyey, eyez]

    def set_position(self, value):
        self._pos[:] = value

    def get_orientation(self):
        return self._ori[:]

    def set_orientation(self, value):
        self._ori[:] = value

    def get_model_matrix(self):
        return m44_pos_rot(self._pos, self._ori)

    def goForward(self, dist):
        forward_world = q_mul_v(self._ori, V3_ZAXIS*-1)
        self._pos += dist*forward_world
        self.viewCenter += dist*forward_world
        
    def goRight(self, dist):
        right_world = q_mul_v(self._ori, V3_XAXIS*1)
        self._pos += dist * right_world
        self.viewCenter += dist*right_world
    
    def goUp(self, dist):
        up_world = q_mul_v(self._ori, V3_YAXIS*1)
        self._pos += dist * up_world
        self.viewCenter += dist*up_world

    def goRightKeepCenter(self, dist):
        right_world = q_mul_v(self._ori, V3_XAXIS*1)
        self._pos += dist * right_world

    def goUpKeepCenter(self, dist):
        up_world = q_mul_v(self._ori, V3_YAXIS*1)
        self._pos += dist * up_world
    
    def get_world_pitch(self):
        o = self._ori
        return np.arctan2(2*o[0]*o[3] - 2*o[1]*o[2], 1 - 2*o[0]*o[0] - 2*o[2]*o[2])
#        Mathf.Atan2(2*x*w - 2*y*z, 1 - 2*x*x - 2*z*z)
        
    def get_world_roll(self):
        o = self._ori
        return np.arctan2(2*o[1]*o[3] - 2*o[0]*o[2], 1 - 2*o[1]*o[1] - 2*o[2]*o[2])
#        Mathf.Atan2(2*y*w - 2*x*z, 1 - 2*y*y - 2*z*z)

    def get_world_yaw(self):
        o = self._ori
        return np.arcsin(2*o[0]*o[1] + 2*o[2]*o[3])
#        Mathf.Asin(2*x*y + 2*z*w)

    def get_world_forward(self):
        return q_mul_v(self._ori, V3_ZAXIS*-1)

    def get_world_up(self):
        return q_mul_v(self._ori, V3_YAXIS)

    def yaw(self, angle):
        """yaw by angle given in radians"""
        q = quat_axis_angle(V3_YAXIS, angle)
        self._ori[:] = q_mul(self._ori, q)
        self.viewCenter = self.standoff * self.get_world_forward() + self.get_position()

    def pitch(self, angle):
        """pitch by angle given in radians"""
        q = quat_axis_angle(V3_XAXIS, angle)
        self._ori[:] = q_mul(self._ori, q)
        self.viewCenter = self.standoff * self.get_world_forward() + self.get_position()

    def roll(self, angle):
        """roll by angle given in radians"""
        q = quat_axis_angle(V3_ZAXIS, angle)
        self._ori[:] = q_mul(self._ori, q)
        self.viewCenter = self.standoff * self.get_world_forward() + self.get_position()

    def look_dir(self, look, up=None):
        ulook = normalize(look)

        if up is None:
            uright = normalize(cross(ulook, V3_YAXIS))
            uup = cross(uright, ulook)
        else:
            uup = normalize(up)
            uright = normalize(cross(ulook, uup))

        matRot = m44()
        matRot[0:3,0] = uright
        matRot[0:3,1] = uup
        matRot[0:3,2] = ulook *-1
        matRot[  3,3] = 1.0

        self._ori[:] = m44_rot_to_q(matRot)

    def look_at(self, world_point, up=None):
        direction = world_point - self._pos
        self.look_dir(direction, up)
