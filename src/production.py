class Plant:
    def __init__(self, name, base_production, attacked=False):
        self.name = name
        self.base_production = base_production
        self.attacked = attacked

    def production_per_second(self):
        #Returns total leafs produced per second.
        multiplier = 1.0
        if self.attacked:
            multiplier = 0.8
        return self.base_production * self.quantity * multiplier
    def isAttacked(self, state):
        self.attacked = state
    # Convert the plant data to a dict that JSON can save
    def to_dict(self):
        return {
            "name": self.name,
            "base_production": self.base_production,
            "attacked": self.attacked,
            "quantity": self.quantity
        }

    # Restore a plant from saved JSON data
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            base_production=data["base_production"],
            attacked=data["attacked"],
            quantity=data["quantity"],
        )
