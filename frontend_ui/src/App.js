import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = "https://ushan256-sudoku.hf.space";

function App() {
  const [grid, setGrid] = useState(Array(9).fill(0).map(() => Array(9).fill(0)));
  const [initialGrid, setInitialGrid] = useState(Array(9).fill(0).map(() => Array(9).fill(0)));
  const [solution, setSolution] = useState([]);
  const [selected, setSelected] = useState({ r: 0, c: 0 });
  const [timer, setTimer] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isGameEnded, setIsGameEnded] = useState(false);
  const [gameStarted, setGameStarted] = useState(false);
  const [notification, setNotification] = useState("");
  const [score, setScore] = useState(0);
  const [difficulty, setDifficulty] = useState(30);
  const [user, setUser] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showVictory, setShowVictory] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [hintedCell, setHintedCell] = useState(null);
  const [cheatLoading, setCheatLoading] = useState(false);
  const [resultModal, setResultModal] = useState({ open: false, type: '', message: '', score: 0 });

  // Use refs to avoid stale closure issues in hooks
  const scoreRef = useRef(score);
  const userRef = useRef(user);
  useEffect(() => { scoreRef.current = score; }, [score]);
  useEffect(() => { userRef.current = user; }, [user]);

  // Timer
  useEffect(() => {
    let t = null;
    if (gameStarted && !isPaused && !isGameEnded && !showVictory) {
      t = setInterval(() => setTimer(prev => prev + 1), 1000);
    }
    return () => { if (t) clearInterval(t); };
  }, [gameStarted, isPaused, isGameEnded, showVictory]);

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
    if (user.trim().length > 2) {
      setIsLoggedIn(true);
      setLeaderboard(prev => {
        if (!prev.find(p => p.name === user.trim())) {
          return [...prev, { name: user.trim(), best: 0 }].sort((a, b) => b.best - a.best);
        }
        return prev;
      });
    } else showToast("ID too short!");
  };

  // FIX: resultModal.open added to dependency array
  const fetchNewGame = useCallback(async () => {
    if (!isLoggedIn) return;
    if (resultModal.open) return showToast('Dismiss result to start a new game');
    try {
      const res = await axios.get(`${API_BASE}/generate/${difficulty}`);
      const solRes = await axios.post(`${API_BASE}/solve`, { grid: res.data.grid });
      setSolution(solRes.data.solution);
      setGrid(res.data.grid);
      setInitialGrid(res.data.grid.map(row => [...row]));
      setTimer(0); setScore(0);
      setIsPaused(false); setIsGameEnded(false); setShowVictory(false);
      setResultModal({ open: false, type: '', message: '', score: 0 });
      setGameStarted(true);
      showToast("System Online");
    } catch (err) { showToast("Backend Error"); }
  }, [difficulty, isLoggedIn, resultModal.open]);

  const handleCheat = async () => {
    if (!isLoggedIn || !gameStarted) return showToast("Start a game first");
    if (cheatLoading) return;
    setCheatLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/solve`, { grid });
      if (!res || !res.data || !res.data.solution) {
        showToast('No solution returned');
        setCheatLoading(false);
        return;
      }
      const solved = res.data.solution;
      if (!Array.isArray(solved) || solved.length !== 9) {
        showToast('Invalid solution');
        setCheatLoading(false);
        return;
      }
      setGrid(solved);
      setInitialGrid(solved.map(row => Array.isArray(row) ? [...row] : []));
      setSolution(solved);
      setScore(prev => {
        const ns = prev - 500;
        setResultModal({ open: true, type: 'win', message: 'Solved by AI', score: ns });
        return ns;
      });
      setShowVictory(true);
      setIsGameEnded(true);
      showToast("Solved by AI");
    } catch (err) { showToast("Cheat failed"); }
    finally { setCheatLoading(false); }
  };

  // FIX: Extracted applyValidationResult into useCallback with stable deps
  const applyValidationResult = useCallback((resultText) => {
    if (resultText === 'Win') {
      setIsGameEnded(true);
      setShowVictory(true);
      setLeaderboard(prev => {
        const currentUser = userRef.current;
        const currentScore = scoreRef.current;
        if (!currentUser) return prev;
        const exists = prev.find(p => p.name === currentUser.trim());
        if (exists) {
          return prev.map(p => p.name === currentUser.trim()
            ? { ...p, best: Math.max(p.best, currentScore) }
            : p
          ).sort((a, b) => b.best - a.best);
        }
        return [...prev, { name: currentUser.trim(), best: currentScore }].sort((a, b) => b.best - a.best);
      });
      setResultModal(prev => ({ open: true, type: 'win', message: 'You solved the puzzle', score: scoreRef.current }));
    } else {
      setIsGameEnded(true);
      setResultModal({ open: true, type: 'lose', message: resultText || 'Game ended', score: scoreRef.current });
    }
  }, []); // stable — uses refs for score and user

  // FIX: applyValidationResult is now stable so safe to include
  useEffect(() => {
    if (!gameStarted || isGameEnded) return;
    const flat = grid.flat();
    const filled = flat.every(v => v !== 0 && v !== null && v !== undefined);
    if (filled) {
      axios.post(`${API_BASE}/validate`, { grid }).then(r => {
        const res = r.data && r.data.result ? r.data.result : 'Invalid';
        applyValidationResult(res);
      }).catch(() => {
        applyValidationResult('Validation failed');
      });
    }
  }, [grid, gameStarted, isGameEnded, applyValidationResult]);

  // FIX: handleInput extracted into useCallback so it's stable for the keydown useEffect
  const handleInput = useCallback((row, col, value, currentGrid, currentInitialGrid, currentSolution) => {
    if (!gameStarted || isPaused || isGameEnded || currentInitialGrid[row][col] !== 0) return;
    const num = parseInt(value.toString().slice(-1));
    if (isNaN(num) || num === 0) return;
    const isCorrect = num === currentSolution[row][col];
    const newGrid = currentGrid.map(r => [...r]);
    newGrid[row][col] = num;
    setGrid(newGrid);
    if (isCorrect) { setScore(s => s + 100); showToast("Correct!"); }
    else { setScore(s => s - 25); showToast("Mistake!"); }
  }, [gameStarted, isPaused, isGameEnded]);

  const getHint = useCallback(async () => {
    if (!gameStarted || isPaused || grid[selected.r][selected.c] !== 0) return;
    try {
      const res = await axios.post(`${API_BASE}/hint?row=${selected.r}&col=${selected.c}`, { grid });
      const n = grid.map(r => [...r]);
      n[selected.r][selected.c] = res.data.value;
      setHintedCell(`${selected.r}-${selected.c}`);
      setGrid(n);
      setScore(s => s - 50);
      setTimeout(() => setHintedCell(null), 1500);
    } catch (err) { showToast("Hint Error"); }
  }, [selected, grid, gameStarted, isPaused]);

  // FIX: handleInput is now stable (useCallback), safe to include
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isLoggedIn || !gameStarted || isPaused) return;
      const { r, c } = selected;
      if (e.key === 'ArrowUp') setSelected({ r: Math.max(0, r - 1), c });
      if (e.key === 'ArrowDown') setSelected({ r: Math.min(8, r + 1), c });
      if (e.key === 'ArrowLeft') setSelected({ r, c: Math.max(0, c - 1) });
      if (e.key === 'ArrowRight') setSelected({ r, c: Math.min(8, c + 1) });
      if (/[1-9]/.test(e.key)) {
        setGrid(currentGrid => {
          setInitialGrid(currentInitialGrid => {
            setSolution(currentSolution => {
              handleInput(r, c, e.key, currentGrid, currentInitialGrid, currentSolution);
              return currentSolution;
            });
            return currentInitialGrid;
          });
          return currentGrid;
        });
      }
      if (e.key.toLowerCase() === 'h') getHint();
      if (e.key.toLowerCase() === 'n') fetchNewGame();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selected, gameStarted, isLoggedIn, isPaused, fetchNewGame, getHint, handleInput]);

  return (
    <div className={`app-shell ${!darkMode ? 'light-mode' : ''}`}>
      {!isLoggedIn && (
        <div className="login-overlay">
          <form className="login-card" onSubmit={handleLogin}>
            <h1 className="neon-title">NEON LOGIN</h1>
            <input className="login-input" value={user} onChange={e => setUser(e.target.value)} placeholder="User ID..." />
            <br />
            <button className="btn btn-primary" type="submit">ENTER SYSTEM</button>
          </form>
        </div>
      )}

      {showVictory && (
        <div className="victory-overlay">
          <div className="victory-card">
            <h1 className="neon-title">VICTORY</h1>
            <p>SCORE: {score}</p>
            <button className="btn btn-primary" onClick={fetchNewGame}>NEW MISSION</button>
          </div>
        </div>
      )}

      {resultModal.open && (
        <div className="result-overlay">
          <div className="result-card">
            <h1 className="neon-title">{resultModal.type === 'win' ? 'VICTORY' : 'GAME OVER'}</h1>
            <p>SCORE: {resultModal.score}</p>
            <p>{resultModal.message}</p>
            <div style={{ marginTop: 12 }}>
              <button className="btn btn-primary" onClick={() => setResultModal({ ...resultModal, open: false })}>CLOSE</button>
            </div>
          </div>
        </div>
      )}

      <aside className="sidebar">
        <div className="sidebar-header">
          <h2 className="sidebar-user">ID: {user}</h2>
          <div className="theme-toggle">
            <span>DARK</span>
            <label className="switch">
              <input type="checkbox" checked={!darkMode} onChange={() => setDarkMode(!darkMode)} />
              <span className="slider"></span>
            </label>
            <span>LIGHT</span>
          </div>
        </div>

        <section className="sidebar-section">
          <h3 className="sidebar-heading">DIFFICULTY</h3>
          <select className="diff-select" value={difficulty} onChange={e => setDifficulty(parseInt(e.target.value))}>
            <option value={15}>Beginner (15)</option>
            <option value={30}>Easy (30)</option>
            <option value={45}>Intermediate (45)</option>
            <option value={55}>Hard (55)</option>
            <option value={65}>Extreme (65)</option>
          </select>
        </section>

        <section className="sidebar-section leaderboard">
          <h3 className="sidebar-heading">LEADERBOARD</h3>
          <div className="leader-list">
            {leaderboard.slice(0, 5).map((p, i) => (
              <div key={p.name} className="leader-row">{i + 1}. {p.name} — {p.best}</div>
            ))}
          </div>
        </section>

        <section className="sidebar-section instructions">
          <h3 className="sidebar-heading">INSTRUCTIONS</h3>
          <div className="instr-text">
            <div>— Enter numbers 1–9 into empty cells</div>
            <div>— Correct entry: +100 pts</div>
            <div>— Mistake: −25 pts</div>
            <div>— Hint: −50 pts</div>
            <div>— AI Solve: −500 pts</div>
          </div>
          <button className="btn btn-cheat" onClick={handleCheat}>
            {cheatLoading ? 'AI SOLVING...' : 'AI SOLVE ALL'}
          </button>
        </section>

        <button className="btn btn-logout" onClick={() => setIsLoggedIn(false)}>LOGOUT</button>
      </aside>

      <main className="container">
        {notification && <div className="neon-toast">{notification}</div>}
        <h1 className="neon-text">NEON SUDOKU</h1>

        <div className="stats-bar">
          <span className="stat-chip">⏱ {Math.floor(timer / 60)}:{(timer % 60).toString().padStart(2, '0')}</span>
          <span className="stat-chip">◈ {score} PTS</span>
        </div>

        <div className="board-wrapper">
          <div className="board">
            {grid.map((row, ri) =>
              row.map((cell, ci) => {
                // Determine 3x3 box for alternating box colours
                const boxRow = Math.floor(ri / 3);
                const boxCol = Math.floor(ci / 3);
                const isAltBox = (boxRow + boxCol) % 2 === 1;
                const isFixed = initialGrid[ri][ci] !== 0;
                const isSelected = selected.r === ri && selected.c === ci;
                const isHinted = hintedCell === `${ri}-${ci}`;
                const isSameRow = selected.r === ri && !isSelected;
                const isSameCol = selected.c === ci && !isSelected;

                let cellClass = 'cell-input';
                if (isFixed) cellClass += ' fixed';
                else cellClass += ' user';
                if (isSelected) cellClass += ' active';
                if (isHinted) cellClass += ' hint-pulse';
                if (isAltBox && !isSelected) cellClass += ' alt-box';
                if (isSameRow || isSameCol) cellClass += ' highlight-cross';
                // Box borders
                if (ci === 2 || ci === 5) cellClass += ' border-right-box';
                if (ri === 2 || ri === 5) cellClass += ' border-bottom-box';

                return (
                  <input
                    key={`${ri}-${ci}`}
                    type="text"
                    inputMode="numeric"
                    className={cellClass}
                    value={cell || ""}
                    onFocus={() => setSelected({ r: ri, c: ci })}
                    onChange={(e) => {
                      setGrid(currentGrid => {
                        setInitialGrid(currentInitialGrid => {
                          setSolution(currentSolution => {
                            handleInput(ri, ci, e.target.value, currentGrid, currentInitialGrid, currentSolution);
                            return currentSolution;
                          });
                          return currentInitialGrid;
                        });
                        return currentGrid;
                      });
                    }}
                    readOnly={isFixed}
                  />
                );
              })
            )}
          </div>
        </div>

        <div className="buttons-grid">
          <button className="btn btn-action" onClick={fetchNewGame}>NEW GAME</button>
          <button className="btn btn-action" onClick={() => setIsPaused(!isPaused)}>
            {isPaused ? "RESUME" : "PAUSE"}
          </button>
          <button className="btn btn-action" onClick={getHint}>AI HINT</button>
          <button className="btn btn-action" onClick={() => {
            axios.post(`${API_BASE}/validate`, { grid }).then(r => {
              if (r.data.result === "Win") { setShowVictory(true); setIsGameEnded(true); }
              else showToast(r.data.result);
            });
          }}>VERIFY</button>
        </div>
      </main>
    </div>
  );
}

export default App;
