import React from 'react'
import { ThemeProvider } from '@/components/theme-provider'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import { SkillSelector } from '@/components/skill-selector'
import LoginPage from '@/components/LoginPage'
import Header from '@/components/Header'
import { Loader2 } from 'lucide-react'

const AppContent = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <Header />
      <main>
        <SkillSelector />
      </main>
    </div>
  );
};

const App = () => {
  return (
    <ThemeProvider defaultTheme="system" storageKey="ai-playground-theme">
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App