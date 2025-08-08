import React from 'react';
import { LogOut, User, Brain } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { ThemeToggle } from './theme-toggle';

const Header = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center gap-3">
          <Brain className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              AI Playground
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Multi-modal AI capabilities
            </p>
          </div>
        </div>

        {/* User Info and Actions */}
        <div className="flex items-center gap-4">
          <ThemeToggle />
          
          {/* User Profile */}
          <div className="flex items-center gap-3 px-3 py-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <User className="w-5 h-5 text-gray-400" />
            <div className="text-sm">
              <div className="font-medium text-gray-900 dark:text-white">
                {user?.name}
              </div>
              <div className="text-gray-500 dark:text-gray-400">
                {user?.email}
              </div>
            </div>
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-3 py-2 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
