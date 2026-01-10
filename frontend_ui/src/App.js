import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

// THIS IS THE KEY: Your Live AI Brain Address
const API_BASE = "https://ushan256-sudoku.hf.space";

function App() {
  const [grid, setGrid] = useState(Array(9).fill(0).map(() => Array(9).fill(0)));
  const [initialGrid, setInitialGrid] = useState([]);
  const [solution, setSolution] = useState([]); 
  const [selected, setSelected] = useState({ r: 0, c: 0 });
  const [timer, setTimer] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isGameEnded, setIsGameEnded] = useState(false);
  const [gameStarted, setGameStarted] = useState(false); 
  const [notification, setNotification] = useState("");
  const [score, setScore] = useState(0);
  const [mistakes, setMistakes] = useState(0); 
  const [difficulty, setDifficulty] = useState(30);
  const [user, setUser] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showVictory, setShowVictory] = useState(false); 

  // PERSISTENCE: Leaderboard from LocalStorage
  const [leaderboard, setLeaderboard] = useState(() => {
    const saved = localStorage.getItem("neon_sudoku_leaderboard");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem("neon_sudoku_leaderboard", JSON.stringify(leaderboard));
  }, [leaderboard]);

  const showToast = (msg) => {
    setNotification(msg);
    setTimeout(() => setNotification(""), 3000);
  };

  const handleLogin = (e) => {
    e.preventDefault();
    const playerName = user.trim();
    if (playerName.length > 2) {
      setIsLoggedIn(true);
      showToast(`Welcome Back, ${playerName}`);
      setLeaderboard(prev => {
        if (!prev.find(p => p.name === playerName)) {
            return [...prev, { name: playerName, best: 0, time: Infinity }].sort((a,b) => b.best - a.best || a.time - b.time);
          }
        return prev;
      });
    } else { showToast("Name too short!"); }
  };

  const updateBestScore = useCallback((finalScore, playerName, finalTime = Infinity) => {
    setLeaderboard(prevLeaderboard => {
      const copy = [...prevLeaderboard];
      const idx = copy.findIndex(p => p.name === playerName);
      if (idx === -1) {
        copy.push({ name: playerName, best: finalScore, time: finalTime });
      } else {
        const current = copy[idx];
        if (finalScore > current.best) {
          copy[idx] = { ...current, best: finalScore, time: finalTime };
        } else if (finalScore === current.best && finalTime < (current.time ?? Infinity)) {
          copy[idx] = { ...current, time: finalTime };
        }
      }
      return copy.sort((a, b) => {
        if (b.best !== a.best) return b.best - a.best;
        const at = a.time ?? Infinity;
        const bt = b.time ?? Infinity;
        return at - bt;
      });
    });
  }, []);

  const handleSwitchUser = () => {
    setIsLoggedIn(false);
    setGameStarted(false);
    setShowVictory(false);
    setGrid(Array(9).fill(0).map(() => Array(9).fill(0)));
    showToast("Logged out.");
  };

  const fetchNewGame = useCallback(async () => {
    if (!isLoggedIn) return;
    try {
      // PROD LINK: Generate
      const res = await axios.get(`${API_BASE}/generate/${difficulty}`);
      const newGrid = res.data.grid;
      
      // PROD LINK: Solve
      const solRes = await axios.post(`${API_BASE}/solve`, { grid: newGrid });
      
      setSolution(solRes.data.solution);
      setGrid(newGrid);
      setInitialGrid(newGrid.map(row => [...row]));
      setTimer(0); setScore(0); setMistakes(0);
      setIsPaused(false); setIsGameEnded(false); setShowVictory(false);
      setGameStarted(true); 
      showToast(`Level ${difficulty} Loaded`);
    } catch (err) { 
      console.error(err);
      showToast("Backend Offline!"); 
    }
  }, [difficulty, isLoggedIn]);

  const handleInput = useCallback((row, col, value) => {
    if (!gameStarted || isGameEnded || isPaused || initialGrid[row][col] !== 0) return;
    
    const isCorrect = value === solution[row][col];
    const newGrid = [...grid];
    newGrid[row][col] = value;
    setGrid(newGrid);

    if (isCorrect) {
      setScore(prev => prev + 100);
      showToast("Correct! +100");
    } else {
      setScore(prev => prev - 25);
      setMistakes(prev => prev + 1); 
      showToast("Incorrect! -25");
    }
  }, [gameStarted, isGameEnded, isPaused, initialGrid, solution, grid]);

  const getHint = useCallback(async () => {
    if (!gameStarted || isGameEnded || isPaused || grid[selected.r][selected.c] !== 0) return;
    try {
      // PROD LINK: Hint
      const res = await axios.post(`${API_BASE}/hint?row=${selected.r}&col=${selected.c}`, { grid });
      const n = [...grid];
      n[selected.r][selected.c] = res.data.value;
      setGrid(n);
      setScore(prev => prev - 50);
      showToast("AI Hint Used (-50)");
    } catch (err) { showToast("Hint Error"); }
  }, [selected, grid, isGameEnded, isPaused, gameStarted]);

  const solveAll = useCallback(async () => {
    if (!gameStarted || isGameEnded) return;
    try {
      let emptyCells = 0;
      grid.forEach(row => row.forEach(cell => { if (cell === 0) emptyCells++; }));
      setGrid(solution);
      setIsGameEnded(true);
      const aiPenalty = emptyCells * 150;
      const finalScore = score - aiPenalty;
      setScore(finalScore);
      updateBestScore(finalScore, user, timer);
      setShowVictory(true); 
    } catch (err) { showToast("AI Solve Error"); }
  }, [grid, solution, isGameEnded, gameStarted, score, user, updateBestScore, timer]);

  const handleKeyDown = useCallback((e) => {
    if (!isLoggedIn || showVictory) return;
    if (e.key === 'n') fetchNewGame();
    if (!gameStarted) return;
    if (e.key === 'p') setIsPaused(prev => !prev);
    if (e.key === 'h') getHint();
    if (e.key === 'a') solveAll(); 

    if (isPaused || isGameEnded) return;
    const { r, c } = selected;
    if (e.key === 'ArrowUp') setSelected({ r: Math.max(0, r - 1), c });
    if (e.key === 'ArrowDown') setSelected({ r: Math.min(8, r + 1), c });
    if (e.key === 'ArrowLeft') setSelected({ r, c: Math.max(0, c - 1) });
    if (e.key === 'ArrowRight') setSelected({ r, c: Math.min(8, c + 1) });
    
    if (/[1-9]/.test(e.key)) handleInput(r, c, parseInt(e.key));
    if (e.key === 'Backspace' && initialGrid[r][c] === 0) {
        const n = [...grid]; n[r][c] = 0; setGrid(n);
    }
  }, [isLoggedIn, showVictory, fetchNewGame, gameStarted, isPaused, getHint, solveAll, isGameEnded, selected, handleInput, initialGrid, grid]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  useEffect(() => {
    let interval;
    if (gameStarted && !isPaused && !isGameEnded) {
      interval = setInterval(() => setTimer(prev => prev + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [isPaused, isGameEnded, gameStarted]);

  const globalRank = leaderboard.findIndex(p => p.name === user) + 1;

  return (
    <div className="app-shell">
      {!isLoggedIn && (
        <div className="login-overlay">
          <form className="login-card" onSubmit={handleLogin}>
            <h1 className="pink">NEON LOGIN</h1>
            <input className="login-input" placeholder="User ID..." value={user} onChange={(e) => setUser(e.target.value)} />
            <br/><button className="btn" type="submit">ENTER SYSTEM</button>
          </form>
        </div>
      )}

      {showVictory && (
        <div className="victory-overlay">
          <div className="victory-card">
            <h1 className="pink">VICTORY</h1>
              <div className="stats-box-modal">
                <p>PLAYER: <span className="blue">{user}</span></p>
                <p>SCORE: <span className="blue">{score}</span></p>
                <p>TIME: <span className="blue">{Math.floor(timer/60)}m {timer%60}s</span></p>
                <p>MISTAKES: <span className="pink">{mistakes}</span></p>
                <p>GLOBAL RANK: <span className="blue">#{globalRank}</span></p>
              </div>
            <button className="btn" onClick={fetchNewGame}>PLAY AGAIN</button>
          </div>
        </div>
      )}

      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>ID: {user}</h2>
          <span className="switch-link" onClick={handleSwitchUser}>SWITCH USER</span>
        </div>

        <section className="instruct-box">
          <h3>INSTRUCTIONS</h3>
          <ul>
            <li><b>[N]</b> New Puzzle</li>
            <li><b>[P]</b> Pause Game</li>
            <li><b>[H]</b> AI Hint</li>
            <li><b>[A]</b> AI Solve All</li>
            <li><b>[Arrows]</b> Navigate</li>
          </ul>
        </section>
        
        <section className="difficulty-box">
          <h3>LEVEL SELECT</h3>
          <select className="diff-select" value={difficulty} onChange={(e) => setDifficulty(parseInt(e.target.value))}>
            <option value={10}>Very Easy (10)</option>
            <option value={30}>Easy (30)</option>
            <option value={45}>Medium (45)</option>
            <option value={60}>Hard (60)</option>
          </select>
        </section>

        <section className="leaderboard-box">
          <h3>LEADERBOARD</h3>
          <div className="leaderboard-list">
            {leaderboard.length === 0 ? "No records yet." : leaderboard.map((p, i) => (
              <div key={i} className={`leaderboard-item ${p.name === user ? "current-user" : ""}`}>
                <span><span className="rank">{i+1}.</span> {p.name}</span>
                <span>{p.best} {p.time && p.time !== Infinity ? `(${Math.floor(p.time/60)}:${(p.time%60).toString().padStart(2,'0')})` : ''}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="score-info-box">
          <h3>SCORING</h3>
          <ul>
            <li>Correct: <span className="blue">+100</span></li>
            <li>Wrong: <span className="pink">-25</span></li>
            <li>AI Hint: <span className="pink">-50</span></li>
            <li>AI Solve: <span className="pink">-150/cell</span></li>
          </ul>
        </section>

        <section className="cheat-box">
          <h3>AI CHEAT</h3>
          <button className="cheat-btn" onClick={solveAll} disabled={!gameStarted}>SOLVE ALL BOARD</button>
        </section>
      </aside>

      <main className="container">
        {notification && <div className="neon-toast">{notification}</div>}
        <h1 className="neon-text">NEON SUDOKU</h1>
        <div className="stats-bar">
          <span>TIME: {Math.floor(timer/60)}:{(timer%60).toString().padStart(2,'0')}</span>
          <span style={{color: score < 0 ? 'var(--neon-pink)' : 'var(--neon-blue)'}}>SCORE: {score}</span>
        </div>

        <div className="board-wrapper">
          {!gameStarted && <div className="board-overlay">PRESS [N] TO START</div>}
          <div className="board" style={{ filter: (isPaused || !gameStarted || showVictory) ? 'blur(10px)' : 'none' }}>
            {grid.map((row, ri) => row.map((cell, ci) => {
              const isError = solution[ri] && grid[ri][ci] !== 0 && grid[ri][ci] !== solution[ri][ci];
              return (
                <input
                  key={`${ri}-${ci}`}
                  readOnly
                  className={`cell-input 
                    ${initialGrid[ri] && initialGrid[ri][ci] !== 0 ? "fixed" : "user"} 
                    ${selected.r === ri && selected.c === ci ? "active" : ""}
                    ${isError ? "error-pulse" : ""}
                    ${ri === 2 || ri === 5 ? "row-boundary" : ""}`}
                  value={cell || ""}
                  onClick={() => gameStarted && setSelected({ r: ri, c: ci })}
                />
              );
            }))}
          </div>
        </div>

        <div className="buttons-grid">
          <button className="btn" onClick={fetchNewGame}>New Game</button>
          <button className="btn" onClick={getHint}>Hint</button>
          <button className="btn" onClick={() => {
            // PROD LINK: Validate
            axios.post(`${API_BASE}/validate`, { grid }).then(r => {
              if (r.data.result === "Win") {
                setIsGameEnded(true);
                updateBestScore(score, user, timer);
                setShowVictory(true); 
              } else { showToast(`Status: ${r.data.result}`); }
            }).catch(() => showToast("Validation Error"));
          }}>Verify</button>
        </div>
      </main>
    </div>
  );
}

export default App;