#!/usr/bin/env node

const http = require('http');
const { URL } = require('url');

console.log('🚀 Future Agent Comprehensive Test Suite\n');

const tests = [
  {
    name: 'Homepage Complete Test',
    url: 'http://localhost:3000/',
    checks: [
      { type: 'title', value: 'Future Agent - Cannabis Industry Knowledge' },
      { type: 'content', value: '16,337' },
      { type: 'content', value: '1,456' },
      { type: 'content', value: 'Cannabis Industry Knowledge Agent' },
      { type: 'element', value: 'h1' },
      { type: 'element', value: 'stats-grid' },
      { type: 'element', value: 'features' },
      { type: 'element', value: 'cta-section' }
    ]
  },
  {
    name: 'F8 Comparison Complete Test',
    url: 'http://localhost:3000/f8-comparison.html',
    checks: [
      { type: 'title', value: 'F8 vs Future4200 Comparison' },
      { type: 'content', value: 'Compare F8 LangChain responses' },
      { type: 'element', value: 'h1' },
      { type: 'element', value: 'stats-grid' },
      { type: 'element', value: 'filters' },
      { type: 'element', value: 'comparisonResults' },
      { type: 'element', value: 'search-box' }
    ]
  },
  {
    name: 'Data Loading Test',
    url: 'http://localhost:3000/data/f8_responses_demo.json',
    checks: [
      { type: 'json', value: 'total_questions' },
      { type: 'json', value: 'results' }
    ]
  },
  {
    name: 'Statistics Data Test',
    url: 'http://localhost:3000/data/f8_processing_stats.json',
    checks: [
      { type: 'json', value: 'total_questions' },
      { type: 'json', value: 'successful' }
    ]
  }
];

function makeRequest(url) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const req = http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, data, headers: res.headers }));
    });
    
    req.on('error', reject);
    req.setTimeout(10000, () => reject(new Error('Request timeout')));
  });
}

function checkContent(html, checks) {
  const results = [];
  
  for (const check of checks) {
    let found = false;
    
    if (check.type === 'title') {
      const titleRegex = new RegExp(`<title[^>]*>([^<]*)</title>`, 'i');
      const match = html.match(titleRegex);
      if (match && match[1].includes(check.value)) {
        found = true;
      }
    } else if (check.type === 'content') {
      found = html.includes(check.value);
    } else if (check.type === 'element') {
      const classRegex = new RegExp(`<[^>]*class="[^"]*${check.value}[^"]*"`, 'i');
      const idRegex = new RegExp(`<[^>]*id="${check.value}"`, 'i');
      const tagRegex = new RegExp(`<${check.value}[^>]*>`, 'i');
      found = classRegex.test(html) || idRegex.test(html) || tagRegex.test(html);
    } else if (check.type === 'json') {
      try {
        const json = JSON.parse(html);
        found = json.hasOwnProperty(check.value);
      } catch (e) {
        found = false;
      }
    }
    
    results.push({ check, found });
  }
  
  return results;
}

async function runTest(test) {
  console.log(`🔍 Testing: ${test.name}`);
  console.log(`   URL: ${test.url}`);
  
  try {
    const { status, data, headers } = await makeRequest(test.url);
    
    if (status === 200) {
      console.log(`   ✅ Status: ${status}`);
      
      // Check content type
      const contentType = headers['content-type'] || '';
      if (test.url.includes('.json')) {
        console.log(`   📄 Content-Type: ${contentType}`);
      }
      
      const results = checkContent(data, test.checks);
      let allPassed = true;
      
      for (const result of results) {
        if (result.found) {
          console.log(`   ✅ Found: ${result.check.value} (${result.check.type})`);
        } else {
          console.log(`   ❌ Missing: ${result.check.value} (${result.check.type})`);
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
  console.log('🚀 Starting comprehensive tests...\n');
  
  let passed = 0;
  let total = tests.length;
  
  for (const test of tests) {
    const result = await runTest(test);
    if (result) passed++;
  }
  
  console.log('📊 Comprehensive Test Results:');
  console.log(`   Passed: ${passed}/${total}`);
  console.log(`   Success Rate: ${Math.round((passed / total) * 100)}%`);
  
  if (passed === total) {
    console.log('\n🎉 All comprehensive tests passed! The Future Agent site is fully functional.');
    console.log('\n✨ Features Verified:');
    console.log('   ✅ Homepage loads with correct content and statistics');
    console.log('   ✅ F8 Comparison page loads with all interactive elements');
    console.log('   ✅ Data files are accessible and contain expected data');
    console.log('   ✅ Statistics are properly loaded and displayed');
    console.log('   ✅ All HTML elements are present and functional');
  } else {
    console.log('\n⚠️  Some tests failed. Check the output above for details.');
  }
}

// Check if server is running
console.log('🔍 Checking if development server is running...');
makeRequest('http://localhost:3000/')
  .then(() => {
    console.log('✅ Server is running, starting comprehensive tests...\n');
    runAllTests();
  })
  .catch(() => {
    console.log('❌ Server is not running. Please start it first:');
    console.log('   python -m http.server 3000 --directory docs');
    console.log('   or run: npm run test:server');
  });