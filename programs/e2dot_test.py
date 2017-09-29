#!/usr/bin/env python

import sys
import time
from functools import wraps

from EMAN2 import *
import libpyCuda

def time_decorator(func):
    @wraps(func)
    def wrapper(*args):
        t0 = time.time()
        func(*args)
        t1 = time.time()
        
        return t1 - t0
    
    return wrapper

@time_decorator
def py_cpp_dot(ims, ref_im):
    for i in range(len(ims)):
        libpyCuda.cpp_dot(ims[i], ref_im)

@time_decorator
def py_gpu_kernel(ims, ref_im):
    for i in range(len(ims)):
        libpyCuda.cuda_dot(ims[i], ref_im)

@time_decorator
def py_thrust_inner_product(ims, ref_im):
    for i in range(len(ims)):
        libpyCuda.thrust_inner_product(ims[i], ref_im)

@time_decorator
def py_thrust_transform_and_reduce(ims, ref_im):
    for i in range(len(ims)):
        libpyCuda.thrust_transform_and_reduce(ims[i], ref_im)

@time_decorator
def py_thrust_transform_reduce(ims, ref_im):
    for i in range(len(ims)):
        libpyCuda.thrust_transform_reduce(ims[i], ref_im)


def main():
    ss = [256, 512]
    nums = range(1,10,5)
    nums.extend(range(10,100,10))
    nums.extend(range(100,251,50))

    im = test_image(0, size=(8, 8))
    py_gpu_kernel([im], im)

    print "# ss \t num \t Cpp \t Cuda \t Thrust"
    
    for s in ss:
        ref_im = test_image(0, size=(s, s))

        for num in nums:
            images = []
            for i in range(num):
                im = test_image(i%10, size=(s, s))
                images.append(im)
        
            t1 = py_cpp_dot(images, ref_im)
            t2 = py_gpu_kernel(images, ref_im)
            t3 = py_thrust_inner_product(images, ref_im)
            t4 = py_thrust_transform_and_reduce(images, ref_im)
            t5 = py_thrust_transform_reduce(images, ref_im)
        
            print s, num, t1, t2, t3, t4, t5
            
        print "\n"


if __name__ == '__main__':
    main()
