// global-teardown.js
async function globalTeardown(config) {
  console.log('🧹 Starting global teardown for MELD Visualizer tests...');
  
  // Clean up any test artifacts
  const fs = require('fs').promises;
  const path = require('path');
  
  try {
    // Clean up temporary test files
    const tempDir = path.join(__dirname, '../reports/temp');
    try {
      await fs.rmdir(tempDir, { recursive: true });
      console.log('🗑️ Cleaned up temporary test files');
    } catch (error) {
      // Directory might not exist, which is fine
    }
    
    // Log test completion
    console.log('📊 Test execution completed');
    console.log('📁 Test reports available in tests/reports/');
    
  } catch (error) {
    console.error('⚠️ Warning during teardown:', error.message);
  }
  
  console.log('✨ Global teardown complete');
}

module.exports = globalTeardown;