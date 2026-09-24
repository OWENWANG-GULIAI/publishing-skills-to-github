import assert from 'node:assert/strict';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const auditScript = path.join(root, 'scripts', 'audit_skill_repository.py');

const validReadme = `# Demo Skill

## Why
Grounded purpose.
## Quick Start
\`\`\`bash
git clone https://github.com/OWENWANG-GULIAI/demo-skill.git
\`\`\`
## Usage
Invoke with authorized input.
## How It Works
Input becomes output.
## Capabilities
- Grounded checks.
## Supported Scenarios
- Repository publishing.
## Example
This is fictional.
## Inputs and Outputs
Text in, report out.
## Repository Structure
- [Skill](SKILL.md)
## Privacy and Safety
Authorized data only.
## Current Version Boundaries
No automatic external writes.
## Contributing
Use anonymized data.
## License
No open-source license granted.
`;

function fixture(readme = validReadme) {
  const directory = mkdtempSync(path.join(os.tmpdir(), 'skill-publisher-'));
  writeFileSync(path.join(directory, 'SKILL.md'), '---\nname: demo-skill\ndescription: Use when demonstrating repository audit behavior.\n---\n');
  writeFileSync(path.join(directory, 'README.md'), readme);
  return directory;
}

function audit(directory) {
  return spawnSync('python3', [auditScript, '--skill-root', directory, '--repo-owner', 'OWENWANG-GULIAI', '--repo-name', 'demo-skill', '--json'], { encoding: 'utf8' });
}

function collectionFixture() {
  const directory = mkdtempSync(path.join(os.tmpdir(), 'skill-collection-'));
  mkdirSync(path.join(directory, 'skills', 'demo-skill'), { recursive: true });
  writeFileSync(path.join(directory, 'README.md'), `# Demo Skills

## 快速开始

\`\`\`bash
git clone https://github.com/OWENWANG-GULIAI/demo-skills.git
\`\`\`

## 技能目录

查看 [catalog](catalog.json)。

## 许可说明

每个包保留各自许可证，详见 [LICENSES](LICENSES.md)。
`);
  writeFileSync(path.join(directory, 'LICENSES.md'), '# 许可说明\n\n仅提供包级许可。\n');
  writeFileSync(path.join(directory, 'catalog.json'), JSON.stringify({
    schema_version: '1.0',
    packages: [{
      id: 'demo-skill',
      path: 'skills/demo-skill',
      source_repository: 'https://github.com/OWENWANG-GULIAI/demo-skill',
      license: 'MIT',
    }],
  }));
  writeFileSync(path.join(directory, 'skills', 'demo-skill', 'SKILL.md'), '---\nname: demo-skill\ndescription: Use when testing a collection audit.\n---\n');
  writeFileSync(path.join(directory, 'skills', 'demo-skill', 'LICENSE'), 'MIT License\n');
  return directory;
}

function auditCollection(directory) {
  return spawnSync('python3', [auditScript, '--collection-root', directory, '--repo-owner', 'OWENWANG-GULIAI', '--repo-name', 'demo-skills', '--json'], { encoding: 'utf8' });
}

test('仓库包含可发布 Skill 的完整结构', () => {
  for (const relativePath of ['SKILL.md', 'README.md', 'LICENSE', 'agents/openai.yaml', 'assets/README.template.md', 'references/readme-standard.md', 'references/publishing-workflow.md', 'references/privacy-and-license.md', 'scripts/audit_skill_repository.py']) {
    assert.equal(existsSync(path.join(root, relativePath)), true, `missing ${relativePath}`);
  }
});

test('人类阅读的 Skill 指令以中文为主', () => {
  for (const relativePath of ['SKILL.md', 'references/readme-standard.md', 'references/publishing-workflow.md', 'references/privacy-and-license.md']) {
    const content = readFileSync(path.join(root, relativePath), 'utf8');
    const han = (content.match(/[\u3400-\u9fff]/g) ?? []).length;
    const latin = (content.match(/[A-Za-z]{2,}/g) ?? []).length;
    assert.ok(han >= 80 && han > latin, `${relativePath} is not Chinese-first`);
  }
});

test('审计器接受结构完整且有事实依据的仓库', (t) => {
  const directory = fixture();
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const result = audit(directory);
  assert.equal(result.status, 0, result.stderr || result.stdout);
  assert.equal(JSON.parse(result.stdout).ok, true);
});

test('审计器接受包级许可的 Skill 合集而不要求根 SKILL 或根 LICENSE', (t) => {
  const directory = collectionFixture();
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const result = auditCollection(directory);
  assert.equal(result.status, 0, result.stderr || result.stdout);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.ok, true);
  assert.equal(payload.mode, 'collection');
  assert.equal(payload.checks.packages, 1);
});

test('审计器拒绝旧 owner、失效链接和敏感信息', (t) => {
  const directory = fixture(validReadme.replace('OWENWANG-GULIAI/demo-skill', 'old-owner/demo-skill').replace('[Skill](SKILL.md)', '[Missing](missing.md)'));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  mkdirSync(path.join(directory, 'examples'));
  const token = `ghp_${'a'.repeat(36)}`;
  const email = ['alice', 'example.com'].join('@');
  const phone = ['138', '0013', '8000'].join('');
  const localPath = ['/', 'Users', 'alice', 'private'].join('/').replace('//', '/');
  writeFileSync(path.join(directory, 'examples', 'unsafe.md'), `Email: ${email}\nPhone: ${phone}\nPath: ${localPath}\nToken: ${token}\n`);
  const result = audit(directory);
  assert.equal(result.status, 1, result.stderr || result.stdout);
  const codes = JSON.parse(result.stdout).errors.map((entry) => entry.code);
  for (const code of ['owner-drift', 'broken-link', 'email', 'phone', 'local-path', 'credential']) assert.ok(codes.includes(code), `missing ${code}`);
});

test('审计器拒绝缺少专业结构的 README', (t) => {
  const directory = fixture('# Demo Skill\n\nTiny summary.\n');
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const result = audit(directory);
  assert.equal(result.status, 1, result.stderr || result.stdout);
  assert.ok(JSON.parse(result.stdout).errors.filter((entry) => entry.code === 'readme-section').length >= 5);
});
