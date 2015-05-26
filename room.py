class Room(object):
    def __init__(self, capacity=0, penalty=0):
        self.capacity = capacity
        self.penalty = penalty

    def __repr__(self):
        return 'Room(capacity: {}, penalty: {})'.format(self.capacity, self.penalty)
