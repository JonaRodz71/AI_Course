import os
import platform
import random
from typing import List, Literal, Union
import copy
import logging


from .domino_components import (
    generate_domino_set,
    Domino,
    Player,
    AI_Player,
    check_play,
    orient_if_needed,
)
from .utils import validate_direction, validate_idx
from .cli_interactions import cli_feedback


def clear_terminal():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# make use of logging if you make 2 AI compete each other
logging.basicConfig(filename="logging.txt", filemode="w", level=logging.INFO)


class DominoState:
    def __init__(
        self,
        ground: List[Domino],  # Corrected type annotation
        tiles: List[Domino],
        players: List[Player],
        turn_idx: int,
    ):
        self.ground = ground
        self.tiles = tiles
        self.players = players
        self.turn_idx = turn_idx

    def __repr__(self):
        return f"<DominoState(ground={self.ground}, tiles={self.tiles}, players={self.players}, turn_idx={self.turn_idx})>"

    def __str__(self):
        return f"DominoState:\nGround: {self.ground}\nTiles: {self.tiles}\nPlayers: {self.players}\nTurn Index: {self.turn_idx}"

    def copy(self):
        return copy.deepcopy(self)

    def change_turn(self):
        self.turn_idx = (self.turn_idx + 1) % len(self.players)



class DominoGame:
    def __init__(self, players: List[str] = ["ai1", "ai2", "ai3", "ai4"], seed=None):
        """Initializes the game with unique AI players.

        Args:
            players (List[str]): List of AI types for each player.
            seed (int, optional): Random seed for reproducibility.
        """
        self.players_types = players
        self.num_players = len(players)
        self.players: List[Player] = []

        for i, ai_type in enumerate(players):
            self.players.append(AI_Player(f"ai {i+1}", ai_type=ai_type))

        if seed is not None:
            random.seed(seed)
        else:
            random.seed()  # Ensure random seed is system-randomized


    def get_initial_state(self):
        """Deals tiles after generating a shuffled domino tile set."""
        tiles = generate_domino_set()
        random.shuffle(tiles)  # Ensure fair shuffling

        # Deal tiles equally among players
        hand_size = len(tiles) // self.num_players
        for i, player in enumerate(self.players):
            player.set_hand(tiles[i * hand_size : (i + 1) * hand_size])

        ground = []
        del tiles[: hand_size * self.num_players]  # Remove dealt tiles from the pool

        turn_idx = 0
        state = DominoState(ground, tiles, self.players, turn_idx)
        return state

    def get_ground_ends(self, ground: List[Domino]):
        """returns ground tiles ends

        Args:
            ground (List[Domino]): ground tiles

        Returns:
            Tuple(int,int): left and right ground tiles ends
        """
        l, r = ground[0].left, ground[-1].right
        return l, r

    def get_valid_moves(self, player: Union[Player, AI_Player], ground: List[Domino]):
        """traverses player's hand, and check validity of each tile. And writes the result onto player object.

        Args:
            player (Player): player to check his valid placements
            ground (List[Domino]): ground tiles

        Returns:
            List[Tuple[bool,bool]]: validity of each tile in player's hand
        """
        hand = player.hand
        conditions = [check_play(ground, tile) for tile in hand]
        player.conditions = conditions

        return conditions

    def get_next_state(
        self, state: DominoState, action: Domino, player: Union[Player, AI_Player]
    ):
        """given current state, action(Domino to place) and the player performing action, this function returns the next state.

        Args:
            state (DominoState): _description_
            action (Domino): _description_
            player (Union[Player,AI_Player]): _description_

        Raises:
            e: An expection if anything goes wrong

        Returns:
            DominoState: next
        """
        try:
            condition = player.conditions[player.hand.index(action)]
        except Exception as e:
            raise e

        if all(condition):
            if type(player) is Player and (
                state.ground[-1].right != state.ground[0].left
            ):
                direction = validate_direction()
            else:
                try:
                    direction = player.double_ended_tile_score
                except:
                    direction = random.choice(["r", "l"])

            l, r = self.get_ground_ends(state.ground)
            if direction == "r":
                state.ground.append(orient_if_needed(l, r, action, direction))
            else:
                state.ground.insert(0, orient_if_needed(l, r, action, direction))
        elif condition[0]:
            state.ground.insert(0, action)
        elif condition[1]:
            state.ground.append(action)

        player.hand.remove(action)
        action.color = state.turn_idx
        return state

    def check_win(self, state: DominoState):
        """Checks if a player has won the game and returns the winner's index.

        Args:
            state (DominoState): Current game state.

        Returns:
            int: Winner index if a player has won, otherwise None.
        """
        for i, player in enumerate(state.players):
            if len(player.hand) == 0:  # A player has emptied their hand
                logging.info(f"WINNER: {player.name}")
                return i  # Return the index of the winning player
        return None  # No winner yet

    def check_deadend(self, state: DominoState):
        """Checks if the game has reached a dead-end and returns the winner's index.

        Args:
            state (DominoState): Current game state.

        Returns:
            int: Winner index if a dead-end occurs, otherwise None.
        """
        if not state.ground:
            return None  # No dead-end if the ground is empty

        l, r = self.get_ground_ends(state.ground)

        # Check if no player can play and no tiles are left to draw
        for player in state.players:
            for tile in player.hand:
                if l in tile or r in tile:
                    return None  # A valid move is still possible

        for tile in state.tiles:
            if l in tile or r in tile:
                return None  # A valid move is still possible

        # Dead-end detected, determine the winner by the lowest hand value
        winner = min(
            enumerate([player.count_hand() for player in state.players]),
            key=lambda x: x[1],
        )[0]
        logging.info(f"  DEADEND, winner:{state.players[winner].name}")
        return winner

    def update_score(self, state: DominoState, winner: int):
        """Updates winning player's score given winner id.

        Args:
            state (DominoState): Current domino state.
            winner (int): Winner index.
        """
        res = sum(
            [
                player.count_hand()
                for i, player in enumerate(state.players)
                if i != winner
            ]
        )
        state.players[winner].score += res

    def evaluate_state(self, state: DominoState):
        """State evaluation for MCTS. It only favours less hand value. Under development to perform more sophisticated evaluation.

        Args:
            state (DominoState): current domino state

        Returns:
            int: state evaluation
            bool: state termination condition
        """
        ai = state.players[1]
        player_with_turn = state.players[state.turn_idx]
        val = -1 * (ai.count_hand())
        is_terminal = not any(
            any(condition)
            for condition in self.get_valid_moves(player_with_turn, state.ground)
        )
        return val, is_terminal

    def is_game_over(self, state):
        """Checks if the game is over."""
        # Check if any player has an empty hand
        for player in state.players:
            if not player.hand:
                return True

        # Check if no valid moves are available for any player
        for player in state.players:
            valid_moves = self.get_valid_moves(player, state.ground)
            if any(any(condition) for condition in valid_moves):
                return False

        # If no valid moves and no empty hands, the game is over
        return True

    def calculate_score(self, state: DominoState):
        """Calculates the score of the game based on the current state.

        Args:
            state (DominoState): The current game state.

        Returns:
            int: The score of the game, calculated as the sum of the values of all tiles in the hands of all players.
        """
        return sum(player.count_hand() for player in state.players)

    def display_ai_types(self):
        """Displays the AI type for each player."""
        for player in self.players:
            if isinstance(player, AI_Player):
                print(f"{player.name} is using AI type: {player.ai_type}")
            else:
                print(f"{player.name} is a human player.")

    def casual_game(self, placement_contexts, final_score=101, cls=True, verbose=False):
        """Casual gameplay logic with optional visualization of the game state.

        Args:
            placement_context: Context for AI move calculation.
            final_score (int): The score limit to end the game.
            cls (bool): Whether to clear the terminal between rounds.
            verbose (bool): Whether to display intermediate game states.
        """
        game = self
        state = game.get_initial_state()
        no_moves_counter = 0  # Counter to track consecutive turns with no valid moves

        while all([player.score <= final_score for player in state.players]):
            if cls and verbose:
                clear_terminal()
            if verbose:
                # Display the current game state
                print(f"Current Ground: {state.ground}")
                for player in state.players:
                    print(f"{player.name}'s Hand: {player.hand} (Score: {player.score})")
                print(f"Player {state.players[state.turn_idx].name}'s Turn")

            valid_moves = game.get_valid_moves(
                state.players[state.turn_idx], state.ground
            )
            if not any([any(placement) for placement in valid_moves]):
                if len(state.tiles) > 0:
                    if verbose:
                        print(f"{state.players[state.turn_idx].name} is drawing a tile...")
                    tile = state.tiles.pop()
                    while (
                        not any(check_play(state.ground, tile)) and len(state.tiles) > 0
                    ):
                        state.players[state.turn_idx].append_tile_to_hand(tile)
                        tile = state.tiles.pop()
                    state.players[state.turn_idx].append_tile_to_hand(tile)
                    no_moves_counter = 0  # Reset counter when a tile is drawn
                    continue
                else:
                    if verbose:
                        print(f"{state.players[state.turn_idx].name} has no valid moves. Skipping turn.")
                    state.change_turn()
                    no_moves_counter += 1
                    # Check if all players are stuck
                    if no_moves_counter >= len(state.players):
                        # Determine the winner by the smallest hand value
                        winner = min(
                            enumerate([player.count_hand() for player in state.players]),
                            key=lambda x: x[1],
                        )[0]
                        if verbose:
                            print(f"No valid moves available for any player. Winner: {state.players[winner].name}")
                        # Update the winner's score
                        game.update_score(state, winner)
                        break
                    continue

            no_moves_counter = 0  # Reset counter when a valid move is made
            if state.turn_idx == 0 and type(state.players[state.turn_idx]) == Player:
                ui_tiles = cli_feedback(state)
                idx = validate_idx(len(ui_tiles))
                action = ui_tiles[idx]
            else:
                current_ai = placement_contexts[state.turn_idx]
                action = current_ai.calc(state)
            if verbose:
                print(f"{state.players[state.turn_idx].name} chose move: {action}")
            state = game.get_next_state(state, action, state.players[state.turn_idx])
            # Check for win or dead-end winner
            c_win, c_deadend = game.check_win(state), game.check_deadend(state)
            winner = c_win if c_win is not None else c_deadend
            if winner is not None:  # A winner or dead-end was detected
                if type(winner) == int:
                    if verbose:
                        print(f"Round Over! Winner: {state.players[winner].name}")
                    game.update_score(state, winner)
                    state = game.get_initial_state()  # Reset the game state for the next round
                    state.turn_idx = winner  # The winner starts the next round
                    continue
            state.change_turn()
        print("<!> Game Over")
        if cls:
            clear_terminal()
        print("Final Scores:")
        for player in state.players:
            if player.score >= 101:
                return player, player.score
                print(f"{player.name}: {player.score}")