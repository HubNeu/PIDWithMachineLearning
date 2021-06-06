"""
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


def convertToPerUnitTime(arg):
    # we have everything in something per minute, here we convert to per iteration
    return arg / 60


def createKeyMomentsTable():
    # tmp[[n,c,V],...]
    tmp = [[0, c[0], V[0]]]
    for n in range(len(c)):
        if n == 0:
            continue
        deltaC = c[n] - c[n - 1]
        deltaV = V[n] - V[n - 1]
        threshC = 0.01
        threshV = 0.12
        if deltaV >= threshV or deltaC >= threshC:
            tmp.append([n, c[n], V[n]])
    return tmp


from tools import PIDController as PID_Controller

# main start

# constraints
vMax = 2000  # maximum length of container in meters
cMax = 1  # maximum concentration, if c>cMax, then sth is wrong

# parameters

# starting volume (m^3)
V = [10]
# starting concentration
c = [0.1]
# target concentration
target_c = 0.25
# sampling time/step time (in seconds)
Tp = 0.5
# concentration of ingredient 1
cd1 = [0.5]
# concentration of ingredient 2
cd2 = [0.2]
# simulationLength (in hours)
simulationLength = 1
# inflow of first ingredient, for now constant (m^3/m)
Qd1 = [convertToPerUnitTime(5)]
# inflow of second ingredient, for now constant (m^3/m)
Qd2 = [convertToPerUnitTime(3)]
# outflow, I thought it'd be Beta*sqrt(h(n)) but apparently it's const (m^3/m)
Qo = [convertToPerUnitTime(5)]

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

# input cap
maxInflow = convertToPerUnitTime(10)

# PID controller data
fPID = open("PIDFillingSettingsConc", "r")
PID_conc = PID_Controller.PIDController(float(fPID.readline()), float(fPID.readline()),
                                        float(fPID.readline()),
                                        Tp)

fPID = open("PIDFillingSettingsFlow", "r")
PID_flow = PID_Controller.PIDController(float(fPID.readline()), float(fPID.readline()), float(fPID.readline()),
                                        Tp)

fConcDiag = open("PID_conc_diagnostic.txt", "w")
fConcDiag.write("e\tde\tdde\tu1\n")

fVolDiag = open("PID_vol_diagnostic.txt", "w")
fVolDiag.write("e\tde\tdde\tu2\n")

# 1: calculate number of iterations
iterations = int(3600 * simulationLength / Tp)

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
    #if tmp_u1 < 0:
        #tmp_u1 = 0
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
    print("Qd1: ", Qd1[n])
    # all of unchanging constants have been swapped for direct indexes
    # modified model
    Qo[0] = Qd1[n] + Qd2[0]
    VNext = (Qd1[n] + Qd2[0] - Qo[0]) * Tp + V[n - 1]
    if VNext > vMax:
        print('Container overflowed! Happened at iteration = ', n)
        f.write("Error, overfilled!\n")
        f.close()
        break
    if VNext < 0:
        print('Container empty! Happened at iteration = ', n)
        f.write("Error, empty!\n")
        f.close()
        break
    V.append(VNext)
    aa = Qd1[n - 1] * (cd1[0] - c[n - 1])
    bb = Qd2[0] * (cd2[0] - c[n - 1])
    delta = (aa + bb) * Tp / V[n - 1]
    cNext = delta + c[n - 1]
    if cNext > cMax:
        print('Concentration too high!')
        f.write("Error, concentration above 100%!\n")
        f.close()
        break
    c.append(cNext)
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

finalScore = createKeyMomentsTable()
f.close()
