import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image/image.dart' as img;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../utils/image_processor.dart';

class PreviewScreen extends StatefulWidget {
  final String imagePath;

  const PreviewScreen({super.key, required this.imagePath});

  @override
  State<PreviewScreen> createState() => _PreviewScreenState();
}

class _PreviewScreenState extends State<PreviewScreen> {
  img.Image? _originalImage;
  img.Image? _processedImage;
  bool _isProcessing = false;
  bool _isEnhanced = false;

  // Enhancement controls
  double _brightness = 0;
  double _contrast = 1.0;
  bool _blackAndWhite = false;

  @override
  void initState() {
    super.initState();
    _loadAndProcessImage();
  }

  Future<void> _loadAndProcessImage() async {
    setState(() => _isProcessing = true);

    try {
      // Load original image
      final bytes = await File(widget.imagePath).readAsBytes();
      final decoded = img.decodeImage(bytes);

      if (decoded != null) {
        setState(() {
          _originalImage = decoded;
          _processedImage = img.Image.from(decoded);
        });

        // Auto-process the image
        await _autoProcess();
      }
    } catch (e) {
      print('Error loading image: $e');
      _showError('Error loading image');
    }

    setState(() => _isProcessing = false);
  }

  Future<void> _autoProcess() async {
    if (_originalImage == null) return;

    setState(() => _isProcessing = true);

    try {
      // Detect document edges
      final corners = await ImageProcessor.detectDocumentEdges(widget.imagePath);

      if (corners != null && corners.length == 4) {
        // Apply perspective transform
        final transformed = await ImageProcessor.applyPerspectiveTransform(
          widget.imagePath,
          corners,
        );

        if (transformed != null) {
          setState(() {
            _processedImage = transformed;
          });
        }
      }
    } catch (e) {
      print('Error processing image: $e');
    }

    setState(() => _isProcessing = false);
  }

  Future<void> _applyEnhancements() async {
    if (_processedImage == null) return;

    setState(() => _isProcessing = true);

    try {
      final enhanced = ImageProcessor.enhanceImage(
        _processedImage!,
        brightness: _brightness.toInt(),
        contrast: _contrast,
        blackAndWhite: _blackAndWhite,
      );

      setState(() {
        _processedImage = enhanced;
        _isEnhanced = true;
      });
    } catch (e) {
      print('Error enhancing image: $e');
      _showError('Error enhancing image');
    }

    setState(() => _isProcessing = false);
  }

  Future<void> _saveImage() async {
    if (_processedImage == null) return;

    setState(() => _isProcessing = true);

    try {
      // Get directory
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final filePath = '${directory.path}/scanned_doc_$timestamp.jpg';

      // Encode and save
      final encoded = img.encodeJpg(_processedImage!, quality: 95);
      await File(filePath).writeAsBytes(encoded);

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Saved to $filePath'),
          action: SnackBarAction(
            label: 'Share',
            onPressed: () => _shareImage(filePath),
          ),
        ),
      );

      Navigator.pop(context);
    } catch (e) {
      print('Error saving image: $e');
      _showError('Error saving image');
    }

    setState(() => _isProcessing = false);
  }

  Future<void> _shareImage(String path) async {
    try {
      await Share.shareXFiles(
        [XFile(path)],
        text: 'Scanned document',
      );
    } catch (e) {
      print('Error sharing: $e');
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Preview & Edit'),
        actions: [
          IconButton(
            onPressed: _isProcessing ? null : _saveImage,
            icon: const Icon(Icons.check),
            tooltip: 'Save',
          ),
        ],
      ),
      body: _isProcessing
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Processing document...'),
                ],
              ),
            )
          : SingleChildScrollView(
              child: Column(
                children: [
                  // Image preview
                  if (_processedImage != null)
                    Container(
                      width: double.infinity,
                      height: MediaQuery.of(context).size.height * 0.5,
                      color: Colors.grey[200],
                      child: InteractiveViewer(
                        child: Image.memory(
                          img.encodeJpg(_processedImage!),
                          fit: BoxFit.contain,
                        ),
                      ),
                    ),

                  // Controls
                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Auto-enhance button
                        ElevatedButton.icon(
                          onPressed: _applyEnhancements,
                          icon: const Icon(Icons.auto_fix_high),
                          label: const Text('Auto-Enhance'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.all(16),
                          ),
                        ),

                        const SizedBox(height: 24),

                        // Manual controls
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Manual Adjustments',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 16),

                                // Brightness
                                Text('Brightness: ${_brightness.toInt()}'),
                                Slider(
                                  value: _brightness,
                                  min: -50,
                                  max: 50,
                                  divisions: 100,
                                  onChanged: (value) {
                                    setState(() => _brightness = value);
                                  },
                                  onChangeEnd: (value) => _applyEnhancements(),
                                ),

                                const SizedBox(height: 8),

                                // Contrast
                                Text('Contrast: ${_contrast.toStringAsFixed(1)}'),
                                Slider(
                                  value: _contrast,
                                  min: 0.5,
                                  max: 2.0,
                                  divisions: 15,
                                  onChanged: (value) {
                                    setState(() => _contrast = value);
                                  },
                                  onChangeEnd: (value) => _applyEnhancements(),
                                ),

                                const SizedBox(height: 8),

                                // Black and white toggle
                                SwitchListTile(
                                  title: const Text('Black & White'),
                                  value: _blackAndWhite,
                                  onChanged: (value) {
                                    setState(() => _blackAndWhite = value);
                                    _applyEnhancements();
                                  },
                                ),
                              ],
                            ),
                          ),
                        ),

                        const SizedBox(height: 16),

                        // Action buttons
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: () => Navigator.pop(context),
                                icon: const Icon(Icons.refresh),
                                label: const Text('Retake'),
                                style: OutlinedButton.styleFrom(
                                  padding: const EdgeInsets.all(16),
                                ),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: _isProcessing ? null : _saveImage,
                                icon: const Icon(Icons.save),
                                label: const Text('Save'),
                                style: ElevatedButton.styleFrom(
                                  padding: const EdgeInsets.all(16),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
