import 'package:flutter/material.dart';
import '../game/stitch_and_circuit_game.dart';

/// Main game overlay providing touch controls and HUD
class GameOverlay extends StatefulWidget {
  final StitchAndCircuitGame game;

  const GameOverlay({super.key, required this.game});

  @override
  State<GameOverlay> createState() => _GameOverlayState();
}

class _GameOverlayState extends State<GameOverlay> {
  bool _isPaused = false;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Touch controls at bottom
        Positioned(
          left: 0,
          right: 0,
          bottom: 0,
          child: _buildTouchControls(),
        ),

        // Pause button at top right
        Positioned(
          top: 40,
          right: 20,
          child: _buildPauseButton(),
        ),

        // Level indicator at top left
        Positioned(
          top: 40,
          left: 20,
          child: _buildLevelIndicator(),
        ),

        // Yarn ball counter
        Positioned(
          top: 40,
          left: 0,
          right: 0,
          child: Center(child: _buildYarnCounter()),
        ),

        // Pause menu overlay
        if (_isPaused) _buildPauseMenu(),
      ],
    );
  }

  Widget _buildTouchControls() {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Left side: Movement controls
          Row(
            children: [
              _buildControlButton(
                icon: Icons.arrow_back,
                onPressed: widget.game.bit.moveLeft,
                onReleased: widget.game.bit.stopMoving,
              ),
              const SizedBox(width: 20),
              _buildControlButton(
                icon: Icons.arrow_forward,
                onPressed: widget.game.bit.moveRight,
                onReleased: widget.game.bit.stopMoving,
              ),
            ],
          ),

          // Right side: Jump button
          _buildControlButton(
            icon: Icons.arrow_upward,
            onPressed: widget.game.bit.jump,
            size: 70,
          ),
        ],
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required VoidCallback onPressed,
    VoidCallback? onReleased,
    double size = 60,
  }) {
    return GestureDetector(
      onTapDown: (_) => onPressed(),
      onTapUp: (_) => onReleased?.call(),
      onTapCancel: () => onReleased?.call(),
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(size / 2),
          border: Border.all(
            color: Colors.white.withOpacity(0.4),
            width: 2,
          ),
        ),
        child: Icon(
          icon,
          color: Colors.white.withOpacity(0.8),
          size: size * 0.5,
        ),
      ),
    );
  }

  Widget _buildPauseButton() {
    return GestureDetector(
      onTap: () {
        setState(() {
          _isPaused = !_isPaused;
          if (_isPaused) {
            widget.game.pauseEngine();
          } else {
            widget.game.resumeEngine();
          }
        });
      },
      child: Container(
        width: 50,
        height: 50,
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.3),
          borderRadius: BorderRadius.circular(25),
        ),
        child: Icon(
          _isPaused ? Icons.play_arrow : Icons.pause,
          color: Colors.white,
          size: 30,
        ),
      ),
    );
  }

  Widget _buildLevelIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.3),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        'World ${widget.game.levelManager.currentWorld} - Level ${widget.game.levelManager.currentLevel}',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 14,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildYarnCounter() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.3),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Yarn ball icon
          Container(
            width: 20,
            height: 20,
            decoration: const BoxDecoration(
              color: Color(0xFF722F37),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            '${widget.game.gameState.totalYarnBalls}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPauseMenu() {
    return Container(
      color: Colors.black.withOpacity(0.7),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(30),
          decoration: BoxDecoration(
            color: const Color(0xFF2A3439),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: const Color(0xFF722F37),
              width: 3,
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'PAUSED',
                style: TextStyle(
                  color: Color(0xFF39FF14),
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 30),
              _buildMenuButton(
                'Resume',
                () {
                  setState(() {
                    _isPaused = false;
                    widget.game.resumeEngine();
                  });
                },
              ),
              const SizedBox(height: 15),
              _buildMenuButton(
                'Restart Level',
                () {
                  widget.game.levelManager.loadLevel(
                    widget.game.levelManager.currentWorld,
                    widget.game.levelManager.currentLevel,
                  );
                  setState(() {
                    _isPaused = false;
                    widget.game.resumeEngine();
                  });
                },
              ),
              const SizedBox(height: 15),
              _buildMenuButton(
                'Settings',
                () {
                  _showSettings();
                },
              ),
              const SizedBox(height: 15),
              _buildMenuButton(
                'Quit to Menu',
                () {
                  // Return to main menu
                  Navigator.of(context).pop();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMenuButton(String text, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 200,
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF722F37),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Text(
          text,
          textAlign: TextAlign.center,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  void _showSettings() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF2A3439),
        title: const Text(
          'Settings',
          style: TextStyle(color: Color(0xFF39FF14)),
        ),
        content: StatefulBuilder(
          builder: (context, setDialogState) {
            return Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                SwitchListTile(
                  title: const Text(
                    'Sound Effects',
                    style: TextStyle(color: Colors.white),
                  ),
                  value: widget.game.gameState.soundEnabled,
                  activeColor: const Color(0xFF722F37),
                  onChanged: (value) {
                    setDialogState(() {
                      widget.game.gameState.soundEnabled = value;
                    });
                  },
                ),
                SwitchListTile(
                  title: const Text(
                    'Music',
                    style: TextStyle(color: Colors.white),
                  ),
                  value: widget.game.gameState.musicEnabled,
                  activeColor: const Color(0xFF722F37),
                  onChanged: (value) {
                    setDialogState(() {
                      widget.game.gameState.musicEnabled = value;
                    });
                  },
                ),
              ],
            );
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              'Close',
              style: TextStyle(color: Color(0xFF722F37)),
            ),
          ),
        ],
      ),
    );
  }
}
