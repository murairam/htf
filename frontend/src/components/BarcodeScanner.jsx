
import React, { useState, useEffect, useRef } from 'react'
import { initBarcodeScanner, stopBarcodeScanner } from '../utils/barcodeScanner'
import Button from './Button'

const BarcodeScanner = ({ onBarcodeDetected }) => {
  const [isScanning, setIsScanning] = useState(false)
  const [isInitialized, setIsInitialized] = useState(false)
  const [error, setError] = useState(null)
  const [manualBarcode, setManualBarcode] = useState('')
  const scannerInitialized = useRef(false)
  const timeoutRef = useRef(null)

  const startScanning = async () => {
    setError(null)
    setIsScanning(true)
    setIsInitialized(false)
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
          setError(typeof err === 'string' ? err : (err.message || 'Failed to access camera'))
          setIsScanning(false)
          setIsInitialized(false)
          scannerInitialized.current = false
        },
        () => {
          // Callback when camera is initialized and started
          console.log('Camera initialized and started')
          scannerInitialized.current = true
          setIsInitialized(true)
        }
      )

      // Set 30 second timeout (increased from 10s)
      timeoutRef.current = setTimeout(() => {
        if (scannerInitialized.current) {
          console.log('Scanner timeout after 30 seconds')
          stopScanning()
          setError('Scan timeout. Please try again or enter barcode manually.')
        }
      }, 30000)

    } catch (err) {
      console.error('Failed to start scanner:', err)
      setError(typeof err === 'string' ? err : (err.message || 'Failed to access camera. Please check permissions or use manual input.'))
      setIsScanning(false)
      setIsInitialized(false)
      scannerInitialized.current = false
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
    setIsInitialized(false)
  }

  const retryScanning = () => {
    console.log('Retrying scanner...')
    stopScanning()
    setTimeout(() => {
      startScanning()
    }, 100)
  }

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      stopScanning()
    }
  }, [])

  // Cleanup timeout when component unmounts or scanning stops
  useEffect(() => {
    if (!isScanning && timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
  }, [isScanning])

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
            <div className="space-y-3">
              <Button onClick={startScanning} className="w-full">
                📷 Start Camera Scan
              </Button>
              <p className="text-xs text-gray-500 text-center">
                Click to start camera and scan a barcode
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <div 
                id="barcode-scanner" 
                className="w-full h-64 bg-black rounded-lg overflow-hidden relative flex items-center justify-center"
                style={{ minHeight: '256px' }}
              >
                <style>{`
                  #barcode-scanner video,
                  #barcode-scanner canvas {
                    width: 100% !important;
                    height: 100% !important;
                    object-fit: cover !important;
                    position: absolute;
                    top: 0;
                    left: 0;
                    background: transparent !important;
                    background-color: transparent !important;
                  }
                  #barcode-scanner > div {
                    width: 100% !important;
                    height: 100% !important;
                    position: relative;
                    background: transparent !important;
                    background-color: transparent !important;
                  }
                  /* Hide QuaggaJS debug overlays */
                  #barcode-scanner .drawingBuffer,
                  #barcode-scanner canvas.drawingBuffer {
                    display: none !important;
                  }
                  /* Hide any canvas that's not the main video canvas */
                  #barcode-scanner canvas:not(:first-of-type) {
                    display: none !important;
                  }
                  /* Make all QuaggaJS containers transparent */
                  #barcode-scanner .viewport-wrapper,
                  #barcode-scanner .viewport,
                  #barcode-scanner .viewport > div,
                  #barcode-scanner > div > div {
                    background: transparent !important;
                    background-color: transparent !important;
                  }
                  /* Force transparency on all child elements except video and root container */
                  #barcode-scanner > div *:not(video):not(canvas) {
                    background-color: transparent !important;
                  }
                  /* Keep root container black */
                  #barcode-scanner {
                    background-color: black !important;
                  }
                `}</style>
                {!isInitialized && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
                    <div className="text-center text-white">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                      <p className="text-sm">Initializing camera...</p>
                      <p className="text-xs text-gray-400 mt-2">Please allow camera access if prompted</p>
                    </div>
                  </div>
                )}
                {isInitialized && (
                  <div className="absolute top-2 left-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded z-20 border border-white border-opacity-30">
                    📹 Camera Active
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <Button onClick={stopScanning} variant="secondary" className="flex-1">
                  ⏹️ Stop Scan
                </Button>
                <Button onClick={retryScanning} variant="secondary" className="flex-1">
                  🔄 Retry Scan
                </Button>
              </div>
              <p className="text-xs text-gray-500 text-center">
                Point camera at barcode. Scanning will stop automatically when detected.
              </p>
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
