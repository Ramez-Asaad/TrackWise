from experta import *
import csv
import io
import os
from flask import Blueprint, render_template, request

kbsystem_bp = Blueprint('kbsystem', __name__)

# Fact for a course
class Course(Fact):
    course_code = Field(str)
    course_name = Field(str)
    description = Field(str)
    prerequisites = Field(list, default=[])
    corequisites = Field(list, default=[])
    credit_hours = Field(int)
    semester_offered = Field(str)

# Fact for a student
class Student(Fact):
    cgpa = Field(float)
    current_credits = Field(int)
    failed_courses = Field(list, default=[])
    completed_courses = Field(list, default=[])

class KBSystem(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.output = []

    @Rule(Student(cgpa=P(lambda x: x < 2.0), current_credits=P(lambda c: c > 12)))
    def cgpa_below_2(self):
        self.output.append("CGPA < 2.0: Max 12 credits allowed.")

    @Rule(Student(cgpa=P(lambda x: 2.0 <= x < 3.0), current_credits=P(lambda c: c > 15)))
    def cgpa_between_2_and_3(self):
        self.output.append("2.0 ≤ CGPA < 3.0: Max 15 credits allowed.")

    @Rule(Student(cgpa=P(lambda x: x >= 3.0), current_credits=P(lambda c: c > 18)))
    def cgpa_above_3(self):
        self.output.append("CGPA ≥ 3.0: Max 18 credits allowed.")

    @Rule(Student(failed_courses=MATCH.failed))
    def retake_failed(self, failed):
        if failed:
            self.output.append(f"Prioritize retaking failed courses: {failed}")

    @Rule(
        AS.student << Student(completed_courses=MATCH.completed),
        Course(course_code=MATCH.code, prerequisites=MATCH.prereqs & P(lambda x: x)),
        TEST(lambda completed, prereqs: not all(prereq.strip() in completed for prereq in prereqs))
    )
    def missing_prereqs(self, code, prereqs, completed):
        missing = [p for p in prereqs if p.strip() not in completed]
        self.output.append(f"Cannot register for {code}: missing prerequisites {missing}")


def load_courses_from_csv(csv_path):
    # Always resolve the path relative to this file's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, csv_path)
    courses = []
    with open(full_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prereqs = [p.strip() for p in row['prerequisites'].split(',')] if row['prerequisites'] else []
            coreqs = [c.strip() for c in row['corequisites'].split(',')] if row['corequisites'] else []
            courses.append(Course(
                course_code=row['course_code'],
                course_name=row['course_name'],
                description=row['description'],
                prerequisites=prereqs,
                corequisites=coreqs,
                credit_hours=int(row['credit_hours']),
                semester_offered=row['semester_offered']
            ))
    return courses

def run_kbsystem_for_student(cgpa, current_credits, completed_courses, failed_courses, csv_path='Data.csv'):
    engine = KBSystem()
    engine.reset()
    student = Student(
        cgpa=cgpa,
        current_credits=current_credits,
        failed_courses=failed_courses,
        completed_courses=completed_courses
    )
    engine.declare(student)
    for course_fact in load_courses_from_csv(csv_path):
        engine.declare(course_fact)
    engine.run()
    return '\n'.join(engine.output)

@kbsystem_bp.route('/student_kbs', methods=['POST'])
def student_kbs():
    cgpa = float(request.form.get('cgpa', 0))
    current_credits = int(request.form.get('current_credits', 0))
    completed_courses = request.form.getlist('completed_courses')
    failed_courses = request.form.getlist('failed_courses')
    policy_feedback = run_kbsystem_for_student(cgpa, current_credits, completed_courses, failed_courses)
    courses = load_courses_from_csv('Data.csv')
    return render_template('student.html', policy_feedback=policy_feedback, courses=courses)

if __name__ == "__main__":
    print("Welcome to the Knowledge-Based System!")
    cgpa = float(input("Enter your CGPA: "))
    current_credits = int(input("Enter your current registered credits: "))
    completed_courses = input("Enter your completed courses (comma-separated course codes): ").split(",")
    completed_courses = [c.strip() for c in completed_courses if c.strip()]
    failed_courses = input("Enter your failed courses (comma-separated course codes): ").split(",")
    failed_courses = [c.strip() for c in failed_courses if c.strip()]

    result = run_kbsystem_for_student(cgpa, current_credits, completed_courses, failed_courses)
    print(result) 