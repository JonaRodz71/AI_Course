def match_tile_in_real_hand(simulated_tile, real_hand):
    #print("[DEBUG] Simulated tile:", simulated_tile, "Type:", type(simulated_tile))
    #print("[DEBUG] Real hand:", real_hand)
    for tile in real_hand:
        #print("   └── Comparing with tile:", tile, "Type:", type(tile))
        if (tile.left == simulated_tile.left and tile.right == simulated_tile.right) or \
           (tile.right == simulated_tile.left and tile.left == simulated_tile.right):
            #print("   ✅ Match found!")
            return tile

    raise ValueError(f"[SAFEGUARD] Tile {simulated_tile} not found in real hand: {real_hand}")



from abc import ABC, abstractmethod

__all__ = ["PlacementContext", "BlindStrategy", "MCTSStrategy", "RuleBasedStrategy", "ClairvoyantStrategy", "ClairvoyanceStrategy"]

import numpy as np
import os
import random

from ..core.domino_components import Player, AI_Player
from .mcts import MCTS
from ..core.utils import get_ground_frequency, get_hand_frequency, load_config


args = load_config(os.path.join(os.path.dirname(__file__), "hyper_parameters.yaml"))


class AIStrategy(ABC):
    @abstractmethod
    def get_domino_placement(self, hand, board):
        pass


class BlindStrategy(AIStrategy):
    """Blindly choose tile from valid hand tiles"""

    def __init__(self, game):
        self.game = game
        try:
            random.seed()
        except:
            pass

    def get_domino_placement(self, state):
        valid_moves = [
            i[1]
            for i in zip(
                [
                    any(condition)
                    for condition in self.game.get_valid_moves(
                        state.players[state.turn_idx],
                        state.ground,
                    )
                ],
                state.players[state.turn_idx].hand,
            )
            if i[0]
        ]
        action = random.choice(valid_moves)
        real_hand = state.players[state.turn_idx].hand
        return match_tile_in_real_hand(action, real_hand)


class RuleBasedStrategy(AIStrategy):
    """ "Classic rule based strategy
    Experts are advised to perform evaluation, and return best probable tile placement
    """

    def __init__(self, game):
        self.game = game
        self.args = args["rule_based"]

    def get_domino_placement(self, state):
        ai = state.players[state.turn_idx]
        ai.double_ended_tile_score = None
        valid_tiles = [
            i[1]
            for i in zip(
                [
                    any(condition)
                    for condition in self.game.get_valid_moves(
                        ai,
                        state.ground,
                    )
                ],
                ai.hand,
            )
            if i[0]
        ]

        # prioritize value
        scores = [tile.count_tile() * self.args["tile_value"] for tile in valid_tiles]
        # prioritize doubles
        scores = [
            s * self.args["double_tiles"] if v.is_double() else s
            for v, s in zip(valid_tiles, scores)
        ]

        # prioritize versatility
        valid_tiles_conditions = [
            condition for condition in ai.conditions if any(condition)
        ]
        hand_frequency = get_hand_frequency(ai.hand)
        for idx, condition in enumerate(valid_tiles_conditions):
            if all(condition):
                playing_left = hand_frequency[valid_tiles[idx].left]
                playing_right = hand_frequency[valid_tiles[idx].right]
                ai.double_ended_tile_score = [
                    playing_left * self.args["tiles_in_hand"],
                    playing_right * self.args["tiles_in_hand"],
                ]
                continue
            elif condition[0]:
                coef = hand_frequency[valid_tiles[idx].left]
            elif condition[1]:
                coef = hand_frequency[valid_tiles[idx].right]
            scores[idx] += coef * self.args["tiles_in_hand"]

        # prtioritize playing safe
        ground_frequency = get_ground_frequency(state.ground)
        for idx, condition in enumerate(valid_tiles_conditions):
            if all(condition):
                playing_left = hand_frequency[valid_tiles[idx].right]
                playing_right = hand_frequency[valid_tiles[idx].left]
                ai.double_ended_tile_score[0] -= (
                    playing_left * self.args["tiles_in_ground"]
                )
                ai.double_ended_tile_score[1] -= (
                    playing_right * self.args["tiles_in_ground"]
                )
                continue

            elif condition[0]:
                coef = ground_frequency[valid_tiles[idx].right]
            elif condition[1]:
                coef = ground_frequency[valid_tiles[idx].left]
            scores[idx] -= coef * self.args["tiles_in_ground"]

        if ai.memory:
            for idx, condition in enumerate(valid_tiles_conditions):
                if condition[0]:
                    tile_half = valid_tiles[idx].left
                elif condition[1]:
                    tile_half = valid_tiles[idx].right
                if tile_half in ai.memory:
                    scores[idx] += self.args["blocking_bonus"]

        if ai.double_ended_tile_score:
            ai.double_ended_tile_score = (
                "l"
                if ai.double_ended_tile_score[0] >= ai.double_ended_tile_score[1]
                else "r"
            )
        action = valid_tiles[np.argmax(scores)]
        real_hand = state.players[state.turn_idx].hand
        return match_tile_in_real_hand(action, real_hand)


class MCTSStrategy(AIStrategy):
    """Monte Carlo Tree Search (MCTS) Strategy.
    This implementation focuses on minimizing the AI player's remaining tiles by identifying the most probable optimal moves. Future enhancements will incorporate more advanced evaluation methods, leveraging the AI player's memory feature for improved decision-making.
    """

    def __init__(self, game):
        self.game = game
        self.mcts = MCTS(game, args["mcts"])

    def get_domino_placement(self, state):
        if not state.ground:
            ai_player = state.players[state.turn_idx]
            action = ai_player.hand[
                max(
                    enumerate([tile.count_tile() for tile in ai_player.hand]),
                    key=lambda x: x[1],
                )[0]
            ]
            real_hand = state.players[state.turn_idx].hand
            return match_tile_in_real_hand(action, real_hand)
    
        ai_state = state.copy()
        ai_state.turn_idx = state.turn_idx
        for i, p_player in enumerate(ai_state.players):
            ai_state.players[i] = AI_Player(f"ai {i+1}", p_player.hand)
    
        mcts_probs = self.mcts.search(ai_state)
    
        if not mcts_probs:
            #print("[WARN] MCTS returned no moves. Falling back to random valid move.")
            valid_moves = [
                i[1]
                for i in zip(
                    [
                        any(condition)
                        for condition in self.game.get_valid_moves(
                            state.players[state.turn_idx], state.ground
                        )
                    ],
                    state.players[state.turn_idx].hand,
                )
                if i[0]
            ]
            action = random.choice(valid_moves)
            real_hand = state.players[state.turn_idx].hand
            return match_tile_in_real_hand(action, real_hand)
    
        action = mcts_probs[np.argmax([i[0] for i in mcts_probs])][1]
        real_hand = state.players[state.turn_idx].hand
        return match_tile_in_real_hand(action, real_hand)



class AlphaBetaMiniMax(AIStrategy):
    """Alpha-Beta MiniMax strategy for AI"""

    def get_domino_placement(self, state):
        raise NotImplementedError("Alpha-beta hasn't yet implemented")


class ClairvoyanceStrategy(AIStrategy):
    """Averaging Over Clairvoyance Strategy.
    Simulates possible future states to evaluate the best move.
    """

    def __init__(self, game, num_simulations=10):
        self.game = game
        self.num_simulations = num_simulations

    def get_domino_placement(self, state):
        valid_moves = [
            i[1]
            for i in zip(
                [
                    any(condition)
                    for condition in self.game.get_valid_moves(
                        state.players[state.turn_idx],
                        state.ground,
                    )
                ],
                state.players[state.turn_idx].hand,
            )
            if i[0]
        ]

        if not valid_moves:
            return None

        scores = []
        for move in valid_moves:
            total_score = 0
            for _ in range(self.num_simulations):
                simulated_state = state.copy()
                # Use get_next_state instead of apply_move
                next_state = self.game.get_next_state(
                    simulated_state, 
                    move,
                    simulated_state.players[simulated_state.turn_idx]
                )
                total_score += self.simulate_game(next_state)
            scores.append(total_score / self.num_simulations)

        best_move_idx = np.argmax(scores)
        real_hand = state.players[state.turn_idx].hand
        return match_tile_in_real_hand(valid_moves[best_move_idx], real_hand)


    def simulate_game(self, state):
        """Simulates a game from the current state and returns a score."""
        no_progress_turns = 0  # Counter to track consecutive turns with no progress
        max_no_progress_turns = len(state.players) * 2  # Safeguard limit
        max_simulation_steps = 100  # Timeout safeguard
        steps = 0  # Step counter

        while not self.game.is_game_over(state):  # Ensure is_game_over exists
            steps += 1
            if steps > max_simulation_steps:  # Timeout safeguard
                break

            current_player = state.players[state.turn_idx]
            if isinstance(current_player, AI_Player):
                valid_moves = [
                    i[1]
                    for i in zip(
                        [
                            any(condition)
                            for condition in self.game.get_valid_moves(
                                current_player, state.ground
                            )
                        ],
                        current_player.hand,
                    )
                    if i[0]
                ]
                if not valid_moves:  # Skip turn if no valid moves
                    no_progress_turns += 1
                    if no_progress_turns >= max_no_progress_turns:
                        break  # Safeguard to prevent infinite loop
                    state.change_turn()
                    continue
                no_progress_turns = 0  # Reset counter if a valid move is made
                move = random.choice(valid_moves)
                # Use get_next_state instead of apply_move
                state = self.game.get_next_state(
                    state,
                    move,
                    current_player
                )
                state.change_turn()
            else:
                break  # Stop simulation if a human player is encountered
        return self.game.calculate_score(state)
    
class PlacementContext:
    def __init__(self, strategy: AIStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: AIStrategy):
        self.strategy = strategy

    def calc(self, *args):
        return self.strategy.get_domino_placement(*args)
