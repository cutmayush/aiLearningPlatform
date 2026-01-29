// ==================== GLOBAL STATE ====================
let currentUser = null;
let currentSemester = 1;
let currentSubjects = [];
let charts = {};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
    loadSubjects();
    initializeCharts();
    loadAnalytics();
    loadRecommendations();
    loadBookmarks();
});

// ==================== UTILITY FUNCTIONS ====================
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('show');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('show');
}

// ==================== USER PROFILE ====================
async function loadUserProfile() {
    try {
        const response = await fetch('/api/profile');
        const profile = await response.json();
        
        if (response.ok) {
            currentUser = profile;
            updateProfileUI(profile);
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function updateProfileUI(profile) {
    document.getElementById('userName').textContent = profile.username;
    document.getElementById('welcomeName').textContent = profile.username;
    document.getElementById('streakDays').textContent = `${profile.streak_days} days`;
    document.getElementById('streakCount').textContent = profile.streak_days;
    document.getElementById('overallProgress').textContent = `${Math.round(profile.overall_progress || 0)}%`;
    document.getElementById('completedTopics').textContent = profile.completed_topics || 0;
    document.getElementById('avgScore').textContent = `${Math.round(profile.avg_score || 0)}%`;
    document.getElementById('totalTime').textContent = `${Math.round((profile.total_time || 0) / 60)}h`;
    
    currentSemester = profile.current_semester || 1;
    document.getElementById('semesterSelect').value = currentSemester;
    document.getElementById('subjectSemesterFilter').value = currentSemester;
    document.getElementById('settingsSemester').value = currentSemester;
}

// ==================== NAVIGATION ====================
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('show');
}

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(`section-${sectionName}`).classList.add('active');
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.nav-item').classList.add('active');
    
    // Update page title
    const titles = {
        'overview': 'Dashboard Overview',
        'subjects': 'My Subjects',
        'progress': 'Learning Progress',
        'recommendations': 'Recommendations',
        'resources': 'Learning Resources',
        'quiz': 'Quizzes',
        'bookmarks': 'My Bookmarks',
        'settings': 'Settings'
    };
    document.getElementById('pageTitle').textContent = titles[sectionName];
    
    // Load section-specific data
    if (sectionName === 'subjects') {
        loadSubjects();
    } else if (sectionName === 'progress') {
        loadAnalytics();
    } else if (sectionName === 'recommendations') {
        loadRecommendations();
    } else if (sectionName === 'bookmarks') {
        loadBookmarks();
    }
    
    // Close mobile sidebar
    if (window.innerWidth < 1024) {
        document.getElementById('sidebar').classList.remove('show');
    }
}

// ==================== SUBJECTS ====================
async function loadSubjects() {
    const semester = document.getElementById('semesterSelect')?.value || 
                    document.getElementById('subjectSemesterFilter')?.value || 
                    currentSemester;
    
    showLoading();
    
    try {
        const response = await fetch(`/api/subjects?semester=${semester}`);
        const subjects = await response.json();
        
        currentSubjects = subjects;
        displaySubjects(subjects);
    } catch (error) {
        console.error('Error loading subjects:', error);
        showToast('Failed to load subjects', 'error');
    } finally {
        hideLoading();
    }
}

function displaySubjects(subjects) {
    const container = document.getElementById('subjectsList');
    
    if (subjects.length === 0) {
        container.innerHTML = '<p class="text-muted">No subjects found for this semester</p>';
        return;
    }
    
    container.innerHTML = subjects.map(subject => `
        <div class="subject-card" onclick="viewSubject(${subject.id})">
            <div class="subject-header">
                <div class="subject-icon">
                    <i class="fas fa-book"></i>
                </div>
            </div>
            <h3 class="subject-title">${subject.name}</h3>
            <p class="subject-description">${subject.description}</p>
            <div class="subject-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
                <p class="progress-text">0/${subject.total_topics} topics completed</p>
            </div>
        </div>
    `).join('');
}

async function viewSubject(subjectId) {
    showLoading();
    
    try {
        const response = await fetch(`/api/subjects/${subjectId}/topics`);
        const topics = await response.json();
        
        displayTopics(subjectId, topics);
    } catch (error) {
        console.error('Error loading topics:', error);
        showToast('Failed to load topics', 'error');
    } finally {
        hideLoading();
    }
}

function displayTopics(subjectId, topics) {
    const subject = currentSubjects.find(s => s.id === subjectId);
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>${subject.name}</h2>
                <button onclick="closeModal()" class="close-btn">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="topics-list">
                    ${topics.map(topic => `
                        <div class="topic-item">
                            <div class="topic-info">
                                <h4>${topic.name}</h4>
                                <p>${topic.description}</p>
                                <span class="badge ${topic.difficulty}">${topic.difficulty}</span>
                            </div>
                            <div class="topic-actions">
                                <button onclick="viewResources(${topic.id})" class="btn-small">
                                    <i class="fas fa-video"></i> Resources
                                </button>
                                <button onclick="startQuiz(${topic.id})" class="btn-small btn-primary">
                                    <i class="fas fa-question-circle"></i> Take Quiz
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add styles for modal
    addModalStyles();
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}

function addModalStyles() {
    if (document.getElementById('modalStyles')) return;
    
    const style = document.createElement('style');
    style.id = 'modalStyles';
    style.textContent = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            animation: fadeIn 0.3s ease;
        }
        
        .modal-content {
            background: white;
            border-radius: 1rem;
            max-width: 800px;
            width: 90%;
            max-height: 80vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            animation: slideUp 0.3s ease;
        }
        
        .modal-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-secondary);
        }
        
        .modal-body {
            padding: 1.5rem;
            overflow-y: auto;
        }
        
        .topics-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .topic-item {
            padding: 1rem;
            background: var(--gray-50);
            border-radius: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }
        
        .topic-info h4 {
            margin-bottom: 0.5rem;
        }
        
        .topic-info p {
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
        }
        
        .badge {
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .badge.beginner { background: #dbeafe; color: #1e40af; }
        .badge.intermediate { background: #fef3c7; color: #92400e; }
        .badge.advanced { background: #fee2e2; color: #991b1b; }
        
        .topic-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .btn-small {
            padding: 0.5rem 1rem;
            border: 1px solid var(--border-color);
            background: white;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: var(--transition);
            font-family: inherit;
        }
        
        .btn-small:hover {
            background: var(--gray-100);
        }
        
        .btn-small.btn-primary {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }
        
        .btn-small.btn-primary:hover {
            background: var(--primary-dark);
        }
    `;
    
    document.head.appendChild(style);
}

// ==================== CHARTS ====================
function initializeCharts() {
    // Progress Chart
    const progressCtx = document.getElementById('progressChart');
    if (progressCtx) {
        charts.progress = new Chart(progressCtx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Not Started'],
                datasets: [{
                    data: [0, 0, 100],
                    backgroundColor: ['#10b981', '#f59e0b', '#e5e7eb']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

async function loadAnalytics() {
    try {
        const response = await fetch('/api/progress/analytics');
        const analytics = await response.json();
        
        if (response.ok) {
            updateAnalyticsCharts(analytics);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function updateAnalyticsCharts(analytics) {
    // Performance Trend Chart
    const trendCtx = document.getElementById('performanceTrendChart');
    if (trendCtx && analytics.performance_trend) {
        const dates = analytics.performance_trend.map(item => item.date);
        const scores = analytics.performance_trend.map(item => item.avg_score);
        
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Average Score',
                    data: scores,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    // Subject Progress Chart
    const subjectCtx = document.getElementById('subjectProgressChart');
    if (subjectCtx && analytics.subject_progress) {
        const subjects = analytics.subject_progress.map(item => item.subject);
        const progress = analytics.subject_progress.map(item => 
            (item.completed / item.total_topics) * 100
        );
        
        new Chart(subjectCtx, {
            type: 'bar',
            data: {
                labels: subjects,
                datasets: [{
                    label: 'Progress (%)',
                    data: progress,
                    backgroundColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    // Analytics Table
    const tableContainer = document.getElementById('analyticsTable');
    if (tableContainer && analytics.subject_progress) {
        tableContainer.innerHTML = `
            <table class="analytics-table">
                <thead>
                    <tr>
                        <th>Subject</th>
                        <th>Total Topics</th>
                        <th>Completed</th>
                        <th>Avg Score</th>
                        <th>Progress</th>
                    </tr>
                </thead>
                <tbody>
                    ${analytics.subject_progress.map(item => `
                        <tr>
                            <td>${item.subject}</td>
                            <td>${item.total_topics}</td>
                            <td>${item.completed || 0}</td>
                            <td>${Math.round(item.avg_score || 0)}%</td>
                            <td>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${(item.completed / item.total_topics) * 100}%"></div>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
}

// ==================== RECOMMENDATIONS ====================
async function loadRecommendations() {
    showLoading();
    
    try {
        const response = await fetch('/api/recommendations');
        const data = await response.json();
        
        if (response.ok) {
            displayRecommendations(data);
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
        showToast('Failed to load recommendations', 'error');
    } finally {
        hideLoading();
    }
}

function displayRecommendations(data) {
    const container = document.getElementById('recommendationsContainer');
    
    let html = '';
    
    // AI Recommendations
    if (data.recommendations && data.recommendations.length > 0) {
        html += `
            <div class="card">
                <div class="card-header">
                    <h3><i class="fas fa-brain"></i> AI Recommendations</h3>
                </div>
                <div class="card-body">
                    ${data.recommendations.map(rec => `
                        <div class="recommendation-item ${rec.priority}">
                            <i class="fas fa-${rec.type === 'revision' ? 'redo' : rec.type === 'progress' ? 'forward' : 'check'}"></i>
                            <p>${rec.message}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Weak Areas
    if (data.weak_areas && data.weak_areas.length > 0) {
        html += `
            <div class="card">
                <div class="card-header">
                    <h3><i class="fas fa-exclamation-triangle"></i> Areas to Improve</h3>
                </div>
                <div class="card-body">
                    <div class="topics-grid">
                        ${data.weak_areas.map(topic => `
                            <div class="topic-card weak">
                                <h4>${topic.name}</h4>
                                <p>${topic.subject_name}</p>
                                <div class="score">Score: ${Math.round(topic.score)}%</div>
                                <button onclick="viewResources(${topic.id})" class="btn-small">
                                    Review Materials
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Next Topics
    if (data.next_topics && data.next_topics.length > 0) {
        html += `
            <div class="card">
                <div class="card-header">
                    <h3><i class="fas fa-forward"></i> Recommended Next Topics</h3>
                </div>
                <div class="card-body">
                    <div class="topics-grid">
                        ${data.next_topics.map(topic => `
                            <div class="topic-card next">
                                <h4>${topic.name}</h4>
                                <p>${topic.subject_name}</p>
                                <span class="badge ${topic.difficulty}">${topic.difficulty}</span>
                                <button onclick="startQuiz(${topic.id})" class="btn-small btn-primary">
                                    Start Learning
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html || '<p class="text-muted">No recommendations available</p>';
}

// ==================== RESOURCES ====================
async function viewResources(topicId) {
    showLoading();
    
    try {
        const language = document.getElementById('resourceLanguage')?.value || 'english';
        const type = document.getElementById('resourceType')?.value || '';
        
        const response = await fetch(`/api/topics/${topicId}/resources?language=${language}&type=${type}`);
        const resources = await response.json();
        
        displayResources(resources);
    } catch (error) {
        console.error('Error loading resources:', error);
        showToast('Failed to load resources', 'error');
    } finally {
        hideLoading();
    }
}

function displayResources(resources) {
    const container = document.getElementById('resourcesList');
    
    if (resources.length === 0) {
        container.innerHTML = '<p class="text-muted">No resources found</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="resources-grid">
            ${resources.map(resource => `
                <div class="resource-card">
                    <div class="resource-icon ${resource.type}">
                        <i class="fas fa-${resource.type === 'video' ? 'play-circle' : 'file-alt'}"></i>
                    </div>
                    <h4>${resource.title}</h4>
                    <div class="resource-meta">
                        <span class="badge">${resource.type}</span>
                        <span class="badge">${resource.language}</span>
                        <span class="badge">${resource.difficulty}</span>
                    </div>
                    <div class="resource-actions">
                        <a href="${resource.url}" target="_blank" class="btn-small btn-primary">
                            <i class="fas fa-external-link-alt"></i> Open
                        </a>
                        <button onclick="bookmarkResource(${resource.id})" class="btn-small">
                            <i class="fas fa-bookmark"></i>
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// ==================== QUIZ ====================
async function startQuiz(topicId) {
    showLoading();
    
    try {
        const response = await fetch(`/api/quiz/${topicId}`);
        const quiz = await response.json();
        
        if (response.ok) {
            displayQuiz(quiz);
        }
    } catch (error) {
        console.error('Error loading quiz:', error);
        showToast('Failed to load quiz', 'error');
    } finally {
        hideLoading();
    }
}

function displayQuiz(quiz) {
    // Close modal if open
    closeModal();
    
    // Show quiz section
    showSection('quiz');
    
    const container = document.getElementById('quizContainer');
    
    let currentQuestion = 0;
    let answers = [];
    let startTime = Date.now();
    
    function renderQuestion() {
        const question = quiz.questions[currentQuestion];
        
        container.innerHTML = `
            <div class="quiz-header">
                <h2>${quiz.topic_name}</h2>
                <div class="quiz-meta">
                    <span><i class="fas fa-layer-group"></i> ${quiz.difficulty}</span>
                    <span><i class="fas fa-question-circle"></i> Question ${currentQuestion + 1}/${quiz.questions.length}</span>
                    <span><i class="fas fa-clock"></i> <span id="timer">00:00</span></span>
                </div>
            </div>
            
            <div class="quiz-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${(currentQuestion / quiz.questions.length) * 100}%"></div>
                </div>
            </div>
            
            <div class="quiz-question">
                <h3>${question.question}</h3>
                <div class="quiz-options">
                    ${question.options.map((option, index) => `
                        <button class="quiz-option" onclick="selectAnswer(${index})">
                            <span class="option-letter">${String.fromCharCode(65 + index)}</span>
                            <span class="option-text">${option}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
            
            <div class="quiz-actions">
                ${currentQuestion > 0 ? '<button onclick="previousQuestion()" class="btn">Previous</button>' : ''}
                <button onclick="nextQuestion()" class="btn btn-primary" id="nextBtn" disabled>
                    ${currentQuestion === quiz.questions.length - 1 ? 'Submit Quiz' : 'Next Question'}
                </button>
            </div>
        `;
        
        // Start timer
        startTimer();
    }
    
    function startTimer() {
        const timerElement = document.getElementById('timer');
        setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            timerElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }, 1000);
    }
    
    window.selectAnswer = (optionIndex) => {
        // Remove previous selection
        document.querySelectorAll('.quiz-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        
        // Mark as selected
        document.querySelectorAll('.quiz-option')[optionIndex].classList.add('selected');
        
        // Store answer
        answers[currentQuestion] = {
            question_id: quiz.questions[currentQuestion].id,
            selected: optionIndex,
            is_correct: optionIndex === quiz.questions[currentQuestion].correct_answer
        };
        
        // Enable next button
        document.getElementById('nextBtn').disabled = false;
    };
    
    window.nextQuestion = () => {
        if (currentQuestion < quiz.questions.length - 1) {
            currentQuestion++;
            renderQuestion();
        } else {
            submitQuiz();
        }
    };
    
    window.previousQuestion = () => {
        if (currentQuestion > 0) {
            currentQuestion--;
            renderQuestion();
        }
    };
    
    async function submitQuiz() {
        const timeTaken = Math.floor((Date.now() - startTime) / 1000);
        
        showLoading();
        
        try {
            const response = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    topic_id: quiz.topic_id,
                    answers: answers,
                    time_taken: timeTaken
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                displayQuizResult(result);
            }
        } catch (error) {
            console.error('Error submitting quiz:', error);
            showToast('Failed to submit quiz', 'error');
        } finally {
            hideLoading();
        }
    }
    
    renderQuestion();
}

function displayQuizResult(result) {
    const container = document.getElementById('quizContainer');
    
    const minutes = Math.floor(result.time_taken / 60);
    const seconds = result.time_taken % 60;
    
    container.innerHTML = `
        <div class="quiz-result">
            <div class="result-icon ${result.score >= 80 ? 'excellent' : result.score >= 60 ? 'good' : 'needs-improvement'}">
                <i class="fas fa-${result.score >= 80 ? 'trophy' : result.score >= 60 ? 'smile' : 'frown'}"></i>
            </div>
            
            <h2>${result.performance}</h2>
            <p class="result-score">${Math.round(result.score)}%</p>
            
            <div class="result-stats">
                <div class="stat">
                    <i class="fas fa-check-circle"></i>
                    <span>${result.correct_answers}/${result.total_questions} Correct</span>
                </div>
                <div class="stat">
                    <i class="fas fa-clock"></i>
                    <span>${minutes}m ${seconds}s</span>
                </div>
                <div class="stat">
                    <i class="fas fa-percentage"></i>
                    <span>${Math.round(result.accuracy)}% Accuracy</span>
                </div>
            </div>
            
            <div class="result-actions">
                <button onclick="showSection('overview')" class="btn">
                    <i class="fas fa-home"></i> Back to Dashboard
                </button>
                <button onclick="showSection('recommendations')" class="btn btn-primary">
                    <i class="fas fa-lightbulb"></i> View Recommendations
                </button>
            </div>
        </div>
    `;
}

// ==================== BOOKMARKS ====================
async function loadBookmarks() {
    try {
        const response = await fetch('/api/bookmarks');
        const bookmarks = await response.json();
        
        if (response.ok) {
            displayBookmarks(bookmarks);
        }
    } catch (error) {
        console.error('Error loading bookmarks:', error);
    }
}

function displayBookmarks(bookmarks) {
    const container = document.getElementById('bookmarksList');
    
    if (bookmarks.length === 0) {
        container.innerHTML = '<p class="text-muted">No bookmarks yet</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="resources-grid">
            ${bookmarks.map(bookmark => `
                <div class="resource-card">
                    <div class="resource-icon ${bookmark.type}">
                        <i class="fas fa-${bookmark.type === 'video' ? 'play-circle' : 'file-alt'}"></i>
                    </div>
                    <h4>${bookmark.title}</h4>
                    <p class="text-muted">${bookmark.subject_name} - ${bookmark.topic_name}</p>
                    <div class="resource-actions">
                        <a href="${bookmark.url}" target="_blank" class="btn-small btn-primary">
                            <i class="fas fa-external-link-alt"></i> Open
                        </a>
                        <button onclick="removeBookmark(${bookmark.id})" class="btn-small">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

async function bookmarkResource(resourceId) {
    try {
        const response = await fetch('/api/bookmarks/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resource_id: resourceId })
        });
        
        if (response.ok) {
            showToast('Bookmark added', 'success');
        }
    } catch (error) {
        console.error('Error adding bookmark:', error);
        showToast('Failed to add bookmark', 'error');
    }
}

async function removeBookmark(bookmarkId) {
    try {
        const response = await fetch(`/api/bookmarks/remove/${bookmarkId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Bookmark removed', 'success');
            loadBookmarks();
        }
    } catch (error) {
        console.error('Error removing bookmark:', error);
        showToast('Failed to remove bookmark', 'error');
    }
}

// ==================== SETTINGS ====================
async function updateSettings(event) {
    event.preventDefault();
    
    const semester = document.getElementById('settingsSemester').value;
    
    showLoading();
    
    try {
        const response = await fetch('/api/profile/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ semester: parseInt(semester) })
        });
        
        if (response.ok) {
            showToast('Settings updated successfully', 'success');
            currentSemester = parseInt(semester);
            loadUserProfile();
        }
    } catch (error) {
        console.error('Error updating settings:', error);
        showToast('Failed to update settings', 'error');
    } finally {
        hideLoading();
    }
}

// ==================== THEME ====================
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

function setTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
    localStorage.setItem('theme', theme);
    
    // Update active theme button
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Load saved theme
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme');
}
