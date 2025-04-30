# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 14:19:39 2025

@author: jonat
"""
import random
import math
from queens_generation import *
from puzzles_generation import *

def simulated_annealing_8_queens(board, schedule=lambda t: 0.99**t, max_steps=10000):
    current = board[:]
    steps = 0

    for t in range(1, max_steps + 1):
        temperature = schedule(t)
        steps += 1

        if evaluate_queens(current) == 0:
            return {
                "solution": current,
                "search_cost": steps,
                "solved": True
            }

        neighbor = get_queen_neighbor(current)
        delta_e = evaluate_queens(neighbor) - evaluate_queens(current)

        if delta_e < 0:
            current = neighbor
        else:
            prob = math.exp(-delta_e / temperature)
            if random.random() < prob:
                current = neighbor

    return {
        "solution": current,
        "search_cost": steps,
        "solved": evaluate_queens(current) == 0
    }

def simulated_annealing_8_puzzle(puzzle, schedule=lambda t: 0.99995 ** t, max_steps=50000):
    current = puzzle[:]
    steps = 0

    for t in range(1, max_steps + 1):
        temperature = schedule(t)
        steps += 1

        if evaluate_puzzle(current) == 0:
            return {
                "solution": current,
                "search_cost": steps,
                "solved": True
            }

        neighbors = get_puzzle_neighbors(current)
        neighbor = random.choice(neighbors)

        delta_e = evaluate_puzzle(neighbor) - evaluate_puzzle(current)

        if delta_e < 0:
            current = neighbor
        else:
            prob = math.exp(-delta_e / temperature)
            if random.random() < prob:
                current = neighbor

    # If we exit the loop without solving
    return {
        "solution": current,
        "search_cost": steps,
        "solved": False
    }

# Helper methods
def evaluate_queens(board):
    
    conflicts = 0
    for i in range(len(board)):
        for j in range(i+1, len(board)):
            if board[i] == board[j]:  # Same row
                conflicts += 1
            elif abs(board[i] - board[j]) == abs(i - j):  # Same diagonal
                conflicts += 1
    return conflicts

def get_queen_neighbor(board):
    
    new_board = board[:]
    col = random.randint(0, 7)
    old_row = new_board[col]
    new_row = random.choice([r for r in range(8) if r != old_row])
    new_board[col] = new_row
    return new_board

def get_puzzle_neighbors(state):
    neighbors = []
    idx = state.index(0)
    row, col = divmod(idx, 3)
    moves = [(-1,0),(1,0),(0,-1),(0,1)]  # up, down, left, right

    for dr, dc in moves:
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:
            new_idx = r * 3 + c
            new_state = state[:]
            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]
            neighbors.append(new_state)
    return neighbors


def evaluate_puzzle(puzzle):
    goal = {n: (i//3, i%3) for i, n in enumerate([1,2,3,4,5,6,7,8,0])}
    total = 0
    for i, tile in enumerate(puzzle):
        if tile == 0:
            continue
        r, c = i // 3, i % 3
        gr, gc = goal[tile]
        total += abs(r - gr) + abs(c - gc)
    return total

boards = generate_multiple_8_queens(5)
puzzles = generate_multiple_8_puzzles(5)

for i in range(5):
    
    print("\n" + "*" *40 + "\n8-Queens\n" + "*"*40 + "\n")
    #initial_board = generate_8_queens()
    result = simulated_annealing_8_queens(boards[i], schedule=lambda t: 0.99**t)
    
    print("Initial Board:")
    print_8_queens(boards[i])
    
    print("Final State:")
    print_8_queens(result["solution"])
    
    print("Solved:", result["solved"])
    print("Search Cost:", result["search_cost"])
    
    print("\n" + "*" *40 + "\n8-Puzzle\n" + "*"*40 + "\n")
    #puzzle = generate_8_puzzle()
    result = simulated_annealing_8_puzzle(puzzles[i])
    
    print("Initial Puzzle:")
    print_8_puzzle(puzzles[i])
    
    print("Final State:")
    print_8_puzzle(result["solution"])
    
    print("Solved:", result["solved"])
    print("Search Cost:", result["search_cost"])