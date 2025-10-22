# Professional Document Scanner

A complete document scanning solution available in two versions:
- **Web App**: Browser-based scanner using OpenCV.js (works on any device)
- **Mobile App**: Native Android & iOS app built with Flutter

Both versions transform photos of documents into professionally scanned images with automatic edge detection, perspective correction, and lighting enhancement.

## Features

- **Automatic Document Detection**: Intelligently detects document edges in photos
- **Perspective Correction**: Transforms skewed documents to perfect rectangular shape
- **Smart Lighting Correction**: Automatically enhances brightness and contrast even in poor lighting
- **Manual Controls**: Fine-tune brightness, contrast, and apply black & white filter
- **High Resolution**: Captures and processes images at highest available camera resolution
- **Cross-Platform**: Works on desktop and mobile devices with camera access
- **No Installation**: Pure web app, no downloads or installations needed

## How It Works

### 1. Edge Detection
Using OpenCV.js computer vision library, the app:
- Converts the image to grayscale
- Applies Gaussian blur to reduce noise
- Uses Canny edge detection to find edges
- Finds contours and identifies the largest quadrilateral (the document)

### 2. Perspective Transformation
Once the document is detected:
- Identifies the four corners of the document
- Calculates the optimal output dimensions (maintaining A4 ratio)
- Applies perspective transform to create a perfect top-down view
- Produces a properly sized scanned document

### 3. Image Enhancement
Multiple enhancement options:
- **Auto-Enhance**: Uses CLAHE (Contrast Limited Adaptive Histogram Equalization) in LAB color space for optimal lighting correction
- **Brightness Control**: Manual adjustment (-50 to +50)
- **Contrast Control**: Manual adjustment (0.5x to 2x)
- **Black & White Mode**: Applies adaptive thresholding for crisp text

## Usage

### Quick Start

1. Open `index.html` in a modern web browser
2. Grant camera permissions when prompted
3. Position your document on a contrasting background
4. Click "Capture Document"
5. Review the processed image
6. Use "Auto-Enhance" for automatic lighting correction
7. Adjust brightness/contrast manually if needed
8. Download the final scanned document

### Using a Local Server

For best results, serve the files using a local web server:

```bash
# Using Python 3
python -m http.server 8000

# Using Python 2
python -m SimpleHTTPServer 8000

# Using Node.js
npx http-server

# Using PHP
php -S localhost:8000
```

Then open `http://localhost:8000` in your browser.

### Best Practices

For optimal results:
- Use good contrast between document and background (e.g., white paper on dark table)
- Ensure the entire document is visible in the frame
- Use adequate lighting (natural light works best)
- Keep the camera steady when capturing
- Position the document as flat as possible

## Technical Details

### Technologies Used
- **HTML5 Canvas API**: Image rendering and manipulation
- **WebRTC getUserMedia**: Camera access
- **OpenCV.js**: Computer vision processing
- **Vanilla JavaScript**: No framework dependencies

### Browser Compatibility
- Chrome/Edge 53+
- Firefox 36+
- Safari 11+
- Mobile browsers with camera support

### Key Algorithms
- **Canny Edge Detection**: Identifies document edges
- **Contour Detection**: Finds document outline
- **Perspective Transform**: Corrects skew and angle
- **CLAHE**: Adaptive histogram equalization for lighting
- **Otsu's Thresholding**: Automatic binary threshold for B&W mode

## Project Structure

This repository contains two complete implementations:

### Web Version (Root Directory)
```
.
├── index.html          # Main HTML interface
├── style.css           # Styling and responsive design
├── app.js             # Core application logic and OpenCV processing
└── README.md          # Main documentation
```

### Mobile Version (mobile_app/)
```
mobile_app/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── screens/                  # Camera and preview screens
│   └── utils/                    # Image processing utilities
├── android/                      # Android configuration
├── ios/                         # iOS configuration
├── pubspec.yaml                 # Flutter dependencies
└── README.md                    # Mobile app documentation
```

## Choosing Your Version

### Use the Web App if:
- You want zero installation
- You need cross-platform compatibility
- You prefer accessing via browser
- You want quick prototyping

### Use the Mobile App if:
- You want native performance
- You need offline functionality
- You want app store distribution
- You prefer dedicated mobile app experience

## Troubleshooting

### Camera Not Working
- Ensure you've granted camera permissions
- Try using HTTPS or localhost (required by some browsers)
- Check if another application is using the camera

### Poor Detection
- Improve lighting conditions
- Increase contrast with background
- Ensure document edges are clearly visible
- Try a darker or lighter background

### Slow Processing
- Normal on first use (OpenCV.js needs to load ~8MB)
- Subsequent scans will be faster
- Lower resolution cameras will process faster

## Future Enhancements

Potential improvements:
- PDF export with multiple pages
- OCR (Optical Character Recognition) for text extraction
- Cloud storage integration
- Batch scanning mode
- Custom page size presets
- Advanced filters (sepia, sharpen, etc.)

## License

This project is open source and available for personal and commercial use.

## Credits

Built with:
- [OpenCV.js](https://docs.opencv.org/4.x/d5/d10/tutorial_js_root.html) - Computer vision library
- Modern web standards (HTML5, CSS3, ES6+)

---

Made with precision and attention to detail for professional document scanning needs.
