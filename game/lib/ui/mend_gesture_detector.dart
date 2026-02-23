import 'package:flame/components.dart';
import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Detects zig-zag gestures for the Mend mechanic
/// Player traces a zig-zag pattern to "stitch" torn objects back together
class MendGestureDetector {
  final List<Vector2> _gesturePoints = [];
  final double _minZigZagAmplitude = 30.0; // Minimum horizontal displacement
  final double _minZigZagCount = 3; // Minimum zig-zags needed
  final double _tolerance = 15.0; // Tolerance for direction changes

  bool _isTracking = false;
  int _zigZagCount = 0;
  int _lastDirection = 0; // -1 left, 1 right

  // Callback when mend is complete
  Function(double completionPercent)? onMendProgress;
  Function()? onMendComplete;

  /// Start tracking a new gesture
  void startTracking(Vector2 position) {
    _gesturePoints.clear();
    _gesturePoints.add(position);
    _isTracking = true;
    _zigZagCount = 0;
    _lastDirection = 0;
  }

  /// Add a point to the gesture
  void addPoint(Vector2 position) {
    if (!_isTracking) return;

    _gesturePoints.add(position);
    _analyzeGesture();
  }

  /// End gesture tracking
  void endTracking() {
    _isTracking = false;

    if (_zigZagCount >= _minZigZagCount) {
      onMendComplete?.call();
    }
  }

  /// Analyze the gesture for zig-zag pattern
  void _analyzeGesture() {
    if (_gesturePoints.length < 3) return;

    // Look at recent points to detect direction changes
    final recent = _gesturePoints.length > 10
        ? _gesturePoints.sublist(_gesturePoints.length - 10)
        : _gesturePoints;

    // Calculate horizontal movement
    double minX = recent.first.x;
    double maxX = recent.first.x;

    for (final point in recent) {
      minX = math.min(minX, point.x);
      maxX = math.max(maxX, point.x);
    }

    final amplitude = maxX - minX;

    // Check for direction change
    if (recent.length >= 2) {
      final prev = recent[recent.length - 2];
      final curr = recent.last;
      final dx = curr.x - prev.x;

      if (dx.abs() > _tolerance) {
        final currentDirection = dx > 0 ? 1 : -1;

        if (_lastDirection != 0 && currentDirection != _lastDirection) {
          // Direction changed - count as zig-zag
          if (amplitude >= _minZigZagAmplitude) {
            _zigZagCount++;
            onMendProgress?.call(_zigZagCount / _minZigZagCount);
          }
        }

        _lastDirection = currentDirection;
      }
    }
  }

  /// Get current zig-zag progress (0-1)
  double get progress => (_zigZagCount / _minZigZagCount).clamp(0.0, 1.0);

  /// Check if currently tracking
  bool get isTracking => _isTracking;

  /// Reset the detector
  void reset() {
    _gesturePoints.clear();
    _isTracking = false;
    _zigZagCount = 0;
    _lastDirection = 0;
  }
}

/// Visual component showing mend progress
class MendProgressIndicator extends PositionComponent {
  double progress = 0;
  final Vector2 targetPosition;
  final double targetWidth;

  MendProgressIndicator({
    required this.targetPosition,
    this.targetWidth = 100,
  }) : super(
          position: targetPosition,
          size: Vector2(targetWidth, 20),
        );

  @override
  void render(Canvas canvas) {
    super.render(canvas);

    // Background
    final bgPaint = Paint()..color = Colors.grey.withOpacity(0.5);
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(0, 0, size.x, size.y),
        const Radius.circular(10),
      ),
      bgPaint,
    );

    // Progress fill
    final progressPaint = Paint()..color = const Color(0xFF722F37);
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(0, 0, size.x * progress, size.y),
        const Radius.circular(10),
      ),
      progressPaint,
    );

    // Stitch pattern on progress
    if (progress > 0) {
      final stitchPaint = Paint()
        ..color = Colors.white.withOpacity(0.5)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2;

      final stitchPath = Path();
      final stitchCount = (progress * 5).floor();

      for (int i = 0; i < stitchCount; i++) {
        final x = (i + 0.5) * (size.x * progress / stitchCount);
        stitchPath.moveTo(x - 5, 5);
        stitchPath.lineTo(x + 5, 15);
        stitchPath.moveTo(x + 5, 5);
        stitchPath.lineTo(x - 5, 15);
      }

      canvas.drawPath(stitchPath, stitchPaint);
    }
  }

  void updateProgress(double newProgress) {
    progress = newProgress.clamp(0.0, 1.0);
  }
}

/// Torn object that can be mended
class TornObject extends PositionComponent {
  bool isMended = false;
  double mendProgress = 0;
  final String id;

  // Visual properties
  final Color tearColor;
  final double tearWidth;

  TornObject({
    required Vector2 position,
    required this.id,
    this.tearColor = Colors.red,
    this.tearWidth = 100,
  }) : super(
          position: position,
          size: Vector2(tearWidth, 40),
          anchor: Anchor.center,
        );

  @override
  void render(Canvas canvas) {
    super.render(canvas);

    if (isMended) {
      // Show mended seam
      _drawMendedSeam(canvas);
    } else {
      // Show tear
      _drawTear(canvas);
    }
  }

  void _drawTear(Canvas canvas) {
    final tearPaint = Paint()
      ..color = tearColor.withOpacity(0.8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4;

    // Jagged tear line
    final tearPath = Path();
    tearPath.moveTo(0, size.y / 2);

    final segments = 8;
    final segmentWidth = size.x / segments;

    for (int i = 0; i < segments; i++) {
      final x = (i + 1) * segmentWidth;
      final yOffset = (i % 2 == 0) ? -10.0 : 10.0;
      tearPath.lineTo(x, size.y / 2 + yOffset);
    }

    canvas.drawPath(tearPath, tearPaint);

    // Glow effect
    final glowPaint = Paint()
      ..color = tearColor.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 10
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 5);
    canvas.drawPath(tearPath, glowPaint);
  }

  void _drawMendedSeam(Canvas canvas) {
    final seamPaint = Paint()
      ..color = const Color(0xFF722F37)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;

    // Cross-stitch pattern
    final stitchCount = 6;
    final stitchWidth = size.x / stitchCount;

    for (int i = 0; i < stitchCount; i++) {
      final x = i * stitchWidth + stitchWidth / 2;

      // X stitch
      canvas.drawLine(
        Offset(x - 8, size.y / 2 - 8),
        Offset(x + 8, size.y / 2 + 8),
        seamPaint,
      );
      canvas.drawLine(
        Offset(x + 8, size.y / 2 - 8),
        Offset(x - 8, size.y / 2 + 8),
        seamPaint,
      );
    }
  }

  void updateMendProgress(double progress) {
    mendProgress = progress;
    if (progress >= 1.0) {
      isMended = true;
    }
  }
}
