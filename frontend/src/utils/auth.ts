/**
 * Mock Authentication Utilities
 * Uses localStorage for simple auth state management
 */

const AUTH_KEY = 'auth';

// Mock credentials
const MOCK_CREDENTIALS = {
    id: 'admin',
    password: 'seoul1234'
};

/**
 * Attempt to login with provided credentials
 * @returns true if successful, false otherwise
 */
export function login(id: string, password: string): boolean {
    if (id === MOCK_CREDENTIALS.id && password === MOCK_CREDENTIALS.password) {
        localStorage.setItem(AUTH_KEY, 'true');
        return true;
    }
    return false;
}

/**
 * Logout the current user
 */
export function logout(): void {
    localStorage.removeItem(AUTH_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
    return localStorage.getItem(AUTH_KEY) === 'true';
}
