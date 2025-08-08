import React from 'react'
import { ThemeProvider } from '@/components/theme-provider'
import { SkillSelector } from '@/components/skill-selector'

const App = () => {
  return (
    <ThemeProvider defaultTheme="system" storageKey="ai-playground-theme">
      <div className="min-h-screen bg-background font-sans antialiased">
        <SkillSelector />
      </div>
    </ThemeProvider>
  )
}

export default App