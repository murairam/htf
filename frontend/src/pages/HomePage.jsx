import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BarcodeScanner from '../components/BarcodeScanner'
import Button from '../components/Button'

const HomePage = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    barcode: '',
    objectives: '',
    image: null
  })
  const [imagePreview, setImagePreview] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleBarcodeDetected = (barcode) => {
    setFormData(prev => ({ ...prev, barcode }))
  }

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setFormData(prev => ({ ...prev, image: file }))
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    
    // Validation
    if (!formData.barcode) {
      setError('Please provide a barcode')
      return
    }
    if (!formData.objectives.trim()) {
      setError('Please describe your business objectives')
      return
    }
    if (!formData.image) {
      setError('Please upload a product image')
      return
    }

    setIsSubmitting(true)

    try {
      const formDataToSend = new FormData()
      formDataToSend.append('barcode', formData.barcode)
      formDataToSend.append('objectives', formData.objectives)
      formDataToSend.append('image', formData.image)

      const response = await fetch('/submit/', {
        method: 'POST',
        body: formDataToSend,
      })

      if (!response.ok) {
        throw new Error('Failed to submit analysis')
      }

      const data = await response.json()
      
      // Navigate to results page
      navigate(`/results/${data.analysis_id}`)
      
    } catch (err) {
      console.error('Submission error:', err)
      setError(err.message || 'Failed to submit analysis. Please try again.')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🌱 Plant-Based Packaging Intelligence
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered marketing & packaging analysis for plant-based food innovation
          </p>
        </div>

        {/* Main Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Image Upload */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Product Image</h3>
            <div className="space-y-4">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                required
              />
              {imagePreview && (
                <div className="mt-4">
                  <img
                    src={imagePreview}
                    alt="Product preview"
                    className="max-w-full h-64 object-contain mx-auto rounded-lg border-2 border-gray-200"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Objectives */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Business Objectives</h3>
            <textarea
              value={formData.objectives}
              onChange={(e) => setFormData(prev => ({ ...prev, objectives: e.target.value }))}
              placeholder="Describe your business objectives (e.g., increase visibility, beat competitor, optimize pricing, improve shelf placement...)"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
              rows="5"
              required
            />
            <p className="mt-2 text-sm text-gray-500">
              Example: "Increase shelf visibility in retail stores and outperform competitor X in the plant-based category"
            </p>
          </div>

          {/* Barcode Scanner */}
          <BarcodeScanner onBarcodeDetected={handleBarcodeDetected} />
          
          {formData.barcode && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm font-medium text-green-800">
                ✓ Barcode captured: <span className="font-mono">{formData.barcode}</span>
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-center">
            <Button
              type="submit"
              disabled={isSubmitting}
              className="w-full md:w-auto px-12"
            >
              {isSubmitting ? 'Submitting...' : 'Analyze Product'}
            </Button>
          </div>
        </form>

        {/* Footer Info */}
        <div className="mt-12 text-center text-sm text-gray-500">
          <p>
            This AI-driven system analyzes plant-based food products to provide
            interpretable scores and strategic marketing recommendations.
          </p>
        </div>
      </div>
    </div>
  )
}

export default HomePage
