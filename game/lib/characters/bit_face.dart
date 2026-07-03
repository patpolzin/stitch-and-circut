import 'dart:math' as math;
import 'dart:ui';

import 'package:flame/components.dart';

import 'bit_character.dart' show BitExpression;

/// Sprite-sheet-driven animated face for Bit's pixel-display screen.
///
/// Renders expressions from `assets/images/knitbit_face_sheet.png`
/// (10 cells, 512px, 5x2 grid — see knitbit_face_sheet.json) and layers the
/// "alive screen" behaviors from the face-system design:
///
/// - **Crossfade**: [setExpression] blends the outgoing and incoming
///   expression textures over ~220ms, reading as a smooth screen redraw.
/// - **Idle glow pulse**: the whole face breathes between ~94-100% opacity
///   on a slow sine, so a static expression never reads as a dead image.
/// - **Scanline sweep**: every few seconds a faint darker band sweeps down
///   the screen, like a CRT refresh.
/// - **Blink flicker**: at a slightly irregular interval the display dips
///   dark for ~70ms — a screen "blink" that works on every expression
///   without per-expression blink frames.
///
/// This component draws only the display content on a black screen; the
/// helmet bezel around it belongs to the character/faceplate art.
class BitFace extends PositionComponent with HasGameRef {
  BitFace({required Vector2 size, Vector2? position})
      : super(size: size, position: position ?? Vector2.zero());

  static const String sheetAsset = 'knitbit_face_sheet.png';
  static const double cellSize = 512;
  static const int gridCols = 5;

  /// Grid cell (col, row) per expression — mirrors knitbit_face_sheet.json.
  static const Map<BitExpression, (int, int)> _cells = {
    BitExpression.idle: (0, 0),
    BitExpression.happy: (1, 0),
    BitExpression.thinking: (2, 0),
    BitExpression.scared: (3, 0),
    BitExpression.effort: (4, 0),
    BitExpression.starEyes: (0, 1),
    BitExpression.confused: (1, 1),
    BitExpression.lowBattery: (2, 1),
    BitExpression.startled: (3, 1),
    BitExpression.relieved: (4, 1),
  };

  // Crossfade
  static const Duration defaultFade = Duration(milliseconds: 220);
  BitExpression _current = BitExpression.idle;
  BitExpression? _previous;
  double _fadeT = 1.0; // 0 -> just started, 1 -> fade complete
  double _fadeSeconds = 0.22;

  // Idle behaviors
  static const double _pulsePeriod = 3.2; // seconds per glow-breath cycle
  static const double _pulseDepth = 0.06; // opacity dip at the bottom of the breath
  static const double _sweepInterval = 4.5; // seconds between scanline sweeps
  static const double _sweepDuration = 0.9; // seconds for one top-to-bottom sweep
  static const double _sweepBandFrac = 0.10; // band height as fraction of face
  static const double _blinkBaseInterval = 4.0; // seconds; jittered per cycle
  static const double _blinkDuration = 0.07; // seconds the display dips dark
  static const double _blinkDim = 0.25; // opacity during the dip

  double _clock = 0;
  int _blinkCycle = 0;
  double _nextBlinkAt = _blinkBaseInterval;

  final Map<BitExpression, Sprite> _sprites = {};
  final Paint _paint = Paint();

  BitExpression get expression => _current;
  bool get isFading => _fadeT < 1.0;

  @override
  Future<void> onLoad() async {
    await super.onLoad();
    final image = await gameRef.images.load(sheetAsset);
    for (final entry in _cells.entries) {
      final (col, row) = entry.value;
      _sprites[entry.key] = Sprite(
        image,
        srcPosition: Vector2(col * cellSize, row * cellSize),
        srcSize: Vector2.all(cellSize),
      );
    }
  }

  /// Switch the display to [expression], crossfading over [fade]
  /// (defaults to [defaultFade]). Setting the current expression is a no-op.
  void setExpression(BitExpression expression, {Duration? fade}) {
    if (expression == _current) return;
    _previous = _current;
    _current = expression;
    _fadeSeconds = (fade ?? defaultFade).inMilliseconds / 1000.0;
    _fadeT = _fadeSeconds <= 0 ? 1.0 : 0.0;
  }

  @override
  void update(double dt) {
    super.update(dt);
    _clock += dt;

    if (_fadeT < 1.0) {
      _fadeT = math.min(1.0, _fadeT + dt / _fadeSeconds);
      if (_fadeT >= 1.0) _previous = null;
    }

    if (_clock >= _nextBlinkAt + _blinkDuration) {
      _blinkCycle++;
      // Deterministic per-cycle jitter (±0.8s) keeps blinks from metronoming.
      final jitter = math.sin(_blinkCycle * 12.9898) * 0.8;
      _nextBlinkAt = _clock + _blinkBaseInterval + jitter;
    }
  }

  double get _idleOpacity {
    final pulse = 1.0 -
        _pulseDepth * (0.5 + 0.5 * math.sin(2 * math.pi * _clock / _pulsePeriod));
    final blinking =
        _clock >= _nextBlinkAt && _clock < _nextBlinkAt + _blinkDuration;
    return blinking ? _blinkDim : pulse;
  }

  @override
  void render(Canvas canvas) {
    super.render(canvas);
    if (_sprites.isEmpty) return;

    final idle = _idleOpacity;
    final rect = Rect.fromLTWH(0, 0, size.x, size.y);

    canvas.drawRect(rect, Paint()..color = const Color(0xFF000000));

    if (_previous != null && _fadeT < 1.0) {
      _paint.color = const Color(0xFFFFFFFF).withOpacity((1 - _fadeT) * idle);
      _sprites[_previous]!.render(canvas, size: size, overridePaint: _paint);
      _paint.color = const Color(0xFFFFFFFF).withOpacity(_fadeT * idle);
      _sprites[_current]!.render(canvas, size: size, overridePaint: _paint);
    } else {
      _paint.color = const Color(0xFFFFFFFF).withOpacity(idle);
      _sprites[_current]!.render(canvas, size: size, overridePaint: _paint);
    }

    _renderScanline(canvas);
  }

  void _renderScanline(Canvas canvas) {
    final phase = _clock % _sweepInterval;
    if (phase >= _sweepDuration) return;
    final t = phase / _sweepDuration;
    final bandH = size.y * _sweepBandFrac;
    // Sweep from just above the face to just below so the band fully exits.
    final y = -bandH + t * (size.y + 2 * bandH);
    canvas.save();
    canvas.clipRect(Rect.fromLTWH(0, 0, size.x, size.y));
    canvas.drawRect(
      Rect.fromLTWH(0, y, size.x, bandH),
      Paint()..color = const Color(0xFF000000).withOpacity(0.18),
    );
    canvas.restore();
  }
}
