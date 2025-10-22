// Global variables
let video, canvas, ctx;
let originalCanvas, processedCanvas;
let originalImage, processedImage;
let opencvReady = false;
let stream = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

function init() {
    // Get DOM elements
    video = document.getElementById('video');
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    originalCanvas = document.getElementById('originalCanvas');
    processedCanvas = document.getElementById('processedCanvas');

    // Setup event listeners
    document.getElementById('captureBtn').addEventListener('click', captureImage);
    document.getElementById('retakeBtn').addEventListener('click', retake);
    document.getElementById('enhanceBtn').addEventListener('click', autoEnhance);
    document.getElementById('downloadBtn').addEventListener('click', downloadImage);

    // Enhancement controls
    document.getElementById('brightnessSlider').addEventListener('input', updateEnhancement);
    document.getElementById('contrastSlider').addEventListener('input', updateEnhancement);
    document.getElementById('bwMode').addEventListener('change', updateEnhancement);

    // Start camera
    startCamera();
}

// OpenCV ready callback
function onOpenCvReady() {
    opencvReady = true;
    console.log('OpenCV.js is ready');
}

// Start camera with high resolution
async function startCamera() {
    try {
        const constraints = {
            video: {
                width: { ideal: 1920 },
                height: { ideal: 1080 },
                facingMode: 'environment' // Use back camera on mobile
            }
        };

        stream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = stream;
        video.play();
    } catch (err) {
        console.error('Error accessing camera:', err);
        alert('Unable to access camera. Please ensure you have granted camera permissions.');
    }
}

// Capture image from video
function captureImage() {
    if (!opencvReady) {
        alert('OpenCV is still loading. Please wait a moment.');
        return;
    }

    showLoading(true);

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0);

    // Get image data
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

    // Process with OpenCV
    setTimeout(() => {
        processDocument(imageData);
    }, 100);
}

// Process document with OpenCV
function processDocument(imageData) {
    try {
        // Convert to OpenCV Mat
        let src = cv.matFromImageData(imageData);
        let original = src.clone();

        // Store original
        originalImage = original;

        // Display original
        displayImage(original, originalCanvas);

        // Detect document edges and apply perspective transform
        let processed = detectAndTransform(src);

        // Store processed image
        processedImage = processed;

        // Display processed
        displayImage(processed, processedCanvas);

        // Switch to processing view
        document.getElementById('cameraSection').style.display = 'none';
        document.getElementById('processingSection').style.display = 'block';

        showLoading(false);

        // Cleanup
        src.delete();
    } catch (err) {
        console.error('Error processing document:', err);
        alert('Error processing document. Please try again.');
        showLoading(false);
    }
}

// Detect document edges and apply perspective transformation
function detectAndTransform(src) {
    let gray = new cv.Mat();
    let blur = new cv.Mat();
    let edges = new cv.Mat();
    let hierarchy = new cv.Mat();
    let contours = new cv.MatVector();

    // Convert to grayscale
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);

    // Apply Gaussian blur
    cv.GaussianBlur(gray, blur, new cv.Size(5, 5), 0);

    // Edge detection
    cv.Canny(blur, edges, 75, 200);

    // Dilate edges to close gaps
    let kernel = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(5, 5));
    cv.dilate(edges, edges, kernel);

    // Find contours
    cv.findContours(edges, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

    // Find the largest contour (assumed to be the document)
    let maxArea = 0;
    let maxContourIndex = -1;

    for (let i = 0; i < contours.size(); i++) {
        let contour = contours.get(i);
        let area = cv.contourArea(contour);

        if (area > maxArea) {
            maxArea = area;
            maxContourIndex = i;
        }
    }

    let result;

    if (maxContourIndex !== -1 && maxArea > src.rows * src.cols * 0.1) {
        // Get the document contour
        let documentContour = contours.get(maxContourIndex);

        // Approximate polygon
        let peri = cv.arcLength(documentContour, true);
        let approx = new cv.Mat();
        cv.approxPolyDP(documentContour, approx, 0.02 * peri, true);

        // If we found a quadrilateral, apply perspective transform
        if (approx.rows === 4) {
            result = fourPointTransform(src, approx);
            approx.delete();
        } else {
            // If no quadrilateral found, use the whole image
            result = src.clone();
            approx.delete();
        }

        documentContour.delete();
    } else {
        // No document found, use whole image
        result = src.clone();
    }

    // Cleanup
    gray.delete();
    blur.delete();
    edges.delete();
    hierarchy.delete();
    contours.delete();
    kernel.delete();

    return result;
}

// Four point perspective transform
function fourPointTransform(image, points) {
    // Extract points
    let pts = [];
    for (let i = 0; i < 4; i++) {
        pts.push({
            x: points.data32S[i * 2],
            y: points.data32S[i * 2 + 1]
        });
    }

    // Order points: top-left, top-right, bottom-right, bottom-left
    pts.sort((a, b) => a.y - b.y);
    let topPoints = pts.slice(0, 2).sort((a, b) => a.x - b.x);
    let bottomPoints = pts.slice(2, 4).sort((a, b) => a.x - b.x);

    let orderedPoints = [
        topPoints[0],    // top-left
        topPoints[1],    // top-right
        bottomPoints[1], // bottom-right
        bottomPoints[0]  // bottom-left
    ];

    // Calculate width and height of new image
    let widthA = Math.hypot(
        orderedPoints[2].x - orderedPoints[3].x,
        orderedPoints[2].y - orderedPoints[3].y
    );
    let widthB = Math.hypot(
        orderedPoints[1].x - orderedPoints[0].x,
        orderedPoints[1].y - orderedPoints[0].y
    );
    let maxWidth = Math.max(widthA, widthB);

    let heightA = Math.hypot(
        orderedPoints[1].x - orderedPoints[2].x,
        orderedPoints[1].y - orderedPoints[2].y
    );
    let heightB = Math.hypot(
        orderedPoints[0].x - orderedPoints[3].x,
        orderedPoints[0].y - orderedPoints[3].y
    );
    let maxHeight = Math.max(heightA, heightB);

    // Standard A4 aspect ratio
    const A4_RATIO = 1.414;
    if (maxWidth / maxHeight > A4_RATIO) {
        maxHeight = maxWidth / A4_RATIO;
    } else {
        maxWidth = maxHeight * A4_RATIO;
    }

    // Source points
    let srcPoints = cv.matFromArray(4, 1, cv.CV_32FC2, [
        orderedPoints[0].x, orderedPoints[0].y,
        orderedPoints[1].x, orderedPoints[1].y,
        orderedPoints[2].x, orderedPoints[2].y,
        orderedPoints[3].x, orderedPoints[3].y
    ]);

    // Destination points
    let dstPoints = cv.matFromArray(4, 1, cv.CV_32FC2, [
        0, 0,
        maxWidth, 0,
        maxWidth, maxHeight,
        0, maxHeight
    ]);

    // Get perspective transform matrix
    let M = cv.getPerspectiveTransform(srcPoints, dstPoints);

    // Apply perspective transform
    let result = new cv.Mat();
    cv.warpPerspective(image, result, M, new cv.Size(maxWidth, maxHeight));

    // Cleanup
    srcPoints.delete();
    dstPoints.delete();
    M.delete();

    return result;
}

// Auto enhance image (lighting and contrast correction)
function autoEnhance() {
    if (!processedImage) return;

    showLoading(true);

    setTimeout(() => {
        try {
            let enhanced = processedImage.clone();

            // Convert to LAB color space for better processing
            let lab = new cv.Mat();
            cv.cvtColor(enhanced, lab, cv.COLOR_RGBA2RGB);
            cv.cvtColor(lab, lab, cv.COLOR_RGB2Lab);

            // Split channels
            let channels = new cv.MatVector();
            cv.split(lab, channels);

            // Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
            let clahe = new cv.CLAHE(2.0, new cv.Size(8, 8));
            let lChannel = channels.get(0);
            clahe.apply(lChannel, lChannel);

            // Merge channels
            cv.merge(channels, lab);

            // Convert back to RGB
            cv.cvtColor(lab, enhanced, cv.COLOR_Lab2RGB);
            cv.cvtColor(enhanced, enhanced, cv.COLOR_RGB2RGBA);

            // Update processed image
            processedImage.delete();
            processedImage = enhanced;

            // Display
            displayImage(processedImage, processedCanvas);

            // Cleanup
            lab.delete();
            channels.delete();

            showLoading(false);
        } catch (err) {
            console.error('Error enhancing image:', err);
            showLoading(false);
        }
    }, 100);
}

// Update enhancement with manual controls
function updateEnhancement() {
    if (!processedImage) return;

    let brightness = parseInt(document.getElementById('brightnessSlider').value);
    let contrast = parseFloat(document.getElementById('contrastSlider').value);
    let bwMode = document.getElementById('bwMode').checked;

    document.getElementById('brightnessValue').textContent = brightness;
    document.getElementById('contrastValue').textContent = contrast.toFixed(1);

    try {
        let enhanced = processedImage.clone();

        // Apply brightness and contrast
        enhanced.convertTo(enhanced, -1, contrast, brightness);

        // Apply black and white if enabled
        if (bwMode) {
            let gray = new cv.Mat();
            cv.cvtColor(enhanced, gray, cv.COLOR_RGBA2GRAY);
            cv.threshold(gray, gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU);
            cv.cvtColor(gray, enhanced, cv.COLOR_GRAY2RGBA);
            gray.delete();
        }

        // Display
        displayImage(enhanced, processedCanvas);

        // Cleanup
        enhanced.delete();
    } catch (err) {
        console.error('Error updating enhancement:', err);
    }
}

// Display OpenCV Mat on canvas
function displayImage(mat, canvasElement) {
    let dst = new cv.Mat();
    let dsize = new cv.Size(0, 0);

    // Resize if too large
    if (mat.cols > 800) {
        let scale = 800 / mat.cols;
        dsize = new cv.Size(mat.cols * scale, mat.rows * scale);
        cv.resize(mat, dst, dsize, 0, 0, cv.INTER_AREA);
    } else {
        dst = mat.clone();
    }

    canvasElement.width = dst.cols;
    canvasElement.height = dst.rows;
    cv.imshow(canvasElement, dst);

    dst.delete();
}

// Download processed image
function downloadImage() {
    if (!processedImage) return;

    // Create temporary canvas for full resolution
    let tempCanvas = document.createElement('canvas');
    tempCanvas.width = processedImage.cols;
    tempCanvas.height = processedImage.rows;

    // Apply current enhancements
    let brightness = parseInt(document.getElementById('brightnessSlider').value);
    let contrast = parseFloat(document.getElementById('contrastSlider').value);
    let bwMode = document.getElementById('bwMode').checked;

    let finalImage = processedImage.clone();
    finalImage.convertTo(finalImage, -1, contrast, brightness);

    if (bwMode) {
        let gray = new cv.Mat();
        cv.cvtColor(finalImage, gray, cv.COLOR_RGBA2GRAY);
        cv.threshold(gray, gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU);
        cv.cvtColor(gray, finalImage, cv.COLOR_GRAY2RGBA);
        gray.delete();
    }

    cv.imshow(tempCanvas, finalImage);

    // Download
    tempCanvas.toBlob(blob => {
        let url = URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = `scanned-document-${Date.now()}.png`;
        a.click();
        URL.revokeObjectURL(url);
    });

    finalImage.delete();
}

// Retake photo
function retake() {
    // Clean up images
    if (originalImage) {
        originalImage.delete();
        originalImage = null;
    }
    if (processedImage) {
        processedImage.delete();
        processedImage = null;
    }

    // Reset controls
    document.getElementById('brightnessSlider').value = 0;
    document.getElementById('contrastSlider').value = 1;
    document.getElementById('bwMode').checked = false;
    document.getElementById('brightnessValue').textContent = '0';
    document.getElementById('contrastValue').textContent = '1';

    // Switch back to camera view
    document.getElementById('processingSection').style.display = 'none';
    document.getElementById('cameraSection').style.display = 'block';
}

// Show/hide loading indicator
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    if (originalImage) originalImage.delete();
    if (processedImage) processedImage.delete();
});
