const fs = require('fs');
const OUT = 'C:/Users/zhaonan/Desktop/多agent/_out.txt';
const log = (...a) => { try { fs.appendFileSync(OUT, a.map(x => typeof x === 'string' ? x : JSON.stringify(x)).join(' ') + '\n'); } catch (e) {} };
fs.writeFileSync(OUT, '');
try {
  const p = 'C:/Users/zhaonan/Desktop/多agent/多Agent.html';
  const html = fs.readFileSync(p, 'utf8');
  log('READ_OK len=' + html.length);

  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  const combined = scripts.join('\n;\n');
  try { new Function(combined); log('SYNTAX_OK scriptCount=' + scripts.length + ' combinedLen=' + combined.length); }
  catch (e) { log('SYNTAX_ERROR: ' + e.message); }

  // 纯逻辑验证分类
  const isHtmlFile = (f) => /\.html?$/i.test(f);
  const cases = ['aurasound-homepage.html', 'AuraSound-Homepage-Design-Spec.md', 'ui-form-mockup.html', 'resource-audit-framework.md', '产品运营项目方案.html'];
  for (const f of cases) log('CLASS ' + f + ' => ' + (isHtmlFile(f) ? 'HTML' : 'NONHTML'));

  // 渲染入口检查：所有设置文件渲染 innerHTML 的地方是否都经过 renderFileContent
  const m = combined.match(/renderFileContent\([^)]*\)/g) || [];
  log('renderFileContent CALLS: ' + JSON.stringify(m));
} catch (e) {
  log('FATAL: ' + e.message + ' | ' + (e.stack || ''));
}
