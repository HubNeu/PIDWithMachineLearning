"""
python script.py Vstart cStart targetC cd1 cd2 Tp sim_length Qd1 Qd2 Qo D1 I1 D1 VMax P2 I2 D2
above uses PID for out to keep V at the same level as in the beginning
OR
python script.py Vstart cStart targetC cd1 cd2 Tp sim_length Qd1 Qd2 Qo D1 I1 D1 VMax
uses predefined Qo as a constant outflow

P1 I1 D1 is for the input pid controllers (the share settings)
P2 I2 D2 is for the output pid controller (optional as shown above)

General idea: solve recursively from n = 0 to N where N = number of iterations derived from time / Tp
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

from tools import PIDController as PID_Controller
import sys


def convertToPerUnitTime(arg):
    # we have everything in something per minute, here we convert to per iteration
    return arg / 60


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
vMax = 9999999  # maximum length of container in meters
cMax = 1  # maximum concentration, if c>cMax, then sth is wrong

# parameters

# starting volume (m^3)
V = [float(sys.argv[1])]
# starting concentration
c = [float(sys.argv[2])]
# target concentration
target_c = float(sys.argv[3])
# concentration of ingredient 1
cd1 = [float(sys.argv[4])]
# concentration of ingredient 2
cd2 = [float(sys.argv[5])]
# sampling time/step time (in seconds)
Tp = float(sys.argv[6])
# simulationLength (in hours)
simulationLength = float(sys.argv[7])
# inflow of first ingredient, for now constant (m^3/m)
Qd1 = [float(sys.argv[8])]
# inflow of second ingredient, for now constant (m^3/m)
Qd2 = [float(sys.argv[9])]
# outflow, I thought it'd be Beta*sqrt(h(n)) but apparently it's const (m^3/m)
Qo = [float(sys.argv[10])]
# input cap
maxInflow = float(sys.argv[11])

# additional variables
e1 = [target_c - c[0]]
de1 = [0]
dde1 = [0]
u1 = [0]
e2 = [0]
de2 = [0]
dde2 = [0]
u2 = [0]
u2_unconstrained = [0]
e3 = [0]
de3 = [0]
dde3 = [0]
u3 = [0]
flag_pid_out = False

# PID controller data
# fPID = open("PIDFillingSettingsConc", "r")
pid1_v1 = float(sys.argv[12])
pid1_v2 = float(sys.argv[13])
pid1_v3 = float(sys.argv[14])
PID_conc = PID_Controller.PIDController(pid1_v1, pid1_v2, pid1_v3, Tp)
# fPID = open("PIDFillingSettingsFlow", "r")
PID_flow = PID_Controller.PIDController(pid1_v1, pid1_v2, pid1_v3, Tp)

if len(sys.argv) == 19:
    flag_pid_out = True
    vMax = float(sys.argv[15])
    pid2_v1 = float(sys.argv[16])
    pid2_v2 = float(sys.argv[17])
    pid2_v3 = float(sys.argv[18])
    # fPID = open("PIDFillingSettingsFlow", "r")
    PID_out = PID_Controller.PIDController(pid2_v1, pid2_v2, pid2_v3, Tp)
"""
fConcDiag = open("PID_conc_diagnostic.txt", "w")
fConcDiag.write("e\tde\tdde\tu1\n")

fVolDiag = open("PID_vol_diagnostic.txt", "w")
fVolDiag.write("e\tde\tdde\tu2\n")

fOutDiag = open("PID_out_diagnostic.txt", "w")
fOutDiag.write("e\tde\tdde\tu2\n")
"""
# 1: calculate number of iterations
iterations = int(3600 * simulationLength / Tp)
lastIteration = 0
"""
f = open("ctrl_mix.txt", "w")
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
    # skip step n = 0
    if n == 0:
        continue
    e1.append(target_c - c[n - 1])
    de1.append(e1[n - 1] - e1[n - 2])

    if n < 2:
        dde1.append(de1[n])
    else:
        dde1.append(e1[n - 1] - 2 * e1[n - 2] + e1[n - 3])

    tmp_u1 = PID_conc.calc_delta_u(de1[n], e1[n], dde1[n]) + u1[n - 1]
    # if tmp_u1 < 0:
    # tmp_u1 = 0
    u1.append(tmp_u1)
    # u1.append(PID_conc.calc_delta_u(de1[n], e1[n], dde1[n]))
    # u1.append(PID_conc.calc_delta_u(de1[n], 0, dde1[n]))
    # u1[n] += u1[n - 1]

    # u1 is x2, x2 - y2 = e2, y2 is V[0]
    e2.append(u1[n] - u1[n - 1])
    de2.append(e2[n] - e2[n - 1])

    if n < 2:
        dde2.append(de2[n])
    else:
        dde2.append(e2[n] - 2 * e2[n - 1] + e2[n - 2])

    tmp_u2 = PID_flow.calc_delta_u(de2[n], e2[n], dde2[n]) + u2[n - 1]
    if tmp_u2 < 0:
        tmp_u2 = 0
    u2.append(tmp_u2)
    """
    u2.append(PID_flow.calc_delta_u(de2[n], e2[n], dde2[n]))
    u2[n] += u2[n - 1]
    """

    u2_unconstrained.append(u2[n])
    if u2[n] > maxInflow:
        u2[n] = maxInflow
    if u2[n] <= 0:
        u2[n] = 0
    Qd1.append(u2[n])
    # Qo.append(Qd1[n] + Qd2[0])
    # print("Qd1: ", Qd1[n])
    # all of unchanging constants have been swapped for direct indexes

    # modified model
    # Qo[0] = Qd1[n] + Qd2[0]

    # modified model with Qo steered with PID
    if flag_pid_out:
        e3.append(V[n - 1] - V[0])
        de3.append(e3[n] - e3[n - 1])

        if n < 2:
            dde3.append(de3[n])
        else:
            dde3.append(e3[n] - 2 * e3[n - 1] + e3[n - 2])

        u3_tmp = PID_out.calc_delta_u(de3[n], e3[n], dde3[n]) + Qo[n - 1]
        if u3_tmp < 0:
            u3_tmp = 0
        u3.append(u3_tmp)
        Qo.append(u3_tmp)
    else:
        Qo.append(Qo[0])

    VNext = (Qd1[n] + Qd2[0] - Qo[n]) * Tp + V[n - 1]
    if VNext > vMax:
        # print('Container overflowed! Happened at iteration = ', n)
        V.append(VNext)
        """
        f.write("Error, overfilled!\n")
        f.close()
        """
        break
    if VNext < 0:
        # print('Container empty! Happened at iteration = ', n)
        V.append(VNext)
        """
        f.write("Error, empty!\n")
        f.close()
        """
        break
    V.append(VNext)
    aa = Qd1[n - 1] * (cd1[0] - c[n - 1])
    bb = Qd2[0] * (cd2[0] - c[n - 1])
    delta = (aa + bb) * Tp / V[n - 1]
    cNext = delta + c[n - 1]
    if cNext > cMax:
        # print('Concentration too high!')
        c.append(cNext)
        """
        f.write("Error, concentration above 100%!\n")
        f.close()
        """
        break
    c.append(cNext)
    lastIteration = n
    """
    f.write(str(n) + "\t")
    f.write(str(VNext) + "\t")
    f.write(str(Qd1[n]) + "\t")
    f.write(str(Qd2[0]) + "\t")
    f.write(str(Qo[0]) + "\t")
    f.write(str(cNext) + "\t")
    f.write(str(cd1[0]) + "\t")
    f.write(str(cd2[0]) + "\n")

    sentence = " ".join([str(e1[n]), "\t", str(de1[n]), "\t", str(dde1[n]), "\t", str(u1[n]), "\n"])
    fConcDiag.write(sentence)
    sentence = " ".join([str(e2[n]), "\t", str(de2[n]), "\t", str(dde2[n]), "\t", str(u2[n]), "\n"])
    fVolDiag.write(sentence)
    sentence = " ".join([str(e3[n]), "\t", str(de3[n]), "\t", str(dde3[n]), "\t", str(u3[n]), "\n"])
    fOutDiag.write(sentence)
    """
key_moments = createKeyMomentsTable()
# print(key_moments)
# f.close()
