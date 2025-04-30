from collections import deque
import copy

# Initial state of the problem 
# Missionaries and Cannibals begin on the left side of the river. 
# Boat begin on the left side of the river.

initial_state = {
    'left': {'missionaries': 3, 'cannibals': 3},
    'right': {'missionaries': 0, 'cannibals': 0},
    'boat': 'left'
}

# Function to check whether the simulation has been completed or has failed.
# The simulation remains incomplete if the left side is still occupied.
# The simulation fails if the cannibals outnumber the missionaries at any point.

def is_valid(state):
    for side in ['left', 'right']:
        if state[side]['missionaries'] < 0 or state[side]['cannibals'] < 0:
            return False
        if state[side]['missionaries'] > 0 and state[side]['cannibals'] > state[side]['missionaries']:
            return False
    return True

# Function to generate next move.
# Moves boat from side to side.
# Adds and removes missionaries/cannibals from the boat.

def generate_next_states(current_state):
    possible_moves = []
    boat_side = current_state['boat']
    other_side = 'left' if boat_side == 'right' else 'right'
    
    for missionaries in range(3):
        for cannibals in range(3):
            if 1 <= missionaries + cannibals <= 2:
                move = {'missionaries': missionaries, 'cannibals': cannibals}
                
                # Checks if state is valid.
                # Makes sure missionaries are not outnumbered on either side.

                if (current_state[boat_side]['missionaries'] >= move['missionaries'] and
                    current_state[boat_side]['cannibals'] >= move['cannibals']):
                    
                    new_state = copy.deepcopy(current_state)
                    new_state[boat_side]['missionaries'] -= move['missionaries']
                    new_state[boat_side]['cannibals'] -= move['cannibals']
                    new_state[other_side]['missionaries'] += move['missionaries']
                    new_state[other_side]['cannibals'] += move['cannibals']
                    new_state['boat'] = other_side
                    
                    if is_valid(new_state):
                        possible_moves.append(new_state)
    return possible_moves

# Function to check whether state has been visited before or not.
# Prevents the Breadth-First Search from repeating previous states.

def state_to_tuple(state):
    return (state['left']['missionaries'], state['left']['cannibals'],
            state['right']['missionaries'], state['right']['cannibals'],
            state['boat'])

# Function that uses Breadth-First Search to find a solution.

def find_solution():
    queue = deque()
    visited = set()
    
    queue.append((initial_state, []))
    visited.add(state_to_tuple(initial_state))
    
    while queue:
        current_state, path = queue.popleft()
        if current_state['left']['missionaries'] == 0 and current_state['left']['cannibals'] == 0:
            return path + [current_state]
        next_states = generate_next_states(current_state)
        for next_state in next_states:
            state_key = state_to_tuple(next_state)
            if state_key not in visited:
                visited.add(state_key)
                new_path = path + [current_state]
                queue.append((next_state, new_path))
    return None

solution = find_solution()
if solution:
    for index, state in enumerate(solution):
        print(f"Step {index + 1}: {state}")
else:
    print("No solution found.")
