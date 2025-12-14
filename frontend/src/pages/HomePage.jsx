import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BarcodeScanner from '../components/BarcodeScanner'
import Header from '../components/Header'
import Footer from '../components/Footer'
import '../styles/cal-inspired.css'

const HomePage = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    business_objective: '',
    barcode: '',
    product_link: '',
    product_description: ''
  })
  const [inputMethod, setInputMethod] = useState('barcode')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleBarcodeDetected = (barcode) => {
    setFormData(prev => ({ ...prev, barcode }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!formData.business_objective || !formData.business_objective.trim()) {
      setError('Business objective is required')
      return
    }

    const hasBarcode = formData.barcode && formData.barcode.trim()
    const hasLink = formData.product_link && formData.product_link.trim()
    const hasDescription = formData.product_description && formData.product_description.trim()

    if (!hasBarcode && !hasLink && !hasDescription) {
      setError('Please provide at least one: barcode, product link, or product description')
      return
    }

    setIsSubmitting(true)

    try {
      const payload = {
        business_objective: formData.business_objective.trim()
      }

      if (hasBarcode) {
        payload.barcode = formData.barcode.trim()
      }
      if (hasLink) {
        payload.product_link = formData.product_link.trim()
      }
      if (hasDescription) {
        payload.product_description = formData.product_description.trim()
      }

      const response = await fetch('/submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
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
    <div className="min-h-screen bg-white flex flex-col">
      <Header />
      
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container mx-auto px-4 text-center">
          <div className="badge mb-4">Plant-Based Intelligence Platform</div>
          <h1 className="hero-title">
            The better way to analyze<br />
            your product packaging
          </h1>
          <p className="hero-subtitle">
            AI-powered marketing & packaging analysis for plant-based food innovation.
            Get comprehensive insights from multiple AI agents in one unified report.
          </p>
        </div>
      </section>

      {/* Main Form Section */}
      <section className="section bg-white">
        <div className="container mx-auto px-4 max-w-4xl">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <div className="card card-elevated">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Business Objective */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Business Objective <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.business_objective}
                  onChange={(e) => setFormData(prev => ({ ...prev, business_objective: e.target.value }))}
                  placeholder="Describe your business objectives (e.g., increase flexitarian appeal, improve shelf visibility, optimize pricing strategy...)"
                  className="textarea-field"
                  rows="4"
                  required
                />
                <p className="mt-2 text-sm text-gray-500">
                  Required: Be specific about what you want to achieve
                </p>
              </div>

              {/* Input Method Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-4">
                  Product Information
                </label>
                <p className="text-sm text-gray-600 mb-4">
                  Choose one method to identify your product:
                </p>
                
                {/* Method Tabs */}
                <div className="flex space-x-2 mb-6 border-b border-gray-200">
                  <button
                    type="button"
                    onClick={() => setInputMethod('barcode')}
                    className={`px-4 py-2 font-medium transition-colors border-b-2 flex items-center space-x-2 ${
                      inputMethod === 'barcode'
                        ? 'border-gray-900 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span>Barcode</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setInputMethod('link')}
                    className={`px-4 py-2 font-medium transition-colors border-b-2 flex items-center space-x-2 ${
                      inputMethod === 'link'
                        ? 'border-gray-900 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    <span>Product Link</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setInputMethod('description')}
                    className={`px-4 py-2 font-medium transition-colors border-b-2 flex items-center space-x-2 ${
                      inputMethod === 'description'
                        ? 'border-gray-900 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <span>Description</span>
                  </button>
                </div>

                {/* Barcode Input */}
                {inputMethod === 'barcode' && (
                  <div>
                    <BarcodeScanner onBarcodeDetected={handleBarcodeDetected} />
                    {formData.barcode && (
                      <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <p className="text-sm text-gray-700">
                          <span className="font-semibold">Detected Barcode:</span>{' '}
                          <span className="font-mono">{formData.barcode}</span>
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Product Link Input */}
                {inputMethod === 'link' && (
                  <div>
                    <input
                      type="url"
                      value={formData.product_link}
                      onChange={(e) => setFormData(prev => ({ ...prev, product_link: e.target.value }))}
                      placeholder="https://www.openfoodfacts.org/product/..."
                      className="input-field"
                    />
                    <p className="mt-2 text-sm text-gray-500">
                      Enter a product URL (e.g., OpenFoodFacts, product website)
                    </p>
                  </div>
                )}

                {/* Product Description Input */}
                {inputMethod === 'description' && (
                  <div>
                    <textarea
                      value={formData.product_description}
                      onChange={(e) => setFormData(prev => ({ ...prev, product_description: e.target.value }))}
                      placeholder="Describe your product (e.g., Plant-based chocolate spread made from hazelnuts and cocoa, suitable for vegans...)"
                      className="textarea-field"
                      rows="4"
                    />
                    <p className="mt-2 text-sm text-gray-500">
                      Provide a detailed description of your product
                    </p>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <div className="flex justify-center pt-4">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`btn-primary ${
                    isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
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
                    <span className="flex items-center space-x-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      <span>Analyze Product</span>
                    </span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="section bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <div className="badge mb-4">How it works</div>
            <h2 className="section-title">
              With us, product analysis is easy
            </h2>
            <p className="section-subtitle">
              Effortless analysis for businesses and individuals, powerful solutions for fast-growing modern companies.
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">01. Provide Product Info</h3>
              <p className="text-gray-600">
                Use barcode scan, product link, or description. We'll handle all the data gathering automatically.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">02. Define Your Objective</h3>
              <p className="text-gray-600">
                Tell us what you want to achieve. We'll tailor the analysis to your specific business goals.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-2">03. Get AI-Powered Insights</h3>
              <p className="text-gray-600">
                Receive comprehensive analysis from multiple AI agents, all unified in one complete report.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="section bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <div className="badge mb-4">Benefits</div>
            <h2 className="section-title">
              Your all-purpose product intelligence app
            </h2>
            <p className="section-subtitle">
              Discover a variety of our advanced features. Comprehensive analysis for plant-based food innovation.
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold mb-2">Comprehensive Scoring</h3>
              <p className="text-gray-600 text-sm">
                Get detailed scores for attractiveness, utility, and positioning with evidence-based explanations.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg className="w-8 h-8 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold mb-2">Image Analysis</h3>
              <p className="text-gray-600 text-sm">
                Automatic package analysis with visual observations and detected problems.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold mb-2">SWOT Analysis</h3>
              <p className="text-gray-600 text-sm">
                Complete strengths, weaknesses, and risks analysis for strategic planning.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold mb-2">Improvement Proposals</h3>
              <p className="text-gray-600 text-sm">
                Actionable recommendations for packaging and marketing improvements.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold mb-2">Go-to-Market Strategy</h3>
              <p className="text-gray-600 text-sm">
                Strategic guidance for shelf positioning, regional relevance, and B2B targeting.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg className="w-8 h-8 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold mb-2">Market Intelligence</h3>
              <p className="text-gray-600 text-sm">
                Competitor analysis and research insights from Plant-Based Intelligence Platform.
              </p>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

export default HomePage
