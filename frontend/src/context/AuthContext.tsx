/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { client } from '../api/client';

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = async () => {
    try {
      const response = await client.get('/auth/me');
      setUser(response.data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        await fetchCurrentUser();
      } else {
        setLoading(false);
      }
    };

    initAuth();

    // Listen to global logout events from axios interceptor
    const handleGlobalLogout = () => {
      setUser(null);
      setLoading(false);
    };

    window.addEventListener('auth_logout', handleGlobalLogout);
    return () => {
      window.removeEventListener('auth_logout', handleGlobalLogout);
    };
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await client.post('/auth/login', { email, password });
      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);
      
      const meResponse = await client.get('/auth/me');
      setUser(meResponse.data);
    } catch (error) {
      setUser(null);
      throw error;
    }
  };

  const logout = async () => {
    try {
      // Defer refresh-token logic, pass empty refresh token for compatibility
      await client.post('/auth/logout', { refresh_token: '' });
    } catch (error) {
      console.error('Logout request failed or refresh token deferred:', error);
    } finally {
      localStorage.removeItem('access_token');
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

