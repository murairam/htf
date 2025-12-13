// Barcode scanner utility using QuaggaJS
// Note: QuaggaJS will be loaded via CDN in index.html

let isQuaggaInitialized = false;
let currentScanner = null;
let detectionHandled = false;

// Helper to wait for QuaggaJS to load
const waitForQuagga = (maxAttempts = 20, delay = 200) => {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const checkQuagga = () => {
      // Check multiple possible locations for QuaggaJS
      let QuaggaInstance = null;
      
      if (typeof window !== 'undefined') {
        QuaggaInstance = window.Quagga || window.quagga || window.QuaggaJS;
      }
      
      // Also check global scope (for non-module scripts)
      if (!QuaggaInstance && typeof Quagga !== 'undefined') {
        QuaggaInstance = Quagga;
      }
      
      if (QuaggaInstance && typeof QuaggaInstance.init === 'function') {
        resolve(QuaggaInstance);
      } else if (attempts < maxAttempts) {
        attempts++;
        setTimeout(checkQuagga, delay);
      } else {
        reject(new Error('QuaggaJS library not loaded. Please refresh the page.'));
      }
    };
    checkQuagga();
  });
};

export const initBarcodeScanner = async (videoElementId, onDetected, onError, onInitialized) => {
  // Wait for QuaggaJS to be available
  let QuaggaInstance;
  try {
    console.log('Waiting for QuaggaJS to load...');
    QuaggaInstance = await waitForQuagga();
    console.log('QuaggaJS loaded successfully');
  } catch (err) {
    console.error('QuaggaJS not loaded:', err);
    onError('Barcode scanner library not loaded. Please refresh the page.');
    return Promise.reject(err);
  }

  // Stop any existing scanner first
  if (isQuaggaInitialized) {
    stopBarcodeScanner();
  }
  
  // Reset detection flag
  detectionHandled = false;

  const targetElement = document.querySelector(`#${videoElementId}`);
  if (!targetElement) {
    console.error(`Element with id "${videoElementId}" not found`);
    onError('Scanner container not found');
    return Promise.reject(new Error('Scanner container not found'));
  }

  // Simplified config for better compatibility
  // Try to get user media first to check permissions
  const constraints = {
    width: { ideal: 640 },
    height: { ideal: 480 },
    facingMode: "environment" // Use back camera on mobile
  };

  const config = {
    inputStream: {
      name: "Live",
      type: "LiveStream",
      target: targetElement,
      constraints: constraints,
    },
    decoder: {
      readers: [
        "ean_reader",
        "ean_8_reader",
        "code_128_reader",
        "code_39_reader",
        "upc_reader",
        "upc_e_reader"
      ]
    },
    locate: true,
    locator: {
      patchSize: "medium",
      halfSample: true
    },
    numOfWorkers: 2,
    frequency: 10,
  };

  return new Promise((resolve, reject) => {
    try {
      console.log('Initializing QuaggaJS with config...');
      QuaggaInstance.init(config, (err) => {
        if (err) {
          console.error('QuaggaJS initialization error:', err);
          const errorMessage = err.message || err.toString() || 'Failed to initialize camera';
          
          // Provide more helpful error messages
          if (errorMessage.includes('Permission') || errorMessage.includes('permission')) {
            onError('Camera permission denied. Please allow camera access and try again.');
          } else if (errorMessage.includes('NotFound') || errorMessage.includes('not found')) {
            onError('No camera found. Please connect a camera or use manual input.');
          } else if (errorMessage.includes('NotAllowed') || errorMessage.includes('not allowed')) {
            onError('Camera access not allowed. Please check browser permissions.');
          } else {
            onError(`Camera error: ${errorMessage}. Please try manual input.`);
          }
          
          isQuaggaInitialized = false;
          reject(err);
          return;
        }
        
        console.log('QuaggaJS initialized successfully, starting camera...');
        isQuaggaInitialized = true;
        currentScanner = { elementId: videoElementId, onDetected, onError };
        
        try {
          QuaggaInstance.start();
          console.log('QuaggaJS start() called');
          
          // Clean up any debug overlays or unwanted elements
          setTimeout(() => {
            // Hide any drawingBuffer canvas (debug overlay)
            const drawingBuffers = targetElement.querySelectorAll('.drawingBuffer, canvas.drawingBuffer');
            drawingBuffers.forEach(canvas => {
              canvas.style.display = 'none';
            });
            
            // Hide any canvas that's not the main video canvas
            const canvases = targetElement.querySelectorAll('canvas');
            if (canvases.length > 1) {
              // Keep only the first canvas (main video), hide others
              for (let i = 1; i < canvases.length; i++) {
                canvases[i].style.display = 'none';
              }
            }
            
            // Make all containers transparent (remove any black/green backgrounds)
            const containers = targetElement.querySelectorAll('.viewport-wrapper, .viewport, div[style*="background"], div');
            containers.forEach(container => {
              // Skip the root container and video element
              if (container.id !== videoElementId && container.tagName !== 'VIDEO' && container.tagName !== 'CANVAS') {
                container.style.backgroundColor = 'transparent';
                container.style.background = 'transparent';
              }
            });
            
            // Also check for any elements with black backgrounds
            const allElements = targetElement.querySelectorAll('*');
            allElements.forEach(element => {
              if (element.tagName !== 'VIDEO' && element.tagName !== 'CANVAS') {
                const bgColor = window.getComputedStyle(element).backgroundColor;
                // If background is black or dark, make it transparent
                if (bgColor && (bgColor.includes('rgb(0, 0, 0)') || bgColor.includes('rgba(0, 0, 0'))) {
                  element.style.backgroundColor = 'transparent';
                  element.style.background = 'transparent';
                }
              }
            });
            
            const videoElement = targetElement.querySelector('video');
            if (videoElement && videoElement.readyState >= 2) {
              console.log('Camera stream is ready');
              // Notify component that initialization is complete
              if (onInitialized) {
                onInitialized();
              }
            } else {
              console.warn('Camera stream not ready yet, but continuing...');
              // Still notify - the stream might start later
              if (onInitialized) {
                onInitialized();
              }
            }
          }, 500);
          
        } catch (startErr) {
          console.error('Error starting QuaggaJS:', startErr);
          onError(`Failed to start camera: ${startErr.message || startErr.toString()}`);
          isQuaggaInitialized = false;
          reject(startErr);
          return;
        }
        
        // Set up detection handler - prevent multiple detections
        QuaggaInstance.onDetected((result) => {
          // Prevent multiple detections
          if (detectionHandled) {
            return;
          }
          
          if (result && result.codeResult && result.codeResult.code) {
            const code = result.codeResult.code.trim();
            console.log('Barcode detected:', code);
            
            // Validate barcode length (EAN/UPC are 8-13 digits)
            if (code.length >= 8 && code.length <= 13 && /^\d+$/.test(code)) {
              detectionHandled = true;
              // Stop scanner before calling callback
              try {
                QuaggaInstance.offDetected();
                QuaggaInstance.stop();
                isQuaggaInitialized = false;
                currentScanner = null;
              } catch (e) {
                console.warn('Error stopping scanner after detection:', e);
              }
              onDetected(code);
            } else {
              console.warn('Invalid barcode format:', code, 'Length:', code.length);
            }
          }
        });
        
        resolve();
      });
    } catch (err) {
      console.error('Exception during QuaggaJS init:', err);
      onError(`Failed to start scanner: ${err.message || err.toString()}`);
      isQuaggaInitialized = false;
      reject(err);
    }
  });
};

export const stopBarcodeScanner = () => {
  let QuaggaInstance = null;
  
  if (typeof window !== 'undefined') {
    QuaggaInstance = window.Quagga || window.quagga || window.QuaggaJS;
  }
  
  if (!QuaggaInstance && typeof Quagga !== 'undefined') {
    QuaggaInstance = Quagga;
  }
  
  if (QuaggaInstance && isQuaggaInitialized) {
    try {
      // Remove detection handler if method exists
      if (typeof QuaggaInstance.offDetected === 'function') {
        QuaggaInstance.offDetected();
      }
      if (typeof QuaggaInstance.stop === 'function') {
        QuaggaInstance.stop();
      }
      isQuaggaInitialized = false;
      currentScanner = null;
      detectionHandled = false;
      console.log('QuaggaJS stopped');
    } catch (err) {
      console.error('Error stopping QuaggaJS:', err);
      // Reset state even if stop fails
      isQuaggaInitialized = false;
      currentScanner = null;
      detectionHandled = false;
    }
  }
};
