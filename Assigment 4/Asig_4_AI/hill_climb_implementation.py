import random

from queens_generation import *
from puzzles_generation import *

def hill_climb_8_queens(board, variant="steepest"):
    """ Solves 8-queens using hill climbing. """
    current = board[:]
    current_value = evaluate_queens(current)
    steps = 0
    
    while True:
        neighbors = get_queen_neighbors(current)
        if not neighbors:
            break
        
        if variant == "steepest":
            next_state = min(neighbors, key=evaluate_queens)
        else:  # First-choice variant
            random.shuffle(neighbors)
            next_state = min(neighbors, key=evaluate_queens)
        
        next_value = evaluate_queens(next_state)
        
        if next_value >= current_value:
            break  # No improvement
        
        current, current_value = next_state, next_value
        steps += 1
    
    return current, current_value == 0, steps

def hill_climb_8_puzzle(puzzle, variant="steepest"):
    """ Solves 8-puzzle using hill climbing. """
    current = puzzle[:]
    current_value = evaluate_puzzle(current)
    steps = 0
    
    while True:
        neighbors = get_puzzle_neighbors(current)
        if not neighbors:
            break
        
        if variant == "steepest":
            next_state = min(neighbors, key=evaluate_puzzle)
        else:  # First-choice variant
            random.shuffle(neighbors)
            next_state = min(neighbors, key=evaluate_puzzle)
        
        next_value = evaluate_puzzle(next_state)
        
        if next_value >= current_value:
            break  # No improvement
        
        current, current_value = next_state, next_value
        steps += 1
    
    return current, current_value == 0, steps

# Helper functions

def get_queen_neighbors(board):
    neighbors = []
    for col in range(len(board)):
        for row in range(8):
            if row != board[col]:
                neighbor = board[:]
                neighbor[col] = row
                neighbors.append(neighbor)
    return neighbors

def get_puzzle_neighbors(state):
    idx = state.index(0)
    row, col = divmod(idx, 3)
    moves = [(-1,0), (1,0), (0,-1), (0,1)]
    
    neighbors = []
    for dr, dc in moves:
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:
            new_idx = r * 3 + c
            new_state = state[:]
            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]
            neighbors.append(new_state)
    return neighbors

def evaluate_queens(board):
    conflicts = sum(
        1 for i in range(len(board)) for j in range(i + 1, len(board))
        if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j)
    )
    return conflicts

def evaluate_puzzle(puzzle):
    goal = {n: (i // 3, i % 3) for i, n in enumerate(range(9))}
    return sum(
        abs(goal[tile][0] - i // 3) + abs(goal[tile][1] - i % 3)
        for i, tile in enumerate(puzzle) if tile != 0
    )

def run_experiments(n, problem="queens", variant="steepest"):
    successes = 0
    total_cost = 0
    
    for _ in range(n):
        if problem == "queens":
            board = [random.randint(0, 7) for _ in range(8)]
            _, solved, steps = hill_climb_8_queens(board, variant)
        else:
            puzzle = random.sample(range(9), 9)
            _, solved, steps = hill_climb_8_puzzle(puzzle, variant)
        
        if solved:
            successes += 1
        total_cost += steps
    
    success_rate = (successes / n) * 100
    
    print(f"Variant: {variant}, Problem: {problem}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Total Search Cost: {total_cost} steps\n")

# Running experiments for all variants
for variant in ["steepest", "first-choice"]:
    for problem in ["queens", "puzzle"]:
        run_experiments(100, problem=problem, variant=variant)
