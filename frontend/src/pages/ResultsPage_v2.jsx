~import React, { useState, useEffect, useRef } from 'react'
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

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

const getNestedValue = (obj, path, defaultValue = null) => {
  return path.split('.').reduce((acc, part) => acc && acc[part], obj) || defaultValue
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

const LoadingScreen = ({ message, progress }) => (
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

const ErrorScreen = ({ error }) => (
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
        <button onClick={() => window.location.reload()} className="btn-primary">
          Retry
        </button>
      </div>
    </div>
    <Footer />
  </div>
)

const PageHeader = ({ analysisId, confidenceLevel }) => (
  <div className="text-center mb-12">
    <div className="badge mb-4">Analysis Results</div>
    <h1 className="text-4xl font-bold text-gray-900 mb-2">
      Product Analysis Dashboard
    </h1>
    <p className="text-gray-600 mb-2">
      Analysis ID: <span className="font-mono text-sm">{analysisId}</span>
    </p>
    {confidenceLevel && (
      <p className="text-sm text-gray-500">
        Confidence Level: <span className="font-semibold capitalize">{confidenceLevel}</span>
      </p>
    )}
  </div>
)

// ============================================================================
// TAB PANELS
// ============================================================================

const OverviewTab = ({ results, merged, imageUrl, productInfo, scores }) => (
  <div className="grid lg:grid-cols-2 gap-6">
    {/* LEFT COLUMN */}
    <div className="space-y-6">
      {/* Product Image */}
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
          {productInfo.barcode && (
            <div>
              <p className="text-sm font-semibold text-gray-700">Barcode</p>
              <p className="text-gray-900 font-mono">{productInfo.barcode}</p>
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
            {scores.attractiveness !== undefined && scores.attractiveness !== null && (
              <ProgressBar value={Number(scores.attractiveness)} label="Attractiveness / Visibility" showValue={true} />
            )}
            {scores.utility !== undefined && scores.utility !== null && (
              <ProgressBar value={Number(scores.utility)} label="Utility & Value" showValue={true} />
            )}
            {scores.positioning !== undefined && scores.positioning !== null && (
              <ProgressBar value={Number(scores.positioning)} label="Positioning" showValue={true} />
            )}
            
            {/* Global Score */}
            {scores.global !== undefined && scores.global !== null && (
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
    </div>

    {/* RIGHT COLUMN */}
    <div className="space-y-6">
      <div className="card card-elevated">
        <h2 className="text-xl font-bold mb-4 text-gray-900">Strategic Recommendations</h2>
        
        {/* SWOT Analysis */}
        {(merged?.swot_analysis?.strengths || merged?.swot_analysis?.weaknesses || merged?.swot_analysis?.risks) && (
          <Accordion title="SWOT Analysis" icon="" defaultOpen={true}>
            <div className="space-y-4">
              {merged.swot_analysis.strengths && merged.swot_analysis.strengths.length > 0 && (
                <div className="bg-green-50 p-3 rounded">
                  <h4 className="font-semibold text-sm text-green-800 mb-2">Strengths</h4>
                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {merged.swot_analysis.strengths.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
              {merged.swot_analysis.weaknesses && merged.swot_analysis.weaknesses.length > 0 && (
                <div className="bg-red-50 p-3 rounded">
                  <h4 className="font-semibold text-sm text-red-800 mb-2">Weaknesses</h4>
                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {merged.swot_analysis.weaknesses.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
              {merged.swot_analysis.risks && merged.swot_analysis.risks.length > 0 && (
                <div className="bg-yellow-50 p-3 rounded">
                  <h4 className="font-semibold text-sm text-yellow-800 mb-2">Risks</h4>
                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {merged.swot_analysis.risks.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Accordion>
        )}

        {/* Packaging Improvements */}
        {merged?.packaging_improvements && merged.packaging_improvements.length > 0 && (
          <Accordion title="Packaging Improvements" icon="">
            <div className="space-y-4">
              {merged.packaging_improvements.map((proposal, index) => {
                let content = ''
                let title = ''
                let source = ''
                
                if (typeof proposal === 'string') {
                  content = proposal
                } else if (proposal && typeof proposal === 'object') {
                  // Handle different formats
                  title = proposal.title || proposal.name || ''
                  content = proposal.proposal || proposal.description || proposal.suggestion || 
                           proposal.improvement || proposal.content || proposal.action_exacte || ''
                  source = proposal.source || ''
                  
                  // If still no content, try other fields
                  if (!content && !title) {
                    if (proposal.probleme && proposal.resultat_attendu) {
                      // Format from image analysis
                      title = proposal.probleme
                      content = proposal.resultat_attendu
                      if (proposal.action_exacte) {
                        content = `${proposal.action_exacte}. ${content}`
                      }
                    } else {
                      // Last resort: show as readable text
                      content = Object.entries(proposal)
                        .filter(([key, value]) => value && typeof value === 'string')
                        .map(([key, value]) => `${key}: ${value}`)
                        .join(' | ')
                    }
                  }
                }
                
                return (
                  <div key={index} className="border-l-4 border-green-500 pl-4 py-2 bg-white rounded">
                    {source && (
                      <span className="inline-block px-2 py-1 text-xs font-semibold text-green-700 bg-green-100 rounded mb-2">
                        {source.toUpperCase()}
                      </span>
                    )}
                    {title && <h4 className="font-semibold text-sm mb-1 text-gray-900">{title}</h4>}
                    <p className="text-gray-700 text-sm">{content || 'No description available'}</p>
                  </div>
                )
              })}
            </div>
          </Accordion>
        )}

        {/* Go-to-Market Strategy */}
        {(merged?.go_to_market_strategy?.shelf_positioning || merged?.go_to_market_strategy?.regional_relevance || merged?.go_to_market_strategy?.b2b_targeting) && (
          <Accordion title="Go-to-Market Strategy" icon="">
            <div className="space-y-4">
              {merged.go_to_market_strategy.shelf_positioning && (
                <div className="bg-white p-3 rounded border border-gray-200">
                  <h4 className="font-semibold text-sm mb-2">Shelf Positioning</h4>
                  <p className="text-sm text-gray-700">{merged.go_to_market_strategy.shelf_positioning}</p>
                </div>
              )}
              {merged.go_to_market_strategy.regional_relevance && (
                <div className="bg-white p-3 rounded border border-gray-200">
                  <h4 className="font-semibold text-sm mb-2">Regional Relevance</h4>
                  <p className="text-sm text-gray-700">{merged.go_to_market_strategy.regional_relevance}</p>
                </div>
              )}
              {merged.go_to_market_strategy.b2b_targeting && (
                <div className="bg-white p-3 rounded border border-gray-200">
                  <h4 className="font-semibold text-sm mb-2">B2B Targeting</h4>
                  <p className="text-sm text-gray-700">{merged.go_to_market_strategy.b2b_targeting}</p>
                </div>
              )}
            </div>
          </Accordion>
        )}
      </div>
    </div>
  </div>
)

const ACEAnalysisTab = ({ merged }) => (
  <div className="space-y-6">
    <div className="card card-elevated">
      <h2 className="text-xl font-bold mb-4 text-gray-900">ACE Framework Analysis</h2>
      <p className="text-gray-600 mb-4">
        Detailed analysis from the ACE Framework including evidence-based explanations, quality insights, and criteria breakdown.
      </p>
      
      {/* Evidence-Based Explanations */}
      {(merged?.evidence_based_explanations?.attractiveness || merged?.evidence_based_explanations?.utility || 
        merged?.evidence_based_explanations?.positioning || merged?.evidence_based_explanations?.global) && (
        <Accordion title="Evidence-Based Explanations" icon="" defaultOpen={true}>
          <div className="space-y-4">
            {merged.evidence_based_explanations.attractiveness && merged.evidence_based_explanations.attractiveness.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2 text-gray-800">Attractiveness</h4>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {merged.evidence_based_explanations.attractiveness.map((exp, idx) => (
                    <li key={idx}>{exp}</li>
                  ))}
                </ul>
              </div>
            )}
            {merged.evidence_based_explanations.utility && merged.evidence_based_explanations.utility.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2 text-gray-800">Utility</h4>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {merged.evidence_based_explanations.utility.map((exp, idx) => (
                    <li key={idx}>{exp}</li>
                  ))}
                </ul>
              </div>
            )}
            {merged.evidence_based_explanations.positioning && merged.evidence_based_explanations.positioning.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2 text-gray-800">Positioning</h4>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {merged.evidence_based_explanations.positioning.map((exp, idx) => (
                    <li key={idx}>{exp}</li>
                  ))}
                </ul>
              </div>
            )}
            {merged.evidence_based_explanations.global && merged.evidence_based_explanations.global.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2 text-gray-800">Global</h4>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {merged.evidence_based_explanations.global.map((exp, idx) => (
                    <li key={idx}>{exp}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Accordion>
      )}

      {/* Quality Insights */}
      {(merged?.quality_insights?.reflector_analysis || merged?.quality_insights?.key_insights || merged?.quality_insights?.improvement_guidelines) && (
        <Accordion title="Quality Insights" icon="">
          <div className="space-y-4">
            {merged.quality_insights.reflector_analysis && (
              <div>
                <h4 className="font-semibold text-sm mb-2 text-gray-800">Reflector Analysis</h4>
                <p className="text-sm text-gray-700">{merged.quality_insights.reflector_analysis}</p>
              </div>
            )}
            {merged.quality_insights.key_insights && merged.quality_insights.key_insights.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2 text-gray-800">Key Insights</h4>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {merged.quality_insights.key_insights.map((insight, idx) => (
                    <li key={idx}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
            {merged.quality_insights.improvement_guidelines && (
              <div>
                <h4 className="font-semibold text-sm mb-2 text-gray-800">Improvement Guidelines</h4>
                <p className="text-sm text-gray-700">{merged.quality_insights.improvement_guidelines}</p>
              </div>
            )}
          </div>
        </Accordion>
      )}
    </div>
  </div>
)

// ============================================================================
// MAIN COMPONENT
// ============================================================================

const ResultsPage = () => {
  const { analysisId } = useParams()
  const [status, setStatus] = useState('connecting')
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('Connecting...')
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)

  // Load saved result on mount
  useEffect(() => {
    const loadSavedResult = async () => {
      try {
        const response = await fetch(`/api/results/${analysisId}/`)
        const data = await response.json()
        
        if (data.success && data.result) {
          setResults(data.result)
          setStatus('completed')
          setProgress(100)
          setMessage('Analysis complete!')
          return true
        }
      } catch (err) {
        console.log('No saved result found or error loading:', err)
      }
      return false
    }

    loadSavedResult().then((loaded) => {
      if (!loaded) {
        connectWebSocket()
      }
    })
  }, [analysisId])

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/analysis/${analysisId}/`
    
    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setStatus('connected')
        setMessage('Connected. Starting analysis...')
      }

      ws.onmessage = (event) => {
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

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }

  // Extract data helpers
  const getMergedData = () => results?.merged || results
  
  const getImageUrl = () => {
    if (!results) return null
    const merged = getMergedData()
    return results.image_front_url || 
           getNestedValue(merged, 'product_information.image_front_url') ||
           null
  }
  
  const getScores = () => {
    if (!results) return null
    const merged = getMergedData()
    
    let scores = merged.scoring_results?.scores || merged.scores || {}
    
    const mappedScores = {
      attractiveness: scores.attractiveness_score ?? scores.attractiveness,
      utility: scores.utility_score ?? scores.utility,
      positioning: scores.positioning_score ?? scores.positioning,
      global: scores.global_score ?? scores.global
    }
    
    const hasAnyScore = Object.values(mappedScores).some(v => v !== undefined && v !== null)
    return hasAnyScore ? mappedScores : null
  }
  
  const getProductInfo = () => {
    if (!results) return {}
    const merged = getMergedData()
    
    const productInfo = merged.product_information || {}
    const basicInfo = productInfo.basic_info || {}
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

  // Render states
  if (error) {
    return <ErrorScreen error={error} />
  }

  if (!results) {
    return <LoadingScreen message={message} progress={progress} />
  }

  // Extract data
  const merged = getMergedData()
  const scores = getScores()
  const imageUrl = getImageUrl()
  const productInfo = getProductInfo()
  const confidenceLevel = merged?.scoring_results?.confidence_level || results?.status

  // Render main content
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header />
      <div className="container mx-auto px-4 py-8 max-w-7xl flex-1">
        <PageHeader analysisId={analysisId} confidenceLevel={confidenceLevel} />

        {/* Tabs */}
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
            {/* Tab 1: Overview */}
            <Tab.Panel>
              <OverviewTab 
                results={results}
                merged={merged}
                imageUrl={imageUrl}
                productInfo={productInfo}
                scores={scores}
              />
            </Tab.Panel>

            {/* Tab 2: Competitor Intelligence */}
            <Tab.Panel>
              <div className="space-y-8">
                {/* ACE Competitor Intelligence */}
                {merged?.competitor_intelligence?.ace && (
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">
                        ACE Analysis
                      </span>
                      <h2 className="text-xl font-bold text-gray-900">📊 Real-Time Competitor Analysis</h2>
                    </div>
                    <CompetitorIntelligence data={merged.competitor_intelligence.ace} />
                  </div>
                )}
                
                {/* Essence Competitor Intelligence */}
                {merged?.competitor_intelligence?.essence && (
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <span className="px-3 py-1 bg-purple-100 text-purple-800 text-xs font-semibold rounded-full">
                        ESSENCE Analysis
                      </span>
                      <h2 className="text-xl font-bold text-gray-900">🔬 Research-Based Insights</h2>
                    </div>
                    <CompetitorIntelligence data={merged.competitor_intelligence.essence} />
                  </div>
                )}
                
                {/* Fallback if no data */}
                {!merged?.competitor_intelligence?.ace && !merged?.competitor_intelligence?.essence && (
                  <div className="text-center py-12 text-gray-500">
                    <p className="text-lg">No competitor intelligence data available</p>
                    <p className="text-sm mt-2">This data comes from ACE and EssenceAI analysis</p>
                  </div>
                )}
              </div>
            </Tab.Panel>

            {/* Tab 3: Marketing Strategy */}
            <Tab.Panel>
              {merged?.marketing_strategy_essence ? (
                <MarketingStrategyEssence data={merged.marketing_strategy_essence} />
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">No marketing strategy data available</p>
                  <p className="text-sm mt-2">This data comes from EssenceAI analysis</p>
                </div>
              )}
            </Tab.Panel>

            {/* Tab 4: Research Insights */}
            <Tab.Panel>
              {merged?.research_insights_essence ? (
                <ResearchInsights data={merged.research_insights_essence} />
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">No research insights data available</p>
                  <p className="text-sm mt-2">This data comes from EssenceAI analysis of scientific papers</p>
                </div>
              )}
            </Tab.Panel>

            {/* Tab 5: ACE Analysis */}
            <Tab.Panel>
              <ACEAnalysisTab merged={merged} />
            </Tab.Panel>
          </Tab.Panels>
        </Tab.Group>

        {/* Debug Panel */}
        {results?.raw_sources && (
          <div className="mt-8">
            <Accordion title="Debug: Raw API Sources" icon="" defaultOpen={false}>
              <div className="space-y-4">
                <p className="text-sm text-gray-600 mb-4">
                  This section shows the raw responses from ACE_Framework and EssenceAI APIs.
                </p>
                
                {results.status && (
                  <div className="bg-blue-50 p-3 rounded border border-blue-200">
                    <p className="text-sm">
                      <span className="font-semibold">Status:</span>{' '}
                      <span className="capitalize">{results.status}</span>
                    </p>
                  </div>
                )}

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
              </div>
            </Accordion>
          </div>
        )}

        {/* Visuals Section */}
        {merged?.visuals && merged.visuals.length > 0 && (
          <div className="mt-8">
            <Accordion title="Visualizations" icon="" defaultOpen={false}>
              <div className="space-y-4">
                <p className="text-sm text-gray-600 mb-4">
                  Charts and visualizations from the analysis.
                </p>
                <VisualsRenderer visuals={merged.visuals} />
              </div>
            </Accordion>
          </div>
        )}

        {/* Complete Data */}
        {merged && (
          <div className="mt-8">
            <Accordion title="Complete Analysis Data" icon="" defaultOpen={false}>
              <div className="space-y-4">
                <p className="text-sm text-gray-600 mb-4">
                  All analysis data from the unified output.
                </p>
                <div className="bg-white p-4 rounded border border-gray-200">
                  <KeyValueRenderer data={merged} maxDepth={6} />
                </div>
              </div>
            </Accordion>
          </div>
        )}

        {/* Status Banner */}
        {results?.status && (
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
          <a href="/" className="btn-primary inline-flex items-center space-x-2">
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
