import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { MessageSquare } from 'lucide-react'

export function ConversationAnalysis() {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <MessageSquare className="w-4 h-4 text-primary" />
        <h3 className="text-lg font-semibold">Conversation Analysis</h3>
      </div>
      
      <Card className="bg-muted/50">
        <CardContent className="pt-4">
          <div className="text-center space-y-2">
            <MessageSquare className="w-12 h-12 text-muted-foreground mx-auto" />
            <h3 className="font-medium">Coming Soon</h3>
            <p className="text-sm text-muted-foreground">
              Speech-to-text and speaker diarization features will be implemented next.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
