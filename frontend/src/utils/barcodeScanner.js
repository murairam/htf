// Barcode scanner utility using QuaggaJS
// Note: QuaggaJS will be loaded via CDN in index.html

export const initBarcodeScanner = (videoElementId, onDetected, onError) => {
  if (typeof Quagga === 'undefined') {
    console.error('QuaggaJS not loaded');
    onError('Barcode scanner library not loaded');
    return null;
  }

  const config = {
    inputStream: {
      name: "Live",
      type: "LiveStream",
      target: document.querySelector(`#${videoElementId}`),
      constraints: {
        width: 640,
        height: 480,
        facingMode: "environment"
      },
    },
    decoder: {
      readers: [
        "ean_reader",
        "ean_8_reader",
        "code_128_reader",
        "code_39_reader",
        "upc_reader",
        "upc_e_reader"
      ],
      debug: {
        drawBoundingBox: true,
        showFrequency: true,
        drawScanline: true,
        showPattern: true
      }
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
    Quagga.init(config, (err) => {
      if (err) {
        console.error('QuaggaJS initialization error:', err);
        onError(err.message || 'Failed to initialize camera');
        reject(err);
        return;
      }
      
      console.log('QuaggaJS initialized successfully');
      Quagga.start();
      
      // Set up detection handler
      Quagga.onDetected((result) => {
        if (result && result.codeResult && result.codeResult.code) {
          console.log('Barcode detected:', result.codeResult.code);
          onDetected(result.codeResult.code);
        }
      });
      
      resolve();
    });
  });
};

export const stopBarcodeScanner = () => {
  if (typeof Quagga !== 'undefined') {
    Quagga.stop();
    console.log('QuaggaJS stopped');
  }
};
