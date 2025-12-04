import math
class Plant:
    def __init__(self, name, base_production, base_cost):
        self.name = name
        self.base_production = base_production
        self.base_cost = base_cost
        self.quantity = 0 #start with 0 owned
        self.attacked = False

    def getProduction(self):
        #Returns total leafs produced per second, before global modifiers
        multiplier = 1.0
        if self.attacked:
            multiplier = 0.8
        return self.base_production * self.quantity * multiplier
    def isAttacked(self, state):
        self.attacked = state

    def getCurrentCost(self):
        #Calculate cost: increases by 15% for every one owned.
        return int(self.base_cost * (1.15 ** self.quantity))
    
    def buy(self):
        self.quantity += 1

    # Convert the plant data to a dict that JSON can save
    def toDict(self):
        return {
            "name": self.name,
            "base_production": self.base_production,
            "attacked": self.attacked,
        }

    # Restore a plant from saved JSON data
    @classmethod
    def fromDict(cls, data):
        return cls(
            name=data["name"],
            base_production=data["base_production"],
            attacked=data["attacked"],
        )
    
class Upgrade:
    def __init__(self, name, cost, multiplier_bonus, description):
        self.name = name
        self.cost = cost
        self.multiplier_bonus = multiplier_bonus # e.g., 0.10 for +10%
        self.description = description
        self.purchased = False

    def buy(self):
        self.purchased = True
