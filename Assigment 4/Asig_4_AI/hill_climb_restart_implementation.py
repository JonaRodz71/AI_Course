from search import *
import random
import numpy as np

# Genera una instancia del 8-puzzle asegurando que sea resoluble
def generate_random_8puzzle():
    puzzle = list(range(9))
    random.shuffle(puzzle)
    while not EightPuzzle(puzzle).check_solvability(puzzle):
        random.shuffle(puzzle)
    return EightPuzzle(puzzle)

# Genera una instancia aleatoria para el problema 8-Queens
def generate_random_8queens():
    state = tuple(random.randint(0, 7) for _ in range(8))
    return NQueensProblem(8, state)

# Función para imprimir claramente el estado del 8-puzzle
def print_puzzle(state):
    for i in range(0, 9, 3):
        print(state[i:i+3])

# Hill climbing con reinicio aleatorio
def random_restart_hill_climbing(problem_generator, restarts=100):
    best_solution = None
    best_value = float('inf')
    steps_taken = 0

    for i in range(restarts):
        problem = problem_generator()
        current = Node(problem.initial)
        steps = 0

        while True:
            neighbors = current.expand(problem)
            if not neighbors:
                break
            neighbor = argmax_random_tie(neighbors, key=lambda node: problem.value(node.state))

            if problem.value(neighbor.state) <= problem.value(current.state):
                break

            current = neighbor
            steps += 1

        if problem.goal_test(current.state):
            print(f"Solución encontrada en reinicio #{i+1}")
            return current.state, i+1, steps

        solution_value = problem.h(current.state)
        if solution_value < best_value:
            best_solution = current.state
            best_value = solution_value
            steps_taken = steps

    print("No se encontró solución óptima después de todos los reinicios.")
    return best_solution, restarts, steps_taken




# Ejecutar 8-puzzle
solution, restarts_used, pasos = random_restart_hill_climbing(generate_random_8puzzle, restarts=100)
if solution:
    print("\nEstado final encontrado (8-puzzle):")
    print_puzzle(solution)
print(f"Reinicios realizados (8-puzzle): {restarts_used}")
print(f"Número total de pasos realizados (8-puzzle): {pasos}")

# Ejecutar 8-queens
solution_q, restarts_q, pasos_q = random_restart_hill_climbing(generate_random_8queens, restarts=100)
if solution_q:
    print("\nEstado final encontrado (8-Queens):")
    print(solution_q)
    print(f"Número de conflictos en la solución: {NQueensProblem(8, solution_q).h(solution_q)}")
print(f"Reinicios realizados (8-Queens): {restarts_q}")
print(f"Número total de pasos realizados (8-Queens): {pasos_q}")
