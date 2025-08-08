import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

// Dummy credentials
const DUMMY_USERS = [
  {
    email: 'admin@plivo.com',
    password: 'admin123',
    name: 'Admin User',
    role: 'admin'
  },
  {
    email: 'user@plivo.com',
    password: 'user123',
    name: 'Regular User',
    role: 'user'
  },
  {
    email: 'test@test.com',
    password: 'test123',
    name: 'Test User',
    role: 'user'
  }
];

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app start
    const savedUser = localStorage.getItem('auth_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email, password) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const foundUser = DUMMY_USERS.find(
      u => u.email === email && u.password === password
    );

    if (foundUser) {
      const userToStore = {
        email: foundUser.email,
        name: foundUser.name,
        role: foundUser.role
      };
      setUser(userToStore);
      localStorage.setItem('auth_user', JSON.stringify(userToStore));
      return { success: true, user: userToStore };
    } else {
      return { success: false, error: 'Invalid email or password' };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('auth_user');
  };

  const value = {
    user,
    login,
    logout,
    isLoading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
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
