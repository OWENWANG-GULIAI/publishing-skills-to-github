#!/usr/bin/env python3
"""Audit a Skill repository before public GitHub publication."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote


TEXT_SUFFIXES = {
    "", ".md", ".mdx", ".txt", ".yaml", ".yml", ".json", ".toml",
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh",
    ".html", ".css", ".xml", ".csv", ".ini", ".cfg", ".env",
}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".venv", "dist"}

SECTION_GROUPS = {
    "why": ("why", "为什么", "价值", "背景"),
    "quick-start": ("quick start", "getting started", "快速开始", "快速上手", "安装"),
    "usage": ("usage", "how to use", "使用方法", "调用", "用法"),
    "workflow": ("how it works", "workflow", "工作原理", "工作流程", "处理流程"),
    "capabilities": ("capabilities", "features", "核心能力", "功能"),
    "scenarios": ("supported scenarios", "use cases", "适用场景", "使用场景"),
    "example": ("example", "examples", "示例", "案例"),
    "inputs-outputs": ("inputs and outputs", "input and output", "输入与输出", "输入输出"),
    "structure": ("repository structure", "project structure", "仓库结构", "项目结构", "目录结构"),
    "privacy": ("privacy and safety", "privacy", "security", "隐私与安全", "隐私", "安全"),
    "boundaries": ("current version boundaries", "limitations", "版本边界", "当前边界", "限制"),
    "contributing": ("contributing", "contribution", "参与贡献", "贡献"),
    "license": ("license", "licence", "许可证", "许可"),
}


def issue(code: str, message: str, path: str, line: int | None = None) -> dict:
    item = {"code": code, "message": message, "path": path}
    if line is not None:
        item["line"] = line
    return item


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", "Dockerfile", "Makefile"}:
            continue
        try:
            if b"\x00" in path.read_bytes()[:4096]:
                continue
        except OSError:
            continue
        yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalized_headings(readme: str) -> list[str]:
    headings = []
    for match in re.finditer(r"(?m)^#{2,6}\s+(.+?)\s*$", readme):
        heading = re.sub(r"[`*_~]", "", match.group(1)).strip().casefold()
        headings.append(heading)
    return headings


def audit_readme(root: Path, owner: str, repo: str, errors: list[dict], warnings: list[dict]) -> None:
    readme_path = root / "README.md"
    if not readme_path.is_file():
        errors.append(issue("missing-readme", "README.md is required for GitHub publication.", "README.md"))
        return

    readme = read_text(readme_path)
    headings = normalized_headings(readme)
    for key, variants in SECTION_GROUPS.items():
        if not any(any(variant in heading for variant in variants) for heading in headings):
            errors.append(issue("readme-section", f"README is missing the professional section: {key}.", "README.md"))

    if not re.search(r"(?im)^#\s+\S", readme):
        errors.append(issue("readme-title", "README must have one clear H1 title.", "README.md"))

    if not re.search(r"```(?:bash|sh|shell|text)?\s*\n[\s\S]*?```", readme, re.IGNORECASE):
        warnings.append(issue("readme-example", "README has no fenced command or invocation example.", "README.md"))

    repo_url = re.compile(
        r"https?://github\.com/([^/\s)]+)/(" + re.escape(repo) + r")(?:\.git)?(?:[/#?\s)]|$)",
        re.IGNORECASE,
    )
    for match in repo_url.finditer(readme):
        found_owner = match.group(1)
        if found_owner.casefold() != owner.casefold():
            errors.append(issue(
                "owner-drift",
                f"Repository link uses owner '{found_owner}', expected '{owner}'.",
                "README.md",
                line_number(readme, match.start()),
            ))

    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for match in link_pattern.finditer(readme):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and raw_target.endswith(">"):
            raw_target = raw_target[1:-1]
        target = raw_target.split(maxsplit=1)[0].strip()
        if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
            continue
        target = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not target:
            continue
        resolved = (readme_path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(issue("broken-link", f"Local README link escapes the repository: {raw_target}", "README.md", line_number(readme, match.start())))
            continue
        if not resolved.exists():
            errors.append(issue("broken-link", f"Local README link does not exist: {raw_target}", "README.md", line_number(readme, match.start())))

    license_path = root / "LICENSE"
    if re.search(r"\bMIT(?: License)?\b", readme, re.IGNORECASE):
        if not license_path.is_file() or "mit license" not in read_text(license_path).casefold():
            errors.append(issue("license-mismatch", "README claims MIT, but LICENSE does not contain the MIT License.", "README.md"))


def audit_sensitive_data(root: Path, allow_emails: set[str], errors: list[dict]) -> int:
    email_pattern = re.compile(r"(?<![\w.+-])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})(?![\w.-])", re.IGNORECASE)
    phone_pattern = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
    id_pattern = re.compile(r"(?<!\d)\d{17}[0-9Xx](?!\d)")
    local_path_pattern = re.compile(re.escape("/" + "Users" + "/") + r"[^/\s]+(?:/[^\s)>'\"]+)?")
    credential_patterns = [
        re.compile(r"gh" + r"p_[A-Za-z0-9]{20,}"),
        re.compile(r"github" + r"_pat_[A-Za-z0-9_]{20,}"),
        re.compile(r"sk" + r"-[A-Za-z0-9]{20,}"),
        re.compile(r"AKIA[A-Z0-9]{16}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ]

    scanned = 0
    for path in iter_text_files(root):
        scanned += 1
        text = read_text(path)
        rel = path.relative_to(root).as_posix()
        for match in email_pattern.finditer(text):
            value = match.group(1).casefold()
            if value.endswith("@users.noreply.github.com") or value in allow_emails:
                continue
            errors.append(issue("email", "Direct email address may expose personal information.", rel, line_number(text, match.start())))
        for code, pattern, message in (
            ("phone", phone_pattern, "Phone-number-shaped value may expose personal information."),
            ("identity-number", id_pattern, "Identity-number-shaped value may expose personal information."),
            ("local-path", local_path_pattern, "Machine-specific absolute path must not be published."),
        ):
            for match in pattern.finditer(text):
                errors.append(issue(code, message, rel, line_number(text, match.start())))
        for pattern in credential_patterns:
            for match in pattern.finditer(text):
                errors.append(issue("credential", "Credential-shaped value must not be published.", rel, line_number(text, match.start())))
    return scanned


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", required=True, help="Root of the Skill repository to audit")
    parser.add_argument("--repo-owner", required=True, help="Expected GitHub owner")
    parser.add_argument("--repo-name", required=True, help="Expected GitHub repository name")
    parser.add_argument("--allow-email", action="append", default=[], help="Explicitly allowed public email; repeatable")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.skill_root).expanduser().resolve()
    errors: list[dict] = []
    warnings: list[dict] = []

    if not root.is_dir():
        result = {"ok": False, "skill_root": str(root), "checks": {"files_scanned": 0}, "errors": [issue("invalid-root", "Skill root is not a directory.", str(root))], "warnings": []}
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else "ERROR: Skill root is not a directory.")
        return 1

    if not (root / "SKILL.md").is_file():
        errors.append(issue("missing-skill", "SKILL.md is required.", "SKILL.md"))

    audit_readme(root, args.repo_owner, args.repo_name, errors, warnings)
    files_scanned = audit_sensitive_data(root, {email.casefold() for email in args.allow_email}, errors)
    result = {
        "ok": not errors,
        "skill_root": str(root),
        "repository": f"{args.repo_owner}/{args.repo_name}",
        "checks": {"files_scanned": files_scanned, "readme_sections": len(SECTION_GROUPS)},
        "errors": errors,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if result["ok"] else "FAIL")
        for item in errors:
            location = f"{item['path']}:{item.get('line', 1)}"
            print(f"ERROR [{item['code']}] {location} {item['message']}")
        for item in warnings:
            location = f"{item['path']}:{item.get('line', 1)}"
            print(f"WARN  [{item['code']}] {location} {item['message']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
