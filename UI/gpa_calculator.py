from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import sys
import os

# Add the inference_engine directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'inference_engine'))

from course_recommender import load_courses_from_csv

gpa_calculator_bp = Blueprint('gpa_calculator', __name__)

# Grade point mapping
GRADE_POINTS = {
    'A+': 4.0,
    'A': 4.0,
    'A-': 3.7,
    'B+': 3.3,
    'B': 3.0,
    'B-': 2.7,
    'C+': 2.3,
    'C': 2.0,
    'C-': 1.7,
    'D+': 1.3,
    'D': 1.0,
    'F': 0.0
}

@gpa_calculator_bp.route('/gpa_calculator', methods=['GET', 'POST'])
def gpa_calculator():
    """Main route for GPA calculator"""
    if request.method == 'GET':
        # Load courses for the form
        try:
            courses = load_courses_from_csv()
        except:
            courses = []
        return render_template('gpa_calculator.html', courses=courses, grade_points=GRADE_POINTS)
    
    elif request.method == 'POST':
        try:
            # Get form data
            course_codes = request.form.getlist('course_codes')
            course_codes_hidden = request.form.getlist('course_codes_hidden')
            grades = request.form.getlist('grades')
            credit_hours = request.form.getlist('credit_hours')
            
            # Use hidden values if available, otherwise use visible values
            final_course_codes = []
            for i in range(len(course_codes)):
                if i < len(course_codes_hidden) and course_codes_hidden[i]:
                    final_course_codes.append(course_codes_hidden[i])
                elif course_codes[i]:
                    final_course_codes.append(course_codes[i])
            
            # Calculate GPA
            total_grade_points = 0
            total_credits = 0
            course_details = []
            
            # Load courses for credit hour lookup
            try:
                courses = load_courses_from_csv()
                course_lookup = {course['course_code']: course for course in courses}
            except:
                course_lookup = {}
            
            for i in range(len(final_course_codes)):
                if final_course_codes[i] and i < len(grades) and grades[i]:
                    # Always get credit hours from database for selected courses
                    if final_course_codes[i] in course_lookup:
                        credits = float(course_lookup[final_course_codes[i]]['credit_hours'])
                    elif i < len(credit_hours) and credit_hours[i]:
                        credits = float(credit_hours[i])
                    else:
                        credits = 3.0  # Default credit hours
                    
                    grade_point = GRADE_POINTS.get(grades[i], 0.0)
                    course_grade_points = grade_point * credits
                    
                    total_grade_points += course_grade_points
                    total_credits += credits
                    
                    course_details.append({
                        'course_code': final_course_codes[i],
                        'course_name': course_lookup.get(final_course_codes[i], {}).get('course_name', 'Unknown Course'),
                        'grade': grades[i],
                        'credit_hours': round(credits, 1),
                        'grade_points': round(grade_point, 2),
                        'total_points': round(course_grade_points, 2)
                    })
            
            # Calculate GPA
            if total_credits > 0:
                gpa = total_grade_points / total_credits
            else:
                gpa = 0.0
            
            # Load courses for the form again
            try:
                courses = load_courses_from_csv()
            except:
                courses = []
            
            return render_template('gpa_calculator.html', 
                                 courses=courses,
                                 grade_points=GRADE_POINTS,
                                 gpa_result={
                                     'gpa': round(gpa, 2),
                                     'total_credits': round(total_credits, 1),
                                     'total_grade_points': round(total_grade_points, 2),
                                     'course_details': course_details
                                 })
        
        except Exception as e:
            flash(f"Error calculating GPA: {str(e)}", "error")
            try:
                courses = load_courses_from_csv()
            except:
                courses = []
            return render_template('gpa_calculator.html', courses=courses, grade_points=GRADE_POINTS)

@gpa_calculator_bp.route('/api/gpa_calculate', methods=['POST'])
def api_gpa_calculate():
    """API endpoint for GPA calculation"""
    try:
        data = request.get_json()
        
        total_grade_points = 0
        total_credits = 0
        
        for course in data['courses']:
            credits = float(course['credit_hours'])
            grade_point = GRADE_POINTS.get(course['grade'], 0.0)
            total_grade_points += grade_point * credits
            total_credits += credits
        
        gpa = total_grade_points / total_credits if total_credits > 0 else 0.0
        
        return jsonify({
            'success': True,
            'gpa': round(gpa, 2),
            'total_credits': round(total_credits, 1),
            'total_grade_points': round(total_grade_points, 2)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400 