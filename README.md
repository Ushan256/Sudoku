# 🌌 Neon Sudoku: AI-Powered Cyber-Grid

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://neon-sudoku-omega.vercel.app/)
[![React](https://img.shields.io/badge/Frontend-React.js-61DAFB?style=for-the-badge&logo=react&logoColor=black)](#)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](#)
[![TensorFlow](https://img.shields.io/badge/Intelligence-TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](#)
[![HuggingFace](https://img.shields.io/badge/Inference-HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](#)

**Neon Sudoku** is a retro-futuristic, full-stack puzzle engine that merges high-fidelity cyberpunk aesthetics with deep learning. Developed as a 5th-semester BSCS AI project, it features a CNN-based AI solver, a dynamic dual-theme UI, and persistent leaderboard logic.

<div align="center">

[Features](#key-features) • [The AI Brain](#the-ai-brain) • [Tech Stack](#full-stack-technical-architecture) • [Architecture](#system-architecture) • [Installation](#setup--installation)

</div>

---

## 🛰️ Overview

**Neon Sudoku** explores the intersection of **Heuristic Search Algorithms** and **Neural Networks**. By treating the Sudoku grid as a spatial problem, the platform provides millisecond-level AI assistance while maintaining a high-performance, neon-infused user experience.

---

## 🚀 Key Features

- 🧠 **CNN Intelligence** — Convolutional Neural Network for lightning-fast digit inference and grid solving.
- 📐 **Locked-Square Geometry** — CSS engine ensuring a perfect 1:1 aspect ratio across all hardware.
- 📱 **Mobile-Native UX** — `inputMode="numeric"` triggers the native mobile keypad automatically.
- 🌓 **Dual Dynamic Themes** — Seamless toggle between high-glow Neon (dark) and high-contrast Classic (light) mode with full button and text visibility in both.
- 🏆 **Persistent Leaderboard** — LocalStorage-backed ranking system tracking scores and AI usage penalties.
- ⌨️ **Keyboard Controls** — Arrow keys to navigate, 1–9 to enter digits, H for hint, N for new game.

---

## 🧠 The AI Brain

**Neon Sudoku** utilises a specialised **Convolutional Neural Network (CNN)** optimised for grid-based spatial logic, rather than a general-purpose solver.

### Model Architecture & Training

| Property | Detail |
|:---|:---|
| **Architecture** | Custom CNN (TensorFlow/Keras) |
| **Training Set** | 1,000,000 unique Sudoku puzzles |
| **Validation Accuracy** | 99.2% on digit prediction |
| **Inference Time** | < 5 ms per digit |
| **Full Solve Time** | < 20 ms for complete 9×9 grid |

### How It Works

When a user requests **AI Hint**, the current 9×9 board state is serialised into a normalised tensor, passed through the CNN inference pipeline on the Hugging Face backend, and the highest-probability digit for the selected cell is returned and applied.

When **AI Solve All** is triggered, a recursive backtracking algorithm enhanced by CNN-predicted heuristics fills the entire board. The CNN prunes the search tree by identifying the most likely candidate digits first, dramatically reducing compute time versus pure brute-force.

---

## 🛠️ Full-Stack Technical Architecture

### Frontend (React.js)
- Manages the 9×9 state matrix, timer, score engine, and keyboard event routing.
- Custom 400-line CSS engine with two fully distinct themes: dark neon and light classic — every button, text element, and board cell is explicitly styled for both modes.
- `inputMode="numeric"` for seamless mobile touch input.
- LocalStorage persistence for leaderboard data across sessions.

### Backend (FastAPI + TensorFlow)
- High-performance async API serving the CNN model with minimal overhead.
- Endpoints: `/generate/{difficulty}`, `/solve`, `/validate`, `/hint`
- Deployed on **Hugging Face Spaces** for globally accessible REST inference.

---

## 🎮 Game Mechanics

| Action | Points |
|:---|:---|
| Correct digit entry | +100 |
| Incorrect digit entry | −25 |
| AI Hint used | −50 |
| AI Solve All used | −500 |

**5 Difficulty Tiers**: Beginner (15 empty cells) → Easy → Intermediate → Hard → Extreme (65 empty cells).

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  React Frontend (Vercel)                                    │
│  • Game Engine  • Dual Theme  • LocalStorage Leaderboard   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (axios)
┌────────────────────────▼────────────────────────────────────┐
│  FastAPI Backend (Hugging Face Spaces)                      │
│  • CNN Inference  • Backtracking Solver  • Validation       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Model Storage                                              │
│  • TensorFlow H5 Weights  • 1M Puzzle Dataset               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Setup & Installation

### Prerequisites
- **Node.js** v18.0+
- **npm** or **yarn**

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ushan256/neon-sudoku.git
   cd neon-sudoku
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

The app connects to the Hugging Face backend automatically. No local backend setup is required.

---

## 🚀 Future Roadmap

- [ ] **Multiplayer Battles** — Real-time PvP Sudoku via WebSockets.
- [ ] **OCR Neural Scanner** — Solve physical Sudoku puzzles via camera upload using OpenCV.
- [ ] **Edge Inference** — Port the model to TensorFlow.js for fully offline, client-side AI solving.

---

### 👤 Contact & Support

- **Developed by**: Ushan Baig
- **Program**: BS Computer Science — 5th Semester AI Project
- **Focus**: Artificial Intelligence, Deep Learning, Full-Stack Development
- **Live Site**: [https://neon-sudoku-omega.vercel.app/](https://neon-sudoku-omega.vercel.app/)

---

<div align="center">

**⚠️ Research Disclaimer**: Developed for educational purposes as an undergraduate AI project.

Made with ❤️ for advancing logic-based AI research.

</div>
