"""
python script.py Vc Qd1 Qd2 Qo cd1 cd2 Tp sim_length VMax
or
python script.py Vc Qd1 Qd2 Qo cd1 cd2 Tp sim_length
for no VMax checking

General idea: solve with iterations from n = 0 to N where N = number of iterations derived from time / Tp
If spare time is found, try going from N to 0 to see how much memory its gonna hog
Starting conditions (can be changed later):

V(0)=V0
V(n+1)=(Qd1(n)+Qd2(n)-Q0(n))*Tp+V(n)
c(0)=c0
c(n+1)=(Qd1(n)*(cd1(n)-c(n))+Qd2(n)*(cd2(n)-c(n)))*Tp/V(n)+c(n)

where:
c   = concentration of ingredient
Qd = inflow of # ingredient
Qo  = outflow of solution
V   = volume of solution
"""

import sys


def createKeyMomentsTable():
    tmp = [[0, V[0], c[0]]]
    tmp_iter = 0
    threshV = 0.01
    threshC = 0.01
    for n in range(len(c) - 1):
        # starting with n = 1
        if n == 0:
            continue
        # calculate delta between current value and last value in the key moments list
        deltaV = abs(V[n] - tmp[tmp_iter][1])
        deltaC = abs(c[n] - tmp[tmp_iter][2])
        # append when >= threshold value
        if deltaV >= threshV or deltaC >= threshC:
            tmp.append([n, V[n], c[n]])
            tmp_iter += 1
    # append the last value in sim manually
    if tmp[-1][0] != c[-1]:
        tmp.append([lastIteration, V[-1], c[-1]])
    return tmp


# main start

# constraints
vMax = 9999999  # maximum size of container in m^3
cMax = 1  # maximum concentration, if c>cMax, then sth is wrong

# parameters

# starting volume (m^3)
V = [float(sys.argv[1])]
# starting concentration, between <0,1>
c = [float(sys.argv[2])]
# inflow of first ingredient, for now constant (m^3/s)
Qd1 = [float(sys.argv[3])]
# inflow of second ingredient, for now constant (m^3/s)
Qd2 = [float(sys.argv[4])]
# outflow, I thought it'd be Beta*sqrt(h(n)) but apparently it's const (m^3/s)
Qo = [float(sys.argv[5])]
# concentration of ingredient 1, between <0,1>
cd1 = [float(sys.argv[6])]
# concentration of ingredient 2, between <0,1>
cd2 = [float(sys.argv[7])]
# sampling time/step time (in seconds)
Tp = float(sys.argv[8])
# simulationLength (in hours)
simulationLength = float(sys.argv[9])
# flag to whether or not use VMax overflow indication
flag_use_vmax = False

if len(sys.argv) == 11:
    # will use overflow indication if given the parameter
    vMax = float(sys.argv[10])
    flag_use_vmax = True

lastIteration = 0

# 1: calculate number of iterations
iterations = int(3600 * simulationLength / Tp)
"""
f = open("mix", "w")
# f.write("number of iterations: ")
# f.write(str(iterations))
# f.write("\n")
f.write("n\t")
f.write("water volume V\t")
f.write("water input Qd1\t")
f.write("water input Qd2\t")
f.write("water output Qo\t")
f.write("concentration c\t")
f.write("concentration cd1\t")
f.write("concentration cd2\n")

f.write("0\t")
f.write(str(V[0]) + "\t")
f.write(str(Qd1[0]) + "\t")
f.write(str(Qd2[0]) + "\t")
f.write(str(Qo[0]) + "\t")
f.write(str(c[0]) + "\t")
f.write(str(cd1[0]) + "\t")
f.write(str(cd2[0]) + "\n")
"""
# 2:loop
for n in range(iterations + 1):
    # print("Value: ", n)  #yay, works, 36k iterations
    # skip step n = 0
    if n == 0:
        continue
    # all of unchanging constants have been swapped for direct indexes
    VNext = (Qd1[0] + Qd2[0] - Qo[0]) * Tp + V[n - 1]
    if VNext > vMax:
        # print('Container overflowed! Happened at iteration = ', n)
        # f.write("Error, overfilled!\n")
        # f.close()
        V.append(VNext)
        c.append(c[n-1])
        break
    if VNext < 0:
        # print('Container Empty! Happened at iteration = ', n)
        # f.write("Error, overfilled!\n")
        # f.close()
        V.append(VNext)
        c.append(c[n - 1])
        break
    cNext = (Qd1[0] * (cd1[0] - c[n - 1]) + Qd2[0] * (cd2[0] - c[n - 1])) * Tp / V[n - 1] + c[n - 1]
    if cNext > cMax:
        # print('Concentration too high!')
        # f.write("Error, concentration above 100%!\n")
        # f.close()
        V.append(VNext)
        c.append(cNext)
        break
    V.append(VNext)
    c.append(cNext)
    lastIteration = n
    """
    f.write(str(n) + "\t")
    f.write(str(VNext) + "\t")
    f.write(str(Qd1[0]) + "\t")
    f.write(str(Qd2[0]) + "\t")
    f.write(str(Qo[0]) + "\t")
    f.write(str(cNext) + "\t")
    f.write(str(cd1[0]) + "\t")
    f.write(str(cd2[0]) + "\n")
    """

# f.close()
key_moments = createKeyMomentsTable()
# print(key_moments)
