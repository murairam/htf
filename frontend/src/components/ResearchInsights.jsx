import React, { useState } from 'react'

const CitationCard = ({ citation, index }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="border-l-4 border-green-500 pl-4 py-3 bg-green-50 rounded-r-lg hover:bg-green-100 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xs font-semibold text-green-700 bg-green-200 px-2 py-1 rounded">
              Source {index + 1}
            </span>
            {citation.relevance_score && (
              <span className="text-xs text-gray-600">
                Relevance: {(citation.relevance_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
          
          <p className="text-sm font-medium text-gray-900 mb-1">
            📄 {citation.file_name || 'Research Paper'}
            {citation.page && ` (Page ${citation.page})`}
          </p>
          
          {citation.excerpt && (
            <div>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-xs text-green-600 hover:text-green-800 font-medium mb-1 flex items-center space-x-1"
              >
                <span>{isExpanded ? '▼' : '▶'}</span>
                <span>{isExpanded ? 'Hide excerpt' : 'Show excerpt'}</span>
              </button>
              
              {isExpanded && (
                <div className="mt-2 p-3 bg-white rounded border border-green-200 shadow-sm">
                  <p className="text-sm text-gray-700 italic leading-relaxed">
                    "{citation.excerpt}"
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const ResearchInsights = ({ data }) => {
  if (!data) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No research insights data available</p>
        <p className="text-sm mt-2">This data comes from EssenceAI analysis of scientific papers</p>
      </div>
    )
  }

  const {
    insights_text,
    domain,
    key_findings,
    citations,
    research_summary,
    methodology
  } = data

  return (
    <div className="space-y-6">
      {/* Main Insights */}
      {insights_text && (
        <div className="card card-elevated bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200">
          <div className="flex items-start space-x-3">
            <span className="text-3xl">🔬</span>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Key Research Findings
                {domain && <span className="text-green-600"> - {domain}</span>}
              </h3>
              <p className="text-gray-700 leading-relaxed">{insights_text}</p>
            </div>
          </div>
        </div>
      )}

      {/* Research Summary */}
      {research_summary && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-3 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">📊</span>
            Research Summary
          </h3>
          <p className="text-gray-700 leading-relaxed">{research_summary}</p>
        </div>
      )}

      {/* Key Findings */}
      {key_findings && key_findings.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">💡</span>
            Key Findings
          </h3>
          <div className="space-y-3">
            {key_findings.map((finding, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                <span className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </span>
                <p className="text-sm text-gray-700 flex-1 pt-1">{finding}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Methodology */}
      {methodology && (
        <div className="card card-elevated bg-gray-50">
          <h3 className="text-lg font-bold mb-3 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🔍</span>
            Research Methodology
          </h3>
          <p className="text-sm text-gray-700 leading-relaxed">{methodology}</p>
        </div>
      )}

      {/* Research Sources / Citations */}
      {citations && citations.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">📚</span>
            Research Sources
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            These insights are based on {citations.length} scientific research {citations.length === 1 ? 'paper' : 'papers'}
          </p>
          <div className="space-y-3">
            {citations.map((citation, index) => (
              <CitationCard key={index} citation={citation} index={index} />
            ))}
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">ℹ️</span>
          <div>
            <h4 className="text-sm font-semibold text-blue-900 mb-1">About Research Insights</h4>
            <p className="text-sm text-blue-800">
              These insights are extracted from peer-reviewed scientific papers using advanced RAG (Retrieval-Augmented Generation) technology. 
              Each insight is backed by citations from the research literature.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResearchInsights
