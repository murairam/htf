
import React, { useState, useEffect, useRef } from 'react'
import { initBarcodeScanner, stopBarcodeScanner } from '../utils/barcodeScanner'
import Button from './Button'

const BarcodeScanner = ({ onBarcodeDetected }) => {
  const [isScanning, setIsScanning] = useState(false)
  const [error, setError] = useState(null)
  const [manualBarcode, setManualBarcode] = useState('')
  const scannerInitialized = useRef(false)
  const timeoutRef = useRef(null)

  const startScanning = async () => {
    setError(null)
    setIsScanning(true)
    scannerInitialized.current = false

    try {
      await initBarcodeScanner(
        'barcode-scanner',
        (code) => {
          console.log('Barcode detected:', code)
          stopScanning()
          onBarcodeDetected(code)
        },
        (err) => {
          console.error('Scanner error:', err)
          setError(err)
          setIsScanning(false)
        }
      )
      
      scannerInitialized.current = true

      // Set 10 second timeout
      timeoutRef.current = setTimeout(() => {
        if (isScanning) {
          console.log('Scanner timeout after 10 seconds')
          stopScanning()
          setError('Scan timeout. Please try again or enter barcode manually.')
        }
      }, 10000)

    } catch (err) {
      console.error('Failed to start scanner:', err)
      setError('Failed to access camera. Please check permissions or use manual input.')
      setIsScanning(false)
    }
  }

  const stopScanning = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    
    if (scannerInitialized.current) {
      stopBarcodeScanner()
      scannerInitialized.current = false
    }
    
    setIsScanning(false)
  }

  const retryScanning = () => {
    console.log('Retrying scanner...')
    stopScanning()
    setTimeout(() => {
      startScanning()
    }, 100)
  }

  useEffect(() => {
    return () => {
      stopScanning()
    }
  }, [])

  return (
    <div className="space-y-4">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Barcode Input</h3>
        
        {/* Camera Scanner */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Camera Scan
          </label>
          
          {!isScanning ? (
            <Button onClick={startScanning} className="w-full">
              Start Camera Scan
            </Button>
          ) : (
            <div className="space-y-3">
              <div 
                id="barcode-scanner" 
                className="w-full h-64 bg-black rounded-lg overflow-hidden"
              />
              <div className="flex gap-2">
                <Button onClick={stopScanning} variant="secondary" className="flex-1">
                  Stop Scan
                </Button>
                <Button onClick={retryScanning} variant="secondary" className="flex-1">
                  Retry Scan
                </Button>
              </div>
            </div>
          )}
          
          {error && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Manual Input Fallback */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Manual Barcode Entry (Fallback)
          </label>
          <input
            type="text"
            value={manualBarcode}
            onChange={(e) => {
              const value = e.target.value.replace(/\D/g, '')
              setManualBarcode(value)
              if (value.length >= 8 && value.length <= 13) {
                onBarcodeDetected(value)
              }
            }}
            placeholder="Enter barcode digits (8-13 digits)"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            pattern="[0-9]*"
            minLength="8"
            maxLength="13"
          />
          <p className="mt-2 text-xs text-gray-500">
            Enter 8-13 digit barcode (EAN/UPC format) - automatically detected when valid
          </p>
        </div>
      </div>
    </div>
  )
}

export default BarcodeScanner
