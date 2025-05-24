from flask import Blueprint, render_template, request, redirect, url_for
import csv
import os
import time

kbeditor_bp = Blueprint('kbeditor', __name__)

class KnowledgeBaseEditor:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), "Data.csv")
        self.file_path = file_path
        self.headers = ["course_code", "course_name", "description", "prerequisites", "corequisites", "credit_hours", "semester_offered"]
        self.courses = self.load_knowledge_base()

    def load_knowledge_base(self):
        courses = []
        if not os.path.exists(self.file_path):
            print(f"Error: {self.file_path} does not exist.")
            return courses
        print(f"Loading {self.file_path}...")
        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                csv_headers = [h.strip().lower() if h else '' for h in reader.fieldnames]
                expected_headers = [h.lower() for h in self.headers]
                print(f"CSV headers: {reader.fieldnames}")
                print(f"Expected headers: {self.headers}")
                if csv_headers != expected_headers:
                    print("Warning: CSV headers do not match expected format. Using default headers.")
                    return []
                for row in reader:
                    print(f"Processing row: {row}")  # Debug
                    try:
                        # Strip whitespace and check if credit_hours is a valid integer
                        credit_str = row["credit_hours"].strip() if row["credit_hours"] else "0"
                        if "." in credit_str:
                            print(f"Skipping {row['course_code']}: credit_hours ({credit_str}) contains decimal - must be an integer")
                            continue
                        credit = int(credit_str)
                        if credit <= 0:
                            print(f"Skipping {row['course_code']}: credit_hours ({credit}) must be a positive integer")
                            continue
                        row["prerequisites"] = row["prerequisites"].split(",") if row["prerequisites"] else []
                        row["corequisites"] = row["corequisites"].split(",") if row["corequisites"] else []
                        row["credit_hours"] = credit  # Store as integer
                        row["last_modified"] = None  # Initialize as None (not stored in CSV)
                        courses.append(row)
                        print(f"Added course: {row['course_code']}")
                    except ValueError:
                        print(f"Skipping {row['course_code']}: invalid credit_hours ({credit_str}) - must be an integer")
                        continue
            print(f"Loaded {len(courses)} courses")
        except Exception as e:
            print(f"Error reading CSV: {e}. Starting with empty knowledge base.")
        return courses

    def save_knowledge_base(self):
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.headers)
                writer.writeheader()
                for course in self.courses:
                    course_copy = course.copy()
                    course_copy["prerequisites"] = ",".join(course["prerequisites"])
                    course_copy["corequisites"] = ",".join(course["corequisites"])
                    course_copy["credit_hours"] = str(course["credit_hours"])  # Save as integer string
                    course_copy.pop("last_modified", None)  # Remove runtime field
                    writer.writerow(course_copy)
            return "Knowledge base saved successfully."
        except Exception as e:
            return f"Error saving knowledge base: {e}"

    def add_course(self, course_code, course_name, description, prerequisites, corequisites, credit, semester):
        if not course_code or not course_name or not description or not semester:
            return "course_code, course_name, description, and semester are required."
        try:
            credit = int(credit)  # Convert to integer
            if credit <= 0:
                return "credit must be a positive integer."
        except ValueError:
            return "credit must be a positive integer."
        if semester not in ["Fall", "Spring", "Both"]:
            return "semester must be 'Fall', 'Spring', or 'Both'."
        if any(course["course_code"] == course_code for course in self.courses):
            return f"Course with code {course_code} already exists."

        course = {
            "course_code": course_code,
            "course_name": course_name,
            "description": description,
            "prerequisites": prerequisites.split(",") if prerequisites else [],
            "corequisites": corequisites.split(",") if corequisites else [],
            "credit_hours": credit,  # Store as integer
            "semester_offered": semester,
            "last_modified": time.time()  # Add timestamp
        }
        self.courses.append(course)
        return self.save_knowledge_base()

    def edit_course(self, course_code, field, new_value):
        for course in self.courses:
            if course["course_code"] == course_code:
                if field not in self.headers:
                    return f"Invalid field {field}. Valid fields: {self.headers}"
                if field == "credit_hours":
                    try:
                        new_value = int(new_value)  # Convert to integer
                        if new_value <= 0:
                            return "credit_hours must be a positive integer."
                    except ValueError:
                        return "credit_hours must be a positive integer."
                if field == "semester_offered" and new_value not in ["Fall", "Spring", "Both"]:
                    return "semester_offered must be 'Fall', 'Spring', or 'Both'."
                if field in ["prerequisites", "corequisites"]:
                    new_value = new_value.split(",") if new_value else []
                course[field] = new_value
                course["last_modified"] = time.time()  # Update timestamp
                return self.save_knowledge_base()
        return f"Course {course_code} not found."

    def delete_course(self, course_code):
        for i, course in enumerate(self.courses):
            if course["course_code"] == course_code:
                self.courses.pop(i)
                return self.save_knowledge_base()
        return f"Course {course_code} not found."

    def view_courses(self):
        return self.courses

# Initialize editor
editor = KnowledgeBaseEditor()

@kbeditor_bp.route('/admin')
def index():
    courses = editor.view_courses()
    message = request.args.get('message', '')
    print(f"Rendering index with {len(courses)} courses: {[course['course_code'] for course in courses]}")  # Debug
    return render_template('admin.html', courses=courses, message=message, now=time.time())

@kbeditor_bp.route('/add', methods=['POST'])
def add():
    course_code = request.form.get('course_code')
    course_name = request.form.get('course_name')
    description = request.form.get('description')
    prerequisites = request.form.get('prerequisites')
    corequisites = request.form.get('corequisites')
    credit = request.form.get('credit')
    semester = request.form.get('semester')
    message = editor.add_course(course_code, course_name, description, prerequisites, corequisites, credit, semester)
    return redirect(url_for('kbeditor.index', message=message))

@kbeditor_bp.route('/edit', methods=['POST'])
def edit():
    course_code = request.form.get('course_code')
    field = request.form.get('field')
    new_value = request.form.get('new_value')
    message = editor.edit_course(course_code, field, new_value)
    return redirect(url_for('kbeditor.index', message=message))

@kbeditor_bp.route('/delete', methods=['POST'])
def delete():
    course_code = request.form.get('course_code')
    message = editor.delete_course(course_code)
    return redirect(url_for('kbeditor.index', message=message))