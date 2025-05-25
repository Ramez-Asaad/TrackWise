from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sys
import os

# Add the inference_engine directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'inference_engine'))

from course_recommender import get_course_recommendations, load_courses_from_csv

inference_engine_bp = Blueprint('inference_engine', __name__)

@inference_engine_bp.route('/course_recommendations', methods=['GET', 'POST'])
def course_recommendations():
    """Main route for course recommendations"""
    if request.method == 'GET':
        # Load courses for the form
        courses = load_courses_from_csv('Data.csv')
        return render_template('course_recommendations.html', courses=courses)
    
    elif request.method == 'POST':
        try:
            # Get form data
            cgpa = float(request.form.get('cgpa', 0))
            current_semester = request.form.get('semester', 'Fall')
            academic_year = int(request.form.get('academic_year', 0))
            
            # Handle multiple selections for passed and failed courses
            passed_courses = request.form.getlist('completed_courses')
            failed_courses = request.form.getlist('failed_courses')
            
            # Get recommendations
            recommendations = get_course_recommendations(
                student_cgpa=cgpa,
                passed_courses=passed_courses,
                failed_courses=failed_courses,
                current_semester=current_semester,
                csv_path='Data.csv',
                academic_year=academic_year
            )
            
            # Load all courses for display
            courses = load_courses_from_csv('Data.csv')
            
            return render_template('course_recommendations.html', 
                                 courses=courses,
                                 recommendations=recommendations,
                                 student_data={
                                     'cgpa': cgpa,
                                     'semester': current_semester,
                                     'academic_year': academic_year,
                                     'passed_courses': passed_courses,
                                     'failed_courses': failed_courses
                                 })
        
        except Exception as e:
            flash(f"Error generating recommendations: {str(e)}", "error")
            courses = load_courses_from_csv('Data.csv')
            return render_template('course_recommendations.html', courses=courses)

@inference_engine_bp.route('/api/recommendations', methods=['POST'])
def api_recommendations():
    """API endpoint for getting course recommendations"""
    try:
        data = request.get_json()
        
        recommendations = get_course_recommendations(
            student_cgpa=data['cgpa'],
            passed_courses=data['passed_courses'],
            failed_courses=data['failed_courses'],
            current_semester=data['current_semester'],
            csv_path='Data.csv',
            academic_year=data.get('academic_year')  # Optional parameter
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400 