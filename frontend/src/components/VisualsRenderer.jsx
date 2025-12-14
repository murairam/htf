import React, { useState, useEffect, useRef } from 'react'

/**
 * Renders visual artifacts from merged.visuals array.
 * Supports: base64 images, plotly charts, and other visual types.
 */
const VisualsRenderer = ({ visuals }) => {
  const [plotlyLoaded, setPlotlyLoaded] = useState(false)
  const plotlyRefs = useRef({})

  // Load Plotly.js dynamically
  useEffect(() => {
    if (typeof window !== 'undefined' && !window.Plotly) {
      const script = document.createElement('script')
      script.src = 'https://cdn.plot.ly/plotly-2.27.0.min.js'
      script.async = true
      script.onload = () => setPlotlyLoaded(true)
      document.head.appendChild(script)
    } else if (window.Plotly) {
      setPlotlyLoaded(true)
    }
  }, [])

  // Render Plotly charts when library is loaded
  useEffect(() => {
    if (plotlyLoaded && window.Plotly) {
      Object.entries(plotlyRefs.current).forEach(([index, ref]) => {
        if (ref && ref.dataset.plotlyData) {
          try {
            const plotlyData = JSON.parse(ref.dataset.plotlyData)
            window.Plotly.newPlot(ref, plotlyData.data, plotlyData.layout || {}, {
              responsive: true,
              displayModeBar: true,
              displaylogo: false
            })
          } catch (error) {
            console.error('Error rendering Plotly chart:', error)
          }
        }
      })
    }
  }, [plotlyLoaded, visuals])

  if (!visuals || !Array.isArray(visuals) || visuals.length === 0) {
    return null
  }

  const renderVisual = (visual, index) => {
    const { type, title, path, format, data_or_url, source } = visual

    return (
      <div key={index} className="bg-white p-4 rounded-lg border border-gray-200 mb-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-semibold text-lg text-gray-900">
            {title || `Visual ${index + 1}`}
          </h4>
          {source && (
            <span className="text-xs px-2 py-1 bg-blue-100 rounded text-blue-700 font-semibold">
              {source.toUpperCase()}
            </span>
          )}
        </div>

        {/* Render based on type */}
        {type === 'base64_image' && data_or_url && (
          <div className="mt-3">
            <img
              src={data_or_url}
              alt={title || 'Visual'}
              className="max-w-full h-auto rounded border border-gray-300 shadow-sm"
              onError={(e) => {
                e.target.style.display = 'none'
                const errorDiv = document.createElement('div')
                errorDiv.className = 'text-gray-500 text-sm p-2 bg-red-50 rounded'
                errorDiv.textContent = 'Image failed to load'
                e.target.parentElement.appendChild(errorDiv)
              }}
            />
          </div>
        )}

        {type === 'plotly_chart' && data_or_url && (
          <div className="mt-3">
            {plotlyLoaded ? (
              <div
                ref={(el) => {
                  if (el) {
                    plotlyRefs.current[index] = el
                    el.dataset.plotlyData = JSON.stringify(data_or_url)
                  }
                }}
                className="w-full"
                style={{ minHeight: '400px' }}
              />
            ) : (
              <div className="p-4 bg-gray-50 rounded text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-600">Loading chart...</p>
              </div>
            )}
          </div>
        )}

        {type === 'detected_visual' && (
          <div className="mt-3 p-3 bg-yellow-50 rounded text-sm text-yellow-800">
            <p>Visual artifact detected but format not fully recognized.</p>
            <p className="text-xs mt-1">
              Check raw_sources for the complete visual data structure.
            </p>
          </div>
        )}

        {type === 'potential_base64' && (
          <div className="mt-3 p-3 bg-blue-50 rounded text-sm text-blue-800">
            <p>Potential base64 image detected.</p>
            {data_or_url && (
              <div className="mt-2">
                <img
                  src={data_or_url}
                  alt={title || 'Visual'}
                  className="max-w-full h-auto rounded border border-gray-300"
                  onError={(e) => {
                    e.target.style.display = 'none'
                    const errorDiv = document.createElement('div')
                    errorDiv.className = 'text-gray-500 text-sm p-2 bg-red-50 rounded'
                    errorDiv.textContent = 'Could not render as image'
                    e.target.parentElement.appendChild(errorDiv)
                  }}
                />
              </div>
            )}
          </div>
        )}

        {/* Fallback for unknown types */}
        {!['base64_image', 'plotly_chart', 'detected_visual', 'potential_base64'].includes(type) && (
          <div className="mt-3 p-3 bg-gray-50 rounded text-sm text-gray-600">
            <p>Visual type: {type}</p>
            {data_or_url && typeof data_or_url === 'string' && data_or_url.length < 500 && (
              <pre className="text-xs bg-white p-2 rounded mt-2 overflow-auto">
                {data_or_url}
              </pre>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {visuals.map((visual, index) => renderVisual(visual, index))}
    </div>
  )
}

export default VisualsRenderer

