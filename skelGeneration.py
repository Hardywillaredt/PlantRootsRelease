
import numpy as np
from random import randint
import random


skelFile = open('D:/testSkeleton.txt', 'w')


rows = []

standoff = 15.0


vertexCount = 1000

vertices = []
edges = []
ifloat = 0.0
for i in range(0, vertexCount):
    ifloat += 0.1
    vertices.append([str(ifloat), str(0), str(0)])

ifloat = 0.0
for edgeI in range(0, vertexCount - 1):
    ifloat += 0.1
    thickness = ifloat
    width = 100 - ifloat
    tempthick = max(thickness, width)
    width = min(thickness, width)
    thickness = tempthick
    edges.append([str(edgeI), str(edgeI + 1), str(thickness), str(width), '1'])

skelFile.write(str(len(vertices)) + ' ' + str(len(edges)) + ' 0\n')

for node in vertices:
    skelFile.write(" ".join(node) + '\n')

for edge in edges:
    skelFile.write(" ".join(edge) + '\n')


#vertexCount = 0
#vertices = []
#for i in range(0, 20):
#    phi = ((1.0 * i) / 10.0) * np.pi
#    row = []
#    for j in range(0, 9):
#        theta = ((1.0 * j + 1) / 10.0) * np.pi
#        x = 0.0 + standoff*np.cos(phi)*np.sin(theta)
#        z = 0.0 + standoff*np.sin(phi)*np.sin(theta)
#        y = 0.0 + standoff*np.cos(theta)
#        pos = [str(x), str(y), str(z)]
#        row.append(pos)
#        vertices.append(pos)
#        vertexCount += 1

#    rows.append(row)

#edgeCount = 0

#random.seed()
#edges = []
#for i in range(0, int(len(rows) / 2)):
#    i = i * 2
#    vertexI = len(rows[i]) * i
#    for j in range(0, len(rows[i]) - 1):
#        thisVertex = vertexI + j
#        upVertex = thisVertex + 1
#        edges.append([str(thisVertex), str(upVertex)])
        
#        edgesToConnect = randint(0, 3)

#        for newEdge in range(0, edgesToConnect):
#            leftOrRight = randint(0, 1)
#            rowj = randint(0, 8)
#            if leftOrRight == 0:
#                rowStart = len(rows[i]) * (i - 1)
#                index = rowStart + rowj
#                edges.append([str(thisVertex), str(index)])


#for edge in edges:
#    thick = random.uniform(0, 1)
#    width = random.uniform(0, 1)

#    if thick < width:
#        tempWidth = width
#        width = thick
#        thick = tempWidth

#    length = 1.0

#    edge.append(str(thick))
#    edge.append(str(width))
#    edge.append(str(length))



#skelFile.write(str(len(vertices)) + ' ' + str(len(edges)) + ' 0\n')

#for node in vertices:
#    skelFile.write(" ".join(node) + '\n')

#for edge in edges:
#    skelFile.write(" ".join(edge) + '\n')


skelFile.close()