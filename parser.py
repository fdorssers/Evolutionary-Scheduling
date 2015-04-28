

def parse_courses(f):
    nr_exams = int(''.join(x for x in f.readline() if x.isdigit()))
    exam_students = {}
    exam_lengths = {}
    for i in range(nr_exams):
        vals = list(map(int, f.readline().split((','))))
        exam_students[i] = vals[1:]
        exam_lengths[i] = vals[0]
    return nr_exams, exam_students, exam_lengths


def parse_periods(f):
    nr_periods = int(''.join(x for x in f.readline() if x.isdigit()))
    period_date = {}
    period_start = {}
    period_length = {}
    period_penalty = {}
    for i in range(nr_periods):
        vals = f.readline().split((','))
        period_date[i] = vals[0]
        period_start[i] = vals[1]
        period_length[i] = vals[2]
        period_penalty[i] = vals[3]
    return nr_periods, period_date, period_start, period_length, period_penalty


def main():
    with open('data/exam_comp_set1.exam') as f:
        parse_courses(f)
        parse_periods(f)

if __name__ == "__main__":
    main()
