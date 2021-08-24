import numpy as np
import matplotlib.pyplot as plt
import cv2
import imageio


if __name__ == "__main__":

    path = '/home/ngc/Desktop/test_data'

    larva = imageio.imread(path + '/perfectly_thresholded.png')


    class Test(object):

        def __init__(self) -> None:
            super().__init__()
            self.ciao = 2
        
        def test_1(self):
            print('ciao')
            return 4

        def test_2(self):
            something = 2

    test = Test()
    first = test.test_1()
    second = test.test_2()

    print(first)
    print(second)
