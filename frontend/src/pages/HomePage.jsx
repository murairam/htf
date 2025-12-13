import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BarcodeScanner from '../components/BarcodeScanner'

const HomePage = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    barcode: '',
    objectives: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleBarcodeDetected = (barcode) => {
    setFormData(prev => ({ ...prev, barcode }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validation
    if (!formData.barcode) {
      setError('Please provide a barcode')
      return
    }
    // Objectives are optional - no validation needed

    setIsSubmitting(true)

    try {
      const formDataToSend = new FormData()
      formDataToSend.append('barcode', formData.barcode)
      formDataToSend.append('objectives', formData.objectives)

      const response = await fetch('/submit/', {
        method: 'POST',
        body: formDataToSend,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Submission failed')
      }

      const data = await response.json()
      navigate(`/results/${data.analysis_id}/`)
    } catch (err) {
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

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Main Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Barcode Scanner */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Product Barcode</h3>
            <BarcodeScanner onBarcodeDetected={handleBarcodeDetected} />
            {formData.barcode && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
                <p className="text-sm text-gray-700">
                  <span className="font-semibold">Detected Barcode:</span>{' '}
                  <span className="font-mono">{formData.barcode}</span>
                </p>
              </div>
            )}
          </div>

          {/* Business Objectives (Optional) */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Business Objectives <span className="text-sm font-normal text-gray-500">(Optional)</span></h3>
            <textarea
              value={formData.objectives}
              onChange={(e) => setFormData(prev => ({ ...prev, objectives: e.target.value }))}
              placeholder="Describe your business objectives (e.g., increase shelf visibility, improve brand perception, optimize pricing strategy, target specific customer segments...)"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
              rows="6"
            />
            <p className="mt-2 text-sm text-gray-500">
              💡 Optional: Be specific about what you want to achieve with your product
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={isSubmitting}
              className={`px-8 py-4 rounded-lg font-semibold text-white text-lg shadow-lg transition-all duration-200 ${
                isSubmitting
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 hover:shadow-xl transform hover:scale-105'
              }`}
            >
              {isSubmitting ? (
                <span className="flex items-center space-x-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Analyzing...</span>
                </span>
              ) : (
                '🚀 Analyze Product'
              )}
            </button>
          </div>
        </form>

        {/* Info Section */}
        <div className="mt-12 bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">How It Works</h3>
          <div className="space-y-3 text-gray-700">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">1️⃣</span>
              <div>
                <p className="font-semibold">Scan or Enter Barcode</p>
                <p className="text-sm text-gray-600">Use your camera to scan the product barcode or enter it manually</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <span className="text-2xl">2️⃣</span>
              <div>
                <p className="font-semibold">Define Your Objectives</p>
                <p className="text-sm text-gray-600">Tell us what you want to achieve with your product</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <span className="text-2xl">3️⃣</span>
              <div>
                <p className="font-semibold">Get AI-Powered Insights</p>
                <p className="text-sm text-gray-600">Receive detailed scores, SWOT analysis, and strategic recommendations</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
