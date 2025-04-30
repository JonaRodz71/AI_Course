# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 14:08:41 2025

@author: jonat
"""

import random

def generate_8_queens():
    return [random.randint(0, 7) for _ in range(8)]

def generate_multiple_8_queens(n):
    return [generate_8_queens() for _ in range(n)]

def print_8_queens(board):
    assert len(board) == 8, "Board must have 8 columns (one for each queen)"
    for row in range(8):
        print("+---" * 8 + "+")
        for col in range(8):
            if board[col] == row:
                print("| Q ", end='')
            else:
                print("|   ", end='')
        print("|")
    print("+---" * 8 + "+\n")

# Example usage:
#queens_boards = generate_multiple_8_queens(10)
#for b in queens_boards:
#    print_8_queens(b)