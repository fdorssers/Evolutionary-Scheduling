from exam import Exam
from period import Period


def parse_int_from_header(header):
    return int(''.join(x for x in header if x.isdigit()))


def parse_exams(f):
    nr_exams = parse_int_from_header(f.readline())
    exams = {}
    for i in range(nr_exams):
        vals = list(map(int, f.readline().split((','))))
        exams[i] = Exam(vals[0], vals[1:])
    return exams


def parse_periods(f):
    nr_periods = parse_int_from_header(f.readline())
    periods = {}
    for i in range(nr_periods):
        vals = f.readline().split((','))
        periods[i] = Period(vals[0], vals[1], vals[2], vals[3])
    return periods


def main():
    periods = {}
    with open('data/exam_comp_set1.exam') as f:
        exams = parse_exams(f)
        periods = parse_periods(f)

if __name__ == "__main__":
    main()
