import React, { useState } from 'react'

const CitationCard = ({ citation, index }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="border-l-4 border-blue-500 pl-4 py-3 bg-blue-50 rounded-r-lg hover:bg-blue-100 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xs font-semibold text-blue-700 bg-blue-200 px-2 py-1 rounded">
              Citation {index + 1}
            </span>
            {citation.relevance_score && (
              <span className="text-xs text-gray-600">
                Relevance: {(citation.relevance_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
          
          <p className="text-sm font-medium text-gray-900 mb-1">
            {citation.file_name || 'Research Paper'}
            {citation.page && ` (Page ${citation.page})`}
          </p>
          
          {citation.excerpt && (
            <div>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-xs text-blue-600 hover:text-blue-800 font-medium mb-1"
              >
                {isExpanded ? '▼ Hide excerpt' : '▶ Show excerpt'}
              </button>
              
              {isExpanded && (
                <div className="mt-2 p-3 bg-white rounded border border-blue-200">
                  <p className="text-sm text-gray-700 italic">
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

const PositioningCard = ({ positioning }) => {
  if (!positioning || Object.keys(positioning).length === 0) {
    return null
  }

  return (
    <div className="card card-elevated bg-gradient-to-br from-purple-50 to-pink-50">
      <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
        <span className="text-2xl mr-2">🎯</span>
        Positioning Strategy
      </h3>
      
      <div className="grid md:grid-cols-3 gap-4">
        {positioning.target_audience && (
          <div className="bg-white p-4 rounded-lg border-2 border-purple-200">
            <h4 className="text-sm font-semibold text-purple-700 mb-2">Target Audience</h4>
            <p className="text-sm text-gray-700">{positioning.target_audience}</p>
          </div>
        )}
        
        {positioning.category && (
          <div className="bg-white p-4 rounded-lg border-2 border-pink-200">
            <h4 className="text-sm font-semibold text-pink-700 mb-2">Category</h4>
            <p className="text-sm text-gray-700">{positioning.category}</p>
          </div>
        )}
        
        {positioning.point_of_difference && (
          <div className="bg-white p-4 rounded-lg border-2 border-indigo-200">
            <h4 className="text-sm font-semibold text-indigo-700 mb-2">Point of Difference</h4>
            <p className="text-sm text-gray-700">{positioning.point_of_difference}</p>
          </div>
        )}
      </div>
    </div>
  )
}

const MarketingStrategyEssence = ({ data }) => {
  if (!data) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No marketing strategy data available</p>
        <p className="text-sm mt-2">This data comes from EssenceAI analysis</p>
      </div>
    )
  }

  const {
    strategy_text,
    segment,
    domain,
    positioning,
    key_messages,
    tactics,
    channels,
    citations,
    segment_profile
  } = data

  return (
    <div className="space-y-6">
      {/* Strategy Header */}
      {(segment || domain || strategy_text) && (
        <div className="card card-elevated bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200">
          <div className="flex items-start space-x-3 mb-4">
            <span className="text-3xl">📋</span>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Marketing Strategy
                {segment && <span className="text-blue-600"> for {segment} Segment</span>}
              </h3>
              {domain && (
                <p className="text-sm text-gray-600 mb-3">
                  <span className="font-semibold">Domain:</span> {domain}
                </p>
              )}
              {strategy_text && (
                <p className="text-gray-700 leading-relaxed">{strategy_text}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Positioning */}
      {positioning && <PositioningCard positioning={positioning} />}

      {/* Segment Profile */}
      {segment_profile && Object.keys(segment_profile).length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">👥</span>
            Segment Profile
          </h3>
          <div className="space-y-3">
            {Object.entries(segment_profile).map(([key, value]) => (
              <div key={key} className="border-l-4 border-green-500 pl-4 py-2 bg-green-50 rounded-r">
                <h4 className="text-sm font-semibold text-gray-800 capitalize mb-1">
                  {key.replace(/_/g, ' ')}
                </h4>
                <p className="text-sm text-gray-700">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Messages */}
      {key_messages && key_messages.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">💬</span>
            Key Messages
          </h3>
          <ul className="space-y-2">
            {key_messages.map((message, index) => (
              <li key={index} className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {index + 1}
                </span>
                <p className="text-sm text-gray-700 flex-1">{message}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tactics */}
      {tactics && tactics.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">⚡</span>
            Marketing Tactics
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {tactics.map((tactic, index) => (
              <div key={index} className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-colors">
                <h4 className="font-semibold text-gray-900 mb-2">
                  {typeof tactic === 'string' ? tactic : (tactic.tactic || tactic.name || `Tactic ${index + 1}`)}
                </h4>
                {typeof tactic === 'object' && tactic.description && (
                  <p className="text-sm text-gray-600">{tactic.description}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Channels */}
      {channels && channels.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">📢</span>
            Recommended Channels
          </h3>
          <div className="grid md:grid-cols-3 gap-3">
            {channels.map((channel, index) => (
              <div key={index} className="bg-gradient-to-br from-blue-50 to-indigo-50 p-3 rounded-lg border border-blue-200">
                <p className="text-sm font-semibold text-gray-900">
                  {typeof channel === 'string' ? channel : (channel.channel || channel.name || 'Channel')}
                </p>
                {typeof channel === 'object' && channel.rationale && (
                  <p className="text-xs text-gray-600 mt-1">{channel.rationale}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Citations */}
      {citations && citations.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">📚</span>
            Research Citations
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            This strategy is backed by {citations.length} scientific research {citations.length === 1 ? 'source' : 'sources'}
          </p>
          <div className="space-y-3">
            {citations.map((citation, index) => (
              <CitationCard key={index} citation={citation} index={index} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default MarketingStrategyEssence
