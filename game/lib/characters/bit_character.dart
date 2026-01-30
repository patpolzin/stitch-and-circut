import 'dart:math' as math;
import 'package:flame/collisions.dart';
import 'package:flame/components.dart';
import 'package:flutter/material.dart';

/// Bit's facial expressions displayed on his CRT screen
enum BitExpression {
  idle, // Blinking smiley
  happy, // Big grin
  thinking, // Thinking dots
  scared, // Wide eyes
  effort, // Straining
  starEyes, // Success!
  confused, // Spinning loading icon (hint needed)
  lowBattery, // Droopy eyes
  startled, // Surprised
  relieved, // Phew!
}

/// The main character - Bit
/// A heavy robot with a CRT monitor head and burgundy knit wiring
class BitCharacter extends PositionComponent with HasGameRef, CollisionCallbacks {
  BitCharacter({
    required Vector2 position,
  }) : super(
          position: position,
          size: Vector2(80, 120),
          anchor: Anchor.bottomCenter,
        );

  // Physics properties (heavy robot!)
  Vector2 velocity = Vector2.zero();
  static const double mass = 100.0;
  static const double maxSpeed = 200.0;
  static const double jumpForce = 400.0;

  // Movement state
  bool isGrounded = false;
  bool isSwinging = false;
  int moveDirection = 0; // -1 left, 0 none, 1 right

  // Expression state
  BitExpression _expression = BitExpression.idle;
  double _blinkTimer = 0;
  bool _isBlinking = false;
  double _expressionTimer = 0;

  // Colors from design doc
  static const Color gunmetalGrey = Color(0xFF2A3439);
  static const Color burgundyYarn = Color(0xFF722F37);
  static const Color neonGreen = Color(0xFF39FF14);
  static const Color screenColor = Color(0xFF0a0a0a);

  @override
  Future<void> onLoad() async {
    await super.onLoad();

    // Add collision shape - capsule approximated by rectangles
    add(RectangleHitbox(
      size: Vector2(60, 100),
      position: Vector2(10, 10),
    ));
  }

  @override
  void update(double dt) {
    super.update(dt);

    // Apply gravity if not grounded
    if (!isGrounded && !isSwinging) {
      velocity.y += 980.0 * dt; // Gravity
    }

    // Apply horizontal movement
    if (moveDirection != 0) {
      velocity.x = moveDirection * 150.0;
    } else if (isGrounded) {
      velocity.x *= 0.8; // Friction
    }

    // Clamp velocity
    velocity.x = velocity.x.clamp(-maxSpeed, maxSpeed);
    velocity.y = velocity.y.clamp(-500, 800);

    // Update position
    position += velocity * dt;

    // Update expression animation
    _updateExpression(dt);
  }

  void _updateExpression(double dt) {
    // Handle blinking for idle expression
    if (_expression == BitExpression.idle) {
      _blinkTimer += dt;
      if (_blinkTimer > 3.0 && !_isBlinking) {
        _isBlinking = true;
        _blinkTimer = 0;
      }
      if (_isBlinking && _blinkTimer > 0.15) {
        _isBlinking = false;
        _blinkTimer = 0;
      }
    }

    // Auto-return to idle after certain expressions
    if (_expression == BitExpression.startled || _expression == BitExpression.relieved) {
      _expressionTimer += dt;
      if (_expressionTimer > 1.5) {
        _expression = BitExpression.idle;
        _expressionTimer = 0;
      }
    }
  }

  @override
  void render(Canvas canvas) {
    super.render(canvas);

    // Draw Bit's body
    _drawBody(canvas);
    _drawHead(canvas);
    _drawFace(canvas);
    _drawArms(canvas);
    _drawLegs(canvas);
  }

  void _drawBody(Canvas canvas) {
    final bodyPaint = Paint()..color = gunmetalGrey;
    final yarnPaint = Paint()
      ..color = burgundyYarn
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4;

    // Torso - heavy industrial plating
    final torsoRect = RRect.fromRectAndRadius(
      Rect.fromLTWH(15, 45, 50, 50),
      const Radius.circular(5),
    );
    canvas.drawRRect(torsoRect, bodyPaint);

    // Yarn detail on torso (knit pattern)
    for (int i = 0; i < 3; i++) {
      canvas.drawLine(
        Offset(20, 55 + i * 15.0),
        Offset(60, 55 + i * 15.0),
        yarnPaint..strokeWidth = 2,
      );
    }
  }

  void _drawHead(Canvas canvas) {
    final headPaint = Paint()..color = gunmetalGrey;
    final screenPaint = Paint()..color = screenColor;

    // CRT Monitor head
    final headRect = RRect.fromRectAndRadius(
      Rect.fromLTWH(10, 0, 60, 50),
      const Radius.circular(8),
    );
    canvas.drawRRect(headRect, headPaint);

    // Screen area
    final screenRect = RRect.fromRectAndRadius(
      Rect.fromLTWH(15, 5, 50, 40),
      const Radius.circular(4),
    );
    canvas.drawRRect(screenRect, screenPaint);
  }

  void _drawFace(Canvas canvas) {
    final facePaint = Paint()..color = neonGreen;

    // Draw based on current expression
    switch (_expression) {
      case BitExpression.idle:
        _drawIdleFace(canvas, facePaint);
        break;
      case BitExpression.happy:
        _drawHappyFace(canvas, facePaint);
        break;
      case BitExpression.thinking:
        _drawThinkingFace(canvas, facePaint);
        break;
      case BitExpression.scared:
        _drawScaredFace(canvas, facePaint);
        break;
      case BitExpression.effort:
        _drawEffortFace(canvas, facePaint);
        break;
      case BitExpression.starEyes:
        _drawStarEyesFace(canvas, facePaint);
        break;
      case BitExpression.confused:
        _drawConfusedFace(canvas, facePaint);
        break;
      case BitExpression.lowBattery:
        _drawLowBatteryFace(canvas, facePaint);
        break;
      case BitExpression.startled:
        _drawStartledFace(canvas, facePaint);
        break;
      case BitExpression.relieved:
        _drawRelievedFace(canvas, facePaint);
        break;
    }
  }

  void _drawIdleFace(Canvas canvas, Paint paint) {
    // Pixel eyes (4x4 squares)
    final eyeSize = _isBlinking ? 2.0 : 6.0;
    canvas.drawRect(Rect.fromLTWH(25, 15, 8, eyeSize), paint);
    canvas.drawRect(Rect.fromLTWH(47, 15, 8, eyeSize), paint);

    // Smile (pixel arc)
    canvas.drawRect(Rect.fromLTWH(30, 32, 4, 4), paint);
    canvas.drawRect(Rect.fromLTWH(34, 36, 12, 4), paint);
    canvas.drawRect(Rect.fromLTWH(46, 32, 4, 4), paint);
  }

  void _drawHappyFace(Canvas canvas, Paint paint) {
    // Big happy eyes
    canvas.drawRect(Rect.fromLTWH(25, 12, 10, 10), paint);
    canvas.drawRect(Rect.fromLTWH(45, 12, 10, 10), paint);

    // Big grin
    canvas.drawRect(Rect.fromLTWH(25, 30, 4, 4), paint);
    canvas.drawRect(Rect.fromLTWH(29, 34, 22, 6), paint);
    canvas.drawRect(Rect.fromLTWH(51, 30, 4, 4), paint);
  }

  void _drawThinkingFace(Canvas canvas, Paint paint) {
    // Looking up eyes
    canvas.drawRect(Rect.fromLTWH(25, 10, 8, 6), paint);
    canvas.drawRect(Rect.fromLTWH(47, 10, 8, 6), paint);

    // Thinking dots
    canvas.drawCircle(const Offset(35, 36), 3, paint);
    canvas.drawCircle(const Offset(45, 36), 3, paint);
  }

  void _drawScaredFace(Canvas canvas, Paint paint) {
    // Wide eyes
    canvas.drawRect(Rect.fromLTWH(22, 12, 12, 12), paint);
    canvas.drawRect(Rect.fromLTWH(46, 12, 12, 12), paint);

    // O mouth
    canvas.drawRect(Rect.fromLTWH(35, 30, 10, 10), paint);
    // Cut out center for O shape
    final bgPaint = Paint()..color = screenColor;
    canvas.drawRect(Rect.fromLTWH(38, 33, 4, 4), bgPaint);
  }

  void _drawEffortFace(Canvas canvas, Paint paint) {
    // Squinting eyes
    canvas.drawRect(Rect.fromLTWH(25, 16, 10, 4), paint);
    canvas.drawRect(Rect.fromLTWH(45, 16, 10, 4), paint);

    // Gritting teeth pattern
    canvas.drawRect(Rect.fromLTWH(28, 32, 6, 8), paint);
    canvas.drawRect(Rect.fromLTWH(37, 32, 6, 8), paint);
    canvas.drawRect(Rect.fromLTWH(46, 32, 6, 8), paint);
  }

  void _drawStarEyesFace(Canvas canvas, Paint paint) {
    // Star eyes - draw simple stars
    _drawStar(canvas, const Offset(29, 16), 8, paint);
    _drawStar(canvas, const Offset(51, 16), 8, paint);

    // Big happy smile
    canvas.drawRect(Rect.fromLTWH(25, 32, 4, 4), paint);
    canvas.drawRect(Rect.fromLTWH(29, 36, 22, 4), paint);
    canvas.drawRect(Rect.fromLTWH(51, 32, 4, 4), paint);
  }

  void _drawStar(Canvas canvas, Offset center, double size, Paint paint) {
    // Simple 4-point pixel star
    canvas.drawRect(
      Rect.fromCenter(center: center, width: size, height: size / 3),
      paint,
    );
    canvas.drawRect(
      Rect.fromCenter(center: center, width: size / 3, height: size),
      paint,
    );
  }

  void _drawConfusedFace(Canvas canvas, Paint paint) {
    // Normal eyes
    canvas.drawRect(Rect.fromLTWH(25, 14, 8, 8), paint);
    canvas.drawRect(Rect.fromLTWH(47, 14, 8, 8), paint);

    // Loading spinner (simple rotation)
    final spinAngle = (_blinkTimer * 4) % (2 * math.pi);
    canvas.save();
    canvas.translate(40, 36);
    canvas.rotate(spinAngle);
    canvas.drawRect(Rect.fromLTWH(-8, -2, 16, 4), paint);
    canvas.drawRect(Rect.fromLTWH(-2, -8, 4, 16), paint);
    canvas.restore();
  }

  void _drawLowBatteryFace(Canvas canvas, Paint paint) {
    final dimPaint = Paint()..color = neonGreen.withOpacity(0.5);

    // Droopy eyes
    canvas.drawRect(Rect.fromLTWH(25, 18, 8, 4), dimPaint);
    canvas.drawRect(Rect.fromLTWH(47, 18, 8, 4), dimPaint);

    // Flat mouth
    canvas.drawRect(Rect.fromLTWH(30, 34, 20, 4), dimPaint);
  }

  void _drawStartledFace(Canvas canvas, Paint paint) {
    // Wide surprised eyes
    canvas.drawRect(Rect.fromLTWH(22, 10, 14, 14), paint);
    canvas.drawRect(Rect.fromLTWH(44, 10, 14, 14), paint);

    // Small o mouth
    canvas.drawCircle(const Offset(40, 36), 5, paint);
    final bgPaint = Paint()..color = screenColor;
    canvas.drawCircle(const Offset(40, 36), 2, bgPaint);
  }

  void _drawRelievedFace(Canvas canvas, Paint paint) {
    // Closed happy eyes (arcs)
    canvas.drawRect(Rect.fromLTWH(25, 18, 10, 3), paint);
    canvas.drawRect(Rect.fromLTWH(45, 18, 10, 3), paint);

    // Relieved smile
    canvas.drawRect(Rect.fromLTWH(32, 34, 16, 4), paint);
  }

  void _drawArms(Canvas canvas) {
    final metalPaint = Paint()..color = gunmetalGrey;
    final yarnPaint = Paint()
      ..color = burgundyYarn
      ..style = PaintingStyle.stroke
      ..strokeWidth = 6
      ..strokeCap = StrokeCap.round;

    // Left arm - yarn wrapped joint
    final leftShoulderPath = Path();
    leftShoulderPath.moveTo(15, 50);
    leftShoulderPath.quadraticBezierTo(5, 60, 10, 80);
    canvas.drawPath(leftShoulderPath, yarnPaint);
    canvas.drawCircle(const Offset(10, 80), 8, metalPaint); // Hand

    // Right arm - yarn wrapped joint
    final rightShoulderPath = Path();
    rightShoulderPath.moveTo(65, 50);
    rightShoulderPath.quadraticBezierTo(75, 60, 70, 80);
    canvas.drawPath(rightShoulderPath, yarnPaint);
    canvas.drawCircle(const Offset(70, 80), 8, metalPaint); // Hand
  }

  void _drawLegs(Canvas canvas) {
    final metalPaint = Paint()..color = gunmetalGrey;
    final yarnPaint = Paint()
      ..color = burgundyYarn
      ..style = PaintingStyle.stroke
      ..strokeWidth = 5;

    // Left leg
    canvas.drawRect(Rect.fromLTWH(20, 95, 15, 20), metalPaint);
    canvas.drawLine(const Offset(27, 95), const Offset(27, 100), yarnPaint);

    // Right leg
    canvas.drawRect(Rect.fromLTWH(45, 95, 15, 20), metalPaint);
    canvas.drawLine(const Offset(52, 95), const Offset(52, 100), yarnPaint);

    // Feet (heavy boots)
    canvas.drawRRect(
      RRect.fromRectAndRadius(Rect.fromLTWH(15, 112, 20, 8), const Radius.circular(2)),
      metalPaint,
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(Rect.fromLTWH(45, 112, 20, 8), const Radius.circular(2)),
      metalPaint,
    );
  }

  /// Set Bit's facial expression
  void setExpression(BitExpression expression) {
    _expression = expression;
    _expressionTimer = 0;
  }

  /// Get Bit's current expression
  BitExpression get expression => _expression;

  /// Check if a touch position is in Bit's arm area (for unravel mechanic)
  bool isInArmArea(Vector2 touchPos) {
    final armArea = Rect.fromLTWH(
      position.x - 50,
      position.y - 80,
      100,
      60,
    );
    return armArea.contains(Offset(touchPos.x, touchPos.y));
  }

  /// Get the position of Bit's arm (for rope attachment)
  Vector2 get armPosition => Vector2(position.x, position.y - 40);

  /// Move Bit left
  void moveLeft() {
    moveDirection = -1;
  }

  /// Move Bit right
  void moveRight() {
    moveDirection = 1;
  }

  /// Stop horizontal movement
  void stopMoving() {
    moveDirection = 0;
  }

  /// Make Bit jump (if grounded)
  void jump() {
    if (isGrounded) {
      velocity.y = -jumpForce;
      isGrounded = false;
    }
  }

  /// Land on ground
  void land(double groundY) {
    position.y = groundY;
    velocity.y = 0;
    isGrounded = true;

    // Show relieved expression if was falling fast
    if (velocity.y > 300) {
      setExpression(BitExpression.startled);
    }
  }
}
