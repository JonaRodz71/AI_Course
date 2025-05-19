import random

class VacuumAgent:
    def __init__(self, environment):
        self.environment = environment
        self.cleaned_tiles = 0
        self.moves = 0

    def act(self):
        """ To be implemented by subclasses. """
        pass
    
class SimpleReflexAgent(VacuumAgent):
    def __init__(self, environment):
        super().__init__(environment)
        self.direction = (0, 1)  # Start moving right
        self.moving_down = True  # Initially move down when hitting a border

    def act(self):
        """ Cleans if dirty; otherwise, moves in a snake pattern. """
        if self.environment.is_dirty():
            self.environment.clean()
            self.cleaned_tiles += 1
        else:
            row, col = self.environment.agent_position

            # Calculate the next move
            new_position = (row + self.direction[0], col + self.direction[1])

            # Check if we hit a horizontal border
            if new_position[1] < 0 or new_position[1] >= self.environment.cols:
                # Move down or up depending on `moving_down` state
                if self.moving_down:
                    new_position = (row + 1, col)  # Move down
                else:
                    new_position = (row - 1, col)  # Move up
                
                # If hitting the bottom, switch to moving up
                if new_position[0] >= self.environment.rows:
                    new_position = (row - 1, col)  # Move up instead
                    self.moving_down = False  # Start moving up

                # If hitting the top, switch to moving down
                elif new_position[0] < 0:
                    new_position = (row + 1, col)  # Move down instead
                    self.moving_down = True  # Start moving down

                # Reverse direction (left ↔ right)
                self.direction = (0, -self.direction[1])

            self.environment.move(new_position)
            self.moves += 1


class RandomReflexAgent(VacuumAgent):
    def act(self):
        """ Cleans if dirty; otherwise, moves randomly. """
        if self.environment.is_dirty():
            self.environment.clean()
            self.cleaned_tiles += 1
        else:
            move = random.choice(self.environment.get_available_moves())
            new_position = (self.environment.agent_position[0] + move[0],
                            self.environment.agent_position[1] + move[1])
            self.environment.move(new_position)
            self.moves += 1

class StateReflexAgent(VacuumAgent):
    def __init__(self, environment):
        super().__init__(environment)
        self.visited_tiles = set()

    def act(self):
        """ Cleans if dirty; otherwise, moves while avoiding revisited tiles. """
        if self.environment.is_dirty():
            self.environment.clean()
            self.cleaned_tiles += 1
        else:
            self.visited_tiles.add(self.environment.agent_position)
            possible_moves = [move for move in self.environment.get_available_moves()
                              if (self.environment.agent_position[0] + move[0],
                                  self.environment.agent_position[1] + move[1]) not in self.visited_tiles]

            if possible_moves:
                move = random.choice(possible_moves)
            else:
                move = random.choice(self.environment.get_available_moves())  # No choice, move randomly

            new_position = (self.environment.agent_position[0] + move[0],
                            self.environment.agent_position[1] + move[1])
            self.environment.move(new_position)
            self.moves += 1

class RationalReflexAgent(VacuumAgent):
    def find_nearest_dirty_tile(self):
        """ Finds the nearest dirty tile using BFS while ensuring no out-of-bounds errors. """
        queue = [(self.environment.agent_position, [])]
        visited = set()

        while queue:
            (current_pos, path) = queue.pop(0)
            row, col = current_pos

            # Ensure we are within bounds before accessing grid
            if 0 <= row < self.environment.rows and 0 <= col < self.environment.cols:
                if self.environment.grid[row][col] == 1:  # Dirty tile found
                    return path

                visited.add(current_pos)

                # Check all available moves (Up, Down, Left, Right)
                for move in self.environment.get_available_moves():
                    new_position = (row + move[0], col + move[1])

                    # Ensure new position is within bounds and not already visited
                    if (0 <= new_position[0] < self.environment.rows and
                        0 <= new_position[1] < self.environment.cols and
                        new_position not in visited):
                        
                        queue.append((new_position, path + [move]))

        return []  # No dirty tile found

    def act(self):
        """ Moves towards the nearest dirty tile or moves randomly if all are clean. """
        if self.environment.is_dirty():
            self.environment.clean()
            self.cleaned_tiles += 1
        else:
            path_to_dirty = self.find_nearest_dirty_tile()
            
            if path_to_dirty:  # If there is a dirty tile, move towards it
                move = path_to_dirty[0]
            else:  # If all are clean, move randomly
                move = random.choice(self.environment.get_available_moves())

            new_position = (self.environment.agent_position[0] + move[0],
                            self.environment.agent_position[1] + move[1])
            self.environment.move(new_position)
            self.moves += 1