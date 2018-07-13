
myFile = open('D:/lotsofpoints.txt', 'w')

xArr = []
yArr = []
zArr = []


for i in range(-2, 2):
    xArr.append(float(i))
    yArr.append(float(i))
    zArr.append(float(i))


pointsArr = []

for x in xArr:
    for y in yArr:
        for z in zArr:
            pointstr = str(x) + ' ' + str(y) + ' ' + str(z)
            pointsArr.append(pointstr)

linesArr = []

for i in range(0, len(pointsArr) - 1):
    lineStr = str(i) + ' ' + str(i+1) + ' 1.0 1.0 1.0'
    linesArr.append(lineStr)



myFile.write(str(len(pointsArr)) + ' ' + str(len(linesArr)) + ' 0 \n')

for point in pointsArr:
    myFile.write(point + ' \n')

for line in linesArr:
    myFile.write(line + ' \n')
    




myFile.close()