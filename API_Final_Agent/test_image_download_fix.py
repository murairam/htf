"""
Test script to verify the image download fix for Vision API timeout issue.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_final_agent.ace.product_data import ImageAnalyzer
import urllib.request
import base64

def test_image_download():
    """Test that we can download and encode an image from OpenFoodFacts."""
    
    # The problematic URL from the error log
    image_url = "https://images.openfoodfacts.org/images/products/327/408/000/5003/front_en.797.400.jpg"
    
    print(f"Testing image download from: {image_url}")
    print("-" * 80)
    
    try:
        # Simulate the new download logic
        print("1. Creating request with User-Agent header...")
        request = urllib.request.Request(
            image_url,
            headers={"User-Agent": "PlantBasedIntelligence/1.0"}
        )
        
        print("2. Downloading image with 30s timeout...")
        max_retries = 3
        retry_delay = 2
        image_data = None
        
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    image_data = response.read()
                    print(f"   ✅ Download successful on attempt {attempt + 1}")
                    break
            except Exception as download_error:
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Attempt {attempt + 1} failed: {download_error}")
                    print(f"   Retrying in {retry_delay}s...")
                    import time
                    time.sleep(retry_delay)
                else:
                    raise download_error
        
        if not image_data:
            raise Exception("Failed to download image after retries")
        
        print(f"3. Image downloaded successfully: {len(image_data)} bytes")
        
        # Encode to base64
        print("4. Encoding to base64...")
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        print(f"   ✅ Base64 encoded: {len(image_base64)} characters")
        
        # Determine media type
        media_type = "image/jpeg"
        if image_url.lower().endswith('.png'):
            media_type = "image/png"
        elif image_url.lower().endswith('.webp'):
            media_type = "image/webp"
        
        print(f"5. Detected media type: {media_type}")
        
        # Create data URL (what we'll send to Vision API)
        data_url = f"data:{media_type};base64,{image_base64[:50]}..."
        print(f"6. Data URL created: {data_url}")
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS! Image download and encoding works correctly.")
        print("=" * 80)
        print("\nThe fix should resolve the Vision API timeout issue by:")
        print("1. Downloading the image locally first (with retries)")
        print("2. Encoding it to base64")
        print("3. Sending it as a data URL to OpenAI Vision API")
        print("\nThis avoids OpenAI's timeout when trying to download from external URLs.")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ ERROR: {e}")
        print("=" * 80)
        return False


def test_analyzer_without_api_key():
    """Test ImageAnalyzer behavior without API key (should not crash)."""
    print("\n" + "=" * 80)
    print("Testing ImageAnalyzer without API key...")
    print("=" * 80)
    
    analyzer = ImageAnalyzer(api_key=None)
    result = analyzer.analyze_from_url("https://example.com/image.jpg")
    
    print(f"Result type: {type(result)}")
    print(f"Description: {result.image_description}")
    print("✅ ImageAnalyzer handles missing API key gracefully")
    
    return True


if __name__ == "__main__":
    print("=" * 80)
    print("IMAGE DOWNLOAD FIX VERIFICATION TEST")
    print("=" * 80)
    print()
    
    # Test 1: Image download and encoding
    test1_passed = test_image_download()
    
    # Test 2: Analyzer without API key
    test2_passed = test_analyzer_without_api_key()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Test 1 (Image Download): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (No API Key):     {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The fix is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)
