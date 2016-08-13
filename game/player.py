
class Player(object):
    """
    Represents a player in Terraria
    """

    def __init__(self):
        super(Player, self).__init__()

        self.skinVarient = 0
        self.hair = None
        self.name = ""
        self.hairDye = ""
        self.hideVisuals = 0
        self.hideVisuals2 = 0
        self.hideMisc = 0
        self.hairColor = None
        self.eyeColor = None
        self.shoeColor = None
        self.life = 0
        self.lifeMax = 0
        self.isMale = False
        self.skinColor = None
        self.shirtColor = None
        self.underShirtColor = None
        self.pantsColor = None
        self.difficulty = 0
        self.mana = 0
        self.manaMax = 0
        self.spawn = (-1, -1)
