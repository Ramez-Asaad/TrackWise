from UI.DB import get_db_client
import pandas as pd
from typing import List, Dict, Optional

# Initialize MongoDB client
client = get_db_client()
if client:
    db = client['trackwise']
else:
    db = None

def init_course_collection():
    """Initialize the courses collection with required indexes"""
    if client:
        try:
            # Create unique index on course_code
            db.courses.create_index('course_code', unique=True)
            print("Course collection initialized successfully")
        except Exception as e:
            print(f"Error creating course collection indexes: {e}")

def migrate_courses_from_csv(csv_path: str) -> bool:
    """Migrate course data from CSV to MongoDB"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Convert DataFrame to list of dictionaries
        courses = []
        for _, row in df.iterrows():
            # Clean up prerequisites and corequisites
            prereqs_str = str(row['prerequisites']) if pd.notna(row['prerequisites']) else ""
            coreqs_str = str(row['corequisites']) if pd.notna(row['corequisites']) else ""
            
            # Parse prerequisites
            if prereqs_str == "No Prerequisites" or prereqs_str == "nan":
                prerequisites = []
            else:
                prerequisites = [p.strip() for p in prereqs_str.split(',') if p.strip()]
            
            # Parse corequisites
            if coreqs_str == "nan" or not coreqs_str.strip():
                corequisites = []
            else:
                corequisites = [c.strip() for c in coreqs_str.split(',') if c.strip()]
            
            course = {
                'course_code': row['course_code'],
                'course_name': row['course_name'],
                'description': str(row['description']) if pd.notna(row['description']) else "",
                'prerequisites': prerequisites,
                'corequisites': corequisites,
                'credit_hours': int(row['credit_hours']),
                'semester_offered': row['semester_offered']
            }
            courses.append(course)
        
        if client:
            # Drop existing courses collection
            db.courses.drop()
            
            # Insert all courses
            result = db.courses.insert_many(courses)
            print(f"Successfully migrated {len(result.inserted_ids)} courses to database")
            return True
        else:
            print("No database connection available")
            return False
            
    except Exception as e:
        print(f"Error migrating courses: {e}")
        return False

def get_all_courses() -> List[Dict]:
    """Get all courses from the database"""
    try:
        if client:
            courses = list(db.courses.find({}, {'_id': 0}))
            return courses
        else:
            return []
    except Exception as e:
        print(f"Error getting courses: {e}")
        return []

def get_course_by_code(course_code: str) -> Optional[Dict]:
    """Get a specific course by its code"""
    try:
        if client:
            course = db.courses.find_one({'course_code': course_code}, {'_id': 0})
            return course
        else:
            return None
    except Exception as e:
        print(f"Error getting course: {e}")
        return None

def add_course(course_data: Dict) -> bool:
    """Add a new course to the database"""
    try:
        if client:
            result = db.courses.insert_one(course_data)
            return bool(result.inserted_id)
        else:
            return False
    except Exception as e:
        print(f"Error adding course: {e}")
        return False

def update_course(course_code: str, course_data: Dict) -> bool:
    """Update an existing course in the database"""
    try:
        if client:
            result = db.courses.update_one(
                {'course_code': course_code},
                {'$set': course_data}
            )
            return result.modified_count > 0
        else:
            return False
    except Exception as e:
        print(f"Error updating course: {e}")
        return False

def delete_course(course_code: str) -> bool:
    """Delete a course from the database"""
    try:
        if client:
            result = db.courses.delete_one({'course_code': course_code})
            return result.deleted_count > 0
        else:
            return False
    except Exception as e:
        print(f"Error deleting course: {e}")
        return False 