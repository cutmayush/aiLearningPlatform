// ==================== AUTHENTICATION FUNCTIONS ====================

function toggleForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    loginForm.classList.toggle('active');
    registerForm.classList.toggle('active');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    const data = {
        username: formData.get('username'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showToast(result.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm-password');
    
    // Validate passwords match
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: password
    };
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Registration successful! Please login.', 'success');
            setTimeout(() => {
                toggleForms();
                form.reset();
            }, 1500);
        } else {
            showToast(result.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

// ==================== FORM VALIDATION ====================

document.addEventListener('DOMContentLoaded', () => {
    // Add real-time validation
    const inputs = document.querySelectorAll('input');
    
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            validateInput(input);
        });
        
        input.addEventListener('input', () => {
            if (input.classList.contains('error')) {
                validateInput(input);
            }
        });
    });
});

function validateInput(input) {
    const value = input.value.trim();
    
    // Remove previous error
    input.classList.remove('error');
    const existingError = input.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Validate based on type
    if (input.required && !value) {
        showInputError(input, 'This field is required');
        return false;
    }
    
    if (input.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showInputError(input, 'Please enter a valid email');
            return false;
        }
    }
    
    if (input.type === 'password' && value && input.minLength) {
        if (value.length < input.minLength) {
            showInputError(input, `Password must be at least ${input.minLength} characters`);
            return false;
        }
    }
    
    return true;
}

function showInputError(input, message) {
    input.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = 'var(--danger)';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    
    input.parentElement.appendChild(errorDiv);
}

// ==================== KEYBOARD SHORTCUTS ====================

document.addEventListener('keydown', (e) => {
    // Alt + L to focus login
    if (e.altKey && e.key === 'l') {
        e.preventDefault();
        const loginForm = document.getElementById('loginForm');
        if (!loginForm.classList.contains('active')) {
            toggleForms();
        }
        document.getElementById('login-username').focus();
    }
    
    // Alt + R to focus register
    if (e.altKey && e.key === 'r') {
        e.preventDefault();
        const registerForm = document.getElementById('registerForm');
        if (!registerForm.classList.contains('active')) {
            toggleForms();
        }
        document.getElementById('register-username').focus();
    }
});
