class Exam(object):
    def __init__(self, duration=0, students=[]):
        self.duration = duration
        self.students = students

    def __repr__(self):
        return 'Exam(duration: {}, students: {})'.format(self.duration, self.students)
