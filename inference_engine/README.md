# Course Recommendation Inference Engine

This is a rule-based inference engine for recommending courses based on student information and course requirements. The engine uses the Experta library to implement expert system rules for course recommendations.

## Features

- Credit Limit Rule: Caps total credits based on CGPA
- Prerequisite Rule: Only recommends courses if all prerequisites are passed
- Co-requisite Rule: Ensures co-requisites are either previously passed or included in recommendations
- Failed Course Priority Rule: Prioritizes failed courses if prerequisites are met
- Semester Availability Rule: Recommends only courses offered in the upcoming semester
- Track Requirement Rule: Ensures recommendations align with the AI track requirements

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Import the course recommender:
```python
from course_recommender import get_course_recommendations
```

2. Call the function with student information:
```python
recommendations = get_course_recommendations(
    student_cgpa=3.2,
    passed_courses=['CSE014', 'CSE015'],
    failed_courses=['CSE111'],
    current_semester='Fall',
    csv_path='path/to/courses.csv'
)
```

## Example

See `example.py` for a complete example of how to use the inference engine.

## Rules Implementation

The inference engine implements the following rules:

1. **Credit Limit Rule**: Based on CGPA:
   - CGPA ≥ 3.5: 21 credits
   - CGPA ≥ 3.0: 18 credits
   - CGPA ≥ 2.5: 15 credits
   - CGPA < 2.5: 12 credits

2. **Prerequisite Rule**: Checks if all prerequisites for a course have been passed

3. **Co-requisite Rule**: Ensures co-requisites are either passed or included in recommendations

4. **Failed Course Priority**: Prioritizes failed courses if prerequisites are met

5. **Semester Availability**: Only recommends courses offered in the current semester

## Data Format

The course data should be provided in a CSV file with the following columns:
- course_code
- course_name
- prerequisites
- corequisites
- credit_hours
- semester_offered 