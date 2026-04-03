/**
 * Output Capture - captures window output for analysis
 * 
 * Status: LIVE (terminal polling only, no screen capture yet)
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const CACHE_DIR = path.join(__dirname, '../output_cache');

// Ensure cache dir exists
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

module.exports = {
  available: true,
  
  /**
   * Capture output from a running window
   * Method: AppleScript to get Terminal content
   */
  captureWindowOutput: async (window_id, window_data) => {
    return new Promise((resolve, reject) => {
      // For now, return placeholder - real Terminal content requires AppleScript
      // which needs screen recording permissions
      const placeholder = {
        window_id,
        captured_at: new Date().toISOString(),
        method: 'placeholder',
        content: 'Output capture requires screen recording permission\n\nMetadata available:\n' + 
                 JSON.stringify(window_data, null, 2),
        lines: [],
        error: 'Screen recording permission not configured'
      };
      
      const cache_file = path.join(CACHE_DIR, `${window_id}_latest.json`);
      fs.writeFileSync(cache_file, JSON.stringify(placeholder, null, 2));
      
      resolve(placeholder);
    });
  },
  
  /**
   * Get last captured output
   */
  getLastOutput: (window_id) => {
    const cache_file = path.join(CACHE_DIR, `${window_id}_latest.json`);
    if (fs.existsSync(cache_file)) {
      return JSON.parse(fs.readFileSync(cache_file, 'utf8'));
    }
    return null;
  }
};
