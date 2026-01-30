import 'package:flame/game.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'game/stitch_and_circuit_game.dart';
import 'ui/game_overlay.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Lock to portrait mode for consistent gameplay
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // Hide system UI for immersive experience
  await SystemChrome.setEnabledSystemUIMode(
    SystemUiMode.immersiveSticky,
  );

  runApp(
    const ProviderScope(
      child: StitchAndCircuitApp(),
    ),
  );
}

class StitchAndCircuitApp extends StatelessWidget {
  const StitchAndCircuitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Stitch & Circuit',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF722F37), // Burgundy - Bit's yarn color
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const GameScreen(),
    );
  }
}

class GameScreen extends StatefulWidget {
  const GameScreen({super.key});

  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  late final StitchAndCircuitGame game;

  @override
  void initState() {
    super.initState();
    game = StitchAndCircuitGame();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Main Game
          GameWidget(
            game: game,
            loadingBuilder: (context) => const Center(
              child: CircularProgressIndicator(
                color: Color(0xFF722F37),
              ),
            ),
            errorBuilder: (context, error) => Center(
              child: Text(
                'Error loading game: $error',
                style: const TextStyle(color: Colors.red),
              ),
            ),
          ),
          // Overlay UI
          GameOverlay(game: game),
        ],
      ),
    );
  }
}
