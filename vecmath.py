from numpy import (
    array,
    clip,
    concatenate,
    cos,
    cross,
    dot,
    float32,
    int32,
    pi,
    sin,
    sqrt,
    tan,
    transpose,
    zeros,
    ndarray
)

from numpy.linalg import det, inv, norm

FLOAT = float32
INT = int32
EPSILON = 1e-10

def arrayf(lst):
    return array(lst, dtype=FLOAT)

def arrayi(lst):
    return array(lst, dtype=INT)

def arraycat(*lst):
    return concatenate(lst)

#
# Matrix/Quaternion/Vector Initializers
#

def v2(x=0.0, y=0.0):
    return array((x,y), dtype=FLOAT)

def v3(x=0.0, y=0.0, z=0.0):
    return array((x,y,z), dtype=FLOAT)

V3_XAXIS = v3(1.0,0.0,0.0)
V3_YAXIS = v3(0.0,1.0,0.0)
V3_ZAXIS = v3(0.0,0.0,1.0)

def v4(x=0.0, y=0.0, z=0.0, w=0.0):
    return array((x,y,z,w), dtype=FLOAT)

def quat(x=0.0, y=0.0, z=0.0, w=0.0):
    return array((x,y,z,w), dtype=FLOAT)

def quat_axis_angle(axis, angle):
    t = angle/2.0
    s = sin(t)
    w = cos(t)
    x, y, z = axis*s
    return array((x,y,z,w), dtype=FLOAT)

def m22():
    return zeros(shape=(2,2), dtype=FLOAT, order='C')

def m23():
    return zeros(shape=(2,3), dtype=FLOAT, order='C')

def m33():
    return zeros(shape=(3,3), dtype=FLOAT, order='C')

def m44():
    return zeros(shape=(4,4), dtype=FLOAT, order='C')

def m31(x = 0.0, y=0.0, z=0.0):
    result = zeros(shape=(3,1), dtype=FLOAT, order='C')
    result[0,0] = x
    result[1,0] = y
    result[2,0] = z
    return result

def m41(x=0.0, y=0.0, z=0.0, w=0.0):
    result = zeros(shape=(4,1), dtype=FLOAT, order='C')
    result[0,0] = x
    result[1,0] = y
    result[2,0] = z
    result[3,0] = w
    return result
#
# Quaternion/Vector Operations
#

def normalize(qv):
    return qv/norm(qv)

def q_conj(q):
    x, y, z, w = q
    return quat(-x, -y, -z, w)

def q_div(q1, q2):
    return q_mul(q1, q_inv(q2))

def q_inv(q):
    x, y, z, w = q
    qc = quat(-x, -y, -z, w)
    return qc/dot(qc,qc)

def q_mul(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2

    return quat(
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
        w1*w2 - x1*x2 - y1*y2 - z1*z2
    )

def q_mul_v(q1, v):
    x, y, z = v
    qv = quat(x, y, z, 0)
    q1_inv = q_inv(q1)
    qw = q_mul(q1, q_mul(qv, q1_inv))
    return qw[0:3]

def q_to_rot(q1):
    x,y,z,w = q1

    xx = x*x
    xy = x*y
    xz = x*z
    xw = x*w
    yy = y*y
    yz = y*z
    yw = y*w
    zz = z*z
    zw = z*w

    return (
        (1-2*(yy+zz),   2*(xy-zw),   2*(xz+yw), 0),
        (  2*(xy+zw), 1-2*(xx+zz),   2*(yz-xw), 0),
        (  2*(xz-yw),   2*(yz+xw), 1-2*(xx+yy), 0),
        (          0,           0,           0, 1)
    )

def m44_mul_m44(m1, m2):
    return dot(m1, m2)

def m44_pos_rot(v,q):
    mat = m44()
    mat[:] = q_to_rot(q)
    mat[0:3,3] = v
    return mat

def m44_rot_to_q(m1):
    if 1 + m1[0,0] + m1[1,1] + m1[2,2] > EPSILON:
        s = 2*sqrt(1+ m1[0,0] + m1[1,1] + m1[2,2])
        return quat(
            (m1[2,1]-m1[1,2])/s,
            (m1[0,2]-m1[2,0])/s,
            (m1[1,0]-m1[0,1])/s,
                          s/4.0
        )

    elif m1[0,0] >= max(m1[1,1], m1[2,2]):
        s = 2*sqrt(1 + m1[0,0] - m1[1,1] - m1[2,2])
        return quat(
                          s/4.0,
            (m1[1,0]+m1[0,1])/s,
            (m1[0,2]+m1[2,0])/s,
            (m1[2,1]-m1[1,2])/s,
        )

    elif m1[1,1] >= m1[2,2]:
        s = 2*sqrt(1 - m1[0,0] + m1[1,1] - m1[2,2])
        return quat(
            (m1[1,0]+m1[0,1])/s,
                          s/4.0,
            (m1[2,1]+m1[1,2])/s,
            (m1[0,2]-m1[2,0])/s
        )

    else:
        s = 2*sqrt(1 - m1[0,0] - m1[1,1] + m1[2,2])
        return quat(
            (m1[0,2]+m1[2,0])/s,
            (m1[2,1]+m1[1,2])/s,
                          s/4.0,
            (m1[1,0]-m1[0,1])/s
        )
