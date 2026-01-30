import 'package:flame/components.dart';
import 'package:flame/events.dart';
import 'package:flame/game.dart';
import 'package:flutter/material.dart';
import '../characters/bit_character.dart';
import '../physics/verlet_rope.dart';
import '../levels/level_manager.dart';
import '../core/game_state.dart';

/// Main game class for Stitch & Circuit
/// A 2.5D physics puzzle-platformer featuring Bit, a robot with knit wiring
class StitchAndCircuitGame extends FlameGame
    with HasCollisionDetection, DragCallbacks, TapCallbacks {
  // Game state
  late GameState gameState;
  late LevelManager levelManager;

  // Main character
  late BitCharacter bit;

  // Active rope (when Bit is unraveling)
  VerletRope? activeRope;

  // Game constants
  static const double gravity = 980.0; // Pixels per second squared
  static const double bitMass = 100.0; // Heavy robot!

  // Colors from design doc
  static const Color burgundyYarn = Color(0xFF722F37);
  static const Color gunmetalGrey = Color(0xFF2A3439);
  static const Color neonGreen = Color(0xFF39FF14);
  static const Color workshopWood = Color(0xFF8B4513);

  @override
  Color backgroundColor() => const Color(0xFF1a1a2e);

  @override
  Future<void> onLoad() async {
    await super.onLoad();

    // Initialize game state
    gameState = GameState();

    // Initialize level manager
    levelManager = LevelManager(this);
    add(levelManager);

    // Create Bit character
    bit = BitCharacter(
      position: Vector2(size.x / 4, size.y / 2),
    );
    add(bit);

    // Add camera to follow Bit
    camera.viewfinder.anchor = Anchor.center;

    // Load first level
    await levelManager.loadLevel(1, 1); // World 1, Level 1

    debugPrint('Stitch & Circuit loaded successfully!');
  }

  @override
  void update(double dt) {
    super.update(dt);

    // Update active rope physics
    activeRope?.update(dt);

    // Update game state
    gameState.update(dt);
  }

  @override
  void onDragStart(DragStartEvent event) {
    super.onDragStart(event);

    // Check if drag started on Bit's arm area (for unravel mechanic)
    final touchPos = event.localPosition;
    if (bit.isInArmArea(touchPos)) {
      startUnravel(touchPos);
    }
  }

  @override
  void onDragUpdate(DragUpdateEvent event) {
    super.onDragUpdate(event);

    // Update rope target if unraveling
    if (activeRope != null) {
      activeRope!.updateTarget(event.localEndPosition);
    }
  }

  @override
  void onDragEnd(DragEndEvent event) {
    super.onDragEnd(event);

    // Complete or cancel unravel action
    if (activeRope != null) {
      completeUnravel();
    }
  }

  /// Start the unravel mechanic - Bit extends yarn from arm
  void startUnravel(Vector2 startPos) {
    activeRope = VerletRope(
      startPoint: bit.armPosition,
      endPoint: startPos,
      segmentCount: 20,
      ropeColor: burgundyYarn,
      maxLength: bit.size.y * 3, // Max 3x Bit's height
    );
    add(activeRope!);

    bit.setExpression(BitExpression.effort);
  }

  /// Complete the unravel action
  void completeUnravel() {
    if (activeRope == null) return;

    // Check what the rope connected to
    final target = levelManager.findTargetAt(activeRope!.endPoint);

    if (target != null) {
      switch (target.type) {
        case TargetType.hook:
          startGrapple(target);
          break;
        case TargetType.powerSource:
          startConduct(target);
          break;
        case TargetType.movableBlock:
          startTether(target);
          break;
        case TargetType.tornObject:
          // Mend requires zig-zag gesture, handled separately
          break;
      }
    } else {
      // No valid target - retract rope
      retractRope();
    }
  }

  /// Grapple to a hook and swing
  void startGrapple(InteractionTarget target) {
    bit.setExpression(BitExpression.happy);
    // Physics handled by rope system
    activeRope?.attachTo(target.position);
  }

  /// Conduct electricity through yarn
  void startConduct(InteractionTarget target) {
    if (activeRope == null) return;

    activeRope!.setConducting(true);
    bit.setExpression(BitExpression.happy);
    levelManager.powerTarget(target);
  }

  /// Tether to a movable block
  void startTether(InteractionTarget target) {
    activeRope?.attachTo(target.position);
    bit.setExpression(BitExpression.effort);
    levelManager.startTethering(target, bit);
  }

  /// Retract the rope back to Bit
  void retractRope() {
    if (activeRope != null) {
      remove(activeRope!);
      activeRope = null;
    }
    bit.setExpression(BitExpression.idle);
  }

  /// Called when a level is completed
  void onLevelComplete() {
    bit.setExpression(BitExpression.starEyes);
    gameState.completeLevel(levelManager.currentWorld, levelManager.currentLevel);
  }

  /// Move to the next level
  Future<void> nextLevel() async {
    await levelManager.loadNextLevel();
    bit.setExpression(BitExpression.idle);
  }
}
