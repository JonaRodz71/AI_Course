import random
import time
import VacuumAgents

class Environment:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.grid = [[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]  # 0 = clean, 1 = dirty
        self.agent_position = (random.randint(0, rows - 1), random.randint(0, cols - 1))  # Random start position
        self.performance = 0  # Tracks agent performance

    def is_dirty(self):
        row, col = self.agent_position
        return self.grid[row][col] == 1

    def clean(self):
        """ Cleans the current tile and increases performance score. """
        row, col = self.agent_position
        if self.grid[row][col] == 1:
            self.grid[row][col] = 0  # Suck dirt
            self.performance += 10  # Reward for cleaning

    def move(self, new_position):
        """ Moves the agent to a new position if within bounds and decreases score for movement cost. """
        row, col = new_position
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.agent_position = (row, col)
            self.performance -= 1  # Penalty for movement

    def get_available_moves(self):
        """ Returns valid moves from the current position. """
        row, col = self.agent_position
        moves = []
        
        if row > 0: moves.append((-1, 0))  # Can move up
        if row < self.rows - 1: moves.append((1, 0))  # Can move down
        if col > 0: moves.append((0, -1))  # Can move left
        if col < self.cols - 1: moves.append((0, 1))  # Can move right

        return moves

    def is_all_clean(self):
        """ Checks if all tiles are clean. """
        return all(all(tile == 0 for tile in row) for row in self.grid)

    def get_map(self):
        """ Returns a visual representation of the environment. """
        display = []
        for r in range(self.rows):
            row_display = []
            for c in range(self.cols):
                if (r, c) == self.agent_position:
                    row_display.append("V")  # Vacuum's position
                elif self.grid[r][c] == 1:
                    row_display.append("D")  # Dirty tile
                else:
                    row_display.append("_")  # Clean tile
            display.append(" | ".join(row_display))
        return "\n".join(display)

class VacuumAgent:
    def __init__(self, environment):
        self.environment = environment
        self.cleaned_tiles = 0
        self.moves = 0

    def act(self):
        """ To be implemented by subclasses. """
        pass

def run_simulation(agent_class, max_moves=1000, rows=5, cols=5, output_file="simulation_output.txt"):
    agents = ['Simple Reflex Agent', 'Random Reflex Agent', 
              'State Reflex Agent', 'Rational Reflex Agent']
    
    with open('simulation_run.txt', "w") as file:
        for agent in agents:
            env = Environment(rows=rows, cols=cols)
            
            if agent == 'Simple Reflex Agent':
                vacuum_agent = VacuumAgents.SimpleReflexAgent(env)
            elif agent == 'Random Reflex Agent':
                vacuum_agent = VacuumAgents.RandomReflexAgent(env)
            elif agent == 'State Reflex Agent':
                vacuum_agent = VacuumAgents.StateReflexAgent(env)
            elif agent == 'Rational Reflex Agent':
                vacuum_agent = VacuumAgents.RationalReflexAgent(env)
            else:
                vacuum_agent = VacuumAgents.VacuumAgent(env)
                
            separator = '*' * 40 + '\n'
            file.write(separator)
            file.write(f"Simulating: {agent}\n")
            file.write(f"Initial State:\n{env.get_map()}\n\n")
            
            print(separator)
            print(f"Simulating: {agent}")
            print(f"Initial State:\n{env.get_map()}\n")
        
            for step in range(max_moves):
                vacuum_agent.act()
                state_output = f"Step {step + 1}:\n{env.get_map()}\n\n"
                file.write(state_output)
                print(state_output)
                time.sleep(0.2)
        
                if env.is_all_clean():
                    file.write("All tiles cleaned! Stopping simulation.\n")
                    print("All tiles cleaned! Stopping simulation.")
                    break
        
            final_score = f"Final Performance Score for {agent}: {env.performance}\n"
            file.write(final_score)
            file.write(separator)
            print(final_score)
            print(separator)
    
    print(f"Simulation results saved to {output_file}")

# Example usage:
run_simulation(VacuumAgent)
