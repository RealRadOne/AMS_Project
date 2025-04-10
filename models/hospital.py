class Hospital:
    def __init__(self, name, location):
        self.name = name
        self.location = location

    def __str__(self):
        return f"Hospital(name={self.name}, location={self.location})"