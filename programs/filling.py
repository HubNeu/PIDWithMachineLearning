"""
General idea: solve recursively from n = 0 to N where N = number of iterations derived from time / Tp
If spare time is found, try going from N to 0 to see how much memory its gonna hog
Starting conditions (can be changed later):

h(0) = h0
h(n+1) = 1/A*(-1*Beta*math.sqrt(h(n))+Qd(n))*Tp+h(n)

where:
A = area of the bottom of the container
Beta = runoff coefficient, for explanation see page 12 of ISS lab 1 presentation
Qd = flow input
Q0 = flow output
Tp = sampling time
h = liquid level inside of container
"""

import math
import sys


def createKeyMomentsTable():
    # tmp[[n,c,V],...]
    tmp = [[0, h[0]]]
    tmp_iter = 0
    threshH = 0.01
    for n in range(len(h) - 1):
        # starting with n = 1
        if n == 0:
            continue
        # calculate delta between current value and last value in the key moments list
        deltaH = abs(h[n] - tmp[tmp_iter][1])
        # append when >= threshold value
        if deltaH >= threshH:
            tmp.append([n, h[n]])
            tmp_iter += 1
    # append the last value in sim manually
    if tmp[-1][0] != h[-1]:
        tmp.append([lastIteration + 1, h[-1]])
    return tmp


# main

# parameters

# Area in m^2
A = float(sys.argv[1])
# runoff coefficient, in m^(5/2)/s
Beta = float(sys.argv[2])
# Flow in in m^3/s, our input variable
Qd = float(sys.argv[3])
# Liquid height during steps, h(0) is the starting condition, in m
h = [float(sys.argv[4])]
# Sampling time/step time
Tp = float(sys.argv[5])
# in hours
SimulationLength = float(sys.argv[6])

# constraints
hMax = float(sys.argv[7])  # maximum length of container in meters

# 1: calculate number of iterations
iterations = int(3600 * SimulationLength / Tp)

lastIteration = 0
"""
f = open("filling_data.txt", "w")
f.write("water level over time:\n")
"""
# 2:loop
"""
f.write(str(h[0]))
f.write("\n")
"""
for n in range(iterations + 1):
    # print("Value: ", n)  #yay, works, 36k iterations
    # skip step n = 0
    if n == 0:
        continue
    hNext = 1 / A * (-1 * Beta * math.sqrt(h[n - 1]) + Qd) * Tp + h[n - 1]
    if hNext > hMax:
        print('Container overflowed! Happened at iteration = ', n, ' equal to time =', n * Tp, ' s.')
        """
        f.write("Error, overfilled!\n")
        f.close()
        """
        # sort of flag that it's gone wrong
        h.append(999999)
        break
    h.append(hNext)
    lastIteration = n
    """
    print(hNext)
    f.write(str(hNext))
    f.write("\n")
    """
key_moments = createKeyMomentsTable()
# print(key_moments)
# f.close()
