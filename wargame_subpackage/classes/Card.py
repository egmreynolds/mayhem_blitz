class Card:
    ranks = ("Guard", "Priest", "Baron", "Handmaid", "Prince", "Curse", "King", "Goblin", "Lich", "Warlord", "Orc", "Slime", "Skeleton", "Soldier", "Captain", "Matyr", "SKIP")
    values = {"Guard" : 1, "Priest" : 2, "Baron" : 3, "Handmaid" : 4, "Prince" : 5, "Curse" : 0, "King" : 6, "Goblin" : 1, "Lich" : 4, "Warlord" : 5, "Slime" : 2, "Orc" : 3, "Skeleton" : 1, "Soldier" : 2, "Captain" : 3, "Matyr" : 2, "SKIP" : -1}
    """
    Need to differentiate attack power from cost.
    """

    def __init__(self, rank):
        self.rank = rank
        self.value = Card.values[self.rank]
    
    def __str__(self):
        return f"{self.rank}_{self.value}"
    
    def __eq__(self, other): 
        if not isinstance(other, Card):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.rank == other.rank and self.value == other.value
    
    def __lt__(self, other):
        return self.value < other.value
    
    def __gt__(self, other):
        return self.value > other.value    
    
    def __hash__(self):
        # necessary for instances to behave sanely in dicts and sets.
        return hash((self.rank, self.value))