from src.domino_ai.core.domino_game import DominoGame
from src.domino_ai.ai.ai_stratigies import PlacementContext, MCTSStrategy, RuleBasedStrategy, BlindStrategy

from src.domino_ai.core.utils import load_config
from src.domino_ai.parser import create_parser


def main():

    parser = create_parser()
    args = parser.parse_args()
    config = load_config("src/config.yaml")

    # Update configuration with command-line arguments
    for k, v in args.__dict__.items():
        if v:
            config[k] = v
    
    ai_win_rates = {"ai 1" : 0, "ai 2" : 0, "ai 3" : 0}
    for i in range(300):
        # initial game engine
        game = DominoGame(["mcts", "rule_based", "blind"])
    
        
        placement_contexts = [
            PlacementContext(RuleBasedStrategy(game)),   # AI 1
            PlacementContext(MCTSStrategy(game)),        # AI 2
            PlacementContext(BlindStrategy(game)),       # AI 3
        ]
        
        winner, score = game.casual_game(placement_contexts, config["score"])
        
        ai_win_rates[winner.name] = ai_win_rates[winner.name] + 1
    
    for ai in ai_win_rates:
        print(ai, ai_win_rates[ai])

if __name__ == "__main__":
    main()
    
