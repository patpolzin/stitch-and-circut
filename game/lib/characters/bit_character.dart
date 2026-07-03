import 'package:flame/collisions.dart';
import 'package:flame/components.dart';
import 'package:flutter/material.dart';

import 'bit_face.dart';

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

  // Expression state. The visible face is the sprite-sheet-driven [BitFace]
  // child (crossfade + idle loop); this class keeps the game-logic state
  // machine (current expression, auto-return-to-idle) and forwards changes.
  late final BitFace face;
  BitExpression _expression = BitExpression.idle;
  double _expressionTimer = 0;

  // Colors from design doc / KnitBit Base Spec (docs/KnitBit-Base-Spec.md).
  // Canonical neutral base yarn is charcoal; burgundy is a selectable theme/skin,
  // not the base default. Theme packs swap `yarnColor` (see §7 of the spec).
  static const Color gunmetalGrey = Color(0xFF2A3439);
  static const Color charcoalYarn = Color(0xFF3A3F44); // canonical base yarn
  static const Color burgundyYarn = Color(0xFF722F37); // theme/skin option, not base
  static const Color neonGreen = Color(0xFF39FF14);
  static const Color screenColor = Color(0xFF0a0a0a);

  /// Active yarn color for the knit wiring. Defaults to the canonical charcoal
  /// base; assign a theme color (e.g. [burgundyYarn]) to reskin Bit.
  Color yarnColor = charcoalYarn;

  @override
  Future<void> onLoad() async {
    await super.onLoad();

    // Add collision shape - capsule approximated by rectangles
    add(RectangleHitbox(
      size: Vector2(60, 100),
      position: Vector2(10, 10),
    ));

    // Animated pixel-display face over the screen area of the CRT head
    // (head is drawn at (10,0,60,50), screen inset at (15,5,50,40)).
    face = BitFace(size: Vector2(50, 40), position: Vector2(15, 5));
    add(face);
    // Catch up on any expression set before this component loaded.
    face.setExpression(_expression, fade: Duration.zero);
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
    // Auto-return to idle after certain expressions. (Blinking/idle life is
    // handled inside BitFace — glow pulse, scanline sweep, blink flicker.)
    if (_expression == BitExpression.startled || _expression == BitExpression.relieved) {
      _expressionTimer += dt;
      if (_expressionTimer > 1.5) {
        setExpression(BitExpression.idle);
      }
    }
  }

  @override
  void render(Canvas canvas) {
    super.render(canvas);

    // Draw Bit's body. The face is NOT painted here — the BitFace child
    // component renders the sprite-sheet expression over the screen area.
    _drawBody(canvas);
    _drawHead(canvas);
    _drawArms(canvas);
    _drawLegs(canvas);
  }

  void _drawBody(Canvas canvas) {
    final bodyPaint = Paint()..color = gunmetalGrey;
    final yarnPaint = Paint()
      ..color = yarnColor
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

  void _drawArms(Canvas canvas) {
    final metalPaint = Paint()..color = gunmetalGrey;
    final yarnPaint = Paint()
      ..color = yarnColor
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
      ..color = yarnColor
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

  /// Set Bit's facial expression (crossfades on the display via [BitFace])
  void setExpression(BitExpression expression) {
    _expression = expression;
    _expressionTimer = 0;
    if (isLoaded) {
      face.setExpression(expression);
    }
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
