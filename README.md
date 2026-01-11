# Neon Sudoku: AI-Powered Cyber-Grid
**Project Link:** [https://soduko-omega.vercel.app/](https://soduko-omega.vercel.app/)

**Neon Sudoku** is a retro-futuristic, full-stack puzzle engine that merges high-fidelity "Cyberpunk" aesthetics with deep learning. Developed as a comprehensive 5th-semester BSCS AI project, it features a custom CNN-based AI solver, a dynamic "No-Overlap" responsive UI, and persistent leaderboard logic.

---

## 🧠 The AI "Brain" (Small Language Model Approach)

Unlike standard brute-force solvers, Neon Sudoku utilizes a specialized **Small Language Model (SLM)** architecture—specifically a Convolutional Neural Network (CNN)—optimized for grid-based spatial logic.

### 1. Model Architecture & Training
* **The SLM Strategy**: By utilizing a specialized CNN instead of a Large Language Model (LLM), we achieved millisecond inference times suitable for real-time gaming without high latency.
* **Dataset**: The model was trained on a dataset of **1 million unique Sudoku puzzles** and their solutions, enabling it to recognize complex digit-spatial relationships.
* **Accuracy**: The model achieved an impressive **99.2% accuracy** on test sets for digit prediction.
* **The "Brain" Flow**: When a user clicks **AI Hint**, the current 9x9 board state is converted into a tensor, processed by the CNN layers, and the highest-probability digit for the selected cell is returned.

### 2. Algorithms
* **Predictive Backtracking**: The backend implements a recursive backtracking algorithm enhanced by AI-predicted heuristics. The CNN "prunes" the search tree by identifying the most likely numbers first, significantly reducing compute time.

---

## 🛠️ Full-Stack Technical Architecture

### **Backend (Intelligence Layer)**
* **FastAPI (Python)**: A high-performance framework used to serve the AI model with minimal overhead.
* **TensorFlow/Keras**: Powering the inference engine for the custom CNN model.
* **Hugging Face**: The backend is hosted as a dedicated "Space" on Hugging Face, ensuring the AI solver is globally accessible via REST API.

### **Frontend (Visual Engine)**
* **React.js**: Manages complex 9x9 state matrices and high-frequency UI updates for the timer and score engines.
* **CSS3 "Neon" Engine**: A 360+ line custom stylesheet providing:
    * **Locked-Square Geometry**: Prevents "board squashing" on monitors by using fractional units and fixed desktop sizing to maintain a perfect 1:1 aspect ratio.
    * **Native Mobile UX**: Implements `inputMode="numeric"` to trigger the native mobile numeric keypad for a seamless touch-screen experience.
    * **Scanline Animation**: A horizontal horizontal "laser-scan" effect that simulates a real-time AI monitoring system.

---

## 🎮 Game Experience & Features

### 🌓 Theme & Display Engine
* **Neon (Dark) Mode**: The default high-contrast aesthetic with glowing `Orbitron` typography and neon-pink accents.
* **Classic (Light) Mode**: A professional, high-contrast alternative optimized for high-brightness environments.

### 🏆 Leaderboard & Logic
* **Local Sign-Up**: Persistent user sessions and "Best Scores" are saved locally via `localStorage`, allowing players to track progress without a centralized database.
* **Scoring System**:
    * **Correct Entry**: +100 Points.
    * **Mistake**: -25 Points accompanied by an automated "Error-Shake" animation.
    * **AI Hint**: -50 Points penalty for utilizing AI assistance.
* **5 Difficulty Tiers**: Ranging from **Beginner (15 empty cells)** to **Extreme (65 empty cells)**.

---

## 🚀 Future Roadmap
* **Multiplayer Battles**: Real-time PvP Sudoku using WebSockets.
* **OCR Solver**: Utilizing Computer Vision to allow users to solve physical newspaper Sudokus by taking a photo.
* **Edge Inference**: Porting the model to TensorFlow.js to allow 100% offline AI solving within the browser.

---

## 🏁 Setup & Installation

1.  **Clone the Repository**: 
    ```bash
    git clone [https://github.com/your-username/soduko-omega.git](https://github.com/your-username/soduko-omega.git)
    ```
2.  **Install Dependencies**: 
    ```bash
    npm install
    ```
3.  **Launch Localhost**: 
    ```bash
    npm start
    ```
