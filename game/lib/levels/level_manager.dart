import 'package:flame/components.dart';
import 'package:flutter/material.dart';
import '../game/stitch_and_circuit_game.dart';
import '../characters/bit_character.dart';

/// Types of interactive targets in the game
enum TargetType {
  hook, // For grappling
  powerSource, // For conducting electricity
  movableBlock, // For tethering
  tornObject, // For mending
}

/// An interactive target in the level
class InteractionTarget {
  final Vector2 position;
  final TargetType type;
  final String id;
  bool isActivated;

  InteractionTarget({
    required this.position,
    required this.type,
    required this.id,
    this.isActivated = false,
  });
}

/// Manages level loading, layout, and interactions
class LevelManager extends Component with HasGameRef<StitchAndCircuitGame> {
  int currentWorld = 1;
  int currentLevel = 1;

  // Level elements
  final List<InteractionTarget> targets = [];
  final List<LevelPlatform> platforms = [];
  final List<YarnBallCollectible> yarnBalls = [];

  // Level boundaries
  late Vector2 levelSize;
  late Vector2 spawnPoint;
  late Vector2 exitPoint;

  // State
  bool levelComplete = false;

  LevelManager(StitchAndCircuitGame game);

  /// Load a specific level
  Future<void> loadLevel(int world, int level) async {
    currentWorld = world;
    currentLevel = level;
    levelComplete = false;

    // Clear previous level
    targets.clear();
    platforms.clear();
    yarnBalls.clear();

    // Load level data based on world/level
    switch (world) {
      case 1: // The Glitchy Garden
        await _loadWorld1Level(level);
        break;
      default:
        await _loadWorld1Level(1); // Fallback to first level
    }
  }

  Future<void> _loadWorld1Level(int level) async {
    final screenSize = gameRef.size;
    levelSize = Vector2(screenSize.x * 2, screenSize.y);

    switch (level) {
      case 1:
        _buildTutorialLevel1(screenSize);
        break;
      case 2:
        _buildTutorialLevel2(screenSize);
        break;
      case 3:
        _buildTutorialLevel3(screenSize);
        break;
      default:
        _buildTutorialLevel1(screenSize);
    }
  }

  /// Level 1-1: Basic Movement - Walk right, climb a small step
  void _buildTutorialLevel1(Vector2 screenSize) {
    spawnPoint = Vector2(100, screenSize.y - 150);
    exitPoint = Vector2(screenSize.x - 100, screenSize.y - 150);

    // Ground platform
    platforms.add(LevelPlatform(
      position: Vector2(0, screenSize.y - 50),
      size: Vector2(screenSize.x * 0.6, 50),
    ));

    // Small step
    platforms.add(LevelPlatform(
      position: Vector2(screenSize.x * 0.4, screenSize.y - 100),
      size: Vector2(100, 50),
    ));

    // Higher platform to exit
    platforms.add(LevelPlatform(
      position: Vector2(screenSize.x * 0.5, screenSize.y - 50),
      size: Vector2(screenSize.x * 0.5, 50),
    ));

    // Yarn ball collectible
    yarnBalls.add(YarnBallCollectible(
      position: Vector2(screenSize.x * 0.3, screenSize.y - 180),
      id: '1-1-1',
    ));
  }

  /// Level 1-2: The Gap - Use Grapple to swing across
  void _buildTutorialLevel2(Vector2 screenSize) {
    spawnPoint = Vector2(100, screenSize.y - 150);
    exitPoint = Vector2(screenSize.x - 100, screenSize.y - 150);

    // Starting platform
    platforms.add(LevelPlatform(
      position: Vector2(0, screenSize.y - 50),
      size: Vector2(screenSize.x * 0.35, 50),
    ));

    // Gap (no platform)

    // Ending platform
    platforms.add(LevelPlatform(
      position: Vector2(screenSize.x * 0.65, screenSize.y - 50),
      size: Vector2(screenSize.x * 0.35, 50),
    ));

    // Hook for swinging
    targets.add(InteractionTarget(
      position: Vector2(screenSize.x * 0.5, screenSize.y * 0.3),
      type: TargetType.hook,
      id: 'hook-1',
    ));

    // Yarn ball (harder to reach, need good swing)
    yarnBalls.add(YarnBallCollectible(
      position: Vector2(screenSize.x * 0.5, screenSize.y * 0.5),
      id: '1-2-1',
    ));
  }

  /// Level 1-3: The Power - Connect battery to gate
  void _buildTutorialLevel3(Vector2 screenSize) {
    spawnPoint = Vector2(100, screenSize.y - 150);
    exitPoint = Vector2(screenSize.x - 100, screenSize.y - 150);

    // Main platform
    platforms.add(LevelPlatform(
      position: Vector2(0, screenSize.y - 50),
      size: Vector2(screenSize.x, 50),
    ));

    // Power source (battery)
    targets.add(InteractionTarget(
      position: Vector2(screenSize.x * 0.3, screenSize.y - 150),
      type: TargetType.powerSource,
      id: 'battery-1',
    ));

    // Gate (blocked until powered)
    targets.add(InteractionTarget(
      position: Vector2(screenSize.x * 0.7, screenSize.y - 150),
      type: TargetType.powerSource,
      id: 'gate-1',
    ));

    // Yarn ball behind gate
    yarnBalls.add(YarnBallCollectible(
      position: Vector2(screenSize.x * 0.85, screenSize.y - 150),
      id: '1-3-1',
    ));
  }

  /// Find an interaction target at a position
  InteractionTarget? findTargetAt(Vector2 position) {
    const hitRadius = 50.0;

    for (final target in targets) {
      if (target.position.distanceTo(position) < hitRadius) {
        return target;
      }
    }
    return null;
  }

  /// Power a target (for conducting electricity)
  void powerTarget(InteractionTarget target) {
    target.isActivated = true;

    // Check if this completes a circuit
    if (target.id.startsWith('gate')) {
      // Find connected battery
      final battery = targets.firstWhere(
        (t) => t.id.startsWith('battery') && t.isActivated,
        orElse: () => target,
      );

      if (battery.isActivated) {
        _openGate(target.id);
      }
    }
  }

  void _openGate(String gateId) {
    // Remove gate from obstacles or animate opening
    debugPrint('Gate $gateId opened!');
  }

  /// Start tethering to a movable block
  void startTethering(InteractionTarget target, BitCharacter bit) {
    // Enable physics interaction between bit and block
    debugPrint('Started tethering to ${target.id}');
  }

  /// Load the next level
  Future<void> loadNextLevel() async {
    if (currentLevel >= 5) {
      // Move to next world
      await loadLevel(currentWorld + 1, 1);
    } else {
      await loadLevel(currentWorld, currentLevel + 1);
    }
  }

  @override
  void render(Canvas canvas) {
    super.render(canvas);

    // Render platforms
    for (final platform in platforms) {
      platform.render(canvas);
    }

    // Render targets
    for (final target in targets) {
      _renderTarget(canvas, target);
    }

    // Render yarn balls
    for (final yarnBall in yarnBalls) {
      yarnBall.render(canvas);
    }

    // Render exit
    _renderExit(canvas);
  }

  void _renderTarget(Canvas canvas, InteractionTarget target) {
    final paint = Paint()..style = PaintingStyle.fill;

    switch (target.type) {
      case TargetType.hook:
        // Draw hook ring
        paint.color = const Color(0xFF8B4513); // Brown
        canvas.drawCircle(
          Offset(target.position.x, target.position.y),
          15,
          paint,
        );
        paint.color = const Color(0xFF654321);
        canvas.drawCircle(
          Offset(target.position.x, target.position.y),
          8,
          Paint()..style = PaintingStyle.stroke..strokeWidth = 4..color = paint.color,
        );
        break;

      case TargetType.powerSource:
        // Draw battery/power outlet
        paint.color = target.isActivated ? Colors.yellow : Colors.grey;
        canvas.drawRRect(
          RRect.fromRectAndRadius(
            Rect.fromCenter(
              center: Offset(target.position.x, target.position.y),
              width: 30,
              height: 40,
            ),
            const Radius.circular(4),
          ),
          paint,
        );
        // Lightning bolt icon
        if (target.isActivated) {
          paint.color = Colors.orange;
          final path = Path();
          path.moveTo(target.position.x, target.position.y - 15);
          path.lineTo(target.position.x - 5, target.position.y);
          path.lineTo(target.position.x + 5, target.position.y);
          path.lineTo(target.position.x, target.position.y + 15);
          canvas.drawPath(path, paint);
        }
        break;

      case TargetType.movableBlock:
        // Draw wooden crate
        paint.color = const Color(0xFF8B4513);
        canvas.drawRect(
          Rect.fromCenter(
            center: Offset(target.position.x, target.position.y),
            width: 50,
            height: 50,
          ),
          paint,
        );
        break;

      case TargetType.tornObject:
        // Draw torn fabric/wire
        paint.color = Colors.grey;
        final tearPaint = Paint()
          ..color = Colors.red.withOpacity(0.5)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3;
        canvas.drawLine(
          Offset(target.position.x - 20, target.position.y),
          Offset(target.position.x + 20, target.position.y),
          tearPaint,
        );
        break;
    }
  }

  void _renderExit(Canvas canvas) {
    // Draw elevator/exit door
    final paint = Paint()..color = Colors.green.withOpacity(0.3);
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromCenter(
          center: Offset(exitPoint.x, exitPoint.y - 40),
          width: 60,
          height: 80,
        ),
        const Radius.circular(8),
      ),
      paint,
    );

    // Arrow indicator
    final arrowPaint = Paint()
      ..color = Colors.green
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;
    canvas.drawLine(
      Offset(exitPoint.x, exitPoint.y - 60),
      Offset(exitPoint.x, exitPoint.y - 30),
      arrowPaint,
    );
    canvas.drawLine(
      Offset(exitPoint.x - 10, exitPoint.y - 40),
      Offset(exitPoint.x, exitPoint.y - 30),
      arrowPaint,
    );
    canvas.drawLine(
      Offset(exitPoint.x + 10, exitPoint.y - 40),
      Offset(exitPoint.x, exitPoint.y - 30),
      arrowPaint,
    );
  }
}

/// A platform in the level
class LevelPlatform {
  final Vector2 position;
  final Vector2 size;
  final Color color;

  LevelPlatform({
    required this.position,
    required this.size,
    this.color = const Color(0xFF8B4513), // Workshop wood
  });

  void render(Canvas canvas) {
    final paint = Paint()..color = color;

    // Draw main platform
    canvas.drawRect(
      Rect.fromLTWH(position.x, position.y, size.x, size.y),
      paint,
    );

    // Draw wood grain lines
    final grainPaint = Paint()
      ..color = color.withOpacity(0.7)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    for (double x = position.x + 10; x < position.x + size.x; x += 20) {
      canvas.drawLine(
        Offset(x, position.y),
        Offset(x, position.y + size.y),
        grainPaint,
      );
    }
  }

  /// Check if a point is on this platform
  bool containsPoint(Vector2 point) {
    return point.x >= position.x &&
        point.x <= position.x + size.x &&
        point.y >= position.y &&
        point.y <= position.y + size.y;
  }
}

/// Collectible yarn ball
class YarnBallCollectible {
  final Vector2 position;
  final String id;
  bool isCollected = false;
  double animationTimer = 0;

  YarnBallCollectible({
    required this.position,
    required this.id,
  });

  void update(double dt) {
    animationTimer += dt;
  }

  void render(Canvas canvas) {
    if (isCollected) return;

    // Bobbing animation
    final bobOffset = (animationTimer * 2).sin() * 5;

    // Draw yarn ball
    final paint = Paint()..color = const Color(0xFF722F37);
    canvas.drawCircle(
      Offset(position.x, position.y + bobOffset),
      15,
      paint,
    );

    // Draw yarn texture lines
    final linePaint = Paint()
      ..color = const Color(0xFF8B3A3A)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    canvas.drawArc(
      Rect.fromCircle(center: Offset(position.x, position.y + bobOffset), radius: 10),
      0,
      3.14,
      false,
      linePaint,
    );
    canvas.drawArc(
      Rect.fromCircle(center: Offset(position.x, position.y + bobOffset), radius: 8),
      1.5,
      3.14,
      false,
      linePaint,
    );

    // Sparkle effect
    if ((animationTimer * 3).toInt() % 2 == 0) {
      final sparklePaint = Paint()..color = Colors.white.withOpacity(0.8);
      canvas.drawCircle(
        Offset(position.x - 5, position.y - 5 + bobOffset),
        2,
        sparklePaint,
      );
    }
  }
}

extension on double {
  double sin() => math.sin(this);
}

class math {
  static double sin(double x) => _sin(x);
  static double _sin(double x) {
    // Simple approximation
    x = x % (2 * 3.14159);
    if (x > 3.14159) x -= 2 * 3.14159;
    return x - (x * x * x) / 6 + (x * x * x * x * x) / 120;
  }
}
