const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');

/**
 * Autonomous Issue Agent - VS Code Chat Participant
 *
 * Provides /issueagent command in chat to:
 * 1. Select next issue from GitHub (using defined order)
 * 2. Run autonomous agent on the issue
 * 3. Stream progress to chat
 * 4. Report success/failure
 */

function activate(context) {
  console.log('Issue Agent extension activated');

  registerResolveIssueParticipant(context);
  registerCreateIssueParticipant(context);
  registerRalphParticipant(context);
}

function getConfiguredAgentProfile(defaultProfile) {
  const cfg = vscode.workspace
    .getConfiguration()
    .get('issueagent.customAgent');
  const configured = (cfg || '').toString().trim();
  return configured || defaultProfile;
}

function registerRalphParticipant(context) {
  const participant = vscode.chat.createChatParticipant(
    'ralph.chat',
    async (request, chatContext, stream, token) => {
      try {
        if (token.isCancellationRequested) {
          return;
        }

        const command = request.command || 'run';

        if (command === 'run') {
          await handleRalphRunCommand(stream, token);
        } else {
          stream.markdown(
            `Unknown command: \`${command}\`. Use \`/ralph\` or \`/ralph run\``,
          );
        }
      } catch (error) {
        stream.markdown(`❌ **Error:** ${error.message}`);
        console.error('Ralph participant error:', error);
      }
    },
  );

  participant.iconPath = vscode.Uri.file(
    path.join(context.extensionPath, 'icon.png'),
  );

  context.subscriptions.push(participant);
}

function registerResolveIssueParticipant(context) {
  // Register chat participant
  const participant = vscode.chat.createChatParticipant(
    'resolve-issue.chat',
    async (request, chatContext, stream, token) => {
      try {
        // Check for cancellation
        if (token.isCancellationRequested) {
          return;
        }

        // Parse command
        const command = request.command || 'run';

        if (command === 'run') {
          await handleRunCommand(request, stream, token);
        } else {
          stream.markdown(
            `Unknown command: \`${command}\`. Use \`/run\`.`,
          );
        }
      } catch (error) {
        stream.markdown(`❌ **Error:** ${error.message}`);
        console.error('Issue Agent error:', error);
      }
    },
  );

  participant.iconPath = new vscode.ThemeIcon('run');

  context.subscriptions.push(participant);
}

function registerCreateIssueParticipant(context) {
  const participant = vscode.chat.createChatParticipant(
    'create-issue.chat',
    async (request, chatContext, stream, token) => {
      try {
        if (token.isCancellationRequested) {
          return;
        }

        const command = request.command || 'run';

        if (command === 'open') {
          await openCreateIssueWorkflowInEditor(stream);
          return;
        }

        if (command !== 'run') {
          stream.markdown(
            `Unknown command: \`${command}\`. Use \`/create-issue\`, \`/create-issue run\`, or \`/create-issue open\`.`,
          );
          return;
        }

        await handleCreateIssueRunCommand(request, stream);
      } catch (error) {
        stream.markdown(`❌ **Error:** ${error.message}`);
        console.error('Create-Issue participant error:', error);
      }
    },
  );

  participant.iconPath = new vscode.ThemeIcon('new-file');

  context.subscriptions.push(participant);
}

async function openCreateIssueWorkflowInEditor(stream) {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  if (!workspaceFolder) {
    stream.markdown('❌ No workspace folder open.');
    return;
  }

  const repoRoot = workspaceFolder.uri.fsPath;
  const workflowPath = path.join(
    repoRoot,
    '.github',
    'prompts',
    'agents',
    'create-issue.md',
  );

  const workflowUri = vscode.Uri.file(workflowPath);
  await vscode.commands.executeCommand('vscode.open', workflowUri);
}

async function handleCreateIssueRunCommand(request, stream) {
  await openCreateIssueWorkflowInEditor(stream);

  const rawText =
    (request.prompt ?? request.message ?? request.text ?? request.query ?? '')
      .toString()
      .trim();

  stream.markdown('## create-issue workflow launcher\n');
  stream.markdown(
    'This participant makes the repo\'s `create-issue` workflow easy to discover in the chat agent menu.\n\n',
  );

  stream.markdown('### How to run the workflow\n');
  if (rawText) {
    stream.markdown(
      `Copy/paste this into Copilot Chat to draft + create the issue:\n\n` +
        `\`\`\`\n@workspace /runSubagent create-issue "${rawText.replace(/"/g, '\\"')}"\n\`\`\`\n`,
    );
  } else {
    stream.markdown(
      'Provide a one-line description after the mention, e.g. `@create-issue add JWT auth to API`, then re-run.\n\n',
    );
    stream.markdown('Or copy/paste and fill in your description:\n\n');
    stream.markdown(
      '```\n@workspace /runSubagent create-issue "<describe the work>"\n```\n',
    );
  }

  stream.markdown('### Why this exists\n');
  stream.markdown(
    '- VS Code\'s agent menu lists **chat participants** provided by extensions (like `@issueagent`).\n' +
      '- The file `.github/prompts/agents/create-issue.md` is a **workflow spec**, not a participant by itself.\n' +
      '- This participant bridges discoverability without duplicating the workflow.\n',
  );
}

/**
 * Handle the main /issueagent command
 */
async function handleRunCommand(request, stream, token) {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];

  if (!workspaceFolder) {
    stream.markdown(
      '❌ No workspace folder open. Please open the AI-Agent-Framework workspace.',
    );
    return;
  }

  const repoRoot = workspaceFolder.uri.fsPath;

  // Check if Python environment is activated
  const venvPath = path.join(repoRoot, '.venv');
  const pythonPath =
    process.platform === 'win32'
      ? path.join(venvPath, 'Scripts', 'python.exe')
      : path.join(venvPath, 'bin', 'python3');

  const agentProfile = getConfiguredAgentProfile('resolve-issue');

  stream.markdown('🤖 **Resolve-Issue Agent Starting...**\n\n');

  // Step 1: Select next issue
  stream.markdown('### 📋 Phase 1: Issue Selection\n');
  stream.markdown('Running `next-issue.py` to find the next issue...\n\n');

  const issueNumber = await selectNextIssue(
    repoRoot,
    pythonPath,
    stream,
    token,
  );

  if (!issueNumber) {
    stream.markdown(
      '❌ **Failed:** Could not select next issue. Check that GitHub CLI is authenticated.\n',
    );
    return;
  }

  if (token.isCancellationRequested) {
    stream.markdown('⚠️ Cancelled by user.\n');
    return;
  }

  stream.markdown(`✅ Selected issue: **#${issueNumber}**\n\n`);

  // Step 2: Run autonomous agent
  stream.markdown('### 🚀 Phase 2: Autonomous Agent Execution\n');
  stream.markdown(
    `Running agent on issue #${issueNumber} with profile \`${agentProfile}\`...\n\n`,
  );

  const success = await runAgent(
    repoRoot,
    pythonPath,
    issueNumber,
    stream,
    token,
    agentProfile,
  );

  // Step 3: Report results
  stream.markdown('\n---\n\n');

  if (success) {
    stream.markdown('### ✅ **Issue Completed Successfully!**\n\n');
    stream.markdown(`The agent has successfully:\n`);
    stream.markdown(`- ✅ Analyzed issue #${issueNumber}\n`);
    stream.markdown(`- ✅ Created implementation plan\n`);
    stream.markdown(`- ✅ Written tests and code\n`);
    stream.markdown(`- ✅ Verified all tests pass\n`);
    stream.markdown(`- ✅ Created pull request\n`);
    stream.markdown(`- ✅ Updated knowledge base\n\n`);
    stream.markdown(`Check GitHub for the new PR!`);
  } else {
    stream.markdown('### ❌ **Issue Resolution Failed**\n\n');
    stream.markdown(
      `The agent encountered errors while working on issue #${issueNumber}.\n\n`,
    );
    stream.markdown(`Please check:\n`);
    stream.markdown(`- Agent logs in the terminal\n`);
    stream.markdown(`- GitHub issue for any automated comments\n`);
    stream.markdown(`- Local git status for uncommitted changes\n`);
  }
}

async function handleRalphRunCommand(stream, token) {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];

  if (!workspaceFolder) {
    stream.markdown(
      '❌ No workspace folder open. Please open the AI-Agent-Framework workspace.',
    );
    return;
  }

  const repoRoot = workspaceFolder.uri.fsPath;
  const venvPath = path.join(repoRoot, '.venv');
  const pythonPath =
    process.platform === 'win32'
      ? path.join(venvPath, 'Scripts', 'python.exe')
      : path.join(venvPath, 'bin', 'python3');

  stream.markdown('🧠 **Ralph Agent Starting...**\n\n');
  stream.markdown('### 📋 Phase 1: Issue Selection\n');
  stream.markdown('Running `next-issue.py` to find the next issue...\n\n');

  const issueNumber = await selectNextIssue(
    repoRoot,
    pythonPath,
    stream,
    token,
  );

  if (!issueNumber) {
    stream.markdown(
      '❌ **Failed:** Could not select next issue. Check that GitHub CLI is authenticated.\n',
    );
    return;
  }

  if (token.isCancellationRequested) {
    stream.markdown('⚠️ Cancelled by user.\n');
    return;
  }

  stream.markdown(`✅ Selected issue: **#${issueNumber}**\n\n`);
  stream.markdown('### 🚀 Phase 2: Ralph Execution\n');
  stream.markdown(
    `Running Ralph agent on issue #${issueNumber} (skill + reviewer gates)...\n\n`,
  );

  const success = await runAgent(
    repoRoot,
    pythonPath,
    issueNumber,
    stream,
    token,
    'ralph',
  );

  // Step 3: Report results
  stream.markdown('\n---\n\n');

  if (success) {
    stream.markdown('### ✅ **Issue Completed Successfully!**\n\n');
    stream.markdown(`The agent has successfully:\n`);
    stream.markdown(`- ✅ Analyzed issue #${issueNumber}\n`);
    stream.markdown(`- ✅ Created implementation plan\n`);
    stream.markdown(`- ✅ Written tests and code\n`);
    stream.markdown(`- ✅ Verified all tests pass\n`);
    stream.markdown(`- ✅ Created pull request\n`);
    stream.markdown(`- ✅ Updated knowledge base\n\n`);
    stream.markdown(`Check GitHub for the new PR!`);
  } else {
    stream.markdown('### ❌ **Issue Resolution Failed**\n\n');
    stream.markdown(
      `The agent encountered errors while working on issue #${issueNumber}.\n\n`,
    );
    stream.markdown(`Please check:\n`);
    stream.markdown(`- Agent logs in the terminal\n`);
    stream.markdown(`- GitHub issue for any automated comments\n`);
    stream.markdown(`- Local git status for uncommitted changes\n`);
  }
}

/**
 * Select the next issue using next-issue.py
 * Returns the issue number or null on failure
 */
async function selectNextIssue(repoRoot, pythonPath, stream, token) {
  return new Promise((resolve) => {
    const scriptPath = path.join(repoRoot, 'scripts', 'next-issue.py');

    const proc = spawn(pythonPath, [scriptPath], {
      cwd: repoRoot,
      env: { ...process.env },
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
      // Stream progress messages
      const lines = data
        .toString()
        .split('\n')
        .filter((l) => l.trim());
      for (const line of lines) {
        if (
          line.includes('✓') ||
          line.includes('→') ||
          line.includes('Next issue')
        ) {
          stream.markdown(`${line}\n`);
        }
      }
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('close', (code) => {
      if (token.isCancellationRequested) {
        proc.kill();
        resolve(null);
        return;
      }

      if (code === 0) {
        // Extract issue number from output
        const match =
          stdout.match(/Next issue:\s*#?(\d+)/i) ||
          stdout.match(/Issue (\d+)/i) ||
          stdout.match(/\[(\d+)\]/);

        if (match) {
          resolve(parseInt(match[1]));
        } else {
          stream.markdown(`⚠️ Could not parse issue number from output\n`);
          resolve(null);
        }
      } else {
        stream.markdown(`❌ next-issue.py failed with code ${code}\n`);
        if (stderr) {
          stream.markdown(`\`\`\`\n${stderr.slice(-500)}\n\`\`\`\n`);
        }
        resolve(null);
      }
    });

    proc.on('error', (err) => {
      stream.markdown(`❌ Failed to run next-issue.py: ${err.message}\n`);
      resolve(null);
    });

    // Handle cancellation
    token.onCancellationRequested(() => {
      proc.kill();
      resolve(null);
    });
  });
}

/**
 * Run the autonomous agent on the selected issue
 * Returns true on success, false on failure
 */
async function runAgent(
  repoRoot,
  pythonPath,
  issueNumber,
  stream,
  token,
  agentProfile,
) {
  return new Promise((resolve) => {
    const scriptPath = path.join(repoRoot, 'scripts', 'work-issue.py');

    const args = [
      scriptPath,
      '--issue',
      issueNumber.toString(),
      '--agent',
      agentProfile || 'autonomous',
    ];

    const proc = spawn(pythonPath, args, {
      cwd: repoRoot,
      env: { ...process.env },
    });

    let phaseEmojis = {
      Analysis: '🔍',
      Planning: '📋',
      Testing: '🧪',
      Implementation: '⚙️',
      Validation: '✓',
      Review: '👀',
      'PR Creation': '📤',
      Learning: '🎓',
    };

    proc.stdout.on('data', (data) => {
      const lines = data
        .toString()
        .split('\n')
        .filter((l) => l.trim());

      for (const line of lines) {
        // Detect phase transitions
        for (const [phase, emoji] of Object.entries(phaseEmojis)) {
          if (line.toLowerCase().includes(phase.toLowerCase())) {
            stream.markdown(`\n**${emoji} ${phase} Phase**\n`);
            break;
          }
        }

        // Stream important messages
        if (
          line.includes('✓') ||
          line.includes('✅') ||
          line.includes('❌') ||
          line.includes('⚠️') ||
          line.includes('→') ||
          line.includes('Creating') ||
          line.includes('Running') ||
          line.includes('Writing')
        ) {
          stream.markdown(`${line}\n`);
        }
      }
    });

    proc.stderr.on('data', (data) => {
      const text = data.toString();
      // Only show actual errors, not debug info
      if (text.includes('Error') || text.includes('Failed')) {
        stream.markdown(`⚠️ ${text}\n`);
      }
    });

    proc.on('close', (code) => {
      if (token.isCancellationRequested) {
        proc.kill();
        resolve(false);
        return;
      }

      resolve(code === 0);
    });

    proc.on('error', (err) => {
      stream.markdown(`❌ Failed to run agent: ${err.message}\n`);
      resolve(false);
    });

    // Handle cancellation
    token.onCancellationRequested(() => {
      proc.kill();
      resolve(false);
    });
  });
}

function deactivate() {
  console.log('Issue Agent extension deactivated');
}

module.exports = {
  activate,
  deactivate,
};
