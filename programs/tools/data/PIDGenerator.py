from programs.tools import PIDSimulation as PIDSim

"""
    THIS FILE NEEDS IT'S SAVE STRUCTURE REDONE
    IT NEEDS TO SAVE TO FILES GROUPED BY THEIR 
    FIRST THREE VALUES (A-B-T) AS LATER WE CHOOSE
    BEST OF EACH OF THESE GROUPS
"""

"""
    create a list of all features with desired step
    then divide that list into 10 smaller lists
    start simulations on all 10 threads
    save simulations to files (independently)
"""


# functions
def simulateAllChildren(pidVals, targetFile):
    # actual simulation
    for values in pidVals:
        thePID = PIDSim.PIDSimulation(values[0], values[1], values[2], values[3],
                                      values[4], values[5], values[6], values[7], values[8],
                                      values[9], values[10], values[11])
        thePID.simulate()
        if (thePID.simDone):
            values[11] = thePID.getSimulationError()
            # save to file
            targetFile.write()
        print('Simulating: ' + str(values))

    return


# main
# listOfParameters = [[A,Beta,Qd0,h0,Tp,SimulationLength,target_level,hMax,maxQd],[...]...]
listOfParameters = []
aValues = []
for n in range(20):
    aValues.append(float(1 + n * 1))

Betas = []
for n in range(20):
    Betas.append(n / 2)

TpList = []
for n in range(10):
    TpList.append(0.1 + 0.1 * n)

# create a list of possible PID values
# P from 1 to 20 with step 1
# I from 0.1 to 5 with step 0.2
# D from 0 to 8 with step 0.4

pVals = []
for n in range(20):
    pVals.append(float(n+1))

iVals = []
for n in range(25):
    iVals.append(0.3 + (n - 1) * 0.2)

dVals = []
for n in range(20):
    dVals.append(0.8 + (n - 1) * 0.4)

file1 = open("data1.txt", "w")
file2 = open("data2.txt", "w")
file3 = open("data3.txt", "w")
file4 = open("data4.txt", "w")
file5 = open("data5.txt", "w")
file6 = open("data6.txt", "w")
file7 = open("data7.txt", "w")
file8 = open("data8.txt", "w")
file9 = open("data9.txt", "w")
file0 = open("data10.txt", "w")
# for each create an entry, all combinations
n = 1
for a in aValues:
    for b in Betas:
        for t in TpList:
            for p in pVals:
                for i in iVals:
                    for d in dVals:
                        if n == 1:
                            file1.write(str([a, b, t, p, i, d]))
                            file1.write('\n')
                            n += 1
                        elif n == 2:
                            file2.write(str([a, b, t, p, i, d]))
                            file2.write('\n')
                            n += 1
                        elif n == 3:
                            file3.write(str([a, b, t, p, i, d]))
                            file3.write('\n')
                            n += 1
                        elif n == 4:
                            file4.write(str([a, b, t, p, i, d]))
                            file4.write('\n')
                            n += 1
                        elif n == 5:
                            file5.write(str([a, b, t, p, i, d]))
                            file5.write('\n')
                            n += 1
                        elif n == 6:
                            file6.write(str([a, b, t, p, i, d]))
                            file6.write('\n')
                            n += 1
                        elif n == 7:
                            file7.write(str([a, b, t, p, i, d]))
                            file7.write('\n')
                            n += 1
                        elif n == 8:
                            file8.write(str([a, b, t, p, i, d]))
                            file8.write('\n')
                            n += 1
                        elif n == 9:
                            file9.write(str([a, b, t, p, i, d]))
                            file9.write('\n')
                            n += 1
                        elif n == 10:
                            file0.write(str([a, b, t, p, i, d]))
                            file0.write('\n')
                            n = 1
file1.close()
file2.close()
file3.close()
file4.close()
file5.close()
file6.close()
file7.close()
file8.close()
file9.close()
file0.close()
