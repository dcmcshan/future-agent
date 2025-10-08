#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

console.log('🚀 Starting Future Agent Playwright Tests...\n');

// Check if we're in the right directory
const currentDir = process.cwd();
console.log(`📁 Current directory: ${currentDir}`);

// Check if docs directory exists
const docsPath = path.join(currentDir, 'docs');
const fs = require('fs');
if (!fs.existsSync(docsPath)) {
  console.error('❌ docs directory not found!');
  process.exit(1);
}

console.log('✅ docs directory found');

// Start the development server
console.log('\n🌐 Starting development server...');
const serverProcess = execSync('python -m http.server 3000 --directory docs', { 
  stdio: 'pipe',
  detached: true 
});

// Wait a moment for server to start
setTimeout(() => {
  console.log('✅ Development server started on http://localhost:3000');
  
  // Run a simple test using curl to check if the server is working
  try {
    const response = execSync('curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/', { 
      encoding: 'utf8',
      timeout: 5000 
    });
    
    if (response.trim() === '200') {
      console.log('✅ Server is responding correctly');
      console.log('\n🎯 You can now run manual tests:');
      console.log('   - Homepage: http://localhost:3000/');
      console.log('   - F8 Comparison: http://localhost:3000/f8-comparison.html');
      console.log('\n📝 To run automated tests, install Playwright properly:');
      console.log('   npm install @playwright/test');
      console.log('   npx playwright install');
      console.log('   npx playwright test');
    } else {
      console.log(`❌ Server returned status code: ${response}`);
    }
  } catch (error) {
    console.log('❌ Could not connect to server:', error.message);
  }
}, 2000);

// Keep the process running
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down development server...');
  process.exit(0);
});