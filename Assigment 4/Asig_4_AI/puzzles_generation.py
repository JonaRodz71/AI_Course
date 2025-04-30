# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 14:03:07 2025

@author: jonat
"""

import random

def is_solvable(puzzle):
    inv_count = 0
    tiles = [tile for tile in puzzle if tile != 0]
    for i in range(len(tiles)):
        for j in range(i+1, len(tiles)):
            if tiles[i] > tiles[j]:
                inv_count += 1
    return inv_count % 2 == 0

def generate_8_puzzle():
    while True:
        board = random.sample(range(9), 9)  # 0 to 8
        if is_solvable(board):
            return board

def generate_multiple_8_puzzles(n):
    return [generate_8_puzzle() for _ in range(n)]

def print_8_puzzle(board):
    assert len(board) == 9, "Board must have exactly 9 tiles"
    for i in range(0, 9, 3):
        row = board[i:i+3]
        print("+---+---+---+")
        print("| {} | {} | {} |".format(
            ' ' if row[0] == 0 else row[0],
            ' ' if row[1] == 0 else row[1],
            ' ' if row[2] == 0 else row[2],
        ))
    print("+---+---+---+\n")

# Example usage:
#puzzles = generate_multiple_8_puzzles(10)
#for p in puzzles:
#    print_8_puzzle(p)