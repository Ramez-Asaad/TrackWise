from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from UI.course_db import get_all_courses, get_course_by_code, add_course, update_course, delete_course

kbeditor_bp = Blueprint('kbeditor', __name__)

class KnowledgeBaseEditor:
    def __init__(self):
        self.headers = ["course_code", "course_name", "description", "prerequisites", "corequisites", "credit_hours", "semester_offered"]
        self.courses = self.load_knowledge_base()

    def load_knowledge_base(self):
        return get_all_courses()

    def add_course(self, course_data):
        return add_course(course_data)

    def update_course(self, course_code, course_data):
        return update_course(course_code, course_data)

    def delete_course(self, course_code):
        return delete_course(course_code)

    def get_course(self, course_code):
        return get_course_by_code(course_code)

# Initialize the knowledge base editor
kb_editor = KnowledgeBaseEditor()

@kbeditor_bp.route('/admin')
def index():
    courses = kb_editor.load_knowledge_base()
    return render_template('admin.html', courses=courses, headers=kb_editor.headers)

@kbeditor_bp.route('/admin/add_course', methods=['POST'])
def add_course_route():
    try:
        course_data = {
            'course_code': request.form.get('course_code'),
            'course_name': request.form.get('course_name'),
            'description': request.form.get('description', ''),
            'prerequisites': [p.strip() for p in request.form.get('prerequisites', '').split(',') if p.strip()],
            'corequisites': [c.strip() for c in request.form.get('corequisites', '').split(',') if c.strip()],
            'credit_hours': int(request.form.get('credit_hours', 0)),
            'semester_offered': request.form.get('semester_offered', '')
        }
        
        if kb_editor.add_course(course_data):
            flash('Course added successfully!', 'success')
        else:
            flash('Failed to add course.', 'error')
            
    except Exception as e:
        flash(f'Error adding course: {str(e)}', 'error')
        
    return redirect(url_for('kbeditor.index'))

@kbeditor_bp.route('/admin/update_course/<course_code>', methods=['POST'])
def update_course_route(course_code):
    try:
        course_data = {
            'course_name': request.form.get('course_name'),
            'description': request.form.get('description', ''),
            'prerequisites': [p.strip() for p in request.form.get('prerequisites', '').split(',') if p.strip()],
            'corequisites': [c.strip() for c in request.form.get('corequisites', '').split(',') if c.strip()],
            'credit_hours': int(request.form.get('credit_hours', 0)),
            'semester_offered': request.form.get('semester_offered', '')
        }
        
        if kb_editor.update_course(course_code, course_data):
            flash('Course updated successfully!', 'success')
        else:
            flash('Failed to update course.', 'error')
            
    except Exception as e:
        flash(f'Error updating course: {str(e)}', 'error')
        
    return redirect(url_for('kbeditor.index'))

@kbeditor_bp.route('/admin/delete_course/<course_code>', methods=['POST'])
def delete_course_route(course_code):
    try:
        if kb_editor.delete_course(course_code):
            flash('Course deleted successfully!', 'success')
        else:
            flash('Failed to delete course.', 'error')
            
    except Exception as e:
        flash(f'Error deleting course: {str(e)}', 'error')
        
    return redirect(url_for('kbeditor.index'))

@kbeditor_bp.route('/admin/get_course/<course_code>')
def get_course_route(course_code):
    course = kb_editor.get_course(course_code)
    if course:
        return jsonify(course)
    else:
        return jsonify({'error': 'Course not found'}), 404