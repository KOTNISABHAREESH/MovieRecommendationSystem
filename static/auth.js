// Authentication related JavaScript functions

// Check if user is logged in
function isLoggedIn() {
    return localStorage.getItem('currentUser') !== null;
}

// Get current user information
function getCurrentUser() {
    const userJson = localStorage.getItem('currentUser');
    return userJson ? JSON.parse(userJson) : null;
}

// Logout function
function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = '/login';
}

// Redirect to login if not logged in
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Update UI based on authentication status
function updateAuthUI() {
    const authLinks = document.getElementById('auth-links');
    if (!authLinks) return;
    
    if (isLoggedIn()) {
        const user = getCurrentUser();
        authLinks.innerHTML = `
            <span class="user-greeting">Welcome, ${user.name}</span>
            <button id="logout-btn" class="auth-btn-small">Logout</button>
        `;
        
        // Add event listener to logout button
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
        }
    } else {
        authLinks.innerHTML = `
            <a href="/login" class="auth-link">Login</a>
            <a href="/signup" class="auth-link">Sign Up</a>
        `;
    }
}

// Initialize authentication
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a protected page (not login, signup, forgot password, or reset password)
    const path = window.location.pathname;
    const authPages = ['/login', '/signup', '/forgot-password', '/reset-password'];
    
    if (!authPages.includes(path)) {
        // This is a protected page, require authentication
        if (!requireAuth()) {
            return; // Stop execution if redirected
        }
    } else if (isLoggedIn() && authPages.includes(path)) {
        // User is already logged in and trying to access an auth page, redirect to home
        window.location.href = '/';
        return;
    }
    
    // Update UI based on authentication status
    updateAuthUI();
});