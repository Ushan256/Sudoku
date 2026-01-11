Neon Sudoku: AI-Powered Cyber-Grid
Live Demo: soduko-omega.vercel.app

Neon Sudoku is a full-stack, intelligent puzzle engine that merges high-fidelity "Cyberpunk" aesthetics with deep learning. Developed as a 6th-semester BSCS project, the application features a custom CNN-based Brain capable of real-time puzzle solving, heuristic-based hint generation, and a fully adaptive responsive UI.

🧠 The AI "Brain" (Small Language Model Approach)
Unlike generic solvers, Neon Sudoku utilizes a specialized Small Language Model (SLM) architecture—a Convolutional Neural Network (CNN)—to treat the Sudoku grid as a spatial image.

1. Model Architecture & Training
The SLM Strategy: By using a specialized CNN instead of a Large Language Model (LLM), we achieve millisecond inference times suitable for real-time gaming without high latency.
Dataset: The model was trained on a dataset of 1 million unique Sudoku puzzles and their solutions, enabling it to recognize complex digit-spatial relationships.
Digit Prediction: When an AI Hint is requested, the backend converts the current 9x9 board state into a tensor, which the model processes to predict the most statistically probable digit for the targeted cell.

2. Algorithms
Predictive Backtracking: The AI combines deep learning with a recursive backtracking algorithm. The CNN "prunes" the search tree by identifying the most likely numbers first, significantly reducing compute time compared to brute-force methods.

🛠️ Full-Stack Architecture
Backend (Intelligence Layer)
FastAPI: A high-performance Python framework used to serve the AI model with minimal overhead.
TensorFlow/Keras: Powering the inference engine for the CNN.
Hugging Face: The backend is hosted as a dedicated "Space" on Hugging Face, ensuring the AI solver is globally accessible via REST API.

Frontend (Visual Engine)
React.js: Manages complex 9x9 state matrices and high-frequency UI updates for the timer and score engines.
CSS3 Cyberpunk Engine: A 360+ line custom stylesheet providing:
Locked-Square Geometry: Prevents "board squashing" by using fractional units and fixed desktop sizing to maintain a perfect 1:1 aspect ratio.
Native Mobile UX: Implements inputMode="numeric" to trigger the native mobile numeric keypad for seamless touch-play.
Scanline Animation: A decorative horizontal "laser-scan" effect that simulates a real-time AI monitoring system.

🎮 Game Experience & Features
🌓 Theme Engine
Neon Mode (Dark): High-contrast aesthetic with glowing Orbitron typography and neon-pink accents.
Classic Mode (Light): A professional, high-contrast alternative for visibility in bright environments.

🏆 Leaderboard & Engagement logic
Local Persistence: Player data and "Best Scores" are saved locally via localStorage, allowing players to track progress without a centralized database.

Scoring Rules:
Correct Entry: +100 Points.
Mistake: -25 Points and an automated "Error-Shake" animation.
AI Hint: -50 Points (Penalty for utilizing AI assistance).
5 Difficulty Tiers: Ranging from Beginner (15 empty cells) to Extreme (65 empty cells) for master-level players.

🚀 Future Roadmap
Multiplayer Battles: Real-time PvP Sudoku using WebSockets.
OCR Solver: Utilizing Computer Vision to allow users to solve physical newspaper Sudokus by taking a photo.
Edge Inference: Porting the Hugging Face model to TensorFlow.js to allow 100% offline AI solving within the browser.

🏁 Setup & Installation
Clone the Repository: git clone https://github.com/yourusername/soduko-omega.git
Install Dependencies: npm install
Launch Localhost: npm start
