# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 16:50:51 2018

@author: Will
"""

import numpy as np

def intersectRayCylinder(rayOrigin : np.array, rayDir : np.array, cP0 : np.array, cP1 : np.array, cR : float, cScale : float = 1.0):
    """
    Refer to geomalgorithms.com/a07-_distance.html for the source of this algorithm, and any analytics therof.
    Returns a tuple of (intersects : bool, hitDistance : float), the first indicates 
    """
    u = rayDir
    v = cP1 - cP0
    v = v / np.linalg.norm(v)
    w = rayOrigin - cP0
    
    a = np.dot(u, u)
    b = np.dot(u, v)
    c = np.dot(v, v)
    d = np.dot(u, w)
    e = np.dot(v, w)
    D = a*c - b*b
    sc = 0.0
    tc = 0.0
    
    
    
    if D < 0.0001:
        dist = -1.0
        if b > c:
            tc = d/b
        else:
            tc = e/c
    else:
        sc = (b*e -c*d) / D
        tc = (a*e - b*d) / D
    
    dP = w + (u*sc) - (tc*v)
    
    dist = np.linalg.norm(dP)
    
    if dist < cR*cScale:
        cylLength = np.linalg.norm(cP1 - cP0)
#        if the cylinder length is larger than the length along the cylinder vector tc
#        or tc is negative (point is behing endpoint)
#        or sc is negative (points is behind the start of the ray)
        if cylLength > tc and tc > 0 and sc > 0:
            return (True, sc)
    return (False, -1.0)
    
    
def intersectRaySphere(rayOrigin : np.array, rayDir : np.array, center : np.array, r : float, scale : float = 1.0):
    rayToCenter = center - rayOrigin
    distOnRay = np.dot(rayDir, rayToCenter)
    
    onRay = rayOrigin + rayDir * distOnRay
    
    dist = np.linalg.norm(center - onRay)
    
    if dist < r*scale and distOnRay > 0:
        return (True, distOnRay)
    
    return (False, -1.0)