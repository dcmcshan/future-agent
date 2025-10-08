#!/usr/bin/env node

const http = require('http');
const https = require('https');
const { URL } = require('url');

console.log('🧪 Future Agent Manual Testing Suite\n');

const tests = [
  {
    name: 'Homepage Load Test',
    url: 'http://localhost:3000/',
    checks: ['h1', 'stats-grid', 'features', 'cta-section']
  },
  {
    name: 'F8 Comparison Page Load Test',
    url: 'http://localhost:3000/f8-comparison.html',
    checks: ['h1', 'stats-grid', 'filters', 'comparisonResults']
  }
];

function makeRequest(url) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const client = parsedUrl.protocol === 'https:' ? https : http;
    
    const req = client.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, data }));
    });
    
    req.on('error', reject);
    req.setTimeout(10000, () => reject(new Error('Request timeout')));
  });
}

function checkContent(html, checks) {
  const results = [];
  
  for (const check of checks) {
    let found = false;
    
    // Check for class-based selectors
    const classRegex = new RegExp(`<[^>]*class="[^"]*${check}[^"]*"`, 'i');
    if (classRegex.test(html)) {
      found = true;
    }
    
    // Check for ID-based selectors
    const idRegex = new RegExp(`<[^>]*id="${check}"`, 'i');
    if (idRegex.test(html)) {
      found = true;
    }
    
    // Check for tag-based selectors
    const tagRegex = new RegExp(`<${check}[^>]*>`, 'i');
    if (tagRegex.test(html)) {
      found = true;
    }
    
    results.push({ check, found });
  }
  
  return results;
}

async function runTest(test) {
  console.log(`🔍 Testing: ${test.name}`);
  console.log(`   URL: ${test.url}`);
  
  try {
    const { status, data } = await makeRequest(test.url);
    
    if (status === 200) {
      console.log(`   ✅ Status: ${status}`);
      
      const results = checkContent(data, test.checks);
      let allPassed = true;
      
      for (const result of results) {
        if (result.found) {
          console.log(`   ✅ Found: ${result.check}`);
        } else {
          console.log(`   ❌ Missing: ${result.check}`);
          allPassed = false;
        }
      }
      
      if (allPassed) {
        console.log(`   🎉 ${test.name} PASSED\n`);
        return true;
      } else {
        console.log(`   ⚠️  ${test.name} PARTIAL PASS\n`);
        return false;
      }
    } else {
      console.log(`   ❌ Status: ${status}\n`);
      return false;
    }
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}\n`);
    return false;
  }
}

async function runAllTests() {
  console.log('🚀 Starting manual tests...\n');
  
  let passed = 0;
  let total = tests.length;
  
  for (const test of tests) {
    const result = await runTest(test);
    if (result) passed++;
  }
  
  console.log('📊 Test Results:');
  console.log(`   Passed: ${passed}/${total}`);
  console.log(`   Success Rate: ${Math.round((passed / total) * 100)}%`);
  
  if (passed === total) {
    console.log('\n🎉 All tests passed! The Future Agent site is working correctly.');
  } else {
    console.log('\n⚠️  Some tests failed. Check the output above for details.');
  }
}

// Check if server is running
console.log('🔍 Checking if development server is running...');
makeRequest('http://localhost:3000/')
  .then(() => {
    console.log('✅ Server is running, starting tests...\n');
    runAllTests();
  })
  .catch(() => {
    console.log('❌ Server is not running. Please start it first:');
    console.log('   python -m http.server 3000 --directory docs');
    console.log('   or run: node run-tests.js');
  });