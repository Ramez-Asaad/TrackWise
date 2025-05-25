# TrackWise - AI-Powered Course Recommendation System

TrackWise is an intelligent academic advising system that uses rule-based inference engines to provide personalized course recommendations for students in the Artificial Intelligence Science track.

## 🚀 Features

### 🤖 AI-Powered Inference Engine
- **Rule-Based Reasoning**: Uses Experta library for intelligent decision making
- **Credit Limit Management**: Automatically calculates credit limits based on CGPA
- **Prerequisite Validation**: Ensures all prerequisites are met before recommendations
- **Co-requisite Handling**: Manages co-requisite requirements
- **Failed Course Priority**: Prioritizes retaking failed courses when prerequisites are met
- **Semester Availability**: Only recommends courses offered in the current semester
- **Track Alignment**: Ensures recommendations align with AI Science track requirements

### 📊 Smart Recommendations
- **Personalized Suggestions**: Based on student's academic history and performance
- **Credit Optimization**: Maximizes credit hours within CGPA-based limits
- **Priority System**: Failed courses get higher priority for retaking
- **Detailed Information**: Shows prerequisites, credit hours, and semester availability

### 🎨 Modern Web Interface
- **Beautiful UI**: Modern, responsive design with gradient backgrounds
- **Interactive Forms**: Multi-select dropdowns with search functionality
- **Real-time Feedback**: Instant recommendations with detailed explanations
- **Progress Tracking**: Visual credit progress bars and summaries

## 📋 System Requirements

### Credit Limits Based on CGPA:
- **CGPA ≥ 3.5**: 21 credits maximum
- **CGPA ≥ 3.0**: 18 credits maximum  
- **CGPA ≥ 2.5**: 15 credits maximum
- **CGPA < 2.5**: 12 credits maximum

### Recommendation Rules:
1. **Prerequisites**: All prerequisite courses must be passed
2. **Co-requisites**: Co-requisite courses must be passed or taken concurrently
3. **Semester Availability**: Only courses offered in the selected semester
4. **Failed Course Priority**: Failed courses are recommended first if prerequisites are met
5. **Credit Limits**: Total recommended credits cannot exceed CGPA-based limit

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd TrackWise
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   cd UI
   python app.py
   ```

4. **Access the application**:
   Open your browser and go to `http://localhost:5000`

## 📁 Project Structure

```
TrackWise/
├── inference_engine/           # AI Inference Engine
│   ├── course_recommender.py   # Main inference logic
│   ├── example.py             # Standalone example
│   └── README.md              # Inference engine documentation
├── UI/                        # Flask Web Application
│   ├── app.py                 # Main Flask app
│   ├── inference_engine.py    # Flask blueprint for AI recommendations
│   ├── Client.py              # User authentication and routing
│   ├── KBSystem.py            # Legacy knowledge-based system
│   ├── KBEditor.py            # Knowledge base editor
│   ├── DB.py                  # Database operations
│   ├── templates/             # HTML templates
│   │   ├── index.html         # Login/signup page
│   │   ├── student.html       # Student dashboard
│   │   ├── course_recommendations.html  # AI recommendations page
│   │   └── admin.html         # Admin dashboard
│   ├── static/                # CSS, JS, and other static files
│   └── Data.csv              # Course database
├── Data.csv                   # Main course database
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🎯 How to Use

### For Students:

1. **Sign Up/Login**: Create an account or login as a student
2. **Access Dashboard**: Choose between AI-powered or legacy recommendations
3. **AI Recommendations** (Recommended):
   - Select your current semester (Fall/Spring)
   - Enter your CGPA
   - Select passed courses from the dropdown
   - Select failed courses (if any)
   - Click "Get AI Recommendations"
4. **View Results**: 
   - See prioritized failed courses to retake
   - View new course recommendations
   - Check credit summary and progress
   - Review prerequisites for each course

### For Administrators:

1. **Login as Admin**: Use admin credentials
2. **Manage Knowledge Base**: Add/edit/delete courses and rules
3. **Monitor System**: View system usage and performance

## 🧠 Inference Engine Details

The inference engine uses the Experta library to implement forward-chaining rule-based reasoning:

### Core Classes:
- **Course**: Represents course information and status
- **Student**: Represents student academic information  
- **EligibleCourse**: Represents courses eligible for recommendation
- **CourseRecommender**: Main inference engine with rules

### Key Rules:
1. **Credit Limit Rule**: Sets maximum credits based on CGPA
2. **Course Eligibility Rule**: Evaluates prerequisites, co-requisites, and semester availability
3. **Failed Course Priority Rule**: Prioritizes failed courses
4. **Regular Course Rule**: Recommends other eligible courses

### Example Usage:
```python
from inference_engine.course_recommender import get_course_recommendations

recommendations = get_course_recommendations(
    student_cgpa=3.2,
    passed_courses=['CSE014', 'CSE015', 'MAT111', 'MAT112'],
    failed_courses=['CSE111'],
    current_semester='Spring',
    csv_path='Data.csv'
)
```

## 🔧 API Endpoints

### Web Routes:
- `GET /`: Login/signup page
- `GET /student_dashboard`: Student dashboard
- `GET /course_recommendations`: AI recommendation form
- `POST /course_recommendations`: Process recommendations

### API Routes:
- `POST /api/recommendations`: JSON API for getting recommendations

## 📊 Sample Data

The system includes comprehensive course data for the AI Science track including:
- Core CS courses (Programming, Data Structures, Algorithms)
- Mathematics courses (Calculus, Linear Algebra, Statistics)
- AI-specific courses (Machine Learning, Neural Networks, NLP)
- Elective courses and general education requirements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 👥 Team

- **Muhammed Mustafa**
- **Ramez Asaad** 
- **Rodina Mohamed**
- **Aya Mamdouh**
- **Noureen Muhammed**

## 📄 License

This project is developed as part of the AIE212 Knowledge-Based Systems course.

---

**TrackWise** - Your intelligent academic companion! 🎓✨
