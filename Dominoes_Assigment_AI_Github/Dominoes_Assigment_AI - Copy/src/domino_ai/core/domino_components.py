from typing import List, Tuple


class Domino:
    """Domino
    representing Domino tile. And providing some useful functionalites.
    """

    def __init__(self, left: int, right: int, color=None):
        self.left = left
        self.right = right
        self.color = color

    def __repr__(self):
        return f"[{self.left} | {self.right}]"

    def get_ground_tile(self):
        """returns string representation of how domino tile is positioned on wooden board.

        Returns:
            str: string representation of domino
        """
        vertical = True if self.left == self.right else False
        return self.get_domino(vertical)

    def get_domino(self, vertical=True):
        if vertical:
            return f"""
┌─┐
{self.right}
├ o ┤
{self.left}
└─┘
"""
        else:
            # return f" [{self.left}|{self.right}] "
            return f"""┌─┬─┐
{self.left}   o   {self.right}
└─┴─┘"""

    def flip(self, inplace=False):
        """Flip the domino tile."""
        if inplace:
            self.left, self.right = self.right, self.left
            return self
        else:
            return Domino(self.right, self.left)

    def count_tile(self):
        """Count the number of pips(dots) in the domino tile."""
        return self.left + self.right

    def __hash__(self):
        """unifying representation of dominos with same right and left. i.e Domino(1,3) equals Domino(3,1)"""
        return hash(frozenset((self.left, self.right)))

    def __eq__(self, other):
        if isinstance(other, Domino):
            return {self.left, self.right} == {other.left, other.right}
        return False

    def __contains__(self, item):
        return item in (self.left, self.right)

    def is_double(self):
        return self.right == self.left


type_Hand = List[Domino]


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []  # Ensure hand is always initialized as a list
        self.score = 0
        self.conditions = []

    def set_hand(self, tiles):
        """Sets the player's hand."""
        self.hand = tiles if tiles else []  # Ensure hand is a list, even if tiles is None

    def append_tile_to_hand(self, tile):
        """Appends a tile to the player's hand."""
        if self.hand is None:  # Safeguard against None
            self.hand = []
        self.hand.append(tile)

    def count_hand(self):
        """Counts the total value of tiles in the player's hand."""
        if self.hand is None:  # Safeguard against None
            return 0
        return sum([tile.count_tile() for tile in self.hand])

    def remove_tile_from_hand(self, tile: Domino):
        self.hand.remove(tile)

    def __repr__(self):
        return f"{self.name}: {self.hand}"


class AI_Player(Player):
    def __init__(self, name: str, ai_type: str = "default"):
        """Initializes an AI player with a specific AI type.

        Args:
            name (str): The name of the AI player.
            ai_type (str): The type of AI logic to use (e.g., "ai1", "ai2").
        """
        super().__init__(name)
        self.ai_type = ai_type  # Store the AI type for this player
        self.memory = None

    def set_memory(self, memory):
        self.memory = memory


def check_play(ground_tiles: List[Domino], tile: Domino) -> Tuple[bool, bool]:
    """Checks the availability of a domino being played in the current ground position.

    Args:
        ground_tiles (List[Domino]): List of Domino (ground).
        tile (Domino): Tile to be checked.

    Returns:
        Tuple[bool, bool]: Represents the ability to play the tile on (left) or (right) side of the ground tiles.
    """
    if not ground_tiles:
        return True, False

    # Check right side
    r = ground_tiles[-1].right == tile.left or ground_tiles[-1].right == tile.right

    # Check left side
    l = ground_tiles[0].left == tile.right or ground_tiles[0].left == tile.left

    # Flip the tile in-place only if needed
    if r and ground_tiles[-1].right == tile.right:
        tile.flip(inplace=True)
    elif l and ground_tiles[0].left == tile.left:
        tile.flip(inplace=True)

    return l, r


def generate_domino_set(num_tiles=7):
    """generating domino set

    Args:
        num_tiles (int, optional): maximum number of pips. Defaults to 7.

    Returns:
        List[Domino]: domino set
    """
    return [Domino(i, j) for i in range(num_tiles) for j in range(i, num_tiles)]


def count_hand(hand):
    return sum([tile.count_tile() for tile in hand])


def orient_if_needed(ground_l, ground_r, tile: Domino, direction: str):
    """

    Args:
        ground_l (int): left side of the ground tiles
        ground_r (int): right side of the ground tiles
        tile (Domino): domino tile
        direction (str): what side should tile be placed (left or right)

    Returns:
        Domino: same domino tile, oriented before placement
    """
    ground = ground_r if direction == "r" else ground_l
    if direction == "r":
        if not ground == tile.left:
            tile.flip(inplace=True)
    else:
        if not ground == tile.right:
            tile.flip(inplace=True)
    return tile


if __name__ == "__main__":
    # players = [Player("abdo"), Player("mohammed")]
    # d = generate_domino_set()
    # players[0].set_hand(d[:7])
    # players[1].set_hand(d[7:14])

    # player_types = ["player", "ai 1", "ai 2", "ai 3", "player 4"]
    # players = [(Player(p) if "player" in p else AI_Player(p)) for p in player_types]
    # for p in players:
    #     print(type(p))

    # d = Domino(1, 2)
    # print(4 in d)
    d1 = Domino(0, 0)
    d2 = Domino(0, 0)
    print(d1 == d2)
    print(hash(d1))
    print(hash(d2))
    pass
