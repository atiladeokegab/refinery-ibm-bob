import * as vscode from 'vscode';
import * as https from 'https';
import * as http from 'http';
import * as path from 'path';

const COBOL_EXTENSIONS = new Set(['.cob', '.cbl', '.jcl']);

let statusBarItem: vscode.StatusBarItem;
let cachedToken: string | null = null;
let lastRefId: string | null = null;

function getConfig() {
    const cfg = vscode.workspace.getConfiguration('refinery');
    return {
        serverUrl: cfg.get<string>('serverUrl', 'http://localhost:8080').replace(/\/$/, ''),
        username: cfg.get<string>('username', 'admin'),
        password: cfg.get<string>('password', 'refinery'),
        estate: cfg.get<boolean>('enableEstateAnalysis', true),
    };
}

async function apiPost(url: string, body: object, token?: string): Promise<unknown> {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify(body);
        const parsed = new URL(url);
        const lib = parsed.protocol === 'https:' ? https : http;
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(data).toString(),
        };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const req = lib.request(
            { hostname: parsed.hostname, port: parsed.port, path: parsed.pathname, method: 'POST', headers },
            (res) => {
                let raw = '';
                res.on('data', (chunk) => { raw += chunk; });
                res.on('end', () => {
                    try { resolve(JSON.parse(raw)); } catch { resolve(raw); }
                });
            }
        );
        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

async function ensureToken(): Promise<string | null> {
    if (cachedToken) return cachedToken;
    const cfg = getConfig();
    try {
        const resp = await apiPost(`${cfg.serverUrl}/api/login`, {
            username: cfg.username,
            password: cfg.password,
        }) as { token?: string };
        if (resp.token) {
            cachedToken = resp.token;
            return cachedToken;
        }
    } catch {
        // server not running
    }
    return null;
}

async function runAudit(filePath: string, workspacePath: string): Promise<void> {
    const cfg = getConfig();

    statusBarItem.text = '$(sync~spin) Refinery: Analysing...';
    statusBarItem.backgroundColor = undefined;
    statusBarItem.show();

    const token = await ensureToken();

    const relativePath = path.relative(workspacePath, filePath).replace(/\\/g, '/');

    let result: {
        verdict?: string;
        blast_radius_score?: number;
        affected_systems_count?: number;
        risk_score?: number;
        ref_id?: string;
    };

    try {
        result = await apiPost(
            `${cfg.serverUrl}/api/audit/run`,
            { repo_path: workspacePath, changed_file: relativePath, estate: cfg.estate },
            token ?? undefined,
        ) as typeof result;
    } catch {
        statusBarItem.text = '$(error) Refinery: Server unreachable';
        return;
    }

    lastRefId = result.ref_id ?? null;

    const blastScore = result.blast_radius_score ?? 0;
    const affectedCount = result.affected_systems_count ?? 0;

    if (result.verdict === 'FLAGGED') {
        statusBarItem.text = `$(error) Refinery: FLAGGED — risk score ${result.risk_score}/100`;
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    } else if (blastScore > 50) {
        statusBarItem.text = `$(warning) Refinery: CRO sign-off required — ${affectedCount} systems affected`;
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    } else {
        statusBarItem.text = `$(check) Refinery: PASS`;
        statusBarItem.backgroundColor = undefined;
    }
}

export function activate(context: vscode.ExtensionContext): void {
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'refinery.openLastContract';
    context.subscriptions.push(statusBarItem);

    const saveWatcher = vscode.workspace.onDidSaveTextDocument(async (doc) => {
        const ext = path.extname(doc.fileName).toLowerCase();
        if (!COBOL_EXTENSIONS.has(ext)) return;

        const folder = vscode.workspace.getWorkspaceFolder(doc.uri);
        if (!folder) return;

        await runAudit(doc.uri.fsPath, folder.uri.fsPath);
    });
    context.subscriptions.push(saveWatcher);

    context.subscriptions.push(
        vscode.commands.registerCommand('refinery.runAudit', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;
            const folder = vscode.workspace.getWorkspaceFolder(editor.document.uri);
            if (!folder) return;
            await runAudit(editor.document.uri.fsPath, folder.uri.fsPath);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('refinery.openLastContract', async () => {
            if (!lastRefId) {
                vscode.window.showInformationMessage('No Refinery audit yet — save a COBOL file to trigger analysis.');
                return;
            }
            const cfg = getConfig();
            const token = await ensureToken();
            const url = `${cfg.serverUrl}/api/certificates/${lastRefId}${token ? `?token=${token}` : ''}`;
            vscode.env.openExternal(vscode.Uri.parse(url));
        })
    );

    statusBarItem.text = '● Refinery ready';
    statusBarItem.show();
}

export function deactivate(): void {
    cachedToken = null;
}
