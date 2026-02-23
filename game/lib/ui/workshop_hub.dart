import 'package:flutter/material.dart';
import '../core/game_state.dart';

/// The Workshop Hub - Main menu and customization station
/// A cozy, messy garage where players can customize Bit and select levels
class WorkshopHub extends StatefulWidget {
  final GameState gameState;
  final Function(int world, int level) onLevelSelected;
  final Function(String color) onYarnColorChanged;

  const WorkshopHub({
    super.key,
    required this.gameState,
    required this.onLevelSelected,
    required this.onYarnColorChanged,
  });

  @override
  State<WorkshopHub> createState() => _WorkshopHubState();
}

class _WorkshopHubState extends State<WorkshopHub> with TickerProviderStateMixin {
  int _selectedTab = 0; // 0: Levels, 1: Customize
  late AnimationController _backgroundController;

  // Yarn color options with their display names and colors
  static const Map<String, YarnColorOption> yarnColors = {
    'burgundy': YarnColorOption('Burgundy', Color(0xFF722F37), 0),
    'blue': YarnColorOption('Ocean Blue', Color(0xFF1E90FF), 5),
    'green': YarnColorOption('Forest Green', Color(0xFF228B22), 10),
    'gold': YarnColorOption('Royal Gold', Color(0xFFFFD700), 20),
    'rainbow': YarnColorOption('Rainbow', Color(0xFFFF69B4), 35),
    'neon': YarnColorOption('Neon Glow', Color(0xFF39FF14), 50),
  };

  @override
  void initState() {
    super.initState();
    _backgroundController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 20),
    )..repeat();
  }

  @override
  void dispose() {
    _backgroundController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Animated workshop background
          _buildBackground(),

          // Main content
          SafeArea(
            child: Column(
              children: [
                _buildHeader(),
                _buildTabBar(),
                Expanded(
                  child: _selectedTab == 0
                      ? _buildLevelSelect()
                      : _buildCustomization(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBackground() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xFF1a1a2e),
            Color(0xFF16213e),
            Color(0xFF1a1a2e),
          ],
        ),
      ),
      child: CustomPaint(
        painter: WorkshopBackgroundPainter(
          animation: _backgroundController,
        ),
        size: Size.infinite,
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          // Game logo/title
          const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'STITCH &',
                style: TextStyle(
                  color: Color(0xFF722F37),
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
              Text(
                'CIRCUIT',
                style: TextStyle(
                  color: Color(0xFF39FF14),
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
            ],
          ),
          const Spacer(),
          // Yarn ball counter
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.3),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFF722F37)),
            ),
            child: Row(
              children: [
                Container(
                  width: 24,
                  height: 24,
                  decoration: const BoxDecoration(
                    color: Color(0xFF722F37),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '${widget.gameState.totalYarnBalls}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.3),
        borderRadius: BorderRadius.circular(25),
      ),
      child: Row(
        children: [
          _buildTab('LEVELS', 0),
          _buildTab('CUSTOMIZE', 1),
        ],
      ),
    );
  }

  Widget _buildTab(String label, int index) {
    final isSelected = _selectedTab == index;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _selectedTab = index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF722F37) : Colors.transparent,
            borderRadius: BorderRadius.circular(25),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isSelected ? Colors.white : Colors.grey,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLevelSelect() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        _buildWorldSection(
          worldNumber: 1,
          worldName: 'The Glitchy Garden',
          description: 'Nature meets technology',
          isUnlocked: true,
        ),
        const SizedBox(height: 20),
        _buildWorldSection(
          worldNumber: 2,
          worldName: 'The Factory Floor',
          description: 'Gears and mechanisms',
          isUnlocked: widget.gameState.unlockedWorlds >= 2,
        ),
        const SizedBox(height: 20),
        _buildWorldSection(
          worldNumber: 3,
          worldName: 'The Cloud Nine',
          description: 'Sky-high challenges',
          isUnlocked: widget.gameState.unlockedWorlds >= 3,
        ),
      ],
    );
  }

  Widget _buildWorldSection({
    required int worldNumber,
    required String worldName,
    required String description,
    required bool isUnlocked,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.3),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isUnlocked
              ? const Color(0xFF722F37)
              : Colors.grey.withOpacity(0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'WORLD $worldNumber',
                style: TextStyle(
                  color: isUnlocked ? const Color(0xFF39FF14) : Colors.grey,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (!isUnlocked) ...[
                const SizedBox(width: 8),
                const Icon(Icons.lock, color: Colors.grey, size: 16),
              ],
            ],
          ),
          const SizedBox(height: 4),
          Text(
            worldName,
            style: TextStyle(
              color: isUnlocked ? Colors.white : Colors.grey,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            description,
            style: TextStyle(
              color: isUnlocked ? Colors.grey : Colors.grey.withOpacity(0.5),
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 16),
          if (isUnlocked)
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: List.generate(5, (index) {
                final level = index + 1;
                final isCompleted = widget.gameState.isLevelCompleted(worldNumber, level);
                final isLevelUnlocked = widget.gameState.isLevelUnlocked(worldNumber, level);

                return _buildLevelButton(
                  worldNumber: worldNumber,
                  level: level,
                  isCompleted: isCompleted,
                  isUnlocked: isLevelUnlocked,
                );
              }),
            )
          else
            const Text(
              'Complete previous world to unlock',
              style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
            ),
        ],
      ),
    );
  }

  Widget _buildLevelButton({
    required int worldNumber,
    required int level,
    required bool isCompleted,
    required bool isUnlocked,
  }) {
    return GestureDetector(
      onTap: isUnlocked
          ? () => widget.onLevelSelected(worldNumber, level)
          : null,
      child: Container(
        width: 55,
        height: 55,
        decoration: BoxDecoration(
          color: isCompleted
              ? const Color(0xFF39FF14).withOpacity(0.3)
              : isUnlocked
                  ? const Color(0xFF722F37)
                  : Colors.grey.withOpacity(0.3),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: isCompleted
                ? const Color(0xFF39FF14)
                : isUnlocked
                    ? const Color(0xFF722F37)
                    : Colors.grey.withOpacity(0.3),
            width: 2,
          ),
        ),
        child: Center(
          child: isUnlocked
              ? Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      '$level',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (isCompleted)
                      const Icon(
                        Icons.star,
                        color: Color(0xFF39FF14),
                        size: 14,
                      ),
                  ],
                )
              : const Icon(Icons.lock, color: Colors.grey, size: 20),
        ),
      ),
    );
  }

  Widget _buildCustomization() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text(
          'YARN COLORS',
          style: TextStyle(
            color: Color(0xFF39FF14),
            fontSize: 16,
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: 16),
        ...yarnColors.entries.map((entry) {
          final colorId = entry.key;
          final option = entry.value;
          final isUnlocked = widget.gameState.unlockedYarnColors[colorId] ?? false;
          final isSelected = widget.gameState.yarnColor == colorId;

          return _buildYarnColorOption(
            colorId: colorId,
            option: option,
            isUnlocked: isUnlocked,
            isSelected: isSelected,
          );
        }),
      ],
    );
  }

  Widget _buildYarnColorOption({
    required String colorId,
    required YarnColorOption option,
    required bool isUnlocked,
    required bool isSelected,
  }) {
    return GestureDetector(
      onTap: isUnlocked ? () => widget.onYarnColorChanged(colorId) : null,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.3),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected
                ? option.color
                : isUnlocked
                    ? Colors.grey.withOpacity(0.3)
                    : Colors.grey.withOpacity(0.1),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            // Color preview
            Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                color: isUnlocked ? option.color : Colors.grey,
                shape: BoxShape.circle,
                boxShadow: isSelected
                    ? [
                        BoxShadow(
                          color: option.color.withOpacity(0.5),
                          blurRadius: 10,
                          spreadRadius: 2,
                        ),
                      ]
                    : null,
              ),
              child: !isUnlocked
                  ? const Icon(Icons.lock, color: Colors.white54)
                  : isSelected
                      ? const Icon(Icons.check, color: Colors.white)
                      : null,
            ),
            const SizedBox(width: 16),
            // Color info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    option.name,
                    style: TextStyle(
                      color: isUnlocked ? Colors.white : Colors.grey,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  if (!isUnlocked)
                    Text(
                      'Collect ${option.requiredYarnBalls} yarn balls',
                      style: const TextStyle(
                        color: Colors.grey,
                        fontSize: 12,
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class YarnColorOption {
  final String name;
  final Color color;
  final int requiredYarnBalls;

  const YarnColorOption(this.name, this.color, this.requiredYarnBalls);
}

/// Custom painter for animated workshop background
class WorkshopBackgroundPainter extends CustomPainter {
  final Animation<double> animation;

  WorkshopBackgroundPainter({required this.animation}) : super(repaint: animation);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    // Draw blueprint grid
    paint.color = const Color(0xFF2A3439).withOpacity(0.3);
    const gridSize = 40.0;

    for (double x = 0; x < size.width; x += gridSize) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y < size.height; y += gridSize) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }

    // Draw floating gears (animated)
    _drawGear(canvas, Offset(size.width * 0.1, size.height * 0.2), 30, animation.value);
    _drawGear(canvas, Offset(size.width * 0.9, size.height * 0.3), 25, -animation.value);
    _drawGear(canvas, Offset(size.width * 0.15, size.height * 0.7), 20, animation.value * 1.5);
    _drawGear(canvas, Offset(size.width * 0.85, size.height * 0.8), 35, -animation.value * 0.8);
  }

  void _drawGear(Canvas canvas, Offset center, double radius, double rotation) {
    final paint = Paint()
      ..color = const Color(0xFF722F37).withOpacity(0.1)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    canvas.save();
    canvas.translate(center.dx, center.dy);
    canvas.rotate(rotation * 2 * 3.14159);

    // Draw gear teeth
    const teethCount = 8;
    for (int i = 0; i < teethCount; i++) {
      final angle = i * 2 * 3.14159 / teethCount;
      final x1 = radius * 0.8 * _cos(angle);
      final y1 = radius * 0.8 * _sin(angle);
      final x2 = radius * _cos(angle);
      final y2 = radius * _sin(angle);
      canvas.drawLine(Offset(x1, y1), Offset(x2, y2), paint);
    }

    // Draw center circle
    canvas.drawCircle(Offset.zero, radius * 0.5, paint);
    canvas.drawCircle(Offset.zero, radius * 0.8, paint);

    canvas.restore();
  }

  double _cos(double x) => _cosApprox(x);
  double _sin(double x) => _cosApprox(x - 3.14159 / 2);

  double _cosApprox(double x) {
    x = x % (2 * 3.14159);
    if (x > 3.14159) x -= 2 * 3.14159;
    return 1 - (x * x) / 2 + (x * x * x * x) / 24;
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
