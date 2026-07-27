const fs = require('fs');
const path = 'C:/Users/zhaonan/Desktop/多agent/多Agent.html';
const s = fs.readFileSync(path, 'utf8');
const scripts = [...s.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
console.log('script count', scripts.length);
let i = 0;
for (const script of scripts) {
  i++;
  try {
    new Function(script);
    console.log('script', i, 'syntax ok');
  } catch (e) {
    console.error('script', i, 'error:', e.message);
    process.exit(1);
  }
}
console.log('all ok');
