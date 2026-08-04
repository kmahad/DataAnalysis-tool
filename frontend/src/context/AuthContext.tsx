import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../api/client';

interface AuthContextType {
  token: string | null;
  username: string | null;
  isAuthenticated: boolean;
  login: (token: string, username: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('datapurify_token'));
  const [username, setUsername] = useState<string | null>(localStorage.getItem('datapurify_user'));

  useEffect(() => {
    if (token && !username) {
      api.getMe()
        .then((res) => {
          setUsername(res.username);
          localStorage.setItem('datapurify_user', res.username);
        })
        .catch(() => logout());
    }
  }, [token]);

  const login = (newToken: string, newUsername: string) => {
    setToken(newToken);
    setUsername(newUsername);
    localStorage.setItem('datapurify_token', newToken);
    localStorage.setItem('datapurify_user', newUsername);
  };

  const logout = () => {
    setToken(null);
    setUsername(null);
    localStorage.removeItem('datapurify_token');
    localStorage.removeItem('datapurify_user');
  };

  return (
    <AuthContext.Provider value={{ token, username, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
