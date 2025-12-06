class SeasonManager:
  def __init__(self):
    self.seasons = ["Spring", "Summer", "Fall"]
    self.current_index = 0
    self.day = 1
    self.days_per_season = 30
    self.year = 1

def update_day(self):
  self.day += 1
  if self.day > self.days_per_season:
    self.day = 1
    self.current_index += 1
    if self.current_index >= len(self.seasons):
      self.current_index = 0
      self.year += 1
      return "prestige"
  return None

def get_current_season(self):
  return self.seasons[self.current_index]

def get_day(self):
  return self.day

def get_year(self):
  return self.year
