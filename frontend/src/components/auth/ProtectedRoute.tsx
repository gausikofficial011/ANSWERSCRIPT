import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-viewport">
        <div className="spinner-medium"></div>
        <p>Verifying session details...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>;
};
