"""
for normal PID with predefined values:
python script.py Area Beta Qd_start h_start Tp simLeng targeth hMax maxInput P_val I_val D_val
for ml version:
python script.py Area Beta Qd_start h_start Tp simLeng targeth hMax maxInput
to use ga version, swap line 87 and 89. mean and std parameters in norm(x) are the same for both
up to 6 places after the comma, so they're aproximated as the same value
"""

import math
import sys

import pandas as pd

import PIDController as PID_Controller
import tensorflow as tf


def norm(x):
    # hardcoded values from data used to train currently used model
    stat = {'mean': [15.926381, 6.080413, 0.549178],
            'std': [3.693254, 2.660454, 0.274814]}
    # I don't get why I need to do it this way (dict -> dataframe -> func)
    # but it wouldn't work with (dataframe -> func) and I don't have time to fuck around
    stats = pd.DataFrame(stat)
    return (x - stats['mean']) / stats['std']


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
        if deltaH >= threshH and h[n] != h[-1]:
            tmp.append([n, h[n]])
            tmp_iter += 1
    # append the last value in sim manually
    if tmp[-1][0] != h[-1]:
        tmp.append([lastIteration + 1, h[-1]])
    return tmp


# main

# Area in m^2
A = float(sys.argv[1])
# runoff coefficient, in m^(5/2)/s
Beta = float(sys.argv[2])
# Flow in in m^3/s, our input variable as Qd[0]=something non 0
Qd = [float(sys.argv[3])]
# Liquid height during steps, h(0) is the starting condition, in m
h = [float(sys.argv[4])]
# Sampling time/step time
Tp = float(sys.argv[5])
# in hours
SimulationLength = float(sys.argv[6])
# desired level
target_level = float(sys.argv[7])

# additional variables
e = [target_level - h[0]]

lastIteration = 0
# constraints
hMax = float(sys.argv[8])  # maximum length of container in meters
maxInput = float(sys.argv[9])
# 1: calculate number of iterations
iterations = int(3600 * SimulationLength / Tp)

pid_val1 = 0
pid_val2 = 0
pid_val3 = 0

if len(sys.argv) == 13:
    # use the predefined values
    pid_val1 = float(sys.argv[10])
    pid_val2 = float(sys.argv[11])
    pid_val3 = float(sys.argv[12])
else:
    # for ml-regression based model:
    model = tf.keras.models.load_model('saved models/version-ml-pid')
    # for ga-based model:
    # model = tf.keras.models.load_model('saved models/version-ga-pid')
    # print(model.summary())
    inpar = pd.DataFrame(norm([A, Beta, Tp]))
    prd = model.predict(inpar.transpose())
    # print(prd)
    # just to be sure, no negative values
    pid_val1 = prd.item(0) if prd.item(0) > 0 else 0
    pid_val2 = prd.item(1) if prd.item(1) > 0 else 0
    pid_val3 = prd.item(2) if prd.item(2) > 0 else 0
# ready the controller
PID_controller = PID_Controller.PIDController(pid_val1, pid_val2, pid_val3, Tp)

"""
f = open("data/controlled_filling/controlled_filling_data", "w")
f.write("water level over time:\n")

fControl = open("data/PID_controller_diagnostic", "w")
fControl.write("e\tde\tdde\tQd\n")
"""

# 2:loop
"""
f.write(str(h[0]))
f.write("\n")

totalError = 0
"""
for n in range(iterations + 1):
    # totalError += abs(e[n])
    # skip step n = 0
    if n == 0:
        h.append(h[n])
        continue
    # calculate errors for the controller
    e.append(target_level - h[n])
    de = e[n] - e[n - 1]

    if n < 2:
        dde = de
    else:
        dde = e[n] - 2 * e[n - 1] + e[n - 2]

    # calculate the signal from PID, remember to sum it
    input = PID_controller.calc_delta_u(de, e[n], dde)
    input += Qd[n - 1]
    if input <= 0:
        input = 0
    if input > maxInput:
        input = maxInput
    Qd.append(input)
    # print("Qd: ", Qd[n])
    # calc next water lever
    hNext = 1 / A * (-1 * Beta * math.sqrt(h[n - 1]) + Qd[n - 1]) * Tp + h[n - 1]
    if hNext > hMax:
        # print('Container overflowed! Happened at iteration = ', n, ' equal to time =', n * Tp, ' s.')
        # f.write("Error, overfilled!\n")
        # f.close()
        # fControl.close()
        h.append(999999)
        break
        # raise ValueError('Try setting different parameters')
    if hNext < 0:
        # print('Container Empty! Happened at iteration = ', n, ' equal to time =', n * Tp, ' s.')
        h.append(999999)
        break
    h.append(hNext)
    lastIteration = n
    # print(hNext)
    """
    f.write(str(hNext))
    f.write("\n")
    sentence = " ".join([str(e[n]), "\t", str(de), "\t", str(dde), "\t", str(Qd[n]), "\n"])
    fControl.write(sentence)
    """
"""
print('total error: ' + str(totalError))
f.close()
fPID.close()
"""
key_moments = createKeyMomentsTable()
# print(key_moments)
