import 'dart:math' as math;
import 'package:flame/components.dart';
import 'package:flutter/material.dart';

/// A point in the Verlet rope simulation
class RopePoint {
  Vector2 position;
  Vector2 oldPosition;
  bool isLocked;
  double mass;

  RopePoint({
    required this.position,
    Vector2? oldPosition,
    this.isLocked = false,
    this.mass = 1.0,
  }) : oldPosition = oldPosition ?? position.clone();

  /// Get velocity from position difference
  Vector2 get velocity => position - oldPosition;
}

/// Verlet Integration rope physics system
/// Creates heavy, floppy yarn-like behavior (not bouncy like springs)
class VerletRope extends Component {
  final List<RopePoint> points = [];
  final double segmentLength;
  final Color ropeColor;
  final double maxLength;
  final double ropeWidth;

  // Physics parameters
  static const double gravity = 980.0;
  static const double damping = 0.99; // Slight damping for heavy feel
  static const int constraintIterations = 10; // More = stiffer rope

  // State
  bool _isConducting = false;
  bool _isAttached = false;
  double _conductPulse = 0;

  // Tension tracking (for visual feedback)
  double _currentTension = 0;
  static const double maxTension = 0.9; // Snap threshold

  VerletRope({
    required Vector2 startPoint,
    required Vector2 endPoint,
    int segmentCount = 20,
    this.ropeColor = const Color(0xFF722F37),
    this.maxLength = 300,
    this.ropeWidth = 8,
  }) : segmentLength = startPoint.distanceTo(endPoint) / segmentCount {
    _initializePoints(startPoint, endPoint, segmentCount);
  }

  void _initializePoints(Vector2 start, Vector2 end, int count) {
    points.clear();

    for (int i = 0; i <= count; i++) {
      final t = i / count;
      final pos = start + (end - start) * t;

      points.add(RopePoint(
        position: pos,
        isLocked: i == 0, // First point attached to Bit
        mass: 1.0 + (i * 0.1), // Heavier towards end (yarn weight)
      ));
    }
  }

  /// Update the rope physics
  @override
  void update(double dt) {
    super.update(dt);

    // Don't simulate too fast
    final clampedDt = dt.clamp(0, 0.033); // Cap at ~30fps physics

    // Apply verlet integration
    _applyVerlet(clampedDt);

    // Apply constraints multiple times for stability
    for (int i = 0; i < constraintIterations; i++) {
      _applyConstraints();
    }

    // Update conducting pulse animation
    if (_isConducting) {
      _conductPulse += dt * 5;
      if (_conductPulse > 2 * math.pi) {
        _conductPulse -= 2 * math.pi;
      }
    }

    // Calculate tension
    _calculateTension();
  }

  /// Verlet integration step
  void _applyVerlet(double dt) {
    for (final point in points) {
      if (point.isLocked) continue;

      final velocity = point.velocity * damping;
      point.oldPosition = point.position.clone();

      // Apply gravity (heavy yarn!)
      velocity.y += gravity * dt * point.mass;

      // Update position
      point.position += velocity;
    }
  }

  /// Apply distance constraints between points
  void _applyConstraints() {
    for (int i = 0; i < points.length - 1; i++) {
      final p1 = points[i];
      final p2 = points[i + 1];

      final delta = p2.position - p1.position;
      final distance = delta.length;
      if (distance == 0) continue;

      final diff = (segmentLength - distance) / distance;
      final offset = delta * diff * 0.5;

      // Move points towards each other
      if (!p1.isLocked) {
        p1.position -= offset;
      }
      if (!p2.isLocked) {
        p2.position += offset;
      }
    }

    // Max length constraint
    _applyMaxLengthConstraint();
  }

  void _applyMaxLengthConstraint() {
    if (points.length < 2) return;

    final totalLength = _calculateTotalLength();
    if (totalLength > maxLength) {
      // Scale down rope to max length
      final scale = maxLength / totalLength;
      final start = points.first.position;

      for (int i = 1; i < points.length; i++) {
        if (points[i].isLocked) continue;

        final offset = points[i].position - start;
        points[i].position = start + offset * scale;
      }
    }
  }

  double _calculateTotalLength() {
    double total = 0;
    for (int i = 0; i < points.length - 1; i++) {
      total += points[i].position.distanceTo(points[i + 1].position);
    }
    return total;
  }

  void _calculateTension() {
    final currentLength = _calculateTotalLength();
    _currentTension = (currentLength / maxLength).clamp(0, 1);
  }

  /// Get the end point of the rope
  Vector2 get endPoint => points.isNotEmpty ? points.last.position : Vector2.zero();

  /// Get start point (attached to Bit)
  Vector2 get startPoint => points.isNotEmpty ? points.first.position : Vector2.zero();

  /// Update the start point (follows Bit's arm)
  void updateStart(Vector2 newStart) {
    if (points.isNotEmpty) {
      points.first.position = newStart;
      points.first.oldPosition = newStart;
    }
  }

  /// Update target while dragging
  void updateTarget(Vector2 target) {
    if (points.isNotEmpty && !_isAttached) {
      points.last.position = target;
      points.last.oldPosition = target;
    }
  }

  /// Attach the rope end to a fixed point
  void attachTo(Vector2 point) {
    if (points.isNotEmpty) {
      points.last.position = point;
      points.last.isLocked = true;
      _isAttached = true;
    }
  }

  /// Detach the rope end
  void detach() {
    if (points.isNotEmpty) {
      points.last.isLocked = false;
      _isAttached = false;
    }
  }

  /// Set conducting state (yarn glows when conducting electricity)
  void setConducting(bool conducting) {
    _isConducting = conducting;
  }

  /// Check if rope is under too much tension (will snap)
  bool get isOverTensioned => _currentTension > maxTension;

  /// Get current tension (0-1)
  double get tension => _currentTension;

  @override
  void render(Canvas canvas) {
    super.render(canvas);

    if (points.length < 2) return;

    // Determine rope color based on state
    Color currentColor = ropeColor;
    if (isOverTensioned) {
      // Red warning when about to snap
      currentColor = Color.lerp(ropeColor, Colors.red, (_currentTension - maxTension) / (1 - maxTension))!;
    }

    // Draw the rope
    _drawRope(canvas, currentColor);

    // Draw conducting glow if powered
    if (_isConducting) {
      _drawConductingEffect(canvas);
    }

    // Draw knit texture
    _drawKnitTexture(canvas);
  }

  void _drawRope(Canvas canvas, Color color) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = ropeWidth
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final path = Path();
    path.moveTo(points.first.position.x, points.first.position.y);

    // Use quadratic bezier for smooth curves
    for (int i = 1; i < points.length - 1; i++) {
      final p0 = points[i - 1].position;
      final p1 = points[i].position;
      final p2 = points[i + 1].position;

      final midX = (p1.x + p2.x) / 2;
      final midY = (p1.y + p2.y) / 2;

      path.quadraticBezierTo(p1.x, p1.y, midX, midY);
    }

    // Final segment
    final last = points.last.position;
    path.lineTo(last.x, last.y);

    canvas.drawPath(path, paint);

    // Draw outline for depth
    final outlinePaint = Paint()
      ..color = color.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = ropeWidth + 4
      ..strokeCap = StrokeCap.round;
    canvas.drawPath(path, outlinePaint);
  }

  void _drawConductingEffect(Canvas canvas) {
    // Pulsing glow effect when conducting electricity
    final glowIntensity = (math.sin(_conductPulse) + 1) / 2;

    final glowPaint = Paint()
      ..color = Colors.yellow.withOpacity(0.3 + glowIntensity * 0.4)
      ..style = PaintingStyle.stroke
      ..strokeWidth = ropeWidth + 8
      ..strokeCap = StrokeCap.round
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 8);

    final path = Path();
    path.moveTo(points.first.position.x, points.first.position.y);

    for (int i = 1; i < points.length; i++) {
      path.lineTo(points[i].position.x, points[i].position.y);
    }

    canvas.drawPath(path, glowPaint);

    // Draw bright core
    final corePaint = Paint()
      ..color = Colors.white.withOpacity(0.5 + glowIntensity * 0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    canvas.drawPath(path, corePaint);
  }

  void _drawKnitTexture(Canvas canvas) {
    // Draw thread-like details for knit texture
    final threadPaint = Paint()
      ..color = ropeColor.withOpacity(0.6)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    // Draw "threads" perpendicular to rope
    for (int i = 0; i < points.length - 1; i += 2) {
      final p1 = points[i].position;
      final p2 = points[i + 1].position;

      final direction = (p2 - p1).normalized();
      final perpendicular = Vector2(-direction.y, direction.x);

      final mid = (p1 + p2) / 2;
      final threadStart = mid + perpendicular * (ropeWidth / 2);
      final threadEnd = mid - perpendicular * (ropeWidth / 2);

      canvas.drawLine(
        Offset(threadStart.x, threadStart.y),
        Offset(threadEnd.x, threadEnd.y),
        threadPaint,
      );
    }
  }

  /// Apply an impulse to the rope (for swinging)
  void applyImpulse(Vector2 impulse, {int? pointIndex}) {
    final index = pointIndex ?? points.length ~/ 2;
    if (index >= 0 && index < points.length && !points[index].isLocked) {
      points[index].position += impulse;
    }
  }

  /// Get the position of a point along the rope (0-1)
  Vector2 getPositionAt(double t) {
    if (points.isEmpty) return Vector2.zero();

    final index = (t * (points.length - 1)).floor();
    final localT = (t * (points.length - 1)) - index;

    if (index >= points.length - 1) {
      return points.last.position;
    }

    return points[index].position + (points[index + 1].position - points[index].position) * localT;
  }
}
