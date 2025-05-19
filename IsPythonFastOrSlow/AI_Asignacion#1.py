#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import numpy as np

def multiply_1d_python(a, b):
    return [a[i] * b[i] for i in range(len(a))]

def multiply_2d_python(A, B):
    rows, cols = len(A), len(B[0])
    result = [[0.0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            for k in range(len(B)):
                result[i][j] += A[i][k] * B[k][j]
    return result

def multiply_1d_numpy(a, b):
    return np.multiply(a, b)

def multiply_2d_numpy(A, B):
    return np.dot(A, B)

def generate_1d_array(size):
    return [random.uniform(0.0, 1.0) for _ in range(size)]

def generate_2d_array(rows, cols):
    return [[random.uniform(0.0, 1.0) for _ in range(cols)] for _ in range(rows)]

sizes_1d = [10, 50, 100, 200, 500]
sizes_2d = [10, 50, 100, 200, 500]

# 1D Multiplication Timing
for size in sizes_1d:
    average_time_python = 0
    average_time_numpy = 0
    for i in range(100):
        a, b = generate_1d_array(size), generate_1d_array(size)
        start_time = time.perf_counter()
        result1 = multiply_1d_python(a, b)
        end_time = time.perf_counter()
        
        average_time_python = average_time_python + (end_time - start_time)
        
        a_np, b_np = np.array(a, dtype=np.float64), np.array(b, dtype=np.float64)
        start_time = time.perf_counter()
        result2 = multiply_1d_numpy(a_np, b_np)
        end_time = time.perf_counter()
        
        average_time_numpy = average_time_numpy + (end_time - start_time)
    
    print(f"1D Array ({size} elements) - Python: {average_time_python/100.0:.6f} seconds")
    print(f"1D Array ({size} elements) - NumPy: {average_time_numpy/100.0:.6f} seconds")
    print("Are the results equal?", np.allclose(result1, result2), " \n")

# 2D Multiplication Timing
for size in sizes_2d:
    average_time_python = 0
    average_time_numpy = 0
    for i in range(10):
        A, B = generate_2d_array(size, size), generate_2d_array(size, size)
        start_time = time.perf_counter()
        result1 = multiply_2d_python(A, B)
        end_time = time.perf_counter()
        
        average_time_python = average_time_python + (end_time - start_time)
        
        A_np, B_np = np.array(A, dtype=np.float64), np.array(B, dtype=np.float64)
        start_time = time.perf_counter()
        result2 = multiply_2d_numpy(A_np, B_np)
        end_time = time.perf_counter()
        
        average_time_numpy = average_time_numpy + (end_time - start_time)
        
    print(f"2D Array ({size}x{size}) - Python: {average_time_python/10.0:.6f} seconds")
    print(f"2D Array ({size}x{size}) - NumPy: {average_time_numpy/10.0:.6f} seconds")
    print("Are the results equal?", np.allclose(result1, result2), " \n")