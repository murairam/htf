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

  const { scores, recommendations, image_url, barcode, objectives } = results

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📊 Analysis Dashboard
          </h1>
          <p className="text-gray-600">Analysis ID: {analysisId}</p>
        </div>

        {/* Two Column Layout */}
        <div className="grid lg:grid-cols-2 gap-6">
          
          {/* LEFT COLUMN - Image & Scores */}
          <div className="space-y-6">
            
            {/* Product Image */}
            <div className="bg-white rounded-xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-3xl border border-gray-100">
              <h2 className="text-xl font-bold mb-4 text-gray-900">Product Image</h2>
              {image_url && (
                <img
                  src={image_url}
                  alt="Product"
                  className="w-full h-80 object-contain rounded-lg border-2 border-gray-200 bg-gray-50"
                />
              )}
            </div>

            {/* Product Details */}
            <div className="bg-white rounded-xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-3xl border border-gray-100">
              <h2 className="text-xl font-bold mb-4 text-gray-900">Product Details</h2>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-semibold text-gray-700">Barcode</p>
                  <p className="text-gray-900 font-mono">{barcode}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-700">Business Objectives</p>
                  <p className="text-gray-900">{objectives}</p>
                </div>
              </div>
            </div>

            {/* Performance Scores */}
            <div className="bg-white rounded-xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-3xl border border-gray-100">
              <h2 className="text-xl font-bold mb-6 text-gray-900">Performance Scores</h2>
              <div className="space-y-4">
                <ProgressBar
                  value={scores.attractiveness}
                  label="Attractiveness / Visibility"
                  showValue={true}
                />
                <ProgressBar
                  value={scores.price}
                  label="Price Positioning"
                  showValue={true}
                />
                <ProgressBar
                  value={scores.utility}
                  label="Utility & Value"
                  showValue={true}
                />
                
                {/* Global Score - Highlighted */}
                <div className="mt-6 pt-6 border-t-2 border-gray-300">
                  <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border-2 border-green-500">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-2xl">🏆</span>
                        <h3 className="text-lg font-bold text-gray-900">Global Score</h3>
                      </div>
                      <div className="text-3xl font-bold text-green-600">
                        {scores.global}
                        <span className="text-lg text-gray-500">/100</span>
                      </div>
                    </div>
                    <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="absolute top-0 left-0 h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full transition-all duration-500 shadow-lg"
                        style={{ width: `${scores.global}%` }}
                      >
                        <div className="absolute inset-0 bg-white opacity-20 animate-pulse"></div>
                      </div>
                    </div>
                    <p className="text-xs text-gray-600 mt-2 text-center italic">
                      Overall performance based on all metrics
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN - Recommendations (Accordions) */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-2xl p-6 transform transition-all duration-300 hover:scale-[1.01] hover:shadow-3xl border border-gray-100">
              <h2 className="text-xl font-bold mb-4 text-gray-900">Strategic Recommendations</h2>
              
              {/* Package Design Accordion */}
              {recommendations.package_design && recommendations.package_design.length > 0 && (
                <Accordion title="Package Design" icon="📦" defaultOpen={true}>
                  <div className="space-y-4">
                    {recommendations.package_design.map((item, index) => (
                      <div key={index} className="border-l-4 border-green-500 pl-4 py-2 bg-white rounded">
                        <h4 className="font-semibold text-base mb-1">{item.title}</h4>
                        <p className="text-gray-700 text-sm mb-2">{item.description}</p>
                        {item.priority && (
                          <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold ${
                            item.priority === 'high' || item.priority === 'critical' 
                              ? 'bg-red-100 text-red-800' 
                              : item.priority === 'medium' 
                              ? 'bg-yellow-100 text-yellow-800' 
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {item.priority.toUpperCase()}
                          </span>
                        )}
                        {item.impact && (
                          <p className="text-xs text-gray-600 mt-2 italic">💡 {item.impact}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </Accordion>
              )}

              {/* Placement Strategy Accordion */}
              {recommendations.placement && (
                <Accordion title="Placement Strategy" icon="📍">
                  <div className="space-y-3">
                    <div className="bg-white p-3 rounded">
                      <p className="text-sm font-semibold text-gray-700 mb-1">Shelf Level</p>
                      <p className="text-gray-900 text-sm">{recommendations.placement.shelf_level}</p>
                    </div>
                    {recommendations.placement.rationale && (
                      <div className="bg-white p-3 rounded">
                        <p className="text-sm font-semibold text-gray-700 mb-1">Rationale</p>
                        <p className="text-gray-900 text-sm">{recommendations.placement.rationale}</p>
                      </div>
                    )}
                    {recommendations.placement.aisle_position && (
                      <div className="bg-white p-3 rounded">
                        <p className="text-sm font-semibold text-gray-700 mb-1">Aisle Position</p>
                        <p className="text-gray-900 text-sm">{recommendations.placement.aisle_position}</p>
                      </div>
                    )}
                    {recommendations.placement.geographic_zones && (
                      <div className="bg-white p-3 rounded">
                        <p className="text-sm font-semibold text-gray-700 mb-2">Geographic Zones</p>
                        <div className="space-y-2">
                          {recommendations.placement.geographic_zones.map((zone, index) => (
                            <div key={index} className="bg-gray-50 p-2 rounded border border-gray-200">
                              <p className="font-medium text-sm">{zone.zone}</p>
                              <p className="text-xs text-gray-600 mt-1">{zone.reasoning}</p>
                              <span className="inline-block mt-1 px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded">
                                {zone.priority}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </Accordion>
              )}

              {/* Commercial Prospection Accordion */}
              {recommendations.prospection && recommendations.prospection.length > 0 && (
                <Accordion title="Commercial Prospection" icon="🎯">
                  <div className="space-y-4">
                    {recommendations.prospection.map((item, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4 py-2 bg-white rounded">
                        <h4 className="font-semibold text-base mb-1">{item.strategy}</h4>
                        <p className="text-gray-700 text-sm mb-2">{item.description}</p>
                        {item.target_segments && (
                          <div className="mt-2">
                            <p className="text-xs font-semibold text-gray-700 mb-1">Target Segments:</p>
                            <ul className="list-disc list-inside text-xs text-gray-600 space-y-0.5">
                              {item.target_segments.map((segment, idx) => (
                                <li key={idx}>{segment}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {item.key_messaging && (
                          <p className="text-xs text-gray-600 mt-2 italic">
                            💬 {item.key_messaging}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </Accordion>
              )}

              {/* Customer Personas Accordion */}
              {recommendations.personas && recommendations.personas.length > 0 && (
                <Accordion title="Customer Profiles" icon="👥">
                  <div className="space-y-3">
                    {recommendations.personas.map((persona, index) => (
                      <div key={index} className="bg-white p-4 rounded border border-gray-200">
                        <h4 className="font-semibold text-base mb-1">{persona.name}</h4>
                        <p className="text-xs text-gray-600 mb-2">Age: {persona.age_range}</p>
                        <p className="text-sm text-gray-700 mb-3">{persona.profile}</p>
                        
                        {persona.motivations && (
                          <div className="mb-2">
                            <p className="text-xs font-semibold text-gray-700 mb-1">Motivations:</p>
                            <ul className="list-disc list-inside text-xs text-gray-600 space-y-0.5">
                              {persona.motivations.map((m, idx) => (
                                <li key={idx}>{m}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {persona.pain_points && (
                          <div className="mb-2">
                            <p className="text-xs font-semibold text-gray-700 mb-1">Pain Points:</p>
                            <ul className="list-disc list-inside text-xs text-gray-600 space-y-0.5">
                              {persona.pain_points.map((p, idx) => (
                                <li key={idx}>{p}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {persona.buying_behavior && (
                          <p className="text-xs text-gray-600 mt-2">
                            <span className="font-semibold">Buying Behavior:</span> {persona.buying_behavior}
                          </p>
                        )}
                        
                        {persona.engagement_strategy && (
                          <p className="text-xs text-gray-600 mt-2 italic">
                            💡 {persona.engagement_strategy}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </Accordion>
              )}

              {/* Distribution Strategy Accordion */}
              {recommendations.distribution && recommendations.distribution.length > 0 && (
                <Accordion title="Distribution Strategy" icon="🚚">
                  <div className="space-y-4">
                    {recommendations.distribution.map((item, index) => (
                      <div key={index} className="border-l-4 border-purple-500 pl-4 py-2 bg-white rounded">
                        <h4 className="font-semibold text-base mb-1">{item.channel}</h4>
                        <p className="text-gray-700 text-sm mb-2">{item.strategy}</p>
                        {item.advantages && (
                          <div className="mt-2">
                            <p className="text-xs font-semibold text-gray-700 mb-1">Advantages:</p>
                            <ul className="list-disc list-inside text-xs text-gray-600 space-y-0.5">
                              {item.advantages.map((adv, idx) => (
                                <li key={idx}>{adv}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {item.implementation && (
                          <p className="text-xs text-gray-600 mt-2 italic">
                            🔧 {item.implementation}
                          </p>
                        )}
                      </div>
                    ))}
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
