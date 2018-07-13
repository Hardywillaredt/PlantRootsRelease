# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import sys
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt

import numpy as np
for directory in sys.path:
    print(directory)
    


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


myColors = getColorList(10, cm.jet)

print(myColors)
print(type(myColors))