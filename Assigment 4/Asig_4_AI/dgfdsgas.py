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

# Hill climbing con reinicio aleatorio
def random_restart_hill_climbing(problem_generator, restarts=100):
    best_solution = None
    best_value = float('inf')

    for i in range(restarts):
        problem = problem_generator()
        solution = hill_climbing(problem)

        if problem.goal_test(solution):
            print(f"Solución encontrada en reinicio #{i+1}")
            return solution, i+1  # devuelve la solución y número de reinicios

        solution_value = problem.h(solution)
        if solution_value < best_value:
            best_solution = solution
            best_value = solution_value

    print("No se encontró solución óptima después de todos los reinicios.")
    return best_solution, restarts

# Ejecución del algoritmo
problem = generate_random_8puzzle()
print("Estado inicial del problema generado:")
print(np.reshape(problem.initial, (3,3)))

solution, restarts_used = random_restart_hill_climbing(generate_random_8puzzle, restarts=50)

if problem.goal_test(solution):
    print("\n:white_check_mark: Solución óptima encontrada:")
else:
    print("\n:warning: No se encontró la solución óptima. Mejor solución encontrada:")

print(np.reshape(solution, (3,3)))
print(f"Reinicios realizados: {restarts_used}")