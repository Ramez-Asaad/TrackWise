from experta import *
import pandas as pd
from typing import List, Dict, Set
import sys
import os

# Add the UI directory to the path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ui_dir = os.path.join(current_dir, 'UI')
if ui_dir not in sys.path:
    sys.path.insert(0, ui_dir)

from course_db import get_all_courses

# Study plan mapping for course prioritization
STUDY_PLAN = {
    # First Year (Semesters 1-2)
    1: {
        'Fall': ['MAT111', 'PHY211', 'CSE014', 'LAN021', 'LAN011', 'LAN114'],  # UC1, UC2
        'Spring': ['MAT112', 'MAT131', 'CSE015', 'CSE315', 'LAN022', 'LIB116']  # UC3
    },
    
    # Second Year (Semesters 3-4)
    2: {
        'Fall': ['MAT212', 'MAT231', 'CSE111', 'CSE131', 'AIE111', 'LAN112'],  # UC4
        'Spring': ['MAT312', 'CSE132', 'CSE221', 'CSE281', 'AIE121', 'AIE191', 'GEO217']
    },
    
    # Third Year (Semesters 5-6)
    3: {
        'Fall': ['CSE233', 'CSE251', 'CSE261', 'AIE231', 'AIE323', 'PSC101'],  # UC5
        'Spring': ['CSE112', 'AIE212', 'AIE213', 'AIE241', 'AIE292', 'MGT301']  # E1
    },
    
    # Fourth Year (Semesters 7-8)
    4: {
        'Fall': ['CSE363', 'AIE322', 'AIE332', 'AIE493'],  # E2, UC6
        'Spring': ['AIE425', 'AIE314', 'AIE494']  # E3, UC7, UE3
    }
}

# Define university requirement course categories
UNIVERSITY_REQUIREMENTS = {
    'MANDATORY_ZERO_CREDIT': ['LAN021', 'LAN022', 'CSE011'],
    'COMPULSORY_TWO_CREDIT': [
        'LAN011', 'LAN114', 'MGT301', 'LAN112', 'GEO217',
        'PSC101', 'LIB116'
    ],
    'ELECTIVE_COURSES': {
        'LAW_ECONOMICS_MANAGEMENT': [
            'PSC102', 'PSC111', 'MGT101', 'ACC101', 'ECO205', 'MGT102'
        ],
        'LANGUAGES': [
            'LAN111', 'MEC013', 'LAN120', 'LAN130', 'LAN140', 'LAN150'
        ],
        'ART_LITERATURE': [
            'DVA014', 'DVA221', 'LAN113', 'LAN115', 'PYS103', 'SOC105'
        ],
        'SKILLS_GENERAL_CULTURE': [
            'SOC216', 'MGT201', 'ADL123', 'HNU110', 'GEO218'
        ],
        'CIVILIZATION_HISTORY': [
            'HIS111', 'HIS113', 'HIS112', 'ARC010'
        ],
        'GLOBAL_ISSUES': [
            'SOC107', 'PSE207', 'GEO216', 'PSC209', 'GEO114'
        ],
        'TECHNOLOGY': [
            'CSE013', 'MEC014', 'CSE012'
        ]
    }
}

# Define all language courses (including mandatory and elective)
LANGUAGE_COURSES = [
    'LAN021',  # English Language 0
    'LAN022',  # English Language 1
    'LAN111',  # English Language 2
    'LAN011',  # Arabic language
    'LAN010',  # Arabic language for non-native speakers
    'LAN120',  # German language
    'LAN130',  # French language
    'LAN140',  # Chinese language
    'LAN150',  # Ancient Egyptian language
    'LAN170',  # English for specific purposes
    'LAN211',  # Academic Writing
    'MEC013'   # Technical Report Writing
]

def get_course_year(course_code: str) -> int:
    """Helper function to determine which year a course belongs to in the study plan"""
    for year, courses in STUDY_PLAN.items():
        if course_code in courses:
            return year
    return 1  # Default to first year if not found

class Course(Fact):
    """Represents a course in the system"""
    course_code = Field(str, mandatory=True)
    course_name = Field(str, mandatory=True)
    prerequisites = Field(list, default=[])
    corequisites = Field(list, default=[])
    credit_hours = Field(int, mandatory=True)
    semester_offered = Field(str, mandatory=True)
    is_passed = Field(bool, default=False)
    is_failed = Field(bool, default=False)
    description = Field(str, default="")

class Student(Fact):
    """Represents a student's information"""
    cgpa = Field(float, mandatory=True)
    passed_courses = Field(list, default=[])
    failed_courses = Field(list, default=[])
    current_semester = Field(str, mandatory=True)  # 'Fall' or 'Spring'

class EligibleCourse(Fact):
    """Represents a course that is eligible for recommendation"""
    course_code = Field(str, mandatory=True)
    credit_hours = Field(int, mandatory=True)
    is_failed = Field(bool, default=False)

class CourseRecommender(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.recommended_courses = []
        self.total_credits = 0
        self.max_credits = 21  # Default max credits
        self.language_course_recommended = False
        self.university_requirements_count = 0
        self.explanations = []  # Track explanations for recommendations
        self.validation_errors = []  # Track validation errors

    def reset(self):
        """Reset the engine state"""
        super().reset()
        self.recommended_courses = []
        self.total_credits = 0
        self.max_credits = 21  # Default max credits
        self.language_course_recommended = False
        self.university_requirements_count = 0
        self.explanations = []
        self.validation_errors = []

    def add_explanation(self, course_code: str, rule_name: str, reason: str):
        """Add an explanation for a course recommendation"""
        self.explanations.append({
            'course_code': course_code,
            'rule': rule_name,
            'reason': reason
        })

    def add_validation_error(self, error_type: str, details: str):
        """Add a validation error"""
        self.validation_errors.append({
            'type': error_type,
            'details': details
        })

    def validate_course_lists(self, passed_courses: List[str], failed_courses: List[str]) -> bool:
        """Validate course lists for logical consistency"""
        # Check for courses that appear in both passed and failed lists
        duplicate_courses = set(passed_courses) & set(failed_courses)
        if duplicate_courses:
            self.add_validation_error(
                'duplicate_courses',
                f"Course(s) {', '.join(duplicate_courses)} cannot be both passed and failed"
            )
            return False
        return True

    def validate_prerequisites_chain(self, course_lookup: Dict[str, Dict], passed_courses: List[str]) -> bool:
        """Validate that prerequisites chain is logically consistent"""
        valid = True
        for course_code, course_info in course_lookup.items():
            if course_code in passed_courses:
                prereqs = course_info['prerequisites']
                if isinstance(prereqs, list) and prereqs:
                    missing_prereqs = [p for p in prereqs if p not in passed_courses]
                    if missing_prereqs:
                        self.add_validation_error(
                            'missing_prerequisites',
                            f"Course {course_code} is marked as passed but its prerequisites {', '.join(missing_prereqs)} are not"
                        )
                        valid = False
        return valid

    def validate_credit_hours(self, course_lookup: Dict[str, Dict], passed_courses: List[str]) -> bool:
        """Validate that total passed credits is within reasonable bounds"""
        total_credits = sum(course_lookup[code]['credit_hours'] for code in passed_courses if code in course_lookup)
        max_possible_credits = len(STUDY_PLAN) * 2 * 21  # 4 years * 2 semesters * max credits per semester
        if total_credits > max_possible_credits:
            self.add_validation_error(
                'excessive_credits',
                f"Total passed credits ({total_credits}) exceeds maximum possible credits ({max_possible_credits})"
            )
            return False
        return True

    def validate_language_progression(self, passed_courses: List[str]) -> bool:
        """Validate that language courses are taken in correct order"""
        valid = True
        # Check English language progression
        if 'LAN022' in passed_courses and 'LAN021' not in passed_courses:
            self.add_validation_error(
                'invalid_language_progression',
                "English Language 1 (LAN022) is passed but English Language 0 (LAN021) is not"
            )
            valid = False
        if 'LAN111' in passed_courses and 'LAN022' not in passed_courses:
            self.add_validation_error(
                'invalid_language_progression',
                "English Language 2 (LAN111) is passed but English Language 1 (LAN022) is not"
            )
            valid = False
        return valid

    def can_recommend_language_course(self, course_code: str) -> bool:
        """Check if a language course can be recommended"""
        if course_code in LANGUAGE_COURSES:
            return not self.language_course_recommended
        return True

    def can_recommend_university_requirement(self) -> bool:
        """Check if another university requirement can be recommended"""
        return self.university_requirements_count < 2

    def is_university_requirement(self, code: str) -> bool:
        """Check if a course is a university requirement"""
        return (code in UNIVERSITY_REQUIREMENTS['MANDATORY_ZERO_CREDIT'] or
                code in UNIVERSITY_REQUIREMENTS['COMPULSORY_TWO_CREDIT'] or
                any(code in category for category in UNIVERSITY_REQUIREMENTS['ELECTIVE_COURSES'].values()))

    def is_in_study_plan(self, code: str, academic_year: int, semester: str) -> bool:
        """Check if a course is scheduled for the given semester in the study plan"""
        try:
            return code in STUDY_PLAN[academic_year][semester]
        except (KeyError, TypeError):
            return False

    @Rule(
        Student(cgpa=MATCH.cgpa),
        salience=100
    )
    def set_credit_limit(self, cgpa):
        """Sets credit limit based on CGPA"""
        if cgpa >= 3.5:
            self.max_credits = 21
        elif cgpa >= 3.0:
            self.max_credits = 18
        elif cgpa >= 2.5:
            self.max_credits = 15
        else:
            self.max_credits = 12
        self.add_explanation("N/A", "Credit Limit", 
            f"Based on your CGPA of {cgpa:.2f}, your maximum credit limit is set to {self.max_credits} credits.")

    @Rule(
        Student(
            passed_courses=MATCH.passed,
            failed_courses=MATCH.failed,
            current_semester=MATCH.semester
        ),
        Course(
            course_code=MATCH.code,
            course_name=MATCH.name,
            prerequisites=MATCH.prereqs,
            corequisites=MATCH.coreqs,
            credit_hours=MATCH.credits,
            semester_offered=MATCH.offered,
            is_passed=False
        ),
        salience=90
    )
    def evaluate_course_eligibility(self, passed, failed, semester, code, name, prereqs, coreqs, credits, offered):
        """Evaluates if a course is eligible for recommendation"""
        
        # Check prerequisites
        clean_prereqs = [p.strip() for p in prereqs if p.strip()]
        if clean_prereqs:
            prereqs_met = all(prereq in passed for prereq in clean_prereqs)
        else:
            prereqs_met = True
        
        # Check corequisites
        clean_coreqs = [c.strip() for c in coreqs if c.strip()]
        if clean_coreqs:
            coreqs_met = all(coreq in passed for coreq in clean_coreqs)
        else:
            coreqs_met = True
        
        # Check semester availability
        semester_available = (semester == offered)
        
        # If all conditions are met, declare as eligible
        if prereqs_met and coreqs_met and semester_available:
            is_failed_course = code in failed
            self.declare(EligibleCourse(
                course_code=code,
                credit_hours=credits,
                is_failed=is_failed_course
            ))

    @Rule(
        EligibleCourse(
            course_code=MATCH.code,
            credit_hours=MATCH.credits,
            is_failed=True
        ),
        TEST(lambda code: get_course_year(code) <= len(STUDY_PLAN)),
        salience=85  # Higher priority for current or previous year failed courses
    )
    def recommend_current_year_failed_course(self, code, credits):
        """Recommends failed courses from current or previous years first"""
        if code not in self.recommended_courses:
            if self.total_credits + credits <= self.max_credits:
                self.recommended_courses.append(code)
                self.total_credits += credits
                self.add_explanation(code, "Failed Course Priority",
                    f"Recommended {code} as a high-priority failed course from your current/previous year that needs to be retaken.")

    @Rule(
        EligibleCourse(
            course_code=MATCH.code,
            credit_hours=MATCH.credits,
            is_failed=True
        ),
        salience=80  # Lower priority for other failed courses
    )
    def recommend_other_failed_course(self, code, credits):
        """Recommends other failed courses"""
        if code not in self.recommended_courses:
            if self.total_credits + credits <= self.max_credits:
                self.recommended_courses.append(code)
                self.total_credits += credits
                self.add_explanation(code, "Failed Course",
                    f"Recommended {code} as it is a failed course that needs to be retaken.")

    @Rule(
        EligibleCourse(
            course_code=MATCH.code,
            credit_hours=MATCH.credits,
            is_failed=False
        ),
        TEST(lambda code: get_course_year(code) <= len(STUDY_PLAN)),
        salience=75  # Higher priority for current year regular courses
    )
    def recommend_current_year_course(self, code, credits):
        """Recommends regular courses from current year"""
        if code not in self.recommended_courses:
            if self.total_credits + credits <= self.max_credits:
                self.recommended_courses.append(code)
                self.total_credits += credits
                self.add_explanation(code, "Current Year Course",
                    f"Recommended {code} as it is part of your current year's study plan.")

    @Rule(
        EligibleCourse(
            course_code=MATCH.code,
            credit_hours=MATCH.credits,
            is_failed=False
        ),
        salience=70  # Lower priority for other regular courses
    )
    def recommend_other_course(self, code, credits):
        """Recommends other eligible courses"""
        if code not in self.recommended_courses:
            if self.total_credits + credits <= self.max_credits:
                self.recommended_courses.append(code)
                self.total_credits += credits
                self.add_explanation(code, "Additional Course",
                    f"Recommended {code} as an additional course that meets all prerequisites and credit requirements.")

    @Rule(
        Student(cgpa=MATCH.cgpa),
        Course(
            course_code=MATCH.code,
            credit_hours=MATCH.credits,
            is_passed=False
        ),
        TEST(lambda code: code in LANGUAGE_COURSES),
        salience=88
    )
    def recommend_language_course(self, code, credits):
        """Recommends language courses with constraints"""
        if (code not in self.recommended_courses and 
            not self.language_course_recommended and 
            self.can_recommend_university_requirement()):
            
            if self.total_credits + credits <= self.max_credits:
                self.recommended_courses.append(code)
                self.total_credits += credits
                self.language_course_recommended = True
                if self.is_university_requirement(code):
                    self.university_requirements_count += 1
                    
                self.add_explanation(code, "Language Course", 
                    f"Recommended {code} to fulfill your language course requirement for this semester.")

    @Rule(
        Student(cgpa=MATCH.cgpa),
        Course(
            course_code=MATCH.code,
            credit_hours=MATCH.credits,
            is_passed=False
        ),
        TEST(lambda code: code in UNIVERSITY_REQUIREMENTS['MANDATORY_ZERO_CREDIT']),
        salience=95
    )
    def recommend_mandatory_zero_credit_course(self, code, credits):
        """Recommends mandatory zero-credit courses"""
        if code not in self.recommended_courses:
            if (not (code in LANGUAGE_COURSES and self.language_course_recommended) and 
                (not self.is_university_requirement(code) or self.can_recommend_university_requirement())):
                
                self.recommended_courses.append(code)
                if code in LANGUAGE_COURSES:
                    self.language_course_recommended = True
                if self.is_university_requirement(code):
                    self.university_requirements_count += 1
                    
                self.add_explanation(code, "Mandatory Course", 
                    f"Recommended {code} as it is a mandatory zero-credit course required for your degree.")

    @Rule(
        Student(cgpa=MATCH.cgpa),
        Course(
            course_code=MATCH.code,
            credit_hours=MATCH.credits,
            is_passed=False
        ),
        TEST(lambda code: code in UNIVERSITY_REQUIREMENTS['COMPULSORY_TWO_CREDIT']),
        salience=90
    )
    def recommend_compulsory_two_credit_course(self, code, credits):
        """Recommends compulsory two-credit courses"""
        if code not in self.recommended_courses:
            if (not (code in LANGUAGE_COURSES and self.language_course_recommended) and 
                (not self.is_university_requirement(code) or self.can_recommend_university_requirement())):
                
                if self.total_credits + credits <= self.max_credits:
                    self.recommended_courses.append(code)
                    self.total_credits += credits
                    if code in LANGUAGE_COURSES:
                        self.language_course_recommended = True
                    if self.is_university_requirement(code):
                        self.university_requirements_count += 1
                        
                    self.add_explanation(code, "Compulsory Course", 
                        f"Recommended {code} as it is a compulsory two-credit course required for your degree.")

    @Rule(
        Student(cgpa=MATCH.cgpa),
        Course(
            course_code=MATCH.code,
            credit_hours=MATCH.credits,
            is_passed=False
        ),
        TEST(lambda code: any(code in category for category in UNIVERSITY_REQUIREMENTS['ELECTIVE_COURSES'].values())),
        salience=85
    )
    def recommend_elective_course(self, code, credits):
        """Recommends elective courses"""
        if code not in self.recommended_courses:
            if (not (code in LANGUAGE_COURSES and self.language_course_recommended) and 
                (not self.is_university_requirement(code) or self.can_recommend_university_requirement())):
                
                if self.total_credits + credits <= self.max_credits:
                    self.recommended_courses.append(code)
                    self.total_credits += credits
                    if code in LANGUAGE_COURSES:
                        self.language_course_recommended = True
                    if self.is_university_requirement(code):
                        self.university_requirements_count += 1
                        
                    # Find which category this elective belongs to
                    category = next(
                        (cat_name for cat_name, courses in UNIVERSITY_REQUIREMENTS['ELECTIVE_COURSES'].items() 
                         if code in courses),
                        "General"
                    )
                    
                    self.add_explanation(code, "Elective Course", 
                        f"Recommended {code} as an elective course from the {category.replace('_', ' ').title()} category.")

def load_courses_from_csv(csv_path: str = None) -> List[Dict]:
    """Loads course data from database"""
    return get_all_courses()

def get_course_recommendations(
    student_cgpa: float,
    passed_courses: List[str],
    failed_courses: List[str],
    current_semester: str,
    csv_path: str,
    academic_year: int = None
) -> Dict:
    """Gets course recommendations based on student information"""
    engine = CourseRecommender()
    
    # Load courses from CSV
    courses = load_courses_from_csv(csv_path)
    course_lookup = {course['course_code']: course for course in courses}
    
    # Validate input data
    validation_passed = True
    validation_passed &= engine.validate_course_lists(passed_courses, failed_courses)
    validation_passed &= engine.validate_prerequisites_chain(course_lookup, passed_courses)
    validation_passed &= engine.validate_credit_hours(course_lookup, passed_courses)
    validation_passed &= engine.validate_language_progression(passed_courses)
    
    if not validation_passed:
        return {
            'error': 'Validation failed',
            'validation_errors': engine.validation_errors
        }
    
    # Calculate academic year if not provided
    if academic_year is None:
        total_passed = len(passed_courses)
        if total_passed <= 12:
            academic_year = 1
        elif total_passed <= 24:
            academic_year = 2
        elif total_passed <= 36:
            academic_year = 3
        else:
            academic_year = 4
    
    # Reset the engine
    engine.reset()
    
    # Declare student facts with all required fields
    engine.declare(Student(
        cgpa=student_cgpa,
        passed_courses=passed_courses,
        failed_courses=failed_courses,
        current_semester=current_semester
    ))
    
    # Declare course facts with study plan consideration
    for course in courses:
        if course['course_code'] not in passed_courses:
            is_in_plan = engine.is_in_study_plan(
                course['course_code'], 
                academic_year, 
                current_semester
            )
            engine.declare(Course(
                course_code=course['course_code'],
                course_name=course['course_name'],
                prerequisites=course['prerequisites'],
                corequisites=course['corequisites'],
                credit_hours=course['credit_hours'],
                semester_offered=course['semester_offered'],
                is_passed=False,
                is_failed=course['course_code'] in failed_courses,
                description=course['description']
            ))
    
    # Run the engine
    engine.run()
    
    # Sort recommendations based on study plan
    sorted_recommendations = sorted(
        engine.recommended_courses,
        key=lambda code: (
            not engine.is_in_study_plan(code, academic_year, current_semester),  # Study plan courses first
            code in failed_courses,  # Then failed courses
            not engine.is_university_requirement(code)  # Then university requirements
        )
    )
    
    # Prepare detailed recommendations
    detailed_recommendations = []
    failed_recommendations = []
    regular_recommendations = []
    
    for course_code in sorted_recommendations:
        course_info = course_lookup[course_code]
        course_detail = {
            'course_code': course_code,
            'course_name': course_info['course_name'],
            'description': course_info['description'],
            'credit_hours': course_info['credit_hours'],
            'semester_offered': course_info['semester_offered'],
            'prerequisites': course_info['prerequisites'],
            'year': academic_year,
            'is_failed': course_code in failed_courses,
            'is_in_study_plan': engine.is_in_study_plan(course_code, academic_year, current_semester),
            'is_university_requirement': engine.is_university_requirement(course_code)
        }
        
        detailed_recommendations.append(course_detail)
        
        if course_code in failed_courses:
            failed_recommendations.append(course_detail)
        else:
            regular_recommendations.append(course_detail)
    
    return {
        'recommended_courses': sorted_recommendations,
        'detailed_recommendations': detailed_recommendations,
        'failed_recommendations': failed_recommendations,
        'regular_recommendations': regular_recommendations,
        'total_credits': engine.total_credits,
        'max_credits': engine.max_credits,
        'credit_limit_reason': f"CGPA {student_cgpa} allows up to {engine.max_credits} credits",
        'semester': current_semester,
        'academic_year': academic_year,
        'university_requirements_count': engine.university_requirements_count,
        'explanations': engine.explanations
    } 