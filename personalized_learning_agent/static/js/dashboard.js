// ==================== GLOBAL STATE ====================
let currentUser = null;
let currentSemester = 1;
let currentSubjects = [];
let charts = {};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
    initializeCharts();
    // Note: loadSubjects will be called after profile loads to get correct semester
    
    // Set default active section safely
    showSection('overview');
});

// ==================== UTILITY FUNCTIONS ====================
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if(toast) {
        toast.textContent = message;
        toast.className = `toast ${type} show`;
        
        // Auto hide after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

function showLoading() {
    const loader = document.getElementById('loadingOverlay');
    if(loader) loader.classList.add('show');
}

function hideLoading() {
    const loader = document.getElementById('loadingOverlay');
    if(loader) loader.classList.remove('show');
}

// ==================== USER PROFILE ====================
async function loadUserProfile() {
    try {
        const response = await fetch('/api/profile');
        if (response.ok) {
            const profile = await response.json();
            currentUser = profile;
            updateProfileUI(profile);
            
            // Load initial data after profile is set
            loadSubjects(); 
            loadRecommendations();
            loadBookmarks();
        } else {
            console.error('Failed to load profile');
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function updateProfileUI(profile) {
    document.getElementById('userName').textContent = profile.username;
    document.getElementById('welcomeName').textContent = profile.username;
    
    // Stats
    document.getElementById('streakDays').textContent = `${profile.streak_days || 0} days`;
    document.getElementById('streakCount').textContent = profile.streak_days || 0;
    
    // Set Global Semester
    if (!currentSemester || currentSemester === 1) {
        currentSemester = profile.current_semester || 1;
    }
    
    syncDropdowns(currentSemester);
}

function syncDropdowns(semester) {
    const semSelect = document.getElementById('semesterSelect');
    if(semSelect) semSelect.value = semester;
    
    const filterSelect = document.getElementById('subjectSemesterFilter');
    if(filterSelect) filterSelect.value = semester;
    
    const settingsSelect = document.getElementById('settingsSemester');
    if(settingsSelect) settingsSelect.value = semester;
}

// ==================== NAVIGATION ====================
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if(sidebar) sidebar.classList.toggle('show');
}

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    const target = document.getElementById(`section-${sectionName}`);
    if (target) {
        target.classList.add('active');
    }
    
    // Update Sidebar Active State
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(sectionName)) {
            item.classList.add('active');
        }
    });

    // Update Header Title
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
    const pageTitle = document.getElementById('pageTitle');
    if(pageTitle) pageTitle.textContent = titles[sectionName] || 'Dashboard';
    
    // Trigger Data Reloads based on section
    if (sectionName === 'subjects') loadSubjects();
    if (sectionName === 'progress') loadAnalytics(currentSemester);
    if (sectionName === 'recommendations') loadRecommendations();
    if (sectionName === 'bookmarks') loadBookmarks();
    
    // Close mobile sidebar
    if (window.innerWidth < 1024) {
        const sidebar = document.getElementById('sidebar');
        if(sidebar) sidebar.classList.remove('show');
    }
}

// ==================== SUBJECTS & ANALYTICS INTEGRATION ====================
async function loadSubjects() {
    let semester = currentSemester;

    // Determine active dropdown value
    const overviewSection = document.getElementById('section-overview');
    const subjectsSection = document.getElementById('section-subjects');

    if (subjectsSection && subjectsSection.classList.contains('active')) {
        const val = document.getElementById('subjectSemesterFilter')?.value;
        if(val) semester = parseInt(val);
    } else if (overviewSection && overviewSection.classList.contains('active')) {
        const val = document.getElementById('semesterSelect')?.value;
        if(val) semester = parseInt(val);
    } else {
        // Fallback checks
        const val = document.getElementById('subjectSemesterFilter')?.value || 
                    document.getElementById('semesterSelect')?.value;
        if(val) semester = parseInt(val);
    }
    
    // Update global state if changed
    if(semester !== currentSemester) {
        currentSemester = semester;
        syncDropdowns(semester);
    }
    
    showLoading();
    
    try {
        const response = await fetch(`/api/subjects?semester=${semester}`);
        const subjects = await response.json();
        
        currentSubjects = subjects;
        displaySubjects(subjects);

        // Load Analytics for the selected semester
        loadAnalytics(semester);

    } catch (error) {
        console.error('Error loading subjects:', error);
        showToast('Failed to load subjects', 'error');
    } finally {
        hideLoading();
    }
}

function displaySubjects(subjects) {
    const container = document.getElementById('subjectsList');
    
    if (!subjects || subjects.length === 0) {
        container.innerHTML = '<p class="text-muted">No subjects found for this semester</p>';
        return;
    }
    
    container.innerHTML = subjects.map(subject => {
        const progress = subject.total_topics > 0 
            ? Math.round((subject.completed / subject.total_topics) * 100) 
            : 0;

        return `
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
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
                <p class="progress-text">${subject.completed || 0}/${subject.total_topics} topics completed</p>
            </div>
        </div>
        `;
    }).join('');
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
                <h2>${subject ? subject.name : 'Topics'}</h2>
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
                                ${topic.user_status === 'completed' ? '<span class="badge" style="background:#d1fae5; color:#065f46">Completed</span>' : ''}
                            </div>
                            <div class="topic-actions">
                                <button onclick="viewResources(${topic.id})" class="btn-small">
                                    <i class="fas fa-video"></i> Resources
                                </button>
                                <button onclick="startQuiz(${topic.id})" class="btn-small btn-primary">
                                    <i class="fas fa-brain"></i> AI Quiz
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    // Add styles dynamically if not present
    addModalStyles();
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}

function addModalStyles() {
    if (document.getElementById('modalStyles')) return;
    const style = document.createElement('style');
    style.id = 'modalStyles';
    style.textContent = `
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.3s ease; }
        .modal-content { background: white; border-radius: 1rem; max-width: 800px; width: 90%; max-height: 80vh; overflow: hidden; display: flex; flex-direction: column; animation: slideUp 0.3s ease; }
        .modal-header { padding: 1.5rem; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
        .close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text-secondary); }
        .modal-body { padding: 1.5rem; overflow-y: auto; }
        .topics-list { display: flex; flex-direction: column; gap: 1rem; }
        .topic-item { padding: 1rem; background: var(--gray-50); border-radius: 0.5rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
        .badge { padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-right: 5px; }
        .badge.beginner { background: #dbeafe; color: #1e40af; }
        .badge.intermediate { background: #fef3c7; color: #92400e; }
        .badge.advanced { background: #fee2e2; color: #991b1b; }
        .topic-actions { display: flex; gap: 0.5rem; }
        .btn-small { padding: 0.5rem 1rem; border: 1px solid var(--border-color); background: white; border-radius: 0.5rem; cursor: pointer; transition: var(--transition); }
        .btn-small:hover { background: var(--gray-100); }
        .btn-small.btn-primary { background: var(--primary); color: white; border-color: var(--primary); }
    `;
    document.head.appendChild(style);
}

// ==================== CHARTS ====================
function initializeCharts() {
    const progressCtx = document.getElementById('progressChart');
    if (progressCtx) {
        charts.progress = new Chart(progressCtx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'Pending'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#10b981', '#e5e7eb']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }
}

async function loadAnalytics(semester = currentSemester) {
    try {
        const response = await fetch(`/api/progress/analytics?semester=${semester}`);
        const analytics = await response.json();
        
        if (response.ok) {
            updateAnalyticsCharts(analytics);
            updateSemesterStats(analytics.semester_stats);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function updateSemesterStats(stats) {
    if (!stats) return;

    // Time Formatting
    const hours = Math.floor((stats.total_time || 0) / 3600);
    const mins = Math.floor(((stats.total_time || 0) % 3600) / 60);
    const timeElem = document.getElementById('totalTime');
    if(timeElem) timeElem.textContent = `${hours}h ${mins}m`;

    // Progress Update
    const completedElem = document.getElementById('completedTopics');
    if(completedElem) completedElem.textContent = stats.completed_topics || 0;

    const percentage = stats.total_topics > 0 
        ? Math.round((stats.completed_topics / stats.total_topics) * 100) 
        : 0;
    
    const progressElem = document.getElementById('overallProgress');
    if(progressElem) progressElem.textContent = `${percentage}%`;
}

function updateAnalyticsCharts(analytics) {
    // Pie Chart
    if (charts.progress) {
        let total = 0, completed = 0;
        if (analytics.semester_stats) {
             total = analytics.semester_stats.total_topics || 0;
             completed = analytics.semester_stats.completed_topics || 0;
        }
        const remaining = Math.max(0, total - completed);
        charts.progress.data.datasets[0].data = [completed, remaining];
        charts.progress.update();
    }

    // Trend Chart
    const trendCtx = document.getElementById('performanceTrendChart');
    if (trendCtx && analytics.performance_trend) {
        if (charts.trend) charts.trend.destroy();

        const dates = analytics.performance_trend.map(item => item.date);
        const scores = analytics.performance_trend.map(item => item.avg_score);
        
        charts.trend = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Avg Score (Selected Sem)',
                    data: scores,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true, max: 100 } }
            }
        });
    }
    
    // Subject Chart
    const subjectCtx = document.getElementById('subjectProgressChart');
    if (subjectCtx && analytics.subject_progress) {
        if (charts.subjects) charts.subjects.destroy();

        const subjects = analytics.subject_progress.map(item => item.subject);
        const progress = analytics.subject_progress.map(item => 
            item.total_topics > 0 ? (item.completed / item.total_topics) * 100 : 0
        );
        
        charts.subjects = new Chart(subjectCtx, {
            type: 'bar',
            data: {
                labels: subjects,
                datasets: [{
                    label: 'Progress (%)',
                    data: progress,
                    backgroundColor: '#667eea',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true, max: 100 } }
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
                        <th>Completed</th>
                        <th>Avg Score</th>
                        <th>Progress</th>
                    </tr>
                </thead>
                <tbody>
                    ${analytics.subject_progress.map(item => `
                        <tr>
                            <td>${item.subject}</td>
                            <td>${item.completed}/${item.total_topics}</td>
                            <td>${Math.round(item.avg_score || 0)}%</td>
                            <td>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${item.total_topics > 0 ? (item.completed / item.total_topics)*100 : 0}%"></div>
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
    } finally {
        hideLoading();
    }
}

function displayRecommendations(data) {
    const container = document.getElementById('recommendationsContainer');
    let html = '';
    
    if (data.recommendations && data.recommendations.length > 0) {
        html += `
            <div class="card mb-3">
                <div class="card-header"><h3><i class="fas fa-brain"></i> AI Suggestions</h3></div>
                <div class="card-body">
                    ${data.recommendations.map(rec => `
                        <div class="recommendation-item ${rec.priority}">
                            <i class="fas fa-lightbulb"></i> <p>${rec.message}</p>
                        </div>
                    `).join('')}
                </div>
            </div>`;
    }

    if (data.weak_areas && data.weak_areas.length > 0) {
        html += `
            <div class="card mb-3">
                <div class="card-header"><h3><i class="fas fa-exclamation-triangle"></i> Focus Areas (Weak Topics)</h3></div>
                <div class="card-body">
                    <div class="topics-grid">
                        ${data.weak_areas.map(topic => `
                            <div class="topic-card weak">
                                <h4>${topic.name}</h4>
                                <p>${topic.subject_name}</p>
                                <div class="score">Score: ${Math.round(topic.score)}%</div>
                                <button onclick="viewResources(${topic.id})" class="btn-small">Review</button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>`;
    }
    
    container.innerHTML = html || '<p class="text-muted">No specific recommendations yet. Keep learning!</p>';
}

// ==================== RESOURCES ====================
async function viewResources(topicId) {
    closeModal();
    showSection('resources');
    showLoading();
    
    try {
        const response = await fetch(`/api/topics/${topicId}/resources`);
        const resources = await response.json();
        displayResources(resources);
    } catch (error) {
        console.error('Error loading resources:', error);
    } finally {
        hideLoading();
    }
}

function displayResources(resources) {
    const container = document.getElementById('resourcesList');
    if (!resources || resources.length === 0) {
        container.innerHTML = '<p class="text-muted">No resources found for this topic.</p>';
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
                    <div class="resource-actions">
                        <a href="${resource.url}" target="_blank" class="btn-small btn-primary">Open</a>
                        <button onclick="bookmarkResource(${resource.id})" class="btn-small"><i class="fas fa-bookmark"></i></button>
                    </div>
                </div>
            `).join('')}
        </div>`;
}

// ==================== QUIZ LOGIC (AI INTEGRATED) ====================
let currentQuiz = null;
let currentQuestionIndex = 0;
let userAnswers = [];
let quizTimer = null;
let quizStartTime = 0;

async function startQuiz(topicId) {
    showLoading();
    showToast('Generative AI is creating your quiz...', 'info'); // UI Feedback for AI Delay
    closeModal();
    
    try {
        const response = await fetch(`/api/quiz/${topicId}`);
        if (!response.ok) throw new Error('Quiz failed to load');
        
        currentQuiz = await response.json();
        
        showSection('quiz');
        currentQuestionIndex = 0;
        userAnswers = new Array(currentQuiz.questions.length).fill(null);
        quizStartTime = Date.now();
        renderQuizQuestion();
        
    } catch (error) {
        console.error('Error starting quiz:', error);
        showToast('Failed to generate quiz. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function renderQuizQuestion() {
    const container = document.getElementById('quizContainer');
    if(!container || !currentQuiz) return;

    const question = currentQuiz.questions[currentQuestionIndex];
    
    container.innerHTML = `
        <div class="quiz-header">
            <h2>${currentQuiz.topic_name}</h2>
            <div class="quiz-meta">
                <span>Q ${currentQuestionIndex + 1} / ${currentQuiz.questions.length}</span>
                <span id="quizTimer">00:00</span>
            </div>
        </div>
        <div class="quiz-progress">
            <div class="progress-bar"><div class="progress-fill" style="width: ${(currentQuestionIndex/currentQuiz.questions.length)*100}%"></div></div>
        </div>
        <div class="quiz-question">
            <h3>${question.question}</h3>
            <div class="quiz-options">
                ${question.options.map((opt, idx) => `
                    <button class="quiz-option ${userAnswers[currentQuestionIndex]?.selected === idx ? 'selected' : ''}" 
                            onclick="selectOption(${idx})">
                        <span class="option-letter">${String.fromCharCode(65+idx)}</span>
                        ${opt}
                    </button>
                `).join('')}
            </div>
        </div>
        <div class="quiz-actions">
            ${currentQuestionIndex > 0 ? `<button onclick="prevQuestion()" class="btn">Previous</button>` : '<div></div>'}
            <button onclick="nextQuestion()" class="btn btn-primary" id="nextBtn" ${!userAnswers[currentQuestionIndex] ? 'disabled' : ''}>
                ${currentQuestionIndex === currentQuiz.questions.length - 1 ? 'Submit' : 'Next'}
            </button>
        </div>
    `;
    
    startQuizTimer();
}

function startQuizTimer() {
    if (quizTimer) clearInterval(quizTimer);
    const timerEl = document.getElementById('quizTimer');
    
    quizTimer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - quizStartTime) / 1000);
        const m = Math.floor(elapsed / 60).toString().padStart(2, '0');
        const s = (elapsed % 60).toString().padStart(2, '0');
        if(timerEl) timerEl.textContent = `${m}:${s}`;
    }, 1000);
}

window.selectOption = (idx) => {
    userAnswers[currentQuestionIndex] = {
        question_id: currentQuiz.questions[currentQuestionIndex].id,
        selected: idx,
        is_correct: idx === currentQuiz.questions[currentQuestionIndex].correct_answer
    };
    renderQuizQuestion();
};

window.nextQuestion = () => {
    if (currentQuestionIndex < currentQuiz.questions.length - 1) {
        currentQuestionIndex++;
        renderQuizQuestion();
    } else {
        submitQuiz();
    }
};

window.prevQuestion = () => {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        renderQuizQuestion();
    }
};

async function submitQuiz() {
    clearInterval(quizTimer);
    showLoading();
    
    const timeTaken = Math.floor((Date.now() - quizStartTime) / 1000);
    const payload = {
        topic_id: currentQuiz.topic_id,
        answers: userAnswers,
        time_taken: timeTaken
    };
    
    try {
        const response = await fetch('/api/quiz/submit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        displayQuizResult(result);
    } catch (error) {
        console.error('Submit failed:', error);
        showToast('Error submitting quiz', 'error');
    } finally {
        hideLoading();
    }
}

function displayQuizResult(result) {
    const container = document.getElementById('quizContainer');
    container.innerHTML = `
        <div class="quiz-result text-center">
            <div class="result-icon ${result.score >= 80 ? 'excellent' : 'good'}">
                <i class="fas fa-trophy"></i>
            </div>
            <h2>Score: ${Math.round(result.score)}%</h2>
            <p>You got ${result.correct_answers} out of ${result.total_questions} correct.</p>
            <div class="result-actions">
                <button onclick="showSection('overview')" class="btn">Dashboard</button>
                <button onclick="showSection('recommendations')" class="btn btn-primary">Next Steps</button>
            </div>
        </div>
    `;
    loadAnalytics(currentSemester);
}

// ==================== BOOKMARKS & SETTINGS ====================
async function loadBookmarks() {
    try {
        const response = await fetch('/api/bookmarks');
        if (response.ok) {
            const bookmarks = await response.json();
            displayBookmarks(bookmarks);
        }
    } catch (e) { console.error(e); }
}

function displayBookmarks(bookmarks) {
    const container = document.getElementById('bookmarksList');
    if (!bookmarks.length) {
        container.innerHTML = '<p class="text-muted">No bookmarks yet.</p>';
        return;
    }
    container.innerHTML = `
        <div class="resources-grid">
            ${bookmarks.map(b => `
                <div class="resource-card">
                    <h4>${b.title}</h4>
                    <p class="text-muted">${b.subject_name}</p>
                    <div class="resource-actions">
                        <a href="${b.url}" target="_blank" class="btn-small">Open</a>
                        <button onclick="removeBookmark(${b.id})" class="btn-small"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            `).join('')}
        </div>`;
}

async function bookmarkResource(resourceId) {
    await fetch('/api/bookmarks/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({resource_id: resourceId})
    });
    showToast('Bookmarked!', 'success');
}

async function removeBookmark(id) {
    await fetch(`/api/bookmarks/remove/${id}`, { method: 'DELETE' });
    loadBookmarks();
    showToast('Removed', 'info');
}

async function updateSettings(event) {
    event.preventDefault();
    const sem = document.getElementById('settingsSemester').value;
    await fetch('/api/profile/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({semester: sem})
    });
    showToast('Settings Saved', 'success');
    currentSemester = parseInt(sem);
    syncDropdowns(currentSemester);
    loadSubjects(); // Reload everything for new semester setting
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
}

function setTheme(theme) {
    if (theme === 'dark') document.body.classList.add('dark-theme');
    else document.body.classList.remove('dark-theme');
}
