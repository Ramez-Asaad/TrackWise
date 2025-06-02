from course_recommender import get_course_recommendations, load_courses_from_csv

def main():
    # Example student information
    student_cgpa = 3.2
    passed_courses = ['CSE014', 'CSE015', 'MAT111', 'MAT112']
    failed_courses = ['CSE111']
    current_semester = 'Spring'

    # Load and print available courses
    print("\nAvailable Courses:")
    print("-----------------")
    courses = load_courses_from_csv()
    for course in courses:
        print(f"{course['course_code']}: {course['course_name']} ({course['semester_offered']})")

    # Print student information
    print(f"\nStudent Information:")
    print("-------------------")
    print(f"CGPA: {student_cgpa}")
    print(f"Passed Courses: {passed_courses}")
    print(f"Failed Courses: {failed_courses}")
    print(f"Current Semester: {current_semester}")

    # Get course recommendations
    recommended_courses = get_course_recommendations(
        student_cgpa=student_cgpa,
        passed_courses=passed_courses,
        failed_courses=failed_courses,
        current_semester=current_semester,
        csv_path=None
    )

    # Print recommendations
    print(f"\nCourse Recommendations for CGPA {student_cgpa}:")
    print("----------------------------------------")
    if recommended_courses:
        for course in recommended_courses:
            course_info = next((c for c in courses if c['course_code'] == course), None)
            if course_info:
                print(f"- {course}: {course_info['course_name']} ({course_info['credit_hours']} credits)")
    else:
        print("No courses recommended. This might be due to:")
        print("1. No courses available in the current semester")
        print("2. Prerequisites not met")
        print("3. Credit limit reached")
        print("4. No failed courses to prioritize")

if __name__ == "__main__":
    main() 