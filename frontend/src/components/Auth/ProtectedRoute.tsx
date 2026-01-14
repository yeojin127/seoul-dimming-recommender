import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../../utils/auth';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

/**
 * Protected Route Component
 * Redirects to /login if user is not authenticated
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    if (!isAuthenticated()) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
};
