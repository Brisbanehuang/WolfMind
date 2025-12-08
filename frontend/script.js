// 全局变量
let currentLogFile = null;
let autoRefreshInterval = null;

// 角色映射
const roleMap = {
    'werewolf': '狼人',
    'villager': '村民',
    'seer': '预言家',
    'witch': '女巫',
    'hunter': '猎人'
};

// 动作图标映射
const actionIcons = {
    '狼人频道': '🐺',
    '狼人投票': '🗡️',
    '女巫行动': '💊',
    '预言家行动': '🔮',
    '公开发言': '🗣️',
    '投票': '🗳️',
    '遗言': '👻',
    '猎人开枪': '🔫'
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadLogFiles();
    setupEventListeners();
});

// 设置事件监听
function setupEventListeners() {
    document.getElementById('logSelector').addEventListener('change', (e) => {
        if (e.target.value) {
            loadGameLog(e.target.value);
        }
    });

    document.getElementById('refreshBtn').addEventListener('click', () => {
        if (currentLogFile) {
            loadGameLog(currentLogFile);
        } else {
            loadLogFiles();
        }
    });

    document.getElementById('autoRefresh').addEventListener('change', (e) => {
        if (e.target.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
}

// 加载日志文件列表
async function loadLogFiles() {
    try {
        const response = await fetch('/api/logs');
        const files = await response.json();

        const selector = document.getElementById('logSelector');
        selector.innerHTML = files.map(file =>
            `<option value="${file.name}">${file.name} (${file.time})</option>`
        ).join('');

        // 自动加载最新的日志
        if (files.length > 0) {
            currentLogFile = files[0].name;
            selector.value = currentLogFile;
            loadGameLog(currentLogFile);
        }
    } catch (error) {
        console.error('加载日志列表失败:', error);
        showError('无法加载日志列表，请确保后端服务正在运行');
    }
}

// 加载游戏日志
async function loadGameLog(filename) {
    try {
        showLoading();
        const response = await fetch(`/api/logs/${filename}`);
        const logContent = await response.text();

        currentLogFile = filename;
        parseAndDisplayLog(logContent);
    } catch (error) {
        console.error('加载日志失败:', error);
        showError('无法加载日志文件');
    }
}

// 开始自动刷新
function startAutoRefresh() {
    stopAutoRefresh();
    autoRefreshInterval = setInterval(() => {
        if (currentLogFile) {
            loadGameLog(currentLogFile);
        }
    }, 3000);
}

// 停止自动刷新
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// 解析并显示日志
function parseAndDisplayLog(logContent) {
    const gameData = parseLogContent(logContent);
    displayGameInfo(gameData);

    // Extract latest actions for bubbles
    const playerActions = getLastActions(gameData);
    displayPlayers(gameData, playerActions);

    // We still keep the rounds history but maybe we can hide it or style it differently later
    // based on user preference, but for now we ensure bubbles are the primary focus
    displayRounds(gameData);
}

// Get the latest significant action/speech for each player
function getLastActions(gameData) {
    const actions = {};
    if (!gameData.rounds || gameData.rounds.length === 0) return actions;

    // Look at the last round, and its last phase
    const lastRound = gameData.rounds[gameData.rounds.length - 1];
    if (!lastRound.phases || lastRound.phases.length === 0) return actions;

    // Iterate through all phases in the last round to build context, 
    // but give priority to the very last things said
    // actually, let's just look at the last phase to avoid cluttering with old news
    const lastPhase = lastRound.phases[lastRound.phases.length - 1];

    lastPhase.actions.forEach(action => {
        if (action.player && (action.speech || action.thought || action.behavior)) {
            // Collect all available content
            const actionData = {};
            if (action.thought) actionData.thought = action.thought;
            if (action.behavior) actionData.behavior = action.behavior;
            if (action.speech) actionData.speech = action.speech;

            // Only update if we have content
            if (Object.keys(actionData).length > 0) {
                actions[action.player] = actionData;
            }
        }
    });

    return actions;
}

// Keep the displayPlayers signature compatible or updated

// 显示玩家卡片和气泡（最新动作）
function displayPlayers(gameData, playerActions) {
    const grid = document.getElementById('playersGrid');
    grid.innerHTML = '';

    const players = gameData.players || [];
    const count = players.length || 0;

    // center surface stays, re-add it
    const surface = document.createElement('div');
    surface.className = 'table-surface';
    surface.innerHTML = '<div class="wolf-logo">🐺</div>';
    grid.appendChild(surface);

    if (count === 0) return;

    // arrange players evenly around a circle
    for (let i = 0; i < count; i++) {
        const p = players[i];
        const angle = (i / count) * Math.PI * 2 - Math.PI / 2; // start at top
        const radiusPercent = 42; // distance from center in percent
        const cx = 50 + Math.cos(angle) * radiusPercent;
        const cy = 50 + Math.sin(angle) * radiusPercent;

        const card = document.createElement('div');
        card.className = `player-card role-${p.role || 'villager'}` + (p.alive === false ? ' dead' : '');
        card.style.left = cx + '%';
        card.style.top = cy + '%';
        card.style.transform = 'translate(-50%, -50%)';

        const content = document.createElement('div');
        content.className = 'player-card-content';
        content.style.background = 'rgba(255,255,255,0.02)';
        content.style.padding = '10px 14px';
        content.style.borderRadius = '12px';
        content.style.minWidth = '120px';
        content.style.textAlign = 'center';

        const avatar = document.createElement('div');
        avatar.className = 'player-avatar';
        avatar.style.width = '56px';
        avatar.style.height = '56px';
        avatar.style.margin = '0 auto 8px';
        avatar.style.borderRadius = '50%';
        avatar.style.border = '3px solid rgba(255,255,255,0.06)';
        avatar.style.display = 'flex';
        avatar.style.alignItems = 'center';
        avatar.style.justifyContent = 'center';
        avatar.style.fontSize = '20px';
        avatar.textContent = p.name || 'P';

        const nameEl = document.createElement('div');
        nameEl.style.fontWeight = '700';
        nameEl.style.marginBottom = '4px';
        nameEl.textContent = p.name || '-';

        const roleBadge = document.createElement('div');
        roleBadge.className = 'player-role-badge';
        roleBadge.style.fontSize = '12px';
        roleBadge.style.padding = '4px 8px';
        roleBadge.style.borderRadius = '999px';
        roleBadge.style.display = 'inline-block';
        roleBadge.style.border = '1px solid rgba(255,255,255,0.04)';
        roleBadge.textContent = roleMap[p.role] || p.role || '未知';

        content.appendChild(avatar);
        content.appendChild(nameEl);
        content.appendChild(roleBadge);

        if (p.alive === false) {
            const deathMark = document.createElement('div');
            deathMark.className = 'death-mark';
            deathMark.textContent = '☠';
            card.appendChild(deathMark);
        }

        card.appendChild(content);
        grid.appendChild(card);

        // add chat bubble if there's recent action
        const act = playerActions && playerActions[p.name];
        if (act) {
            const bubble = document.createElement('div');
            bubble.className = 'chat-bubble ' + (Math.sin(angle) > 0 ? 'pos-bottom' : 'pos-top');
            bubble.style.left = cx + '%';
            // place bubble slightly offset vertically
            bubble.style.transform = 'translateX(-50%)';

            const inner = document.createElement('div');
            inner.className = 'bubble-content-scroll';

            if (act.thought) {
                const s = document.createElement('div');
                s.className = 'bubble-section section-thought';
                s.textContent = act.thought;
                inner.appendChild(s);
            }
            if (act.behavior) {
                const b = document.createElement('div');
                b.className = 'bubble-section section-behavior';
                b.textContent = act.behavior;
                inner.appendChild(b);
            }
            if (act.speech) {
                const sp = document.createElement('div');
                sp.className = 'bubble-section section-speech';
                sp.textContent = act.speech;
                inner.appendChild(sp);
            }

            bubble.appendChild(inner);
            grid.appendChild(bubble);
        }
    }
}

// 解析日志内容
function parseLogContent(content) {
    const lines = content.split('\n');
    const gameData = {
        gameId: '',
        startTime: '',
        endTime: '',
        status: '进行中',
        players: [],
        rounds: []
    };

    let currentRound = null;
    let currentPhase = null;
    let currentAction = null;
    let currentLogState = null; // 'thought', 'behavior', 'speech', 'details'

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // 解析游戏ID
        if (line.startsWith('游戏ID:')) {
            gameData.gameId = line.split(':')[1].trim();
        }

        // 解析开始时间
        if (line.startsWith('开始时间:')) {
            gameData.startTime = line.split('开始时间:')[1].trim();
        }

        // 解析结束时间
        if (line.startsWith('游戏结束时间:')) {
            gameData.endTime = line.split('游戏结束时间:')[1].trim();
        }

        // 解析游戏结束状态
        if (line.includes('游戏结束:')) {
            gameData.status = line.split('游戏结束:')[1].split('。')[0].trim();
        }

        // 解析玩家列表
        if (line.startsWith('- Player')) {
            const match = line.match(/- (Player\d+): (\w+)/);
            if (match) {
                gameData.players.push({
                    name: match[1],
                    role: match[2],
                    alive: true
                });
            }
        }

        // 解析回合
        if (line.match(/^第 \d+ 回合$/)) {
            if (currentRound) {
                gameData.rounds.push(currentRound);
            }
            currentRound = {
                number: parseInt(line.match(/\d+/)[0]),
                phases: []
            };
            currentPhase = null;
        }

        // 解析阶段
        if (line === '【夜晚阶段】') {
            currentPhase = { type: 'night', actions: [] };
            if (currentRound) currentRound.phases.push(currentPhase);
        } else if (line === '【白天阶段】') {
            currentPhase = { type: 'day', actions: [] };
            if (currentRound) currentRound.phases.push(currentPhase);
        }

        // 解析动作
        if (line.match(/^\[\d{2}:\d{2}:\d{2}\]/)) {
            const timeMatch = line.match(/\[(\d{2}:\d{2}:\d{2})\]/);
            const actionMatch = line.match(/\] (.+?) \| (.+)/);

            if (timeMatch && actionMatch) {
                currentAction = {
                    time: timeMatch[1],
                    type: actionMatch[1],
                    player: actionMatch[2],
                    thought: '',
                    behavior: '',
                    speech: '',
                    details: ''
                };

                if (currentPhase) {
                    currentPhase.actions.push(currentAction);
                }
            }
        }

        // 解析心声、表现、发言 (Multi-line support)
        if (currentAction) {
            if (line.startsWith('(心声)')) {
                currentAction.thought = line.substring(4).trim();
                currentLogState = 'thought';
            } else if (line.startsWith('(表现)')) {
                currentAction.behavior = line.substring(4).trim();
                currentLogState = 'behavior';
            } else if (line.startsWith('(发言)')) {
                currentAction.speech = line.substring(4).trim();
                currentLogState = 'speech';
            } else if (line.includes('投票给') || line.includes('查验') || line.includes('使用')) {
                currentAction.details = line;
                currentLogState = 'details';
            } else if (currentLogState && currentAction && !line.startsWith('[') && !line.startsWith('游戏ID:') && !line.startsWith('开始时间:') && !line.startsWith('游戏结束') && !line.startsWith('- Player') && !line.match(/^第 \d+ 回合$/) && !line.match(/^[【📢💀📊]/)) {
                // Continuation of previous field
                if (currentLogState === 'thought') currentAction.thought += '\n' + line;
                if (currentLogState === 'behavior') currentAction.behavior += '\n' + line;
                if (currentLogState === 'speech') currentAction.speech += '\n' + line;
            }
        }

        // 解析投票结果
        if (line.match(/📊 .+投票结果/)) {
            const resultMatch = line.match(/📊 (.+投票结果 .+)/);
            if (resultMatch && currentPhase) {
                currentPhase.actions.push({
                    type: 'vote_result',
                    details: resultMatch[1]
                });
            }
        }

        // 解析死亡公告
        if (line.match(/💀 (夜晚死亡|白天死亡)/)) {
            const deathMatch = line.match(/💀 (夜晚死亡|白天死亡) (.+)/);
            if (deathMatch && currentPhase) {
                currentPhase.actions.push({
                    type: 'death',
                    details: `${deathMatch[1]}: ${deathMatch[2]}`
                });

                // 更新玩家状态
                const deadPlayers = deathMatch[2].split(',').map(p => p.trim());
                deadPlayers.forEach(playerName => {
                    const player = gameData.players.find(p => p.name === playerName);
                    if (player) player.alive = false;
                });
            }
        }

        // 解析系统公告
        if (line.match(/📢 系统公告/)) {
            let announcement = '';
            i++;
            while (i < lines.length && !lines[i].includes('[') && lines[i].trim()) {
                announcement += lines[i].trim() + ' ';
                i++;
            }
            if (currentPhase) {
                currentPhase.actions.push({
                    type: 'system',
                    details: announcement.trim()
                });
            }
        }
    }

    // 添加最后一个回合
    if (currentRound) {
        gameData.rounds.push(currentRound);
    }

    return gameData;
}

// 显示游戏信息
function displayGameInfo(gameData) {
    document.getElementById('gameId').textContent = gameData.gameId || '-';
    document.getElementById('startTime').textContent = gameData.startTime || '-';
    document.getElementById('endTime').textContent = gameData.endTime || '游戏进行中';
    document.getElementById('gameStatus').textContent = gameData.status || '进行中';
}

// 显示回合
function displayRounds(gameData) {
    const roundsContainer = document.getElementById('roundsContainer');
    roundsContainer.innerHTML = gameData.rounds.map(round => `
        <div class="round-card">
            <div class="round-header">第 ${round.number} 回合</div>
            <div class="round-content">
                ${round.phases.map(phase => displayPhase(phase)).join('')}
            </div>
        </div>
    `).join('');
}

// 显示阶段
function displayPhase(phase) {
    const phaseTitle = phase.type === 'night' ? '🌙 夜晚阶段' : '☀️ 白天阶段';
    return `
        <div class="phase-section">
            <div class="phase-title">${phaseTitle}</div>
            ${phase.actions.map(action => displayAction(action)).join('')}
        </div>
    `;
}

// 显示动作
function displayAction(action) {
    if (action.type === 'vote_result') {
        return `<div class="vote-result">📊 ${action.details}</div>`;
    }

    if (action.type === 'death') {
        return `<div class="death-announcement">💀 ${action.details}</div>`;
    }

    if (action.type === 'system') {
        return `<div class="system-announcement">📢 ${action.details}</div>`;
    }

    const icon = actionIcons[action.type] || '📝';

    return `
        <div class="action-item">
            <div class="action-header">
                <span class="action-icon">${icon}</span>
                <span>${action.type} | ${action.player}</span>
                <span class="action-time">${action.time}</span>
            </div>
            <div class="action-content">
                ${action.thought ? `<div class="thought">${action.thought}</div>` : ''}
                ${action.behavior ? `<div class="behavior">${action.behavior}</div>` : ''}
                ${action.speech ? `<div class="speech">${action.speech}</div>` : ''}
                ${action.details ? `<div style="margin-top: 8px; color: #6c757d;">${action.details}</div>` : ''}
            </div>
        </div>
    `;
}

// 显示加载中
function showLoading() {
    document.getElementById('roundsContainer').innerHTML = '<div class="loading">⏳ 加载中...</div>';
}

// 显示错误
function showError(message) {
    document.getElementById('roundsContainer').innerHTML = `<div class="error">❌ ${message}</div>`;
}


