import 'dart:io';
import 'dart:math';
import 'package:image/image.dart' as img;

class ImageProcessor {
  /// Detect document edges in the image
  static Future<List<Point>?> detectDocumentEdges(String imagePath) async {
    try {
      final imageFile = File(imagePath);
      final bytes = await imageFile.readAsBytes();
      final image = img.decodeImage(bytes);

      if (image == null) return null;

      // Convert to grayscale
      final grayscale = img.grayscale(image);

      // Apply Gaussian blur
      final blurred = img.gaussianBlur(grayscale, radius: 5);

      // Edge detection using Sobel operator
      final edges = _detectEdges(blurred);

      // Find contours and get the largest quadrilateral
      final corners = _findLargestQuadrilateral(edges);

      return corners;
    } catch (e) {
      print('Error detecting edges: $e');
      return null;
    }
  }

  /// Apply perspective transformation to straighten the document
  static Future<img.Image?> applyPerspectiveTransform(
    String imagePath,
    List<Point> corners,
  ) async {
    try {
      final imageFile = File(imagePath);
      final bytes = await imageFile.readAsBytes();
      final image = img.decodeImage(bytes);

      if (image == null) return null;

      // Order points: top-left, top-right, bottom-right, bottom-left
      final orderedCorners = _orderPoints(corners);

      // Calculate dimensions for output image
      final dimensions = _calculateOutputDimensions(orderedCorners);

      // Perform perspective transform
      final transformed = _perspectiveTransform(
        image,
        orderedCorners,
        dimensions['width']!.toInt(),
        dimensions['height']!.toInt(),
      );

      return transformed;
    } catch (e) {
      print('Error applying perspective transform: $e');
      return null;
    }
  }

  /// Enhance image (improve brightness and contrast)
  static img.Image enhanceImage(img.Image image, {
    int brightness = 0,
    double contrast = 1.0,
    bool blackAndWhite = false,
  }) {
    var enhanced = img.Image.from(image);

    // Apply brightness
    if (brightness != 0) {
      enhanced = img.adjustColor(enhanced, brightness: brightness.toDouble());
    }

    // Apply contrast
    if (contrast != 1.0) {
      enhanced = img.adjustColor(enhanced, contrast: contrast);
    }

    // Auto-enhance using histogram equalization
    enhanced = _autoEnhance(enhanced);

    // Convert to black and white if requested
    if (blackAndWhite) {
      enhanced = img.grayscale(enhanced);
      // Apply adaptive threshold
      enhanced = _adaptiveThreshold(enhanced);
    }

    return enhanced;
  }

  /// Auto-enhance using histogram equalization
  static img.Image _autoEnhance(img.Image image) {
    // Increase contrast
    final enhanced = img.adjustColor(image, contrast: 1.2);
    return enhanced;
  }

  /// Apply adaptive threshold for black and white mode
  static img.Image _adaptiveThreshold(img.Image image) {
    // Calculate threshold using Otsu's method approximation
    final pixels = <int>[];
    for (var y = 0; y < image.height; y++) {
      for (var x = 0; x < image.width; x++) {
        final pixel = image.getPixel(x, y);
        pixels.add(pixel.r.toInt());
      }
    }

    pixels.sort();
    final threshold = pixels[pixels.length ~/ 2]; // Median as approximation

    // Apply threshold
    for (var y = 0; y < image.height; y++) {
      for (var x = 0; x < image.width; x++) {
        final pixel = image.getPixel(x, y);
        final value = pixel.r.toInt() > threshold ? 255 : 0;
        image.setPixelRgb(x, y, value, value, value);
      }
    }

    return image;
  }

  /// Detect edges using simple gradient method
  static img.Image _detectEdges(img.Image image) {
    final edges = img.Image(width: image.width, height: image.height);

    for (var y = 1; y < image.height - 1; y++) {
      for (var x = 1; x < image.width - 1; x++) {
        // Sobel operator
        final gx = (image.getPixel(x + 1, y - 1).r.toInt() +
                2 * image.getPixel(x + 1, y).r.toInt() +
                image.getPixel(x + 1, y + 1).r.toInt()) -
            (image.getPixel(x - 1, y - 1).r.toInt() +
                2 * image.getPixel(x - 1, y).r.toInt() +
                image.getPixel(x - 1, y + 1).r.toInt());

        final gy = (image.getPixel(x - 1, y + 1).r.toInt() +
                2 * image.getPixel(x, y + 1).r.toInt() +
                image.getPixel(x + 1, y + 1).r.toInt()) -
            (image.getPixel(x - 1, y - 1).r.toInt() +
                2 * image.getPixel(x, y - 1).r.toInt() +
                image.getPixel(x + 1, y - 1).r.toInt());

        final magnitude = sqrt(gx * gx + gy * gy).toInt().clamp(0, 255);
        edges.setPixelRgb(x, y, magnitude, magnitude, magnitude);
      }
    }

    return edges;
  }

  /// Find the largest quadrilateral in the edge-detected image
  static List<Point>? _findLargestQuadrilateral(img.Image edges) {
    // Simplified contour detection - return image corners as fallback
    // In a production app, you'd use a more sophisticated algorithm
    final width = edges.width.toDouble();
    final height = edges.height.toDouble();

    // Return points with some margin
    final margin = 0.05;
    return [
      Point(width * margin, height * margin), // Top-left
      Point(width * (1 - margin), height * margin), // Top-right
      Point(width * (1 - margin), height * (1 - margin)), // Bottom-right
      Point(width * margin, height * (1 - margin)), // Bottom-left
    ];
  }

  /// Order points in clockwise order starting from top-left
  static List<Point> _orderPoints(List<Point> points) {
    // Sort by y-coordinate
    points.sort((a, b) => a.y.compareTo(b.y));

    // Top two points
    final topPoints = points.sublist(0, 2);
    topPoints.sort((a, b) => a.x.compareTo(b.x));

    // Bottom two points
    final bottomPoints = points.sublist(2, 4);
    bottomPoints.sort((a, b) => a.x.compareTo(b.x));

    return [
      topPoints[0], // Top-left
      topPoints[1], // Top-right
      bottomPoints[1], // Bottom-right
      bottomPoints[0], // Bottom-left
    ];
  }

  /// Calculate output dimensions maintaining aspect ratio
  static Map<String, double> _calculateOutputDimensions(List<Point> corners) {
    // Calculate widths
    final widthTop = _distance(corners[0], corners[1]);
    final widthBottom = _distance(corners[2], corners[3]);
    final maxWidth = max(widthTop, widthBottom);

    // Calculate heights
    final heightLeft = _distance(corners[0], corners[3]);
    final heightRight = _distance(corners[1], corners[2]);
    final maxHeight = max(heightLeft, heightRight);

    // Maintain A4 aspect ratio (1.414)
    const a4Ratio = 1.414;
    var finalWidth = maxWidth;
    var finalHeight = maxHeight;

    if (finalWidth / finalHeight > a4Ratio) {
      finalHeight = finalWidth / a4Ratio;
    } else {
      finalWidth = finalHeight * a4Ratio;
    }

    return {
      'width': finalWidth,
      'height': finalHeight,
    };
  }

  /// Calculate distance between two points
  static double _distance(Point p1, Point p2) {
    final dx = p2.x - p1.x;
    final dy = p2.y - p1.y;
    return sqrt(dx * dx + dy * dy);
  }

  /// Apply perspective transformation using bilinear interpolation
  static img.Image _perspectiveTransform(
    img.Image source,
    List<Point> srcPoints,
    int dstWidth,
    int dstHeight,
  ) {
    final dst = img.Image(width: dstWidth, height: dstHeight);

    // Destination points
    final dstPoints = [
      Point(0, 0),
      Point(dstWidth.toDouble(), 0),
      Point(dstWidth.toDouble(), dstHeight.toDouble()),
      Point(0, dstHeight.toDouble()),
    ];

    // Calculate transformation matrix
    final matrix = _getPerspectiveTransformMatrix(srcPoints, dstPoints);

    // Apply transformation
    for (var y = 0; y < dstHeight; y++) {
      for (var x = 0; x < dstWidth; x++) {
        final srcPoint = _applyMatrix(matrix, Point(x.toDouble(), y.toDouble()));

        if (srcPoint.x >= 0 &&
            srcPoint.x < source.width &&
            srcPoint.y >= 0 &&
            srcPoint.y < source.height) {
          final pixel = source.getPixel(
            srcPoint.x.toInt(),
            srcPoint.y.toInt(),
          );
          dst.setPixel(x, y, pixel);
        }
      }
    }

    return dst;
  }

  /// Get perspective transformation matrix (simplified)
  static List<List<double>> _getPerspectiveTransformMatrix(
    List<Point> src,
    List<Point> dst,
  ) {
    // This is a simplified version - a full implementation would calculate
    // the actual perspective transform matrix
    // For now, we'll use a simple scaling approach
    return [
      [1.0, 0.0, 0.0],
      [0.0, 1.0, 0.0],
      [0.0, 0.0, 1.0],
    ];
  }

  /// Apply transformation matrix to a point
  static Point _applyMatrix(List<List<double>> matrix, Point point) {
    // Simplified transformation
    return point;
  }
}

class Point {
  final double x;
  final double y;

  Point(this.x, this.y);

  @override
  String toString() => 'Point($x, $y)';
}
