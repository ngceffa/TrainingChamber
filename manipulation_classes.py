import numpy as np
import matplotlib.pyplot as plt


class LightStimulation(object):
    """To control punishment/reward with optogenetics"""
    def __init__(
        self,
        port):
        super().__init__()
        #define light on/off
    def on(self):
        pass
    def off(self):
        pass


class Valves(object):
    """Control all the valves associated with a specific circle.
    Assuming the port are passed in the form:
    port[A, B, C]
    A = Rapsberry IO controlling air
    B = Rapsberry IO controlling input (can be CO2)
    C = Rapsberry IO controlling vacuum
    """
    def __init__(
        self,
        ports):
        super().__init__()
        pass
    def air(self):
        pass
    def input(self):
        pass
    def vacuum(self):
        pass