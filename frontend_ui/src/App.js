import React, { useState, useEffect, useCallback } from 'react';
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
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [darkMode, setDarkMode] = useState(true);
  const [hintedCell, setHintedCell] = useState(null);
  const [cheatLoading, setCheatLoading] = useState(false);
  const [resultModal, setResultModal] = useState({ open: false, type: '', message: '', score: 0 });
  // Timer increments while a game is active and not paused or ended
  useEffect(() => {
    let t = null;
    if (gameStarted && !isPaused && !isGameEnded && !showVictory) {
      t = setInterval(() => setTimer(prev => prev + 1), 1000);
    }
    return () => { if (t) clearInterval(t); };
  }, [gameStarted, isPaused, isGameEnded, showVictory]);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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
          return [...prev, { name: user.trim(), best: 0 }].sort((a,b) => b.best - a.best);
        }
        return prev;
      });
    } else showToast("ID too short!");
  };

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
      setGameStarted(true); 
      showToast("System Online");
    } catch (err) { showToast("Backend Error"); }
  }, [difficulty, isLoggedIn]);

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
      // validate shape
      if (!Array.isArray(solved) || solved.length !== 9) {
        showToast('Invalid solution');
        setCheatLoading(false);
        return;
      }
      setGrid(solved);
      setInitialGrid(solved.map(row => Array.isArray(row) ? [...row] : []));
      setSolution(solved);
      setScore(s => s - 500); // allow negative totals after full cheat
      setShowVictory(true);
      setIsGameEnded(true);
      // show result modal with final score
      setScore(prev => {
        const ns = prev - 500;
        setResultModal({ open: true, type: 'win', message: 'Solved by AI', score: ns });
        return ns;
      });
      showToast("Solved by AI");
    } catch (err) { showToast("Cheat failed"); }
    finally { setCheatLoading(false); }
  };

  const handleInput = (row, col, value) => {
    if (!gameStarted || isPaused || isGameEnded || initialGrid[row][col] !== 0) return;
    const num = parseInt(value.toString().slice(-1));
    if (isNaN(num) || num === 0) return;
    const isCorrect = num === solution[row][col];
    const newGrid = [...grid];
    newGrid[row][col] = num;
    setGrid(newGrid);
    if (isCorrect) { setScore(s => s + 100); showToast("Correct!"); }
    else { setScore(s => s - 25); showToast("Mistake!"); }
  };

  const getHint = useCallback(async () => {
    if (!gameStarted || isPaused || grid[selected.r][selected.c] !== 0) return;
    try {
      const res = await axios.post(`${API_BASE}/hint?row=${selected.r}&col=${selected.c}`, { grid });
      const n = [...grid];
      n[selected.r][selected.c] = res.data.value;
      setHintedCell(`${selected.r}-${selected.c}`);
      setGrid(n); setScore(s => s - 50);
      setTimeout(() => setHintedCell(null), 1500);
    } catch (err) { showToast("Hint Error"); }
  }, [selected, grid, gameStarted, isPaused]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isLoggedIn || !gameStarted || isPaused) return;
      const { r, c } = selected;
      if (e.key === 'ArrowUp') setSelected({ r: Math.max(0, r - 1), c });
      if (e.key === 'ArrowDown') setSelected({ r: Math.min(8, r + 1), c });
      if (e.key === 'ArrowLeft') setSelected({ r, c: Math.max(0, c - 1) });
      if (e.key === 'ArrowRight') setSelected({ r, c: Math.min(8, c + 1) });
      if (/[1-9]/.test(e.key)) handleInput(r, c, e.key);
      if (e.key.toLowerCase() === 'h') getHint();
      if (e.key.toLowerCase() === 'n') fetchNewGame();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selected, gameStarted, isLoggedIn, isPaused, fetchNewGame, getHint]);

  return (
    <div className={`app-shell ${!darkMode ? 'light-mode' : ''}`}>
      {!isLoggedIn && (
        <div className="login-overlay">
          <form className="login-card" onSubmit={handleLogin}>
            <h1 className="pink">NEON LOGIN</h1>
            <input className="login-input" value={user} onChange={e=>setUser(e.target.value)} placeholder="User ID..." />
            <br/><button className="btn" type="submit">ENTER SYSTEM</button>
          </form>
        </div>
      )}

          {showVictory && (
        <div className="victory-overlay">
          <div className="victory-card">
            <h1 className="pink">VICTORY</h1>
            <p>SCORE: {score}</p>
            <button className="btn" onClick={fetchNewGame}>NEW MISSION</button>
          </div>
        </div>
      )}

      {resultModal.open && (
        <div className="result-overlay">
          <div className="result-card">
            <h1 className="pink">{resultModal.type === 'win' ? 'VICTORY' : 'GAME OVER'}</h1>
            <p>SCORE: {resultModal.score}</p>
            <p>{resultModal.message}</p>
            <div style={{marginTop:12}}>
              <button className="btn" onClick={() => setResultModal({ ...resultModal, open: false })}>CLOSE</button>
            </div>
          </div>
        </div>
      )}

      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>ID: {user}</h2>
          <div className="theme-toggle">
            <label className="switch">
              <input type="checkbox" checked={!darkMode} onChange={()=>setDarkMode(!darkMode)} />
              <span className="slider"></span>
            </label>
          </div>
        </div>
        <section>
          <h3>DIFFICULTY</h3>
          <select className="diff-select" value={difficulty} onChange={e=>setDifficulty(parseInt(e.target.value))}>
            <option value={15}>Beginner (15)</option>
            <option value={30}>Easy (30)</option>
            <option value={45}>Intermediate (45)</option>
            <option value={55}>Hard (55)</option>
            <option value={65}>Extreme (65)</option>
          </select>
        </section>

        <section className="leaderboard">
          <h3>LEADERBOARD</h3>
          <div className="leader-list">
            {leaderboard.slice(0,5).map((p, i) => (
              <div key={p.name} className="leader-row">{i+1}. {p.name} — {p.best}</div>
            ))}
          </div>
        </section>

        <section className="instructions">
          <h3>INSTRUCTIONS</h3>
          <div className="instr-text">
            <div>- Enter numbers 1-9 into empty cells.</div>
            <div>- Correct entry: +100</div>
            <div>- Mistake: -25</div>
            <div>- Hint: -50</div>
            <div>- Cheat (solve): -500</div>
          </div>
          <button className="btn small cheat" onClick={handleCheat}>{cheatLoading ? 'AI SOLVE ALL...' : 'AI SOLVE ALL'}</button>
        </section>

        <button className="btn logout-btn" onClick={()=>setIsLoggedIn(false)}>LOGOUT</button>
      </aside>

      <main className="container">
        {notification && <div className="neon-toast">{notification}</div>}
        <h1 className="neon-text">NEON SUDOKU</h1>
        <div className="stats-bar">
          <span>TIME: {Math.floor(timer/60)}:{(timer%60).toString().padStart(2,'0')}</span>
          <span>SCORE: {score}</span>
        </div>
        <div className="board-wrapper">
          <div className="board">
            {grid.map((row, ri) => row.map((cell, ci) => (
              <input
                key={`${ri}-${ci}`}
                type="text"
                inputMode="numeric"
                className={`cell-input ${initialGrid[ri][ci]!==0?'fixed':'user'} ${selected.r===ri&&selected.c===ci?'active':''} ${hintedCell===`${ri}-${ci}`?'hint-pulse':''} ${ri===2||ri===5?'row-boundary':''}`}
                value={cell || ""}
                onFocus={() => setSelected({ r: ri, c: ci })}
                onChange={(e) => handleInput(ri, ci, e.target.value)}
                readOnly={initialGrid[ri][ci] !== 0}
              />
            )))}
          </div>
        </div>
        <div className="buttons-grid">
          <button className="btn" onClick={fetchNewGame}>NEW GAME</button>
          <button className="btn" onClick={() => setIsPaused(!isPaused)}>{isPaused?"RESUME":"PAUSE"}</button>
          <button className="btn" onClick={getHint}>AI HINT</button>
          <button className="btn" onClick={() => {
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