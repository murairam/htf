import React, { useState } from 'react'

const Accordion = ({ title, icon, children, defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="border-2 border-gray-200 rounded-xl overflow-hidden mb-4 shadow-lg transform transition-all duration-300 hover:shadow-2xl hover:scale-[1.01]">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 bg-gradient-to-r from-white to-gray-50 hover:from-gray-50 hover:to-gray-100 transition-all duration-300"
      >
        <div className="flex items-center space-x-3">
          <span className="text-2xl transform transition-transform duration-300 hover:scale-110">{icon}</span>
          <h3 className="font-semibold text-lg text-gray-900">{title}</h3>
        </div>
        <svg
          className={`w-6 h-6 text-gray-500 transition-all duration-300 ${
            isOpen ? 'transform rotate-180 text-green-600' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isOpen && (
        <div className="p-5 bg-gradient-to-br from-gray-50 to-white border-t-2 border-gray-200 shadow-inner">
          {children}
        </div>
      )}
    </div>
  )
}

export default Accordion
