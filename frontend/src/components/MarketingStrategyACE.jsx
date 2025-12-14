import React from 'react'

const MarketingStrategyACE = ({ data }) => {
  if (!data) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No ACE marketing strategy data available</p>
      </div>
    )
  }

  const {
    positioning,
    target_segments,
    key_messages,
    channels,
    tactics,
    pricing_strategy,
    summary
  } = data

  return (
    <div className="space-y-6">
      {/* Summary */}
      {summary && (
        <div className="card card-elevated bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200">
          <div className="flex items-start space-x-3">
            <span className="text-3xl">📋</span>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Strategy Summary</h3>
              <p className="text-gray-700 leading-relaxed">{summary}</p>
            </div>
          </div>
        </div>
      )}

      {/* Positioning */}
      {positioning && (
        <div className="card card-elevated bg-gradient-to-br from-purple-50 to-pink-50">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🎯</span>
            Positioning Strategy
          </h3>
          
          <div className="space-y-4">
            {positioning.primary && (
              <div className="bg-white p-4 rounded-lg border-2 border-purple-200">
                <h4 className="text-sm font-semibold text-purple-700 mb-2">Primary Position</h4>
                <p className="text-lg font-bold text-gray-900 capitalize">{positioning.primary}</p>
              </div>
            )}
            
            {positioning.description && (
              <div className="bg-white p-4 rounded-lg border-2 border-pink-200">
                <h4 className="text-sm font-semibold text-pink-700 mb-2">Description</h4>
                <p className="text-sm text-gray-700">{positioning.description}</p>
              </div>
            )}
            
            {positioning.strengths && positioning.strengths.length > 0 && (
              <div className="bg-white p-4 rounded-lg border-2 border-green-200">
                <h4 className="text-sm font-semibold text-green-700 mb-2">Strengths</h4>
                <ul className="space-y-1">
                  {positioning.strengths.map((strength, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {positioning.differentiation && positioning.differentiation.length > 0 && (
              <div className="bg-white p-4 rounded-lg border-2 border-indigo-200">
                <h4 className="text-sm font-semibold text-indigo-700 mb-2">Differentiation</h4>
                <ul className="space-y-1">
                  {positioning.differentiation.map((diff, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="text-indigo-500 mr-2">→</span>
                      {diff}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Target Segments */}
      {target_segments && target_segments.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">👥</span>
            Target Segments
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {target_segments.map((segment, index) => (
              <div key={index} className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-bold text-gray-900">{segment.name}</h4>
                  {segment.priority && (
                    <span className={`text-xs px-2 py-1 rounded ${
                      segment.priority === 'Primary' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {segment.priority}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-2">{segment.description}</p>
                {segment.size && (
                  <p className="text-xs text-gray-500">Market Size: <span className="font-semibold">{segment.size}</span></p>
                )}
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

      {/* Channels */}
      {channels && channels.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">📢</span>
            Distribution Channels
          </h3>
          <div className="grid md:grid-cols-2 gap-3">
            {channels.map((channel, index) => (
              <div key={index} className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200">
                <h4 className="text-sm font-semibold text-gray-900 mb-2">{channel.channel}</h4>
                <p className="text-xs text-gray-600">{channel.rationale}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tactics */}
      {tactics && tactics.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">⚡</span>
            Marketing Tactics
          </h3>
          <div className="space-y-4">
            {tactics.map((tactic, index) => (
              <div key={index} className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-gray-900">{tactic.phase}</h4>
                  {tactic.timeline && (
                    <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                      {tactic.timeline}
                    </span>
                  )}
                </div>
                {tactic.actions && tactic.actions.length > 0 && (
                  <ul className="space-y-1 mt-2">
                    {tactic.actions.map((action, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-start">
                        <span className="text-blue-500 mr-2">•</span>
                        {action}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pricing Strategy */}
      {pricing_strategy && (
        <div className="card card-elevated bg-gradient-to-br from-green-50 to-emerald-50">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">💰</span>
            Pricing Strategy
          </h3>
          <div className="space-y-3">
            {pricing_strategy.recommendation && (
              <div className="bg-white p-4 rounded-lg border-2 border-green-200">
                <h4 className="text-sm font-semibold text-green-700 mb-2">Recommendation</h4>
                <p className="text-sm text-gray-700">{pricing_strategy.recommendation}</p>
              </div>
            )}
            {pricing_strategy.rationale && (
              <div className="bg-white p-4 rounded-lg border-2 border-emerald-200">
                <h4 className="text-sm font-semibold text-emerald-700 mb-2">Rationale</h4>
                <p className="text-sm text-gray-700">{pricing_strategy.rationale}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default MarketingStrategyACE
