import React from 'react'
import { Link } from 'react-router-dom'

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-lg font-bold text-gray-900">Plant-Based Intelligence Platform</span>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              AI-powered marketing & packaging analysis for plant-based food innovation
            </p>
            <p className="text-xs text-gray-500">
              © 2025 Plant-Based Intelligence Platform. All rights reserved.
            </p>
          </div>

          {/* Solutions */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Solutions</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  For Individuals
                </Link>
              </li>
              <li>
                <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  For Teams
                </Link>
              </li>
              <li>
                <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  Enterprise
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  API
                </Link>
              </li>
              <li>
                <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  Help Docs
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Company</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  Privacy
                </Link>
              </li>
              <li>
                <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  Terms
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer

