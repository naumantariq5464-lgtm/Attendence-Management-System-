/**
 * AMS Frontend API Utility Module
 * 
 * Shared helpers for all frontend pages:
 *  - API_BASE constant
 *  - Token management (localStorage)
 *  - authFetch() — auto-attaches JWT header
 *  - Auth guards for protected pages
 */

// ── API Base URL ──
// When served by FastAPI, frontend is at /static/*, API at /api/*
// During development, both run on the same server
const API_BASE = "https://ams-backend-seven.vercel.app";

// ══════════════════════════════════════════════════
//  TOKEN MANAGEMENT
// ══════════════════════════════════════════════════

function getToken() {
  return localStorage.getItem('ams_token');
}

function setToken(token) {
  localStorage.setItem('ams_token', token);
}

function clearToken() {
  localStorage.removeItem('ams_token');
  localStorage.removeItem('ams_user');
}

function getUser() {
  const raw = localStorage.getItem('ams_user');
  return raw ? JSON.parse(raw) : null;
}

function setUser(user) {
  localStorage.setItem('ams_user', JSON.stringify(user));
}

// ══════════════════════════════════════════════════
//  AUTH FETCH — Adds JWT header automatically
// ══════════════════════════════════════════════════

async function authFetch(url, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });

  // Handle 401: Token expired or invalid
  if (response.status === 401) {
    clearToken();
    window.location.href = '/static/login.html';
    return null;
  }

  return response;
}

// ══════════════════════════════════════════════════
//  AUTH GUARDS
// ══════════════════════════════════════════════════

function requireAuth(requiredRole = null) {
  const token = getToken();
  const user = getUser();

  if (!token || !user) {
    window.location.href = '/static/login.html';
    return false;
  }

  if (requiredRole && user.role !== requiredRole) {
    // Wrong role — redirect to correct dashboard
    if (user.role === 'admin') {
      window.location.href = '/static/admin-dashboard.html';
    } else if (user.role === 'teacher') {
      window.location.href = '/static/teacher-dashboard.html';
    } else {
      window.location.href = '/static/student-dashboard.html';
    }
    return false;
  }

  return true;
}

function isLoggedIn() {
  const user = getUser();
  // Ensure both token exists and user object is properly structured (has name and role)
  return !!getToken() && !!user && !!user.name && !!user.role;
}

function logout() {
  clearToken();
  window.location.href = '/static/login.html';
}

// ══════════════════════════════════════════════════
//  UTILITY HELPERS
// ══════════════════════════════════════════════════

function showApiError(response, defaultMsg = 'Something went wrong.') {
  return response.json().then(data => {
    return data.detail || defaultMsg;
  }).catch(() => defaultMsg);
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function getDayName(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { weekday: 'long' });
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good Morning';
  if (hour < 17) return 'Good Afternoon';
  return 'Good Evening';
}
