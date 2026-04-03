/**
 * Window Analyze Hook - LIVE IMPLEMENTATION
 * 
 * Analyzes window state and suggests next steps
 * NO AUTO-EXECUTION - suggestions only
 */

const output_capture = require('./output_capture');

module.exports = {
  available: true,
  
  /**
   * Analyze window based on metadata and output
   */
  analyzeWindow: async (window_data) => {
    const analysis = {
      window_id: window_data.id,
      analyzed_at: new Date().toISOString(),
      metadata_check: analyzeMetadata(window_data),
      health_check: analyzeHealth(window_data),
      suggested_actions: [],
      warnings: [],
      confidence: 'medium'
    };
    
    // Capture current output
    const output = await output_capture.captureWindowOutput(window_data.id, window_data);
    analysis.output_summary = {
      method: output.method,
      error: output.error || null,
      available: !output.error
    };
    
    // Generate suggestions based on state
    analysis.suggested_actions = generateSuggestions(window_data, analysis);
    
    return analysis;
  },
  
  /**
   * Analyze specific output text
   */
  analyzeOutput: async (output_text) => {
    const lines = output_text.split('\n');
    const errors = lines.filter(l => l.match(/error|fail|exception/i));
    const warnings = lines.filter(l => l.match(/warn|deprecated/i));
    
    return {
      total_lines: lines.length,
      errors_found: errors.length,
      warnings_found: warnings.length,
      error_samples: errors.slice(0, 3),
      warning_samples: warnings.slice(0, 3),
      status: errors.length > 0 ? 'errors_present' : (warnings.length > 0 ? 'warnings_present' : 'clean')
    };
  }
};

/**
 * Analyze metadata completeness
 */
function analyzeMetadata(w) {
  const checks = {
    has_command: !!w.cmd,
    has_env: !!w.env,
    has_reason: !!w.reason,
    has_nta: !!w.nta,
    is_locked: w.locked,
    is_critical: w.criticality === 'critical'
  };
  
  const complete_count = Object.values(checks).filter(v => v).length;
  checks.completeness = Math.round((complete_count / Object.keys(checks).length) * 100);
  
  return checks;
}

/**
 * Analyze health indicators
 */
function analyzeHealth(w) {
  const issues = [];
  
  if (w.health === 'red') {
    issues.push('Window health is RED');
  }
  
  if (w.locked && !w.safe_close) {
    // This is expected for critical windows
  } else if (!w.locked && w.criticality === 'critical') {
    issues.push('Critical window is not locked');
  }
  
  if (w.state !== 'running') {
    issues.push(`Window state is ${w.state}, not running`);
  }
  
  return {
    status: issues.length === 0 ? 'healthy' : 'issues_found',
    issues,
    risk_level: issues.length > 1 ? 'medium' : (issues.length === 1 ? 'low' : 'none')
  };
}

/**
 * Generate actionable suggestions
 */
function generateSuggestions(w, analysis) {
  const suggestions = [];
  
  // Health-based suggestions
  if (w.health === 'red') {
    suggestions.push({
      priority: 'high',
      action: 'investigate_health',
      description: 'Window health is RED - investigate errors or restart',
      safe_to_auto: false
    });
  }
  
  if (w.health === 'yellow' && !w.locked) {
    suggestions.push({
      priority: 'low',
      action: 'consider_lock',
      description: 'Consider locking this window if it should persist',
      safe_to_auto: false
    });
  }
  
  // Type-based suggestions
  if (w.type === 'watcher' && w.state === 'running') {
    suggestions.push({
      priority: 'low',
      action: 'check_logs',
      description: 'Watcher is running - check for new alerts',
      safe_to_auto: true
    });
  }
  
  if (w.type === 'service' && w.criticality === 'critical') {
    suggestions.push({
      priority: 'medium',
      action: 'verify_endpoints',
      description: 'Critical service - verify endpoints are responding',
      safe_to_auto: true
    });
  }
  
  // NTA-based suggestions
  if (w.nta) {
    suggestions.push({
      priority: 'medium',
      action: 'check_nta_task',
      description: `Check NTA task status: ${w.nta}`,
      safe_to_auto: true,
      command: `missionctl nta_task ${w.nta}`
    });
  }
  
  // Memory-based suggestions
  if (w.memory?.last_error) {
    suggestions.push({
      priority: 'high',
      action: 'review_last_error',
      description: `Previous error recorded: ${w.memory.last_error}`,
      safe_to_auto: false
    });
  }
  
  // Default suggestion if no specific ones
  if (suggestions.length === 0) {
    suggestions.push({
      priority: 'low',
      action: 'monitor',
      description: 'Window appears healthy - continue monitoring',
      safe_to_auto: true
    });
  }
  
  return suggestions;
}
