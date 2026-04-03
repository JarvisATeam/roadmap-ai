/**
 * Window Watch Hook - LIVE IMPLEMENTATION
 * 
 * Monitors selected window for changes and triggers analysis
 */

const fs = require("fs");
const crypto = require("crypto");
const { execSync } = require("child_process");
const path = require("path");

const STATE_FILE = path.join(__dirname, "../watch_state.json");

module.exports = {
  available: true,
  
  startWatch: async (window_id, interval = 3000) => {
    const state = readState();
    state.active_window = window_id;
    state.watching = true;
    state.updated_at = new Date().toISOString();
    writeState(state);
    return { ok: true, window_id, interval };
  },
  
  stopWatch: async () => {
    const state = readState();
    state.watching = false;
    state.updated_at = new Date().toISOString();
    writeState(state);
    return { ok: true };
  },
  
  getWatchStatus: async (window_id) => {
    const state = readState();
    return {
      watching: state.watching,
      active_window: state.active_window,
      last_hash: state.last_hash,
      updated_at: state.updated_at
    };
  }
};

function readState() {
  if (!fs.existsSync(STATE_FILE)) {
    return {
      active_window: null,
      last_hash: null,
      last_output: null,
      watching: false,
      updated_at: null
    };
  }
  return JSON.parse(fs.readFileSync(STATE_FILE, "utf-8"));
}

function writeState(s) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(s, null, 2));
}

function hash(str) {
  return crypto.createHash("sha1").update(str).digest("hex");
}

function getOutput() {
  try {
    return execSync("~/.ginie/mission-control/scripts/missionctl status", { timeout: 5000, shell: "/bin/zsh" }).toString();
  } catch {
    return "";
  }
}

function loop() {
  const s = readState();
  if (!s.watching || !s.active_window) return;

  const out = getOutput();
  const h = hash(out);

  if (h !== s.last_hash) {
    console.log(`[${new Date().toISOString()}] WATCH: change detected for ${s.active_window}`);

    s.last_hash = h;
    s.last_output = out.substring(0, 500); // Store first 500 chars
    s.updated_at = new Date().toISOString();
    writeState(s);

    // Trigger analysis via API
    try {
      execSync(`curl -s -X POST http://localhost:3000/windows/${s.active_window}/analyze`, { timeout: 3000 });
      console.log(`[${new Date().toISOString()}] WATCH: analysis triggered`);
    } catch (err) {
      console.error(`[${new Date().toISOString()}] WATCH: analysis failed -`, err.message);
    }
  }
}

// Run loop if executed directly
if (require.main === module) {
  console.log(`[${new Date().toISOString()}] WATCH LOOP STARTED`);
  setInterval(loop, 3000);
}
