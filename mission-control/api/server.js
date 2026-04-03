const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;
const ACTIONS_FILE = path.join(__dirname, '../actions.json');
const PROJECTS_FILE = path.join(__dirname, '../projects.json');
const REGISTRY_FILE = path.join(process.env.HOME, '.ginie/mission-control/registry.json');
const MEMORY_FILE = path.join(__dirname, '../window_memory.json');
const DASHBOARD_DIR = path.join(__dirname, '../dashboard');
const HOOKS_DIR = path.join(__dirname, '../hooks');

app.use(express.json());
app.use(express.static(DASHBOARD_DIR));

let actions = {}, projects = {}, registry = {}, memory = {};

// Load analyze hook with correct path
let window_analyze = null;
try {
  window_analyze = require(path.join(HOOKS_DIR, 'window_analyze.js'));
  console.log('window_analyze hook loaded successfully');
} catch (err) {
  console.warn('window_analyze hook not available:', err.message);
}

function loadRegistry() {
  try {
    actions = JSON.parse(fs.readFileSync(ACTIONS_FILE, 'utf8'));
    projects = JSON.parse(fs.readFileSync(PROJECTS_FILE, 'utf8'));
    if (fs.existsSync(REGISTRY_FILE)) registry = JSON.parse(fs.readFileSync(REGISTRY_FILE, 'utf8'));
    if (fs.existsSync(MEMORY_FILE)) memory = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
  } catch (err) { console.error('Registry load error:', err.message); }
}

function saveMemory() {
  try { fs.writeFileSync(MEMORY_FILE, JSON.stringify(memory, null, 2)); }
  catch (err) { console.error('Memory save error:', err.message); }
}

function deriveHealth(w, mem) {
  if (mem.last_error) return 'red';
  if (w.state === 'running' && w.locked) return 'green';
  if (w.locked) return 'yellow';
  if (w.state === 'running') return 'yellow';
  return 'unknown';
}

function mapWindow(w) {
  const mem = memory[w.id] || {};
  const health = deriveHealth(w, mem);
  return {
    id: w.id,
    project: w.project || null,
    title: w.title || null,
    cmd: w.start_cmd || null,
    cmd_source: w.start_cmd ? 'live' : 'unknown',
    type: w.type || null,
    env: w.environment || null,
    env_source: w.environment ? 'live' : 'unknown',
    cwd: w.cwd || null,
    criticality: w.criticality || null,
    locked: w.locked || false,
    safe_close: w.safe_to_close === 'yes',
    safe_source: w.safe_to_close ? 'live' : 'unknown',
    reason: w.why_open || null,
    reason_source: w.why_open ? 'live' : 'unknown',
    state: w.state || null,
    nta: w.nta_tasks && w.nta_tasks.length > 0 ? w.nta_tasks.join(', ') : null,
    registered_at: w.registered_at || null,
    health,
    health_source: 'derived',
    memory: mem
  };
}

loadRegistry();

app.get('/', (req, res) => res.sendFile(path.join(DASHBOARD_DIR, 'index.html')));
app.get('/actions', (req, res) => res.json(actions));
app.get('/projects', (req, res) => res.json(projects));

app.get('/windows', (req, res) => {
  const windows = (registry.windows || []).map(mapWindow);
  const byProject = {};
  windows.forEach(w => { 
    const proj = w.project || 'unknown';
    byProject[proj] = byProject[proj] || []; 
    byProject[proj].push(w); 
  });
  res.json({ windows, byProject, total: windows.length });
});

app.get('/windows/:id', (req, res) => {
  const win = (registry.windows || []).find(w => w.id === req.params.id);
  if (!win) return res.status(404).json({ error: 'Window not found' });
  res.json(mapWindow(win));
});

app.post('/windows/:id/analyze', async (req, res) => {
  const win = (registry.windows || []).find(w => w.id === req.params.id);
  if (!win) return res.status(404).json({ error: 'Window not found' });
  
  if (!window_analyze || !window_analyze.available) {
    return res.status(503).json({ error: 'Analysis engine not available' });
  }
  
  try {
    const mapped = mapWindow(win);
    const analysis = await window_analyze.analyzeWindow(mapped);
    res.json({ ok: true, analysis });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

app.get('/window-memory/:id', (req, res) => {
  const mem = memory[req.params.id];
  if (!mem) return res.status(404).json({ error: 'Memory not found' });
  res.json(mem);
});

app.post('/window-memory/:id', (req, res) => {
  const id = req.params.id;
  if (!memory[id]) memory[id] = { window_id: id };
  memory[id] = { ...memory[id], ...req.body, updated_at: new Date().toISOString() };
  saveMemory();
  res.json({ ok: true, memory: memory[id] });
});

app.post('/watch/start', (req, res) => {
  const { window_id } = req.body;
  if (!window_id) return res.status(400).json({ ok: false, error: 'Invalid window_id' });
  if (!memory[window_id]) memory[window_id] = { window_id };
  memory[window_id].watch_active = true;
  memory[window_id].updated_at = new Date().toISOString();
  saveMemory();
  res.json({ ok: true, message: 'Watch registered', window_id });
});

app.post('/watch/stop', (req, res) => {
  const { window_id } = req.body;
  if (!window_id || !memory[window_id]) return res.status(400).json({ ok: false, error: 'Invalid window_id' });
  memory[window_id].watch_active = false;
  memory[window_id].updated_at = new Date().toISOString();
  saveMemory();
  res.json({ ok: true, message: 'Watch stopped', window_id });
});

app.get('/status', (req, res) => {
  const status = { cloudbot: false, heartbeat_ok: false, windows: 0, locked: 0 };
  if (registry.windows) { status.windows = registry.windows.length; status.locked = registry.windows.filter(w => w.locked).length; }
  exec('ps aux | grep cloudbot.main | grep -v grep', { shell: '/bin/zsh' }, (e, out) => {
    status.cloudbot = out.trim().length > 0;
    exec('tail -1 ~/.ginie/heartbeat.log', { shell: '/bin/zsh' }, (e2, out2) => {
      status.heartbeat_ok = out2.includes('Health=GREEN');
      res.json(status);
    });
  });
});

app.post('/run', (req, res) => {
  const { action_id } = req.body;
  if (!action_id || !actions[action_id]) return res.status(400).json({ ok: false, error: 'Invalid action_id' });
  const action = actions[action_id];
  if (action.enabled === false) return res.status(400).json({ ok: false, error: 'Action not enabled' });
  exec(action.cmd, { timeout: 10000, shell: '/bin/zsh', env: { ...process.env, HOME: process.env.HOME } }, (error, stdout, stderr) => {
    res.json({ ok: !error, action_id, cmd: action.cmd, output: (stdout + stderr).split('\n').slice(-20).join('\n'), exit_code: error ? 1 : 0 });
  });
});


// WATCH CONTROL ENDPOINTS
let window_watch = null;
try {
  window_watch = require(path.join(HOOKS_DIR, 'window_watch.js'));
  console.log('window_watch hook loaded successfully');
} catch (err) {
  console.warn('window_watch hook not available:', err.message);
}

app.post('/watch/select', async (req, res) => {
  const { window_id } = req.body;
  if (!window_id) return res.status(400).json({ ok: false, error: 'Invalid window_id' });
  
  if (window_watch && window_watch.available) {
    const result = await window_watch.startWatch(window_id);
    res.json(result);
  } else {
    res.status(503).json({ ok: false, error: 'Watch engine not available' });
  }
});

app.post('/watch/deselect', async (req, res) => {
  if (window_watch && window_watch.available) {
    const result = await window_watch.stopWatch();
    res.json(result);
  } else {
    res.status(503).json({ ok: false, error: 'Watch engine not available' });
  }
});

app.get('/watch/status', async (req, res) => {
  if (window_watch && window_watch.available) {
    const status = await window_watch.getWatchStatus();
    res.json(status);
  } else {
    res.json({ watching: false, available: false });
  }
});


app.listen(PORT, () => console.log('Mission Control API v2.3 on http://localhost:' + PORT));
