'''
Barcode decoding through peak detection

Author: Shashwat Shukla
Date: 14th April 2018
'''
# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pylab
import copy
import scipy.signal as sig

x = np.loadtxt("data.txt")  # raw barcode data

x = x[30:820]  # extract forward pass
dx = np.gradient(x)  # derivative of raw data

m = np.max(x)
x = x * 1000 / m # Calibrate reading on white to 1000. 1024 = 3.3V on the ADC

y = np.zeros(np.size(x))  # smoothened data
w = 5
win = np.ones(w) / w
y = np.convolve(x, win)
y = y[w-1:-(w-1)]
y = np.convolve(y, win)
y = y[w-1:-(w-1)]
y = np.convolve(y, win)
y = y[w-1:-(w-1)]
y = np.convolve(y, win)
y = y[w-1:-(w-1)]
y = np.convolve(y, win)
y = y[w-1:-(w-1)]

dy = np.gradient(y)  # derivative of smoothened data

d2y = np.zeros(np.size(dy))  # smoothened derivative of smoothened data
eps = 0.9  # 0.9
d2y[0] = dy[0]
for i in range(1, np.size(dy)):
    d2y[i] = (1 - eps) * dy[i - 1] + eps * d2y[i - 1]


plt.subplot(3, 1, 1)
plt.plot(x)
plt.subplot(3, 1, 2)
plt.plot(y)
plt.subplot(3, 1, 3)
plt.plot(d2y[:-5])
plt.show()

amax = np.array(sig.argrelextrema(d2y, np.greater))[0]  # maxima
amin = np.array(sig.argrelextrema(d2y, np.less))[0]  # minima
while(amax[0] < amin[0]):  # first extrema must be a minima
    np.delete(amax, 0)
while(amin[1] < amax[0]): # ensure that minima and maxima alternate in the start
    np.delete(amin, 0)
maxim = np.zeros(d2y.size)
maxim[amax] = 1
minim = np.zeros(d2y.size)
minim[amin] = 1


# Remove insignificant extrema
gap = 10
change = 0.1
for i in range(amax.size):
    if(amax[i] + gap < d2y.size):
        if(d2y[amax[i]] - d2y[amax[i] + gap] < change):
            maxim[amax[i]] = 0
    if(amax[i] > gap):
        if(d2y[amax[i]] - d2y[amax[i] - gap] < change):
            maxim[amax[i]] = 0

for i in range(amin.size):
    if(amin[i] + gap < d2y.size):
        if(d2y[amin[i] + gap] - d2y[amin[i]] < change):
            minim[amin[i]] = 0
    if(amin[i] > gap):
        if(d2y[amin[i] - gap] - d2y[amin[i]] < change):
            minim[amin[i]] = 0

extrem = minim + maxim
val = np.multiply(extrem, d2y)

# Remove small extrema
eps = 0.2 # 2
for i in range(val.size):
    if(np.abs(val[i]) < eps):
        val[i] = 0
    if(np.abs(val[i - 1]) > 0 or np.abs(val[i - 2]) > 0 or np.abs(val[i - 3]) > 0 or np.abs(val[i - 4]) > 0 or np.abs(val[i - 5]) > 0
       or np.abs(val[i - 6]) > 0 or np.abs(val[i - 7]) > 0 or np.abs(val[i - 8]) > 0 or np.abs(val[i - 9]) > 0):
        val[i] = 0


plt.subplot(411)
plt.plot(y)
plt.subplot(412)
plt.plot(d2y)
plt.subplot(413)
plt.plot(extrem)
plt.subplot(414)
plt.plot(val)
plt.show()


# Render the recovered barcode
barcode = np.zeros(val.size)
k = 0
for i in range(val.size):
    if(np.abs(val[i]) > 0):
        k = (k + 1) % 2
    barcode[i] = k

plt.stem(barcode, markerfmt=' ')
plt.show()

# Compute barcode widths
edge = np.array(np.where(val != 0))
edge = edge[0]
edges = edge[3:-6]
bars = np.zeros(24)
for i in range(24):
    bars[i] = edges[i + 1] - edges[i]
e = np.zeros((6, 4))
for i in range(6):
    e[i] = bars[4 * i:4 * i + 4]
    scale = np.sum(e[i])
    e[i] = 7 * e[i] / scale
widths = np.round(e).astype(int)
print(widths)

# Decode barcode
final = np.zeros(51)
final[0]  = 1
final[1]  = 0
final[2]  = 1
final[45] = 0
final[46] = 1
final[47] = 0
final[48] = 1
final[49] = 0
final[50] = 1

r = 3
k = 0
for i in range(6):
    for j in range(4):
        final[r:r+widths[i][j]] = k
        r = r + widths[i][j]
        k = (k + 1) % 2


def parity(a):
    return np.sum(a) % 2

def digit(a, p):
    if(p == 1):
        a = (a + 1) % 2;
        a = a[::-1]

    if(a[0]==0 and a[1]==1 and a[2]==0 and a[3]==0 and a[4]==1 and a[5]==1 and a[6]==1):
        return 0
    elif(a[0]==0 and a[1]==1 and a[2]==1 and a[3]==0 and a[4]==0 and a[5]==1 and a[6]==1):
        return 1
    elif(a[0]==0 and a[1]==0 and a[2]==1 and a[3]==1 and a[4]==0 and a[5]==1 and a[6]==1):
        return 2
    elif(a[0]==0 and a[1]==1 and a[2]==0 and a[3]==0 and a[4]==0 and a[5]==0 and a[6]==1):
        return 3
    elif(a[0]==0 and a[1]==0 and a[2]==1 and a[3]==1 and a[4]==1 and a[5]==0 and a[6]==1):
        return 4
    elif(a[0]==0 and a[1]==1 and a[2]==1 and a[3]==1 and a[4]==0 and a[5]==0 and a[6]==1):
        return 5
    elif(a[0]==0 and a[1]==0 and a[2]==0 and a[3]==0 and a[4]==1 and a[5]==0 and a[6]==1):
        return 6
    elif(a[0]==0 and a[1]==0 and a[2]==1 and a[3]==0 and a[4]==0 and a[5]==0 and a[6]==1):
        return 7
    elif(a[0]==0 and a[1]==0 and a[2]==0 and a[3]==1 and a[4]==0 and a[5]==0 and a[6]==1):
        return 8
    elif(a[0]==0 and a[1]==0 and a[2]==1 and a[3]==0 and a[4]==1 and a[5]==1 and a[6]==1):
        return 9
    else:
        return -1


def check(b):
    if(b[0]==1):
        b = (b + 1) % 2

    if(b[2]==0 and b[3]==1 and b[4]==1 and b[5]==1):
        return 0
    elif(b[2]==1 and b[3]==0 and b[4]==1 and b[5]==1):
        return 1
    elif(b[2]==1 and b[3]==1 and b[4]==0 and b[5]==1):
        return 2
    elif(b[2]==1 and b[3]==1 and b[4]==1 and b[5]==0):
        return 3
    elif(b[2]==0 and b[3]==0 and b[4]==1 and b[5]==1):
        return 4
    elif(b[2]==1 and b[3]==0 and b[4]==0 and b[5]==1):
        return 5
    elif(b[2]==1 and b[3]==1 and b[4]==0 and b[5]==0):
        return 6
    elif(b[2]==0 and b[3]==1 and b[4]==0 and b[5]==1):
        return 7
    elif(b[2]==0 and b[3]==1 and b[4]==1 and b[5]==0):
        return 8
    elif(b[2]==1 and b[3]==0 and b[4]==1 and b[5]==0):
        return 9
    else:
        return -1

b = np.zeros(6)
out = np.zeros(8) 
def convert():
    for j in range(6):
        b[j] = parity(final[3 + 7*j:3 + 7*j + 7])
        out[1+j] = digit(final[3 + 7*j:3 + 7*j + 7].astype(int), b[j])
  
convert()
out[0] = b[0]
out[7] = check(b.astype(int))
out = out.astype(int)
print("Final Barcode: ")
print(out)



