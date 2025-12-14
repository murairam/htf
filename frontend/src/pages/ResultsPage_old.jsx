import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { Tab } from '@headlessui/react'
import ProgressBar from '../components/ProgressBar'
import Accordion from '../components/Accordion'
import KeyValueRenderer from '../components/KeyValueRenderer'
import VisualsRenderer from '../components/VisualsRenderer'
import CompetitorIntelligence from '../components/CompetitorIntelligence'
import MarketingStrategyEssence from '../components/MarketingStrategyEssence'
import ResearchInsights from '../components/ResearchInsights'
import Header from '../components/Header'
import Footer from '../components/Footer'
import '../styles/cal-inspired.css'

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

const ResultsPage = () => {
  const { analysisId } = useParams()
  const [status, setStatus] = useState('connecting')
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('Connecting...')
  const [results, setResults] = useState(null) // Full unified response from API_Final_Agent
  const [showDebug, setShowDebug] = useState(false) // Debug panel toggle
  const [error, setError] = useState(null)
  const wsRef = useRef(null)

  // Load saved result on mount (reload-safe)
  useEffect(() => {
    const loadSavedResult = async () => {
      try {
        const response = await fetch(`/api/results/${analysisId}/`)
        const data = await response.json()
        
        if (data.success && data.result) {
          // Result already exists - load it
          setResults(data.result)
          setStatus('completed')
          setProgress(100)
          setMessage('Analysis complete!')
          return true // Indicate we loaded saved result
        }
      } catch (err) {
        console.log('No saved result found or error loading:', err)
      }
      return false
    }

    loadSavedResult().then((loaded) => {
      // Only connect WebSocket if we didn't load a saved result
      if (!loaded) {
        connectWebSocket()
      }
    })
  }, [analysisId])

  const connectWebSocket = () => {
    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/analysis/${analysisId}/`
    
    console.log('Connecting to WebSocket:', wsUrl)
    
    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        setStatus('connected')
        setMessage('Connected. Starting analysis...')
      }

      ws.onmessage = (event) => {
        console.log('WebSocket message:', event.data)
        const data = JSON.parse(event.data)

        if (data.type === 'status') {
          setStatus(data.status)
          setProgress(data.progress || 0)
          setMessage(data.message || '')
          
          if (data.status === 'error') {
            setError(data.message)
          }
        } else if (data.type === 'final_result') {
          // data.payload is the unified JSON from API_Final_Agent
          // Contains: analysis_id, input, status, merged, raw_sources, errors
          setResults(data.payload)
          setStatus('completed')
          setProgress(100)
          setMessage('Analysis complete!')
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setError('Connection error. Please refresh the page.')
        setStatus('error')
      }

      ws.onclose = () => {
        console.log('WebSocket closed')
      }

    } catch (err) {
      console.error('Failed to create WebSocket:', err)
      setError('Failed to connect. Please refresh the page.')
      setStatus('error')
    }

    // Cleanup
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }

  // Helper function to safely get nested values
  const getNestedValue = (obj, path, defaultValue = null) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj) || defaultValue
  }

  // Get merged data (default display) or fallback to full results for backward compatibility
  const getMergedData = () => {
    if (!results) return null
    // API_Final_Agent returns {merged, raw_sources, ...}
    // Use merged by default, fallback to results for old format
    return results.merged || results
  }

  // Extract image URL - support both old and new format
  const getImageUrl = () => {
    if (!results) return null
    const merged = getMergedData()
    // Try new format first (from product_information or root)
    return results.image_front_url || 
           getNestedValue(merged, 'product_information.image_front_url') ||
           getNestedValue(merged, 'product_information.ace.image_front_url') ||
           getNestedValue(merged, 'product_information.essence.image_front_url') ||
           null
  }

  // Extract scores - adapt to new format with _score suffix
  const getScores = () => {
    if (!results) return null
    const merged = getMergedData()
    
    // Try merged.scoring_results first, then fallback
    let scores = merged.scoring_results?.scores || 
                 merged.scoring_results?.ace?.scores ||
                 merged.scoring_results?.essence?.scores ||
                 merged.scores || 
                 {}
    
    // Map new format to display format (handle both _score suffix and without)
    const mappedScores = {
      attractiveness: scores.attractiveness_score ?? scores.attractiveness,
      utility: scores.utility_score ?? scores.utility,
      positioning: scores.positioning_score ?? scores.positioning,
      global: scores.global_score ?? scores.global
    }
    
    // Return null only if all scores are undefined/null
    const hasAnyScore = Object.values(mappedScores).some(v => v !== undefined && v !== null)
    return hasAnyScore ? mappedScores : null
  }

  // Extract product info - adapt to new nested structure
  const getProductInfo = () => {
    if (!results) return {}
    const merged = getMergedData()
    
    // Try merged structure first
    const productInfo = merged.product_information || {}
    const basicInfo = productInfo.basic_info || productInfo.ace?.basic_info || productInfo.essence?.basic_info || {}
    const businessObj = merged.business_objective || results.input?.business_objective || {}
    
    return {
      barcode: results.input?.barcode || basicInfo.product_id || results.barcode,
      objectives: businessObj.objective_description || 
                  results.input?.business_objective || 
                  results.objectives || 
                  businessObj,
      name: basicInfo.name,
      brand: basicInfo.brand,
      category: basicInfo.category,
      productId: basicInfo.product_id
    }
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <div className="text-center">
            <div className="mb-4 flex justify-center">
              <svg className="w-16 h-16 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="btn-primary"
            >
              Retry
            </button>
          </div>
        </div>
        <Footer />
      </div>
    )
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="card card-elevated max-w-2xl w-full">
            <div className="text-center mb-6">
              <div className="text-6xl mb-4 text-blue-500">
                <svg className="w-16 h-16 mx-auto animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Analyzing Your Product</h2>
              <p className="text-gray-600">{message}</p>
            </div>
            
            <div className="space-y-4">
              <ProgressBar value={progress} max={100} label="Analysis Progress" />
              
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600"></div>
                <span>Processing...</span>
              </div>
            </div>
          </div>
        </div>
        <Footer />
      </div>
    )
  }

  const scores = getScores()
  const imageUrl = getImageUrl()
  const productInfo = getProductInfo()
  
  // Debug: Log scores structure
  if (results && !scores) {
    console.log('Warning: Scores not found. Results structure:', {
      hasScoringResults: !!results.scoring_results,
      scoringResults: results.scoring_results,
      hasScores: !!results.scores,
      scores: results.scores
    })
  }
  
  // Extract data from new format
  // Use merged data for all extractions
  const merged = getMergedData()
  
  // Extract packaging proposals - handle multiple formats
  let packagingProposals = []
  const rawPackaging = merged?.packaging_improvements || merged?.packaging_improvement_proposals
  if (Array.isArray(rawPackaging)) {
    packagingProposals = rawPackaging
  } else if (rawPackaging && typeof rawPackaging === 'object') {
    // If it's an object, try to extract proposals array or convert to array
    packagingProposals = rawPackaging.proposals || Object.values(rawPackaging).filter(v => typeof v === 'string' || (v && typeof v === 'object'))
  }
  
  const gtmStrategy = merged?.go_to_market_strategies?.[0]?.strategy || merged?.go_to_market_strategy || {}
  const swotAnalysis = merged?.swot_analysis?.[0]?.analysis || merged?.swot_analysis || {}
  const imageAnalysis = merged?.image_analysis || {}
  const evidenceExplanations = merged?.evidence_based_explanations || {}
  const qualityInsights = merged?.quality_insights || {}
  const criteriaBreakdown = merged?.scoring_results?.criteria_breakdown || {}
  const confidenceLevel = merged?.scoring_results?.confidence_level || results?.status

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header />
      <div className="container mx-auto px-4 py-8 max-w-7xl flex-1">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="badge mb-4">Analysis Results</div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Product Analysis Dashboard
          </h1>
          <p className="text-gray-600 mb-2">Analysis ID: <span className="font-mono text-sm">{analysisId}</span></p>
          {confidenceLevel && (
            <p className="text-sm text-gray-500">
              Confidence Level: <span className="font-semibold capitalize">{confidenceLevel}</span>
            </p>
          )}
        </div>

        {/* Tabs Navigation */}
        <Tab.Group>
          <Tab.List className="flex space-x-1 rounded-xl bg-gradient-to-r from-blue-100 to-indigo-100 p-1 mb-8 shadow-lg">
            {['Overview', 'Competitor Intelligence', 'Marketing Strategy', 'Research Insights', 'ACE Analysis'].map((tab) => (
              <Tab
                key={tab}
                className={({ selected }) =>
                  classNames(
                    'w-full rounded-lg py-3 px-4 text-sm font-semibold leading-5 transition-all duration-200',
                    'focus:outline-none focus:ring-2 ring-offset-2 ring-offset-blue-400 ring-white ring-opacity-60',
                    selected
                      ? 'bg-white text-blue-700 shadow-md transform scale-105'
                      : 'text-gray-700 hover:bg-white/[0.5] hover:text-blue-600'
                  )
                }
              >
                {tab}
              </Tab>
            ))}
          </Tab.List>

          <Tab.Panels>
            {/* Overview Tab */}
            <Tab.Panel>
              <div className="grid lg:grid-cols-2 gap-6">
          
          {/* LEFT COLUMN - Image & Scores */}
          <div className="space-y-6">
            
            {/* Product Image - Only show if image_front_url exists */}
            {imageUrl && (
              <div className="card card-elevated">
                <h2 className="text-xl font-bold mb-4 text-gray-900">Product Image</h2>
                <img
                  src={imageUrl}
                  alt="Product"
                  className="w-full h-80 object-contain rounded-lg border-2 border-gray-200 bg-gray-50"
                  onError={(e) => {
                    e.target.style.display = 'none'
                    e.target.parentElement.innerHTML = '<p class="text-gray-500 text-center py-8">Image not available</p>'
                  }}
                />
              </div>
            )}

            {/* Product Details */}
            <div className="card card-elevated">
              <h2 className="text-xl font-bold mb-4 text-gray-900">Product Details</h2>
              <div className="space-y-3">
                {productInfo.name && (
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Product Name</p>
                    <p className="text-gray-900">{productInfo.name}</p>
                  </div>
                )}
                {productInfo.brand && (
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Brand</p>
                    <p className="text-gray-900">{productInfo.brand}</p>
                  </div>
                )}
                {productInfo.productId && (
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Product ID</p>
                    <p className="text-gray-900 font-mono">{productInfo.productId}</p>
                  </div>
                )}
                {productInfo.barcode && (
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Barcode</p>
                    <p className="text-gray-900 font-mono">{productInfo.barcode}</p>
                  </div>
                )}
                {productInfo.category && (
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Category</p>
                    <p className="text-gray-900">{productInfo.category}</p>
                  </div>
                )}
                {productInfo.objectives && (
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Business Objectives</p>
                    <p className="text-gray-900">{productInfo.objectives}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Performance Scores */}
            {scores && (
              <div className="card card-elevated">
                <h2 className="text-xl font-bold mb-6 text-gray-900">Performance Scores</h2>
                <div className="space-y-4">
                  {(scores.attractiveness !== undefined && scores.attractiveness !== null) && (
                    <ProgressBar
                      value={Number(scores.attractiveness)}
                      label="Attractiveness / Visibility"
                      showValue={true}
                    />
                  )}
                  {(scores.utility !== undefined && scores.utility !== null) && (
                    <ProgressBar
                      value={Number(scores.utility)}
                      label="Utility & Value"
                      showValue={true}
                    />
                  )}
                  {(scores.positioning !== undefined && scores.positioning !== null) && (
                    <ProgressBar
                      value={Number(scores.positioning)}
                      label="Positioning"
                      showValue={true}
                    />
                  )}
                  
                  {/* Global Score - Highlighted */}
                  {(scores.global !== undefined && scores.global !== null) && (
                    <div className="mt-6 pt-6 border-t-2 border-gray-300">
                      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border-2 border-green-500">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <svg className="w-6 h-6 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                            <h3 className="text-lg font-bold text-gray-900">Global Score</h3>
                          </div>
                          <div className="text-3xl font-bold text-green-600">
                            {Number(scores.global).toFixed(1)}
                            <span className="text-lg text-gray-500">/100</span>
                          </div>
                        </div>
                        <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="absolute top-0 left-0 h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full transition-all duration-500 shadow-lg"
                            style={{ width: `${Number(scores.global)}%` }}
                          >
                            <div className="absolute inset-0 bg-white opacity-20 animate-pulse"></div>
                          </div>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 text-center italic">
                          Overall performance based on all metrics
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Image Analysis - New Section */}
            {imageAnalysis.package_description && (
              <div className="card card-elevated">
                <h2 className="text-xl font-bold mb-4 text-gray-900">Image Analysis</h2>
                <p className="text-gray-700 mb-4">{imageAnalysis.package_description}</p>
                
                {imageAnalysis.visual_observations && imageAnalysis.visual_observations.length > 0 && (
                  <div className="mb-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Visual Observations</h3>
                    <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                      {imageAnalysis.visual_observations.map((obs, idx) => (
                        <li key={idx}>{obs}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {imageAnalysis.detected_problems && imageAnalysis.detected_problems.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Detected Problems</h3>
                    <div className="space-y-2">
                      {imageAnalysis.detected_problems.map((problem, idx) => (
                        <div key={idx} className="border-l-4 border-red-400 pl-3 py-2 bg-red-50 rounded">
                          <p className="text-sm font-semibold text-gray-900">{problem.probleme}</p>
                          {problem.indice_visuel && (
                            <p className="text-xs text-gray-600 mt-1">Tip: {problem.indice_visuel}</p>
                          )}
                          <div className="flex items-center space-x-2 mt-2">
                            {problem.gravite && (
                              <span className={`text-xs px-2 py-1 rounded ${
                                problem.gravite === 'Important' || problem.gravite === 'Critique'
                                  ? 'bg-red-200 text-red-800'
                                  : 'bg-yellow-200 text-yellow-800'
                              }`}>
                                {problem.gravite}
                              </span>
                            )}
                            {problem.impact && (
                              <span className="text-xs text-gray-600">Impact: {problem.impact}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* RIGHT COLUMN - Recommendations (Accordions) */}
          <div className="space-y-6">
            <div className="card card-elevated">
              <h2 className="text-xl font-bold mb-4 text-gray-900">Strategic Recommendations</h2>
              
              {/* SWOT Analysis - Updated for new format */}
              {(swotAnalysis.strengths || swotAnalysis.weaknesses || swotAnalysis.risks) && (
                <Accordion title="SWOT Analysis" icon="" defaultOpen={true}>
                  <div className="space-y-4">
                    {swotAnalysis.strengths && swotAnalysis.strengths.length > 0 && (
                      <div className="bg-green-50 p-3 rounded">
                        <h4 className="font-semibold text-sm text-green-800 mb-2">Strengths</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {swotAnalysis.strengths.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {swotAnalysis.weaknesses && swotAnalysis.weaknesses.length > 0 && (
                      <div className="bg-red-50 p-3 rounded">
                        <h4 className="font-semibold text-sm text-red-800 mb-2">Weaknesses</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {swotAnalysis.weaknesses.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {swotAnalysis.risks && swotAnalysis.risks.length > 0 && (
                      <div className="bg-yellow-50 p-3 rounded">
                        <h4 className="font-semibold text-sm text-yellow-800 mb-2">Risks</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {swotAnalysis.risks.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </Accordion>
              )}

              {/* Packaging Improvements - Updated for multiple formats */}
              {packagingProposals && packagingProposals.length > 0 && (
                <Accordion title="Packaging Improvements" icon="">
                  <div className="space-y-4">
                    {packagingProposals.map((proposal, index) => {
                      // Handle different proposal formats
                      let content = ''
                      let title = ''
                      
                      if (typeof proposal === 'string') {
                        content = proposal
                      } else if (proposal && typeof proposal === 'object') {
                        title = proposal.title || proposal.name || ''
                        content = proposal.description || proposal.suggestion || proposal.improvement || proposal.content || ''
                        
                        // If no content found, try to stringify the object
                        if (!content && !title) {
                          content = JSON.stringify(proposal)
                        }
                      }
                      
                      return (
                        <div key={index} className="border-l-4 border-green-500 pl-4 py-2 bg-white rounded">
                          {title && <h4 className="font-semibold text-sm mb-1 text-gray-900">{title}</h4>}
                          <p className="text-gray-700 text-sm">{content || 'No description available'}</p>
                        </div>
                      )
                    })}
                  </div>
                </Accordion>
              )}

              {/* Go-to-Market Strategy */}
              {(gtmStrategy.shelf_positioning || gtmStrategy.regional_relevance || gtmStrategy.b2b_targeting) && (
                <Accordion title="Go-to-Market Strategy" icon="">
                  <div className="space-y-4">
                    {gtmStrategy.shelf_positioning && (
                      <div className="bg-white p-3 rounded border border-gray-200">
                        <h4 className="font-semibold text-sm mb-2">Shelf Positioning</h4>
                        <p className="text-sm text-gray-700">{gtmStrategy.shelf_positioning}</p>
                      </div>
                    )}
                    {gtmStrategy.regional_relevance && (
                      <div className="bg-white p-3 rounded border border-gray-200">
                        <h4 className="font-semibold text-sm mb-2">Regional Relevance</h4>
                        <p className="text-sm text-gray-700">{gtmStrategy.regional_relevance}</p>
                      </div>
                    )}
                    {gtmStrategy.b2b_targeting && (
                      <div className="bg-white p-3 rounded border border-gray-200">
                        <h4 className="font-semibold text-sm mb-2">B2B Targeting</h4>
                        <p className="text-sm text-gray-700">{gtmStrategy.b2b_targeting}</p>
                      </div>
                    )}
                  </div>
                </Accordion>
              )}

              {/* Evidence-Based Explanations - New Section */}
              {(evidenceExplanations.attractiveness || evidenceExplanations.utility || 
                evidenceExplanations.positioning || evidenceExplanations.global) && (
                <Accordion title="Evidence-Based Explanations" icon="">
                  <div className="space-y-4">
                    {evidenceExplanations.attractiveness && evidenceExplanations.attractiveness.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Attractiveness</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {evidenceExplanations.attractiveness.map((exp, idx) => (
                            <li key={idx}>{exp}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {evidenceExplanations.utility && evidenceExplanations.utility.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Utility</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {evidenceExplanations.utility.map((exp, idx) => (
                            <li key={idx}>{exp}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {evidenceExplanations.positioning && evidenceExplanations.positioning.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Positioning</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {evidenceExplanations.positioning.map((exp, idx) => (
                            <li key={idx}>{exp}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {evidenceExplanations.global && evidenceExplanations.global.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Global</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {evidenceExplanations.global.map((exp, idx) => (
                            <li key={idx}>{exp}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </Accordion>
              )}

              {/* Quality Insights - New Section */}
              {(qualityInsights.reflector_analysis || qualityInsights.key_insights || qualityInsights.improvement_guidelines) && (
                <Accordion title="Quality Insights" icon="">
                  <div className="space-y-4">
                    {qualityInsights.reflector_analysis && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Reflector Analysis</h4>
                        <p className="text-sm text-gray-700">{qualityInsights.reflector_analysis}</p>
                      </div>
                    )}
                    {qualityInsights.key_insights && qualityInsights.key_insights.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Key Insights</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {qualityInsights.key_insights.map((insight, idx) => (
                            <li key={idx}>{insight}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {qualityInsights.improvement_guidelines && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Improvement Guidelines</h4>
                        <p className="text-sm text-gray-700">{qualityInsights.improvement_guidelines}</p>
                      </div>
                    )}
                  </div>
                </Accordion>
              )}

              {/* Criteria Breakdown - New Section */}
              {Object.keys(criteriaBreakdown).length > 0 && (
                <Accordion title="Criteria Breakdown" icon="">
                  <div className="space-y-4">
                    {criteriaBreakdown.attractiveness && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Attractiveness</h4>
                        <div className="text-sm text-gray-700 space-y-1">
                          {Object.entries(criteriaBreakdown.attractiveness).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                              <span className="font-semibold">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {criteriaBreakdown.utility && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Utility</h4>
                        <div className="text-sm text-gray-700 space-y-1">
                          {Object.entries(criteriaBreakdown.utility).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                              <span className="font-semibold">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {criteriaBreakdown.positioning && (
                      <div>
                        <h4 className="font-semibold text-sm mb-2 text-gray-800">Positioning</h4>
                        <div className="text-sm text-gray-700 space-y-1">
                          {Object.entries(criteriaBreakdown.positioning).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                              <span className="font-semibold">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </Accordion>
              )}
            </div>
          </div>
        </div>

        {/* Debug Panel - Raw Sources */}
        {results && results.raw_sources && (
          <div className="mt-8">
            <Accordion 
              title="Debug: Raw API Sources" 
              icon=""
              defaultOpen={showDebug}
            >
              <div className="space-y-4">
                <p className="text-sm text-gray-600 mb-4">
                  This section shows the raw responses from ACE_Framework and EssenceAI APIs.
                  Useful for debugging and understanding the data structure.
                </p>
                
                {/* Status Info */}
                {results.status && (
                  <div className="bg-blue-50 p-3 rounded border border-blue-200">
                    <p className="text-sm">
                      <span className="font-semibold">Status:</span>{' '}
                      <span className="capitalize">{results.status}</span>
                    </p>
                    {results.errors && results.errors.length > 0 && (
                      <div className="mt-2">
                        <p className="text-sm font-semibold text-red-700">Errors:</p>
                        <ul className="list-disc list-inside text-sm text-red-600">
                          {results.errors.map((err, idx) => (
                            <li key={idx}>
                              {err.source}: {err.error}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* ACE Raw Source */}
                {results.raw_sources.ace && (
                  <div className="bg-white p-4 rounded border border-gray-200">
                    <h4 className="font-semibold text-sm mb-2 text-gray-800">
                      ACE_Framework Raw Response
                    </h4>
                    <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto max-h-96 border border-gray-100">
                      {JSON.stringify(results.raw_sources.ace, null, 2)}
                    </pre>
                  </div>
                )}

                {/* EssenceAI Raw Source */}
                {results.raw_sources.essence && (
                  <div className="bg-white p-4 rounded border border-gray-200">
                    <h4 className="font-semibold text-sm mb-2 text-gray-800">
                      EssenceAI Raw Response
                    </h4>
                    <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto max-h-96 border border-gray-100">
                      {JSON.stringify(results.raw_sources.essence, null, 2)}
                    </pre>
                  </div>
                )}

                {/* Full Merged Data */}
                {results.merged && (
                  <div className="bg-white p-4 rounded border border-gray-200">
                    <h4 className="font-semibold text-sm mb-2 text-gray-800">
                      Merged Data Structure
                    </h4>
                    <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto max-h-96 border border-gray-100">
                      {JSON.stringify(results.merged, null, 2)}
                    </pre>
                  </div>
                )}

                {/* Input Echo */}
                {results.input && (
                  <div className="bg-white p-4 rounded border border-gray-200">
                    <h4 className="font-semibold text-sm mb-2 text-gray-800">
                      Input Echo
                    </h4>
                    <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto border border-gray-100">
                      {JSON.stringify(results.input, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </Accordion>
          </div>
        )}

        {/* Visuals Section - if merged.visuals exists */}
        {merged && merged.visuals && merged.visuals.length > 0 && (
          <div className="mt-8">
            <Accordion title="Visualizations" icon="" defaultOpen={true}>
              <div className="space-y-4">
                <p className="text-sm text-gray-600 mb-4">
                  Charts and visualizations from the analysis.
                </p>
                <VisualsRenderer visuals={merged.visuals} />
              </div>
            </Accordion>
          </div>
        )}

        {/* Complete Merged Data - Generic Renderer */}
        {merged && (
          <div className="mt-8">
            <Accordion title="Complete Analysis Data" icon="" defaultOpen={false}>
              <div className="space-y-4">
                <p className="text-sm text-gray-600 mb-4">
                  All analysis data from the unified output. This view shows all fields dynamically.
                </p>
                <div className="bg-white p-4 rounded border border-gray-200">
                  <KeyValueRenderer data={merged} maxDepth={6} />
                </div>
              </div>
            </Accordion>
          </div>
        )}

        {/* Status Banner */}
        {results && results.status && (
          <div className={`mt-8 p-4 rounded-lg border ${
            results.status === 'ok' ? 'bg-green-50 border-green-200' :
            results.status === 'partial' ? 'bg-yellow-50 border-yellow-200' :
            'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-sm">
                  Analysis Status: <span className="capitalize">{results.status}</span>
                </p>
                {results.status === 'partial' && (
                  <p className="text-xs mt-1 text-yellow-800">
                    Some data may be missing. Check errors section for details.
                  </p>
                )}
                {results.status === 'error' && (
                  <p className="text-xs mt-1 text-red-800">
                    Analysis encountered errors. Check debug panel for details.
                  </p>
                )}
              </div>
              {results.errors && results.errors.length > 0 && (
                <div className="text-xs text-red-700">
                  {results.errors.length} error(s)
                </div>
              )}
            </div>
          </div>
        )}

        {/* Back Button */}
        <div className="text-center mt-12 mb-8">
          <a
            href="/"
            className="btn-primary inline-flex items-center space-x-2"
          >
            <span>←</span>
            <span>Analyze Another Product</span>
          </a>
        </div>
      </div>
      <Footer />
    </div>
  )
}

export default ResultsPage
