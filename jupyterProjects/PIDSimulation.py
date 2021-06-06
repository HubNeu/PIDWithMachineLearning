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
import PIDController as PID_Controller


class PIDSimulation:
    # first quality measure: (we sum all error through )
    sumOfError = 0

    def __init__(self, argA, argBeta, argQd, argh, argTp, argSimulationLength, argtarget_level, argHMax, argMaxQd, argP,
                 argI, argD):
        # Area in m^2
        self.A = argA
        # runoff coefficient, in m^(5/2)/s
        self.Beta = argBeta
        # Flow in in m^3/s, our input variable as Qd[0]=something non 0
        self.Qd = [argQd]
        # Liquid height during steps, h(0) is the starting condition, in m
        self.h = [argh]
        # Sampling time/step time
        self.Tp = argTp
        # in hours
        self.SimulationLength = argSimulationLength
        # desired level
        self.target_level = argtarget_level

        # additional variables
        # error
        self.e = [self.target_level - self.h[0]]
        # max height of container in meters
        self.hMax = argHMax
        # max input flow
        self.maxQd = argMaxQd
        self.iterations = int(3600 * self.SimulationLength / self.Tp)
        self.pidValues = [argP, argI, argD, argTp]
        self.PID_controller = PID_Controller.PIDController(argP,
                                                           argI,
                                                           argD,
                                                           self.Tp)
        self.simDone = False

    def simulate(self):
        self.simDone = True
        for n in range(self.iterations + 1):
            # calculate error in this step
            self.e.append(self.target_level - self.h[n])
            # sum the error (our quality measure)
            self.sumOfError += abs(self.e[n])
            # skip step n = 0
            if n == 0:
                self.h.append(self.h[n])
                continue

            # calculate errors for the controller
            de = self.e[n] - self.e[n - 1]

            # error[n-2] is 0 if we didn't get past 2nd iteration
            if n < 2:
                dde = de
            else:
                dde = self.e[n] - 2 * self.e[n - 1] + self.e[n - 2]

            # calculate the signal from PID, remember to sum it
            newInput = self.PID_controller.calc_delta_u(de, self.e[n], dde)
            newInput += self.Qd[n - 1]
            if newInput <= 0:
                newInput = 0
            if newInput >= self.maxQd:
                newInput = self.maxQd
            self.Qd.append(newInput)

            # calc next water lever
            # h(n+1) = 1/A*(-1*Beta*math.sqrt(h(n))+Qd(n))*Tp+h(n)
            hNext = 1 / self.A * (-1 * self.Beta * math.sqrt(self.h[n - 1]) + self.Qd[n]) * self.Tp + self.h[n - 1]
            if hNext > self.hMax:
                # print('Container overflowed! Happened at iteration = ', n, ' equal to time =', n * self.Tp, ' s.')
                self.simDone = False
                break
                # raise ValueError('Try setting different parameters')
            if hNext < 0:
                hNext = 0
            self.h.append(hNext)
        return

    def getSimulation(self):
        if self.simDone:
            self.pidValues.append(self.sumOfError)
            return self.pidValues
        else:
            self.pidValues.append(0.0)
            return self.pidValues

    def getSimulationError(self):
        return self.sumOfError

"""
# Test:
Qd = [float(0)]
h = [float(0)]
simulationLength = 0.75
targetLevel = 4
h_Max = 10
max_Qd = 25
values = [1.0, 1.0, 0.1, 1.0, 4.1000000000000005, 5.6000000000000005]
test = PIDSimulation(values[0], values[1], Qd[0], h[0], values[2],
                     simulationLength, targetLevel, h_Max, max_Qd, values[3],
                     values[4], values[5])
# test = PIDSimulation(1.0, 1.0, 0, 0, 0.1, 0.5, 4, 10, 25, 2, 0.7, 4.4)
test.simulate()
print('Simulation results:')
print('P\tI\tD\tTp\terror')
print(test.getSimulation())
"""