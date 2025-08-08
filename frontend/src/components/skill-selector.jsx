import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ImageAnalysis } from '@/components/skills/image-analysis'
import { ConversationAnalysis } from '@/components/skills/conversation-analysis'
import { DocumentSummarization } from '@/components/skills/document-summarization'
import { Brain, Image, FileText, MessageSquare } from 'lucide-react'

const SKILLS = [
  {
    id: 'image-analysis',
    name: 'Image Analysis',
    description: 'Upload images and generate detailed textual descriptions',
    icon: Image,
    component: ImageAnalysis
  },
  {
    id: 'conversation-analysis',
    name: 'Conversation Analysis',
    description: 'Upload audio files for speech-to-text and speaker diarization',
    icon: MessageSquare,
    component: ConversationAnalysis
  },
  {
    id: 'document-summarization',
    name: 'Document Summarization',
    description: 'Upload documents (PDF, DOC) or URLs for content summaries',
    icon: FileText,
    component: DocumentSummarization
  }
]

export function SkillSelector() {
  const [selectedSkill, setSelectedSkill] = useState(null)

  const handleSkillChange = (skillId) => {
    const skill = SKILLS.find(s => s.id === skillId)
    setSelectedSkill(skill)
  }

  const SelectedComponent = selectedSkill?.component

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Description */}
      <div className="text-center space-y-2">
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Select an AI skill below to explore multi-modal capabilities including image analysis, 
          conversation processing, and document summarization.
        </p>
      </div>

      {/* Skill Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Choose Your AI Skill
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <select 
              onChange={(e) => handleSkillChange(e.target.value)}
              value={selectedSkill?.id || ""}
              className="w-full px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <option value="" disabled hidden>Select an AI skill to get started...</option>
              {SKILLS.map((skill) => (
                <option key={skill.id} value={skill.id}>
                  {skill.name}
                </option>
              ))}
            </select>
            
            {selectedSkill && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <selectedSkill.icon className="w-4 h-4" />
                {selectedSkill.description}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Selected Skill Component */}
      {selectedSkill && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <selectedSkill.icon className="w-5 h-5 text-primary" />
              {selectedSkill.name}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SelectedComponent />
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      {!selectedSkill && (
        <Card className="bg-muted/50">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {SKILLS.map((skill) => {
                  const IconComponent = skill.icon
                  return (
                    <div key={skill.id} className="p-4 bg-background rounded-lg border">
                      <IconComponent className="w-8 h-8 text-primary mx-auto mb-2" />
                      <h3 className="font-medium text-sm">{skill.name}</h3>
                      <p className="text-xs text-muted-foreground mt-1">
                        {skill.description}
                      </p>
                    </div>
                  )
                })}
              </div>
              <p className="text-sm text-muted-foreground">
                Select a skill from the dropdown above to begin exploring AI capabilities
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
