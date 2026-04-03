/**
 * Screen Watch Hook - NOT IMPLEMENTED
 * 
 * Future integration point for screen capture + AI analysis
 * 
 * Interface:
 * - watchCurrentWindow() → captures screenshot, sends to AI
 * - analyzeContext() → returns project context
 * - suggestAction() → returns recommended action_id
 * 
 * Status: STUB ONLY
 */

module.exports = {
  available: false,
  
  watchCurrentWindow: async () => {
    throw new Error('Screen watch not implemented');
  },
  
  analyzeContext: async () => {
    throw new Error('Context analysis not implemented');
  },
  
  suggestAction: async () => {
    throw new Error('Action suggestion not implemented');
  }
};
