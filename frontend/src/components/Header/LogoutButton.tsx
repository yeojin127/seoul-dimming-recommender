import React from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../../utils/auth';

export const LogoutButton: React.FC = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <button onClick={handleLogout} className="logout-button">
            로그아웃
        </button>
    );
};
