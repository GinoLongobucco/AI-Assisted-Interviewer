const API_URL = "http://localhost:8000";

/**
 * Admin authentication and management service
 */

// Helper to get token from localStorage
const getToken = () => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('adminToken');
    }
    return null;
};

// Helper to set token in localStorage
const setToken = (token) => {
    if (typeof window !== 'undefined') {
        localStorage.setItem('adminToken', token);
    }
};

// Helper to remove token
export const logout = () => {
    if (typeof window !== 'undefined') {
        localStorage.removeItem('adminToken');
        localStorage.removeItem('adminEmail');
    }
};

/**
 * Admin login
 */
export async function adminLogin(email, password) {
    const res = await fetch(`${API_URL}/api/admin/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Login failed");
    }

    const data = await res.json();

    // Store token and email
    setToken(data.access_token);
    if (typeof window !== 'undefined') {
        localStorage.setItem('adminEmail', data.admin.email);
    }

    return data;
}

/**
 * Get all interviews with pagination and filters
 */
export async function getInterviews(page = 1, limit = 20, filters = {}) {
    const token = getToken();
    if (!token) {
        throw new Error("Not authenticated");
    }

    const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
    });

    if (filters.role) {
        params.append('role', filters.role);
    }
    if (filters.email) {
        params.append('email', filters.email);
    }

    const res = await fetch(`${API_URL}/api/admin/interviews?${params}`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    });

    if (!res.ok) {
        if (res.status === 401) {
            logout();
            throw new Error("Authentication expired. Please login again.");
        }
        throw new Error("Error fetching interviews");
    }

    return await res.json();
}

/**
 * Get detailed interview data
 */
export async function getInterviewDetail(interviewId) {
    const token = getToken();
    if (!token) {
        throw new Error("Not authenticated");
    }

    const res = await fetch(`${API_URL}/api/admin/interviews/${interviewId}`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    });

    if (!res.ok) {
        if (res.status === 401) {
            logout();
            throw new Error("Authentication expired. Please login again.");
        }
        throw new Error("Error fetching interview details");
    }

    return await res.json();
}

/**
 * Get current configuration
 */
export async function getAdminConfig() {
    const token = getToken();
    if (!token) {
        throw new Error("Not authenticated");
    }

    const res = await fetch(`${API_URL}/api/admin/config`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    });

    if (!res.ok) {
        if (res.status === 401) {
            logout();
            throw new Error("Authentication expired. Please login again.");
        }
        throw new Error("Error fetching configuration");
    }

    return await res.json();
}

/**
 * Update configuration
 */
export async function updateAdminConfig(config) {
    const token = getToken();
    if (!token) {
        throw new Error("Not authenticated");
    }

    const res = await fetch(`${API_URL}/api/admin/config`, {
        method: "PUT",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(config),
    });

    if (!res.ok) {
        if (res.status === 401) {
            logout();
            throw new Error("Authentication expired. Please login again.");
        }
        const error = await res.json();
        throw new Error(error.detail || "Error updating configuration");
    }

    return await res.json();
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
    return !!getToken();
}

/**
 * Get stored admin email
 */
export function getAdminEmail() {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('adminEmail');
    }
    return null;
}
