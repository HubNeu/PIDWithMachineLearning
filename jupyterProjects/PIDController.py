class PIDController:
    """
    incremental PID controller, equations (from ISS_Wyklad_2 page 20):

    delta_u[n]=u[n]-u[n-1]
    delta_u[n]=Kp(de[n]+Tp/Ti*e[n]+Td/Tp*d^2e(n))

    where d^2e=de[n]-de[n-1]=e[n]-2*e[n-1]+e[n+2]
    """

    def __init__(self, argKp, argTi, argTd, argTp):
        self.Kp = argKp
        self.Ti = argTi
        self.Td = argTd
        self.Tp = argTp

    def calc_delta_u(self, de, e, dde):
        return self.Kp * (de + (self.Tp / self.Ti * e) + (self.Td / self.Tp * dde))