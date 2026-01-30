import 'package:flame_audio/flame_audio.dart';

/// Manages all game audio including sound effects and music
/// Bit's sounds are low-pitched, warm tones (like cello/woodwind synthesized)
class AudioManager {
  bool _soundEnabled = true;
  bool _musicEnabled = true;
  bool _initialized = false;

  // Sound effect names (to be created as audio files)
  static const String sfxFootstepMetal = 'footstep_metal.wav';
  static const String sfxFootstepYarn = 'footstep_yarn.wav';
  static const String sfxLand = 'land_heavy.wav';
  static const String sfxJump = 'jump.wav';
  static const String sfxGrappleAttach = 'grapple_click.wav';
  static const String sfxGrappleRelease = 'grapple_release.wav';
  static const String sfxSwing = 'swing_whoosh.wav';
  static const String sfxConduct = 'electric_pulse.wav';
  static const String sfxMendStitch = 'stitch.wav';
  static const String sfxMendComplete = 'mend_complete.wav';
  static const String sfxCollectYarn = 'collect_yarn.wav';
  static const String sfxLevelComplete = 'level_complete.wav';
  static const String sfxBitHappy = 'bit_beep_happy.wav';
  static const String sfxBitSad = 'bit_beep_sad.wav';
  static const String sfxBitEffort = 'bit_beep_effort.wav';
  static const String sfxBitStartled = 'bit_beep_startled.wav';

  // Music tracks
  static const String musicWorkshop = 'music_workshop.mp3';
  static const String musicGlitchyGarden = 'music_glitchy_garden.mp3';
  static const String musicPuzzle = 'music_puzzle.mp3';

  // Singleton instance
  static final AudioManager _instance = AudioManager._internal();
  factory AudioManager() => _instance;
  AudioManager._internal();

  /// Initialize the audio system
  Future<void> initialize() async {
    if (_initialized) return;

    // Pre-load frequently used sounds
    try {
      await FlameAudio.audioCache.loadAll([
        sfxFootstepMetal,
        sfxLand,
        sfxGrappleAttach,
        sfxCollectYarn,
      ]);
      _initialized = true;
    } catch (e) {
      // Audio files may not exist yet during development
      print('Audio initialization note: $e');
      _initialized = true;
    }
  }

  /// Set sound effects enabled/disabled
  set soundEnabled(bool value) {
    _soundEnabled = value;
  }

  bool get soundEnabled => _soundEnabled;

  /// Set music enabled/disabled
  set musicEnabled(bool value) {
    _musicEnabled = value;
    if (!value) {
      stopMusic();
    }
  }

  bool get musicEnabled => _musicEnabled;

  /// Play a sound effect
  Future<void> playSfx(String sound, {double volume = 1.0}) async {
    if (!_soundEnabled) return;

    try {
      await FlameAudio.play(sound, volume: volume);
    } catch (e) {
      // Silently fail if sound doesn't exist
      print('Sound not found: $sound');
    }
  }

  /// Play footstep sound (alternates between metal and yarn damped)
  int _footstepCount = 0;
  Future<void> playFootstep() async {
    _footstepCount++;
    final sound = _footstepCount % 2 == 0 ? sfxFootstepMetal : sfxFootstepYarn;
    await playSfx(sound, volume: 0.5);
  }

  /// Play landing sound (heavy thud)
  Future<void> playLand({bool heavy = false}) async {
    await playSfx(sfxLand, volume: heavy ? 1.0 : 0.7);
  }

  /// Play grapple attach sound (satisfying click)
  Future<void> playGrappleAttach() async {
    await playSfx(sfxGrappleAttach);
  }

  /// Play swing sound
  Future<void> playSwing() async {
    await playSfx(sfxSwing, volume: 0.6);
  }

  /// Play conducting electricity sound
  Future<void> playConduct() async {
    await playSfx(sfxConduct);
  }

  /// Play mend stitch sound
  Future<void> playMendStitch() async {
    await playSfx(sfxMendStitch, volume: 0.4);
  }

  /// Play yarn ball collection sound
  Future<void> playCollectYarn() async {
    await playSfx(sfxCollectYarn);
  }

  /// Play level complete fanfare
  Future<void> playLevelComplete() async {
    await playSfx(sfxLevelComplete);
  }

  /// Play Bit's expression sounds (R2-D2 style but warmer)
  Future<void> playBitExpression(BitSound sound) async {
    switch (sound) {
      case BitSound.happy:
        await playSfx(sfxBitHappy, volume: 0.7);
        break;
      case BitSound.sad:
        await playSfx(sfxBitSad, volume: 0.7);
        break;
      case BitSound.effort:
        await playSfx(sfxBitEffort, volume: 0.7);
        break;
      case BitSound.startled:
        await playSfx(sfxBitStartled, volume: 0.8);
        break;
    }
  }

  /// Start playing background music
  Future<void> playMusic(String track) async {
    if (!_musicEnabled) return;

    try {
      await FlameAudio.bgm.play(track, volume: 0.4);
    } catch (e) {
      print('Music not found: $track');
    }
  }

  /// Stop background music
  void stopMusic() {
    FlameAudio.bgm.stop();
  }

  /// Pause background music
  void pauseMusic() {
    FlameAudio.bgm.pause();
  }

  /// Resume background music
  void resumeMusic() {
    if (_musicEnabled) {
      FlameAudio.bgm.resume();
    }
  }

  /// Play workshop hub music
  Future<void> playWorkshopMusic() async {
    await playMusic(musicWorkshop);
  }

  /// Play level music based on world
  Future<void> playLevelMusic(int world) async {
    switch (world) {
      case 1:
        await playMusic(musicGlitchyGarden);
        break;
      default:
        await playMusic(musicPuzzle);
    }
  }

  /// Dispose of audio resources
  void dispose() {
    FlameAudio.bgm.dispose();
  }
}

/// Bit's expression sound types
enum BitSound {
  happy,
  sad,
  effort,
  startled,
}
