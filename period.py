class Period(object):

    def __init__(self, date="", start="", duration=0, penalty=0):
        self.date = date
        self.start = start
        self.duration = duration
        self.penalty = penalty

    def __repr__(self):
        return 'date: {}, start: {}, duration: {}, penalty: {}'.format(self.date, self.start, self.duration, self.penalty)
