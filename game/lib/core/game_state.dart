import 'package:flutter/foundation.dart';

/// Manages the overall game state including progress, settings, and collectibles
class GameState {
  // Progress tracking
  final Map<String, bool> _completedLevels = {};
  final Set<String> _collectedYarnBalls = {};

  // Current session state
  int currentWorld = 1;
  int currentLevel = 1;
  int attempts = 0;
  double sessionTime = 0;

  // Player stats
  int totalYarnBalls = 0;
  int unlockedWorlds = 1;

  // Settings
  bool soundEnabled = true;
  bool musicEnabled = true;
  String yarnColor = 'burgundy'; // Current yarn skin

  // Available yarn colors (unlockables)
  final Map<String, bool> unlockedYarnColors = {
    'burgundy': true, // Default
    'blue': false,
    'green': false,
    'gold': false,
    'rainbow': false,
    'neon': false,
  };

  GameState();

  /// Update game state each frame
  void update(double dt) {
    sessionTime += dt;
  }

  /// Mark a level as complete
  void completeLevel(int world, int level) {
    final key = '$world-$level';
    _completedLevels[key] = true;

    // Unlock next level/world
    if (level >= 5) {
      // 5 levels per world
      unlockedWorlds = (unlockedWorlds < world + 1) ? world + 1 : unlockedWorlds;
    }

    debugPrint('Level $key completed! Unlocked worlds: $unlockedWorlds');
  }

  /// Check if a level is completed
  bool isLevelCompleted(int world, int level) {
    return _completedLevels['$world-$level'] ?? false;
  }

  /// Check if a level is unlocked
  bool isLevelUnlocked(int world, int level) {
    if (world > unlockedWorlds) return false;
    if (world < unlockedWorlds) return true;

    // For current unlocked world, check previous level
    if (level == 1) return true;
    return isLevelCompleted(world, level - 1);
  }

  /// Collect a yarn ball
  void collectYarnBall(String id) {
    if (!_collectedYarnBalls.contains(id)) {
      _collectedYarnBalls.add(id);
      totalYarnBalls++;

      // Check for color unlocks
      _checkColorUnlocks();

      debugPrint('Collected yarn ball: $id. Total: $totalYarnBalls');
    }
  }

  void _checkColorUnlocks() {
    // Unlock colors based on total yarn balls collected
    if (totalYarnBalls >= 5) unlockedYarnColors['blue'] = true;
    if (totalYarnBalls >= 10) unlockedYarnColors['green'] = true;
    if (totalYarnBalls >= 20) unlockedYarnColors['gold'] = true;
    if (totalYarnBalls >= 35) unlockedYarnColors['rainbow'] = true;
    if (totalYarnBalls >= 50) unlockedYarnColors['neon'] = true;
  }

  /// Change yarn color (if unlocked)
  bool setYarnColor(String color) {
    if (unlockedYarnColors[color] == true) {
      yarnColor = color;
      return true;
    }
    return false;
  }

  /// Record a puzzle attempt (for analytics/hints)
  void recordAttempt() {
    attempts++;
  }

  /// Reset attempt counter (when starting new puzzle)
  void resetAttempts() {
    attempts = 0;
  }

  /// Get hint data for AI narrator
  Map<String, dynamic> getHintContext() {
    return {
      'attempts': attempts,
      'sessionTime': sessionTime,
      'currentWorld': currentWorld,
      'currentLevel': currentLevel,
    };
  }

  /// Convert state to JSON for saving
  Map<String, dynamic> toJson() {
    return {
      'completedLevels': _completedLevels,
      'collectedYarnBalls': _collectedYarnBalls.toList(),
      'totalYarnBalls': totalYarnBalls,
      'unlockedWorlds': unlockedWorlds,
      'yarnColor': yarnColor,
      'unlockedYarnColors': unlockedYarnColors,
      'soundEnabled': soundEnabled,
      'musicEnabled': musicEnabled,
    };
  }

  /// Load state from JSON
  void fromJson(Map<String, dynamic> json) {
    _completedLevels.clear();
    final levels = json['completedLevels'] as Map<String, dynamic>? ?? {};
    levels.forEach((key, value) {
      _completedLevels[key] = value as bool;
    });

    _collectedYarnBalls.clear();
    final balls = json['collectedYarnBalls'] as List<dynamic>? ?? [];
    _collectedYarnBalls.addAll(balls.cast<String>());

    totalYarnBalls = json['totalYarnBalls'] as int? ?? 0;
    unlockedWorlds = json['unlockedWorlds'] as int? ?? 1;
    yarnColor = json['yarnColor'] as String? ?? 'burgundy';
    soundEnabled = json['soundEnabled'] as bool? ?? true;
    musicEnabled = json['musicEnabled'] as bool? ?? true;

    final colors = json['unlockedYarnColors'] as Map<String, dynamic>? ?? {};
    colors.forEach((key, value) {
      unlockedYarnColors[key] = value as bool;
    });
  }
}
