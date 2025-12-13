import React from 'react'

const ProgressBar = ({ value, max = 100, label, showValue = true }) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  
  // Color based on value
  const getColor = () => {
    if (percentage >= 75) return 'bg-green-500'
    if (percentage >= 50) return 'bg-yellow-500'
    if (percentage >= 25) return 'bg-orange-500'
    return 'bg-red-500'
  }

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          {showValue && (
            <span className="text-sm font-bold text-gray-900">{value}/{max}</span>
          )}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
        <div
          className={`h-full ${getColor()} transition-all duration-500 ease-out flex items-center justify-end pr-2`}
          style={{ width: `${percentage}%` }}
        >
          {percentage > 10 && (
            <span className="text-xs font-bold text-white">{Math.round(percentage)}%</span>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProgressBar
