# Document Scanner Mobile App

A professional document scanner app for **Android** and **iOS** built with Flutter. Scan documents with automatic edge detection, perspective correction, and smart lighting enhancement.

## Features

### Core Functionality
- **Live Camera Preview**: Real-time camera view with document guide overlay
- **Automatic Edge Detection**: Intelligently detects document boundaries
- **Perspective Correction**: Transforms skewed photos into perfect rectangular scans
- **Smart Image Enhancement**: Auto-enhance with brightness and contrast correction
- **Manual Controls**: Fine-tune brightness, contrast, and apply filters
- **Black & White Mode**: Crisp text scanning with adaptive thresholding
- **Save & Share**: Save scanned documents and share instantly

### Mobile-Optimized
- **High Resolution**: Uses device's maximum camera resolution
- **Flash Control**: Toggle flash for low-light conditions
- **Responsive UI**: Beautiful Material Design interface
- **Cross-Platform**: Single codebase for both Android and iOS
- **Offline Processing**: All processing happens on-device, no internet required

## Screenshots

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Home Screen   │  │  Camera View    │  │  Preview/Edit   │
│                 │  │                 │  │                 │
│  Document       │  │  [Live Camera]  │  │  [Processed]    │
│  Scanner        │  │                 │  │                 │
│                 │  │  [Guidelines]   │  │  Brightness     │
│  [Scan Button]  │  │                 │  │  Contrast       │
│  [Gallery]      │  │  [Capture]      │  │  B&W Mode       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Installation & Setup

### Prerequisites

1. **Install Flutter**
   - Follow the official guide: https://docs.flutter.dev/get-started/install
   - Verify installation: `flutter doctor`

2. **Install Dependencies**
   ```bash
   cd mobile_app
   flutter pub get
   ```

### Running the App

#### Android

1. **Connect an Android device** or start an emulator
2. **Enable Developer Mode** on your device
3. **Run the app:**
   ```bash
   flutter run
   ```

#### iOS

1. **Open Xcode** and ensure you have the latest version
2. **Connect an iPhone** or start a simulator
3. **Run the app:**
   ```bash
   flutter run
   ```

### Building Release Versions

#### Android APK
```bash
flutter build apk --release
```
Output: `build/app/outputs/flutter-apk/app-release.apk`

#### Android App Bundle (for Play Store)
```bash
flutter build appbundle --release
```
Output: `build/app/outputs/bundle/release/app-release.aab`

#### iOS (requires macOS with Xcode)
```bash
flutter build ios --release
```
Then open `ios/Runner.xcworkspace` in Xcode to archive and distribute.

## Project Structure

```
mobile_app/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── screens/
│   │   ├── camera_screen.dart    # Camera with live preview
│   │   └── preview_screen.dart   # Image preview and editing
│   └── utils/
│       └── image_processor.dart  # Image processing utilities
├── android/                      # Android-specific files
│   └── app/
│       └── src/main/
│           └── AndroidManifest.xml
├── ios/                         # iOS-specific files
│   └── Runner/
│       └── Info.plist
└── pubspec.yaml                 # Dependencies
```

## Dependencies

### Main Packages
- **camera** (^0.10.5+5): Camera access and control
- **image** (^4.1.3): Image processing and manipulation
- **edge_detection** (^1.1.1): Document edge detection
- **path_provider** (^2.1.1): File system access
- **permission_handler** (^11.0.1): Runtime permissions
- **share_plus** (^7.2.1): Share functionality

## How It Works

### 1. Camera Capture
- Uses device's back camera with high resolution
- Displays guide overlay to help position documents
- Flash toggle for low-light conditions
- Capture button with smooth animation

### 2. Image Processing Pipeline

```
Capture Image
     ↓
Convert to Grayscale
     ↓
Apply Gaussian Blur (noise reduction)
     ↓
Edge Detection (Sobel operator)
     ↓
Find Contours & Detect Document
     ↓
Apply Perspective Transform
     ↓
Enhancement (brightness/contrast)
     ↓
Save/Share
```

### 3. Enhancement Features

**Auto-Enhancement:**
- Adaptive brightness correction
- Contrast optimization
- Histogram equalization

**Manual Controls:**
- Brightness: -50 to +50
- Contrast: 0.5x to 2.0x
- Black & White mode with adaptive thresholding

## Permissions

### Android
- `CAMERA`: Required for camera access
- `WRITE_EXTERNAL_STORAGE`: Save scanned documents
- `READ_EXTERNAL_STORAGE`: Access gallery images
- `READ_MEDIA_IMAGES`: Android 13+ media access

### iOS
- `NSCameraUsageDescription`: Camera access for scanning
- `NSPhotoLibraryUsageDescription`: Access photo library
- `NSPhotoLibraryAddUsageDescription`: Save to photo library

## Usage Guide

### Quick Start

1. **Launch the app**
2. **Tap "Scan Document"**
3. **Grant camera permission** when prompted
4. **Position your document** within the guide overlay
5. **Tap the capture button** (white circle)
6. **Review the processed image**
7. **Apply enhancements:**
   - Tap "Auto-Enhance" for automatic improvement
   - Use sliders for manual brightness/contrast
   - Toggle "Black & White" for text documents
8. **Save or Share** the final scan

### Best Practices

**For Best Results:**
- Use contrasting background (white paper on dark surface)
- Ensure good lighting
- Keep document flat
- Position camera parallel to document
- Capture entire document within frame

**Lighting Tips:**
- Natural light works best
- Use flash in low light
- Avoid shadows on document
- Even lighting prevents one-sided darkness

## Troubleshooting

### Camera Not Working
- Grant camera permissions in Settings
- Restart the app
- Check if another app is using the camera

### Poor Edge Detection
- Improve lighting
- Use contrasting background
- Ensure document is flat
- Check that document edges are visible

### App Crashes
- Check Flutter version: `flutter --version`
- Clean build: `flutter clean && flutter pub get`
- Update dependencies: `flutter pub upgrade`

### Build Errors

**Android:**
```bash
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
flutter run
```

**iOS:**
```bash
cd ios
pod deintegrate
pod install
cd ..
flutter clean
flutter pub get
flutter run
```

## Performance

- **Fast Processing**: Native image processing
- **Efficient Memory**: Optimized for mobile devices
- **Battery Friendly**: Minimal background activity
- **Offline**: No internet required

## Future Enhancements

Planned features:
- Multi-page PDF export
- OCR (text extraction)
- Cloud storage integration
- Batch scanning mode
- Custom filters
- Document organization
- Password protection
- QR code scanning

## Development

### Running Tests
```bash
flutter test
```

### Code Formatting
```bash
flutter format lib/
```

### Analyzing Code
```bash
flutter analyze
```

## Contributing

This is an open-source project. Contributions are welcome!

## License

Open source - free for personal and commercial use.

## Technical Details

### Minimum Requirements
- **Android**: API Level 21 (Android 5.0) or higher
- **iOS**: iOS 11.0 or higher
- **Flutter**: 3.0.0 or higher

### Camera Specifications
- Resolution: Up to 1080p (device-dependent)
- Format: JPEG
- Focus: Auto-focus supported

### Image Processing
- **Edge Detection**: Sobel operator
- **Perspective Transform**: Homography matrix
- **Enhancement**: Histogram equalization
- **Threshold**: Otsu's method for B&W

## Support

For issues or questions:
- Check the troubleshooting section
- Review Flutter documentation
- Open an issue on GitHub

---

Built with Flutter for professional document scanning on mobile devices.
