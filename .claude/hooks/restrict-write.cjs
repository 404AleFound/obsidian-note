const fs = require('fs');
const path = require('path');

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const event = JSON.parse(input);
    const toolInput = event.tool_input || {};
    const target = toolInput.file_path || toolInput.notebook_path || toolInput.path;

    if (!target) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'PreToolUse',
          permissionDecision: 'deny',
          permissionDecisionReason: '无法确认目标路径，只允许写入 assays 文件夹。'
        }
      }));
      return;
    }

    const projectRoot = path.resolve(process.cwd());
    const absoluteTarget = path.resolve(projectRoot, target);
    const assaysRoot = path.resolve(projectRoot, 'assays') + path.sep;

    if (!absoluteTarget.toLowerCase().startsWith(assaysRoot.toLowerCase())) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'PreToolUse',
          permissionDecision: 'deny',
          permissionDecisionReason: '写入已限制为 assays 文件夹。'
        }
      }));
    }
  } catch {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        permissionDecision: 'deny',
        permissionDecisionReason: '无法验证写入路径，已拒绝操作。'
      }
    }));
  }
});
