# Stitch & Circuit

A 2.5D physics puzzle-adventure game for iOS and Android featuring **Bit** - a robot made of heavy industrial metal and warm, hand-knit wiring.

## Game Overview

**Stitch & Circuit** challenges players to fix a broken world by mending connections, bridging gaps, and powering up the environment. Unlike traditional robot games focused on destruction, this game teaches the logic of connectivity through intuitive puzzle mechanics.

### Target Audience
- **Primary:** Children ages 6-10
- **Secondary:** Parents and Educators (co-play)

### Core Mechanics

1. **Unravel** - Drag Bit's knit arms to:
   - **Grapple & Swing** across gaps
   - **Conduct Electricity** to power devices
   - **Tether** and pull movable objects

2. **Mend** - Trace a zig-zag pattern to stitch torn objects back together

## Tech Stack

- **Framework:** Flutter 3.x
- **Game Engine:** Flame 1.15+
- **Language:** Dart
- **Physics:** Custom Verlet Integration (for rope/yarn physics)
- **Platforms:** iOS 12+, Android 5.0+

## Project Structure

```
game/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── core/
│   │   ├── game_state.dart       # Progress, settings, collectibles
│   │   └── motherboard_narrator.dart  # AI narrator system
│   ├── game/
│   │   └── stitch_and_circuit_game.dart  # Main game class
│   ├── characters/
│   │   └── bit_character.dart    # Bit with pixel face expressions
│   ├── physics/
│   │   └── verlet_rope.dart      # Yarn physics simulation
│   ├── levels/
│   │   └── level_manager.dart    # Level loading and interaction
│   ├── ui/
│   │   ├── game_overlay.dart     # Touch controls and HUD
│   │   ├── workshop_hub.dart     # Main menu and customization
│   │   └── mend_gesture_detector.dart  # Zig-zag gesture detection
│   └── audio/
│       └── audio_manager.dart    # Sound effects and music
├── assets/
│   ├── images/                   # Sprites and backgrounds
│   ├── audio/                    # Sound effects and music
│   └── levels/                   # Level data JSON files
├── android/                      # Android configuration
├── ios/                          # iOS configuration
└── pubspec.yaml                  # Dependencies
```

## Getting Started

### Prerequisites

1. Install [Flutter](https://flutter.dev/docs/get-started/install) (3.2.0+)
2. Install Android Studio or Xcode for mobile development
3. Set up device emulators or connect physical devices

### Installation

```bash
# Navigate to game directory
cd game

# Get dependencies
flutter pub get

# Run on connected device/emulator
flutter run
```

### Building for Release

#### Android

```bash
# Build APK
flutter build apk --release

# Build App Bundle (recommended for Play Store)
flutter build appbundle --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

#### iOS

```bash
# Build for iOS (requires macOS with Xcode)
flutter build ios --release

# Open in Xcode for archive and distribution
open ios/Runner.xcworkspace
```

## Game Design

### The Protagonist: Bit

- **Head:** CRT Monitor shape, Gunmetal Grey plating
- **Face:** Pixelated neon green LED grid with expressions:
  - Idle (blinking smiley)
  - Happy, Thinking, Scared, Effort
  - Star Eyes (success!)
  - Confused (loading spinner for hints)
- **Body:** Heavy industrial armor plates
- **Joints:** Burgundy knit wiring (the key mechanic!)

### The World: "The Workshop"

Backgrounds styled as blueprints, pegboards, and oversized workbenches using wood, iron, chalkboard, and yarn materials.

### Levels

**World 1: The Glitchy Garden (Tutorial)**
- Level 1-1: Basic Movement
- Level 1-2: The Gap (Grapple & Swing)
- Level 1-3: The Power (Conduct Electricity)
- Levels 1-4 to 1-5: Combined mechanics
- Boss: "The Tangle" (unknotting puzzle)

### AI Narrator: Motherboard

A context-aware narrator that:
- Provides instant encouraging feedback
- Analyzes failure patterns for specific hints
- Supports optional LLM integration for dynamic hints

## Physics System

The yarn uses **Verlet Integration** for realistic rope physics:
- Feels "heavy" and "floppy" like thick yarn
- Responds to gravity and momentum
- Includes tension feedback (turns red when overstretched)
- High friction on "velcro" surfaces, slides on "glass"

## Customization

Players collect **Yarn Balls** to unlock new yarn colors:
- Burgundy (default)
- Ocean Blue (5 balls)
- Forest Green (10 balls)
- Royal Gold (20 balls)
- Rainbow (35 balls)
- Neon Glow (50 balls)

## Monetization (Planned)

- **Free:** World 1 (5 levels)
- **Premium:** $4.99 one-time purchase for full game
- **No Ads:** Safe for children

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add license information]

## Credits

Character Design: Bit concept art provided in repository (`knitbit.png`, `red.png`)
