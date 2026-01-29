# 🎓 Personalized Learning Path Agent

**AI-Driven Web Application for B.Tech CSE Students**

A modern, intelligent web application that provides personalized learning paths, smart recommendations, and comprehensive progress tracking for Computer Science Engineering students.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🌟 Features

### 🔐 **Authentication System**
- Beautiful, animated login/register interface
- Secure password hashing
- Session management
- Input validation

### 📚 **Academic Management**
- Support for all 8 semesters
- 20+ subjects across semesters
- Topic-wise learning modules
- Difficulty-based content (Beginner/Intermediate/Advanced)

### 📊 **Progress Tracking**
- Real-time progress visualization
- Topic completion tracking
- Study time monitoring
- Learning streak system
- Performance analytics with charts

### 🧠 **AI-Powered Recommendations**
- Identifies weak areas
- Suggests next topics
- Personalized study plans
- Smart learning pace analysis

### 📺 **Learning Resources**
- YouTube video recommendations
- Curated articles
- Multi-language support (English, Hindi, Odia)
- Resource bookmarking

### 🧪 **Quiz System**
- Adaptive difficulty
- Time-bound assessments
- Instant feedback
- Detailed performance analysis
- Quiz history tracking

### 📈 **Analytics Dashboard**
- Performance trend graphs
- Subject-wise progress charts
- Detailed analytics tables
- Visual insights

### 🎨 **Modern UI/UX**
- Responsive design (mobile, tablet, desktop)
- Dark/Light theme toggle
- Smooth animations
- Intuitive navigation
- Clean, professional interface

---

## 📁 Project Structure

```
personalized_learning_agent/
│
├── app.py                          # Main Flask application
├── learning_agent.db               # SQLite database (auto-generated)
├── requirements.txt                # Python dependencies
├── README.md                       # Documentation
│
├── templates/                      # HTML templates
│   ├── index.html                 # Login/Register page
│   └── dashboard.html             # Main dashboard
│
└── static/                        # Static assets
    ├── css/
    │   ├── style.css              # Global styles
    │   └── dashboard.css          # Dashboard-specific styles
    │
    └── js/
        ├── auth.js                # Authentication logic
        └── dashboard.js           # Dashboard functionality
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- VS Code (recommended)

### Step 1: Extract the Project
```bash
# Extract the ZIP file to your desired location
cd path/to/personalized_learning_agent
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 5: Access the Application
1. Open your web browser
2. Navigate to `http://localhost:5000`
3. Register a new account or use test credentials

---

## 💡 Usage Guide

### First Time Setup

1. **Register an Account**
   - Click "Create an account" on the login page
   - Fill in username, email, and password
   - Submit the form

2. **Login**
   - Enter your credentials
   - Access the dashboard

3. **Set Your Semester**
   - Go to Settings (sidebar)
   - Select your current semester (1-8)
   - Save settings

4. **Explore Subjects**
   - Navigate to "My Subjects"
   - Select your semester
   - Click on any subject to view topics

5. **Start Learning**
   - View learning resources (videos/articles)
   - Take quizzes to test knowledge
   - Track your progress

### Key Workflows

#### **Taking a Quiz**
1. Go to "My Subjects"
2. Select a subject
3. Click on a topic
4. Click "Take Quiz"
5. Answer questions
6. View results and recommendations

#### **Viewing Resources**
1. Navigate to "Learning Resources"
2. Select language preference
3. Filter by type (video/article)
4. Click "Open" to access content
5. Bookmark useful resources

#### **Checking Progress**
1. Go to "Learning Progress"
2. View performance trends
3. Analyze subject-wise progress
4. Identify areas for improvement

#### **Getting Recommendations**
1. Navigate to "Recommendations"
2. Review AI-generated suggestions
3. See weak areas
4. Follow recommended next topics

---

## 🎯 Sample Data

The application comes with pre-populated sample data:

### **Semesters 1-8**
Each semester contains relevant subjects:
- Semester 1: Programming in C, Mathematics-I, Physics
- Semester 2: Data Structures, Java OOP, Mathematics-II
- Semester 3: DBMS, Operating Systems, Computer Networks
- Semester 4: Algorithms, Web Technologies, Software Engineering
- Semester 5: AI, Machine Learning, Compiler Design
- Semester 6: Deep Learning, Cloud Computing, Cyber Security
- Semester 7: NLP, Big Data, IoT
- Semester 8: Blockchain, Quantum Computing

### **Topics**
Sample topics for Java, DBMS, and Web Technologies with:
- Beginner, Intermediate, and Advanced levels
- Multiple learning resources per topic
- YouTube video links
- Article references

---

## 🔧 Configuration

### Database Configuration
The application uses SQLite database (`learning_agent.db`). The database is automatically created on first run with sample data.

To reset the database:
1. Delete `learning_agent.db` file
2. Restart the application

### Customization

#### Adding New Subjects
Edit `app.py` and add subjects to the `subjects_data` array in the `insert_sample_data()` function.

#### Adding New Topics
Add topics to the `topics_data` array with appropriate subject_id references.

#### Adding Resources
Add learning resources to the `resources_data` array with topic_id references.

---

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLite** - Lightweight database
- **Werkzeug** - Security utilities

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling with custom properties
- **JavaScript** - Interactivity
- **Chart.js** - Data visualization
- **Font Awesome** - Icons
- **Google Fonts** - Typography

### Architecture
- RESTful API design
- Session-based authentication
- Responsive design principles
- Component-based UI

---

## 🎨 UI/UX Highlights

- **Gradient Backgrounds** - Modern purple/blue gradients
- **Smooth Animations** - Fade-ins, slide-ups, transitions
- **Responsive Layout** - Mobile-first design
- **Intuitive Navigation** - Clear sidebar menu
- **Visual Feedback** - Toast notifications, loading states
- **Accessibility** - Semantic HTML, keyboard shortcuts

---

## 📱 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

---

## 🔒 Security Features

- Password hashing with Werkzeug
- SQL injection prevention
- Session management
- Input validation
- CSRF protection (Flask-CORS)

---

## 🚧 Future Enhancements

Potential features for future versions:

- [ ] Machine learning-based recommendation engine
- [ ] Real-time collaboration features
- [ ] Video conferencing integration
- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced analytics with ML insights
- [ ] Gamification (badges, leaderboards)
- [ ] Social features (study groups, forums)
- [ ] Integration with external learning platforms
- [ ] Voice-based navigation
- [ ] Offline mode support

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Database not created
- **Solution**: Ensure write permissions in the project directory

**Issue**: Port 5000 already in use
- **Solution**: Change port in `app.py`: `app.run(port=5001)`

**Issue**: Static files not loading
- **Solution**: Clear browser cache, restart Flask

**Issue**: Login not working
- **Solution**: Check browser console for errors, verify database exists

---

## 📝 API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /logout` - User logout

### Profile
- `GET /api/profile` - Get user profile
- `POST /api/profile/update` - Update profile

### Subjects & Topics
- `GET /api/subjects?semester=X` - Get subjects by semester
- `GET /api/subjects/<id>/topics` - Get topics for subject
- `GET /api/topics/<id>` - Get topic details

### Learning Resources
- `GET /api/topics/<id>/resources` - Get topic resources
- `GET /api/recommendations` - Get AI recommendations

### Progress
- `POST /api/progress/update` - Update progress
- `GET /api/progress/analytics` - Get analytics data

### Quiz
- `GET /api/quiz/<topic_id>` - Get quiz questions
- `POST /api/quiz/submit` - Submit quiz answers

### Bookmarks
- `GET /api/bookmarks` - Get user bookmarks
- `POST /api/bookmarks/add` - Add bookmark
- `DELETE /api/bookmarks/remove/<id>` - Remove bookmark

---

## 💻 Development

### Running in Development Mode
```bash
python app.py
```
Flask will run with debug mode enabled, providing:
- Auto-reload on code changes
- Detailed error messages
- Interactive debugger

### Testing
To test the application:
1. Register multiple test users
2. Navigate through all sections
3. Take quizzes and view results
4. Check analytics and recommendations
5. Test on different screen sizes

---

## 📄 License

This project is created for educational purposes.

---

## 👥 Contributors

Developed as a comprehensive learning management system for B.Tech CSE students.

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Inspect browser console for errors

---

## 🎓 Academic Context

**Ideal for:**
- Final year projects
- Hackathons
- Portfolio showcase
- Learning web development
- Understanding full-stack applications

**Learning Outcomes:**
- Flask web framework
- RESTful API design
- Database management
- Frontend development
- UI/UX design principles
- Authentication systems
- Data visualization

---

## ⚡ Quick Start Summary

```bash
# 1. Navigate to project directory
cd personalized_learning_agent

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run application
python app.py

# 6. Open browser to http://localhost:5000
```

---

## 🌟 Key Highlights

✅ **Complete Full-Stack Application**
✅ **Production-Ready Code**
✅ **Comprehensive Documentation**
✅ **Sample Data Included**
✅ **Modern UI/UX**
✅ **Responsive Design**
✅ **AI-Powered Features**
✅ **Secure Authentication**
✅ **Visual Analytics**
✅ **Easy to Deploy**

---

**Happy Learning! 🚀**

*Making education personalized, intelligent, and accessible.*
