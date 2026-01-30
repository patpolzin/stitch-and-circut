import 'dart:async';
import 'package:flutter/foundation.dart';

/// Motherboard - The AI Narrator that provides context-aware hints and encouragement
/// Uses a hybrid approach: local pre-recorded lines for instant feedback,
/// with optional cloud LLM for specific hint generation
class MotherboardNarrator {
  // Callback for displaying narrator text
  Function(String message, NarratorTone tone)? onSpeak;

  // Player state tracking for context-aware hints
  int _failureCount = 0;
  String _lastFailurePoint = '';
  double _idleTime = 0;
  bool _hintShown = false;

  // Hint cooldown to prevent spam
  DateTime? _lastHintTime;
  static const Duration _hintCooldown = Duration(seconds: 10);

  // Pre-recorded generic lines for instant feedback
  static const Map<NarratorEvent, List<String>> _genericLines = {
    NarratorEvent.levelStart: [
      "Let's see what we've got here...",
      "A new puzzle awaits!",
      "Time to put those circuits to work!",
    ],
    NarratorEvent.success: [
      "Excellent work!",
      "You've got this!",
      "Perfectly stitched!",
      "Connection established!",
    ],
    NarratorEvent.fail: [
      "Oops!",
      "That didn't quite work...",
      "Let's try a different approach.",
      "Almost had it!",
    ],
    NarratorEvent.collectYarn: [
      "Ooh, a yarn ball!",
      "Nice find!",
      "That's going in the collection!",
    ],
    NarratorEvent.levelComplete: [
      "Level complete! Great job!",
      "You did it!",
      "Another puzzle solved!",
    ],
    NarratorEvent.idle: [
      "Need a hint?",
      "Take your time...",
      "Try touching Bit's arm!",
    ],
  };

  // Context-specific hints based on failure points
  static const Map<String, String> _contextualHints = {
    'gap_too_wide': "Try swinging further before you let go!",
    'fell_short': "You might need more momentum. Try a longer swing!",
    'rope_snapped': "The yarn turned red - that means it's stretched too far!",
    'missed_hook': "Aim for the hook! Drag from Bit's arm to the ring.",
    'no_power': "That looks unpowered. Find a battery to connect!",
    'swing_timing': "Release at the peak of your swing for maximum distance!",
    'mend_incomplete': "Keep tracing that zig-zag pattern to mend!",
  };

  MotherboardNarrator();

  /// Initialize narrator for a new level
  void startLevel(int world, int level) {
    _failureCount = 0;
    _lastFailurePoint = '';
    _idleTime = 0;
    _hintShown = false;

    speak(NarratorEvent.levelStart);
  }

  /// Report a success action
  void reportSuccess() {
    speak(NarratorEvent.success);
    _failureCount = 0;
  }

  /// Report a failure with context
  void reportFailure(String failurePoint) {
    _failureCount++;
    _lastFailurePoint = failurePoint;

    speak(NarratorEvent.fail);

    // After multiple failures, offer a hint
    if (_failureCount >= 3 && !_hintShown) {
      _scheduleContextualHint(failurePoint);
    }
  }

  /// Report yarn collection
  void reportYarnCollected() {
    speak(NarratorEvent.collectYarn);
  }

  /// Report level completion
  void reportLevelComplete() {
    speak(NarratorEvent.levelComplete);
  }

  /// Update idle tracking
  void update(double dt) {
    _idleTime += dt;

    // Show idle hint after 10 seconds of inactivity
    if (_idleTime > 10 && !_hintShown) {
      speak(NarratorEvent.idle);
      _hintShown = true;
    }
  }

  /// Reset idle timer (called when player takes action)
  void resetIdle() {
    _idleTime = 0;
  }

  /// Speak a generic line for an event
  void speak(NarratorEvent event, {String? customMessage}) {
    if (!_canSpeak()) return;

    String message;
    if (customMessage != null) {
      message = customMessage;
    } else {
      final lines = _genericLines[event] ?? ["..."];
      message = lines[DateTime.now().millisecond % lines.length];
    }

    final tone = _getToneForEvent(event);
    onSpeak?.call(message, tone);
    _lastHintTime = DateTime.now();
  }

  void _scheduleContextualHint(String failurePoint) {
    // Delay hint slightly for better UX
    Future.delayed(const Duration(milliseconds: 1500), () {
      final hint = _contextualHints[failurePoint];
      if (hint != null) {
        speak(NarratorEvent.hint, customMessage: hint);
        _hintShown = true;
      }
    });
  }

  bool _canSpeak() {
    if (_lastHintTime == null) return true;
    return DateTime.now().difference(_lastHintTime!) > _hintCooldown;
  }

  NarratorTone _getToneForEvent(NarratorEvent event) {
    switch (event) {
      case NarratorEvent.success:
      case NarratorEvent.collectYarn:
      case NarratorEvent.levelComplete:
        return NarratorTone.encouraging;
      case NarratorEvent.fail:
        return NarratorTone.supportive;
      case NarratorEvent.hint:
      case NarratorEvent.idle:
        return NarratorTone.helpful;
      case NarratorEvent.levelStart:
        return NarratorTone.neutral;
    }
  }

  /// Generate a context-aware hint using game state (for LLM integration)
  /// Returns a hint JSON payload that can be sent to a cloud LLM
  Map<String, dynamic> generateHintPayload() {
    return {
      'attempts': _failureCount,
      'failure_point': _lastFailurePoint,
      'idle_time': _idleTime,
      'prompt': 'Generate an encouraging hint for a child (ages 6-10) who is '
          'playing a puzzle game. They have failed $_failureCount times at '
          '"$_lastFailurePoint". Keep the response under 15 words, friendly, '
          'and focus on the specific mechanic they\'re struggling with.',
    };
  }

  /// Process LLM response and speak it
  void processLLMResponse(String response) {
    // Sanitize and validate response
    if (response.length > 100) {
      response = response.substring(0, 100);
    }

    speak(NarratorEvent.hint, customMessage: response);
  }
}

/// Types of narrator events
enum NarratorEvent {
  levelStart,
  success,
  fail,
  collectYarn,
  levelComplete,
  idle,
  hint,
}

/// Tone of the narrator's voice (for audio selection)
enum NarratorTone {
  encouraging, // Happy, upbeat
  supportive, // Gentle, understanding
  helpful, // Informative, clear
  neutral, // Default
}

/// Widget for displaying narrator messages
class NarratorDisplay {
  String currentMessage = '';
  NarratorTone currentTone = NarratorTone.neutral;
  double displayTimer = 0;
  bool isVisible = false;

  static const double displayDuration = 3.0; // seconds

  void showMessage(String message, NarratorTone tone) {
    currentMessage = message;
    currentTone = tone;
    displayTimer = displayDuration;
    isVisible = true;

    debugPrint('[Motherboard] $message');
  }

  void update(double dt) {
    if (isVisible) {
      displayTimer -= dt;
      if (displayTimer <= 0) {
        isVisible = false;
      }
    }
  }

  double get opacity => isVisible ? (displayTimer / displayDuration).clamp(0.3, 1.0) : 0.0;
}
