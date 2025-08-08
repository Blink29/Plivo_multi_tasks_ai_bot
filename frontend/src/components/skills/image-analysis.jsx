import React, { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Upload, Image as ImageIcon, Loader2, Eye, FileImage } from 'lucide-react'
import { MarkdownRenderer } from '@/components/markdown-renderer'

const API_BASE_URL = 'http://localhost:8000'

export function ImageAnalysis() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
      if (!validTypes.includes(file.type)) {
        setError('Please select a valid image file (JPEG, PNG, GIF, or WebP)')
        return
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB')
        return
      }

      setSelectedFile(file)
      setError(null)
      setAnalysis(null)

      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleAnalyze = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!selectedFile) return

    setIsAnalyzing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('image', selectedFile)

      const response = await fetch(`${API_BASE_URL}/api/analyze-image`, {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        setAnalysis(data.analysis)
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to analyze image')
      }
    } catch (error) {
      console.error('Error analyzing image:', error)
      setError(error.message || 'Failed to analyze image. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    setSelectedFile(null)
    setPreview(null)
    setAnalysis(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <FileImage className="w-4 h-4 text-primary" />
          <h3 className="text-lg font-semibold">Upload Image</h3>
        </div>
        
        <div 
          className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center hover:border-primary/50 transition-colors"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          {preview ? (
            <div className="space-y-4">
              <img 
                src={preview} 
                alt="Preview" 
                className="max-w-full max-h-64 mx-auto rounded-lg shadow-md"
              />
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                </p>
                <div className="flex gap-2 justify-center">
                  <Button 
                    onClick={handleAnalyze} 
                    disabled={isAnalyzing} 
                    className="gap-2"
                    type="button"
                  >
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Eye className="w-4 h-4" />
                        Analyze Image
                      </>
                    )}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={handleReset}
                    type="button"
                  >
                    Choose Different Image
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div 
              className="space-y-4 cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <ImageIcon className="w-12 h-12 text-muted-foreground mx-auto" />
              <div className="space-y-2">
                <h3 className="text-lg font-medium">Upload an Image</h3>
                <p className="text-muted-foreground">
                  Click here or drag and drop an image file
                </p>
                <p className="text-sm text-muted-foreground">
                  Supports JPEG, PNG, GIF, WebP (max 10MB)
                </p>
              </div>
              <Button className="gap-2" type="button">
                <Upload className="w-4 h-4" />
                Select Image
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="pt-4">
            <p className="text-destructive text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-primary" />
            <h3 className="text-lg font-semibold">Image Analysis</h3>
            <Badge variant="secondary" className="gap-1">
              <ImageIcon className="w-3 h-3" />
              AI Generated
            </Badge>
          </div>
          
          <Card>
            <CardContent className="pt-4">
              <MarkdownRenderer content={analysis} />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Instructions */}
      {!selectedFile && !analysis && (
        <Card className="bg-muted/50">
          <CardContent className="pt-4">
            <div className="space-y-2">
              <h4 className="font-medium text-sm">How it works:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Upload any image file (JPEG, PNG, GIF, WebP)</li>
                <li>• Our AI will analyze the image content</li>
                <li>• Get detailed descriptions of objects, scenes, text, and more</li>
                <li>• Perfect for accessibility, content moderation, or general analysis</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
