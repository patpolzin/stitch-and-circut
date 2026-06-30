# PR FAQ

# **PR/FAQ (Press Release / Frequently Asked Questions)**

*Note: This section follows the "Working Backwards" method. It imagines the product is already launched and describes it to the public to ensure the vision is clear.*

## **FOR IMMEDIATE RELEASE**

### **New Mobile Game "Stitch & Circuit" Proves Technology Can Be Cozy**

**SAN FRANCISCO** — *Stitch & Circuit*, a new puzzle-adventure game for iOS and Android, launches today, introducing the world to "Bit"—a robot built from heavy industrial metal and warm, hand-knit wiring. Unlike traditional robot games focused on destruction, *Stitch & Circuit* challenges players to fix a broken world by mending connections, bridging gaps, and powering up the environment.

Designed for children aged 6–10, the game utilizes a unique "soft-body" physics engine where players must unravel Bit’s knit arms to swing across chasms, conduct electricity, and stitch broken landscapes back together.

"We wanted to build a game that teaches the logic of connectivity without feeling like a textbook," says the lead developer. "Bit represents the intersection of the digital and the physical. He shows kids that technology isn't just about code; it's about connecting things—and people—together."

The game features an adaptive AI narrator, "Motherboard," who encourages players based on their unique playstyle, making every puzzle-solving journey feel personal.

### **Internal FAQ**

**Q: What is the core differentiator of this game?**

**A:** The **"Material Contrast" mechanic**. Most physics games treat objects as rigid bodies. *Stitch & Circuit* combines rigid mechanics (Bit’s heavy metal body) with soft-body fluid dynamics (his knit wiring). Players must master the tension, slack, and swing of the yarn to solve puzzles, offering a tactile experience rare in mobile gaming.

**Q: Is this an educational game?**

**A:** It is "stealth learning." We do not quiz the player on math. Instead, the mechanics of completing circuits, managing cable length, and logical sequencing teach the fundamentals of engineering and computer science intuitively.

**Q: How does the AI integration work?**

**A:** We utilize a lightweight LLM integration for the narrator, "Motherboard." Instead of pre-baked generic praise, Motherboard analyzes the player's failure points (e.g., "You're trying to swing too fast") and offers context-aware hints, mimicking a supportive parent or teacher sitting next to them.

---

# PRD

# **Product Requirements Document (PRD)**

## **1\. Executive Summary**

* **Product Name:** Stitch & Circuit  
* **Platform:** Mobile (iOS, Android \- Tablet Optimized)  
* **Engine:** Unity 6 (2D/2.5D)  
* **Target Audience:** Children 6–10 (Primary), Parents/Educators (Secondary)  
* **Core Loop:** Enter Room → Assess Broken Element → Unravel Bit’s Wiring to Bridge/Fix → Exit Room.

## **2\. Character Design & Art Direction**

### **2.1 The Protagonist: "Bit"**

* **Visuals:**  
  * **Head:** CRT Monitor shape, Gunmetal Grey plating.  
  * **Face:** Pixelated neon green LED grid. Displays emotions (Happy, Thinking, Scared, Effort).  
  * **Body:** Heavy industrial armor plates.  
  * **Joints/Cabling:** **Braided Knit Wiring** (Thick texture, visible individual threads). The canonical *neutral base* yarn is **dark charcoal**; burgundy and other colors are selectable theme/skin swaps, not the base default. See `docs/KnitBit-Base-Spec.md` (§1, §7) for the canonical Species DNA and theme color legend.  
* **Audio:**  
  * **Movement:** Heavy metallic *clank* mixed with a muffled *thud* (dampened by the yarn).  
  * **Voice:** R2-D2 style beeps, but lower pitch and "warmer" tones (like a cello or woodwind synthesized).

### **2.2 The World**

* **Aesthetic:** "The Workshop." Backgrounds look like blueprints, pegboards, and oversized workbenches.  
* **Materials:** Wood, Iron, Chalkboard, Yarn.

## **3\. Gameplay Mechanics**

### **3.1 The "Unravel" Mechanic (Core)**

* **Input:** Touch & Drag from Bit’s shoulder/hand.  
* **Physics Constraints:**  
  * **Max Length:** The wire can extend 3x Bit’s body height.  
  * **Tension:** The wire must have "slack." It is not a laser beam. If the player pulls too tight, the wire turns red (visual cue) and snaps back.  
  * **Friction:** The knit texture creates high friction. It sticks to "Velcro" surfaces but slides off "Glass" surfaces.

### **3.2 Interaction Types**

| Action | Description | Visual Cue |
| :---- | :---- | :---- |
| **Grapple** | Attach hand to a hook/ring. | Hand makes a satisfying *click* sound. |
| **Conduct** | Connect a power source to a dead output. | The burgundy wire glows with a pulsing internal light. |
| **Tether** | Attach wire to a movable block and pull. | Bit leans back, heels digging into the ground (heavy animation). |
| **Mend** | Zig-zag touch gesture over a rip. | Sewing animation; the rift closes. |

### **3.3 The "Face" UI (Diegetic)**

The UI should be minimized. Bit’s face communicates game state:

* **Idle:** Blinking Smiley.  
* **Low Battery (Time Limit):** Eyes droop, smile fades.  
* **Success:** Star Eyes.  
* **Confusion (Puzzle hint needed):** A spinning loading icon.

## **4\. Technical Architecture**

### **4.1 Physics Engine**

* **Requirement:** Must support **Verlet Integration** or a Chain Collider system for the rope physics. The rope needs to feel "heavy" (like a thick nautical rope or wool braid), not bouncy like a rubber band.  
* **Collision:** Bit needs a Capsule Collider for the body and Box Colliders for the feet (to prevent rolling).

### **4.2 AI Narrator ("Motherboard")**

* **Architecture:** Hybrid approach.  
  * **Local:** Pre-recorded generic lines for latency-free reaction ("Great job\!", "Oops\!").  
  * **Cloud (Optional API):** For specific hint generation. The game sends a JSON packet of the game state (e.g., {attempts: 5, failure\_point: "gap\_too\_wide"}) to the LLM, which returns a text hint displayed as a subtitle.

### **4.3 Level Design Tools**

* **Tilemap System:** Modular "Workshop" tiles (Rulers, Screws, Wood blocks).  
* **Spline Tool:** For creating organic "yarn" paths in the environment.

## **5\. User Journey (Level 1 Example)**

1. **Start:** Bit falls out of a delivery chute. *Thud.*  
2. **Obstacle 1:** A gap in the floor.  
3. **Action:** Player drags Bit’s arm to a hook on the ceiling.  
4. **Physics:** Bit swings. Player releases touch at the apex of the swing.  
5. **Landing:** Bit lands. Face displays "Startled" then "Relieved."  
6. **Obstacle 2:** A dark elevator.  
7. **Action:** Player touches a battery, drags wire to the elevator plug.  
8. **Feedback:** Wire pulses. Elevator lights up.  
9. **Goal:** Bit enters the elevator. Level Complete.

## **6\. Success Metrics (KPIs)**

* **Completion Rate:** % of users who finish the Tutorial (World 1). Target: \>75%.  
* **Frustration Metric:** Average \# of attempts per puzzle before quitting. (Used to tune difficulty).  
* **"Toy" Factor:** Average time spent in the "Customization" menu playing with Bit’s colors (indicates emotional attachment).

# Concept

### **1\. High-Level Concept**

* **Genre:** 2.5D Physics Puzzle / Platformer.  
* **Platform:** iOS, Android (Tablet optimized).  
* **Target Audience:** Kids 6–10 (Primary), Parents (Secondary/Co-play).  
* **Engine Recommendation:** **Unity** (C\#) or **Godot**. (Given the physics requirements of the "rope" mechanics, a dedicated game engine is better than a web-wrapper like React Native, though Flutter \+ Flame is a viable alternative if you prefer Dart).

---

### **2\. Core Mechanics (The "verbs" of the game)**

The gameplay revolves around Bit’s unique anatomy: **Heavy Metal Body \+ Flexible Knit Wiring.**

#### **A. Movement (The Tank)**

* **Input:** Left/Right virtual joystick or "Tap to Move."  
* **Physics:** Bit is heavy. He doesn't floaty-jump; he lands with a satisfying metallic *thud*. He cannot jump very high on his own.  
* **Sound Cue:** Clanking metal steps, muted by the knit joints.

#### **B. The "Unravel" Mechanic (The Hero Feature)**

Bit can detach his hands/forearms, which remain connected to his body by the burgundy knit yarn.

* **Input:** Touch & Drag from Bit’s body to a target.  
* **Physics:** The yarn behaves like a rope (tension, slack, swing).  
* **Three Modes of Use:**  
  1. **Grapple & Swing:** Target a hook/ring. Bit retracts the yarn to pull himself up or swing across gaps.  
  2. **Conducting Power:** Target a "dead" battery or plug. Bit acts as a live wire, completing the circuit to open doors or power elevators.  
  3. **Tethering:** Target a movable object (e.g., a block). Bit walks backward to pull the object, or hangs from a ledge to lower the object down.

#### **C. The "Mend" Mechanic**

* **Context:** Some objects in the world are "torn" (e.g., a ripped canvas bridge or a frayed wire).  
* **Action:** The player traces a zig-zag pattern on the screen.  
* **Visual:** Bit’s yarn rapidly stitches the object back together.

---

### **3\. Game Loop & Level Progression**

**The "Hub": The Workshop**

* A cozy, messy garage.  
* **Customization Station:** Change yarn color (Skins).  
* **Mission Board:** Select levels.

**World 1: The Glitchy Garden (Tutorial Zone)**

* **Theme:** Nature vs. Tech. Oversized flowers mixed with solar panels.  
* **Level 1-1:** *Basic Movement.* Walk right, climb a small step.  
* **Level 1-2:** *The Gap.* Use the **Grapple** to swing across a small stream.  
* **Level 1-3:** *The Power.* Connect a battery to a gate to open the path.  
* **Boss:** **"The Tangle."** A messy ball of rogue wires blocking the path. The player must carefully unknot it (rotation puzzle) rather than fight it.

---

### **4\. UI/UX Design (Diegetic)**

Since this is for kids, we want to minimize on-screen text. We will use Bit’s face as the primary UI.

* **Health/Status:** No health bars. If Bit gets hurt (falls too far), his screen flickers static, and he looks dizzy.  
* **Success:** The pixel face turns into a "Big Grin" or "Star Eyes."  
* **Hint System:** If the player idles for 10 seconds, Bit taps on the screen "glass" (the device screen) and points to the solution.

---

### **5\. Technical Architecture & AI Integration**

Given your background, here is how we can integrate modern tech into the workflow:

#### **A. The "Soft Body" Physics (The Knit Wire)**

* **Implementation:** Use **Verlet Integration** for the rope physics. This creates a rope that feels "heavy" and "floppy" like thick yarn, rather than stiff like a spring.  
* **Rendering:** Use a line renderer with a repeating texture of a braided knit pattern.

#### **B. Generative AI Integration (Your Edge)**

Since you are interested in LLMs and AI, we can add a unique "infinite" aspect to the game:

* **Dynamic Storytelling (LLM):** The narrator (a "Motherboard" voice) can react to *how* the player plays.  
  * *Input:* "Player failed the jump 3 times."  
  * *LLM Output:* "Oof, that looked like a heavy landing. Maybe try shortening the wire before you swing?"  
* **Generative Textures:** Use Stable Diffusion/Midjourney to generate the background art assets (scenery) to keep development speed high.

---

### **6\. Monetization & Retention (Ethical)**

* **Premium Unlock:** First World (5 levels) is free. One-time purchase of $4.99 for the full game.  
* **No Ads:** Crucial for the "Educational/Safe" market.  
* **Collectibles:** "Yarn Balls" hidden in levels. Collecting them unlocks new patterns for Bit’s wiring (Stripes, Neon, Gold).

---

### **7\. Next Steps: The Prototype Plan**

To get this moving, I recommend a 2-week sprint to build a "Greybox" prototype (no art, just blocks).

1. **Day 1-3:** Set up the Character Controller (Movement \+ Gravity).  
2. **Day 4-7:** Build the **"Unravel" Physics**. Get the rope to feel good (swinging is hard to get right\!).  
3. **Day 8-10:** Build one puzzle: "Swing across a gap \+ Plug into a socket."  
4. **Day 11-14:** Add the "Bit" 3D model (or 2D sprite) and the pixel face animations.

