import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import ProgressBar from '../components/ProgressBar'
import Accordion from '../components/Accordion'

const ResultsPage = () => {
  const { analysisId } = useParams()
  const [status, setStatus] = useState('connecting')
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('Connecting...')
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)

  useEffect(() => {
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
  }, [analysisId])

  // Helper function to safely get nested values
  const getNestedValue = (obj, path, defaultValue = null) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj) || defaultValue
  }

  // Extract image URL - support both old and new format
  const getImageUrl = () => {
    if (!results) return null
    // Try new format first (from product_information or root)
    return results.image_front_url || 
           getNestedValue(results, 'product_information.image_front_url') ||
           null
  }

  // Extract scores - adapt to new format with _score suffix
  const getScores = () => {
    if (!results) return null
    
    // Try new format first (scoring_results.scores)
    let scores = results.scoring_results?.scores || results.scores || {}
    
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
    
    const basicInfo = results.product_information?.basic_info || {}
    const businessObj = results.business_objective || {}
    
    return {
      barcode: results.barcode || basicInfo.product_id,
      objectives: businessObj.objective_description || results.objectives || results.business_objective,
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
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-2xl w-full">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🔄</div>
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
    )
  }

  const scores = getScores()
  const imageUrl = getImageUrl()
  const productInfo = getProductInfo()
  
  // Debug: Log scores structure
  if (results && !scores) {
    console.log('⚠️ Scores not found. Results structure:', {
      hasScoringResults: !!results.scoring_results,
      scoringResults: results.scoring_results,
      hasScores: !!results.scores,
      scores: results.scores
    })
  }
  
  // Extract data from new format
  const packagingProposals = results.packaging_improvement_proposals || []
  const gtmStrategy = results.go_to_market_strategy || {}
  const swotAnalysis = results.swot_analysis || {}
  const imageAnalysis = results.image_analysis || {}
  const evidenceExplanations = results.evidence_based_explanations || {}
  const qualityInsights = results.quality_insights || {}
  const criteriaBreakdown = results.scoring_results?.criteria_breakdown || {}
  const confidenceLevel = results.scoring_results?.confidence_level

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📊 Analysis Dashboard
          </h1>
          <p className="text-gray-600">Analysis ID: {analysisId}</p>
          {confidenceLevel && (
            <p className="text-sm text-gray-500 mt-1">
              Confidence Level: <span className="font-semibold capitalize">{confidenceLevel}</span>
            </p>
          )}
        </div>

        {/* Two Column Layout */}
        <div className="grid lg:grid-cols-2 gap-6">
          
          {/* LEFT COLUMN - Image & Scores */}
          <div className="space-y-6">
            
            {/* Product Image - Only show if image_front_url exists */}
            {imageUrl && (
              <div className="bg-white rounded-xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-3xl border border-gray-100">
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
            <div className="bg-white rounded-xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-3xl border border-gray-100">
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
              <div className="bg-white rounded-xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-3xl border border-gray-100">
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
                            <span className="text-2xl">🏆</span>
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
              <div className="bg-white rounded-xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-3xl border border-gray-100">
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
                            <p className="text-xs text-gray-600 mt-1">💡 {problem.indice_visuel}</p>
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
            <div className="bg-white rounded-xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.01] hover:shadow-3xl border border-gray-100">
              <h2 className="text-xl font-bold mb-4 text-gray-900">Strategic Recommendations</h2>
              
              {/* SWOT Analysis - Updated for new format */}
              {(swotAnalysis.strengths || swotAnalysis.weaknesses || swotAnalysis.risks) && (
                <Accordion title="SWOT Analysis" icon="📊" defaultOpen={true}>
                  <div className="space-y-4">
                    {swotAnalysis.strengths && swotAnalysis.strengths.length > 0 && (
                      <div className="bg-green-50 p-3 rounded">
                        <h4 className="font-semibold text-sm text-green-800 mb-2">💪 Strengths</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {swotAnalysis.strengths.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {swotAnalysis.weaknesses && swotAnalysis.weaknesses.length > 0 && (
                      <div className="bg-red-50 p-3 rounded">
                        <h4 className="font-semibold text-sm text-red-800 mb-2">⚠️ Weaknesses</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                          {swotAnalysis.weaknesses.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {swotAnalysis.risks && swotAnalysis.risks.length > 0 && (
                      <div className="bg-yellow-50 p-3 rounded">
                        <h4 className="font-semibold text-sm text-yellow-800 mb-2">⚡ Risks</h4>
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

              {/* Packaging Improvements - Updated for string array */}
              {packagingProposals && packagingProposals.length > 0 && (
                <Accordion title="Packaging Improvements" icon="📦">
                  <div className="space-y-4">
                    {packagingProposals.map((proposal, index) => (
                      <div key={index} className="border-l-4 border-green-500 pl-4 py-2 bg-white rounded">
                        <p className="text-gray-700 text-sm">{typeof proposal === 'string' ? proposal : (proposal.title || proposal.description || proposal)}</p>
                      </div>
                    ))}
                  </div>
                </Accordion>
              )}

              {/* Go-to-Market Strategy */}
              {(gtmStrategy.shelf_positioning || gtmStrategy.regional_relevance || gtmStrategy.b2b_targeting) && (
                <Accordion title="Go-to-Market Strategy" icon="🎯">
                  <div className="space-y-4">
                    {gtmStrategy.shelf_positioning && (
                      <div className="bg-white p-3 rounded border border-gray-200">
                        <h4 className="font-semibold text-sm mb-2">📍 Shelf Positioning</h4>
                        <p className="text-sm text-gray-700">{gtmStrategy.shelf_positioning}</p>
                      </div>
                    )}
                    {gtmStrategy.regional_relevance && (
                      <div className="bg-white p-3 rounded border border-gray-200">
                        <h4 className="font-semibold text-sm mb-2">🌍 Regional Relevance</h4>
                        <p className="text-sm text-gray-700">{gtmStrategy.regional_relevance}</p>
                      </div>
                    )}
                    {gtmStrategy.b2b_targeting && (
                      <div className="bg-white p-3 rounded border border-gray-200">
                        <h4 className="font-semibold text-sm mb-2">🤝 B2B Targeting</h4>
                        <p className="text-sm text-gray-700">{gtmStrategy.b2b_targeting}</p>
                      </div>
                    )}
                  </div>
                </Accordion>
              )}

              {/* Evidence-Based Explanations - New Section */}
              {(evidenceExplanations.attractiveness || evidenceExplanations.utility || 
                evidenceExplanations.positioning || evidenceExplanations.global) && (
                <Accordion title="Evidence-Based Explanations" icon="🔍">
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
                <Accordion title="Quality Insights" icon="💡">
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
                <Accordion title="Criteria Breakdown" icon="📋">
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

        {/* Back Button */}
        <div className="text-center mt-8">
          <a
            href="/"
            className="inline-block px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold shadow-md"
          >
            ← Analyze Another Product
          </a>
        </div>
      </div>
    </div>
  )
}

export default ResultsPage
