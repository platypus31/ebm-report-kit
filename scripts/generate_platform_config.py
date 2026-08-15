#!/usr/bin/env python3
"""
跨平台 AI 工具設定檔產生器。

`CLAUDE.md` 是**唯一權威**；其他平台的設定檔＝「該平台的 header 一行 ＋ CLAUDE.md 全文」：
  - Claude Code      → CLAUDE.md（來源，本工具不覆寫它）
  - Gemini CLI       → GEMINI.md
  - Cursor           → .cursorrules
  - GitHub Copilot   → .github/copilot-instructions.md
  - OpenAI Codex CLI → AGENTS.md

內容直接從 CLAUDE.md 讀取，不在本檔硬編任何文案——硬編過的版本曾與 CLAUDE.md 長期脫節，
執行它反而會用過期內容覆蓋掉正確的檔案。

用法：
    python3 scripts/generate_platform_config.py                    # 重新產生全部衍生檔
    python3 scripts/generate_platform_config.py --platform gemini  # 只產生 Gemini
    python3 scripts/generate_platform_config.py --check            # 只檢查是否同步（不寫檔）
    python3 scripts/generate_platform_config.py --list             # 列出支援的平台
"""

import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# CLAUDE.md 是單一權威來源
SOURCE_PLATFORM = "claude"
SOURCE_FILENAME = "CLAUDE.md"

# ── 平台定義 ──
# header：衍生檔的第一行標記（讓人一眼看出這是複本、真身在 CLAUDE.md）。
#         來源平台為 None。
PLATFORMS = {
    "claude": {
        "filename": SOURCE_FILENAME,
        "display_name": "Claude Code",
        "header": None,
    },
    "gemini": {
        "filename": "GEMINI.md",
        "display_name": "Gemini CLI",
        "header": "<!-- Gemini CLI 設定；內容同 CLAUDE.md -->",
    },
    "cursor": {
        "filename": ".cursorrules",
        "display_name": "Cursor",
        "header": "# Cursor 設定；內容同 CLAUDE.md",
    },
    "copilot": {
        "filename": ".github/copilot-instructions.md",
        "display_name": "GitHub Copilot",
        "header": "# GitHub Copilot 設定；內容同 CLAUDE.md",
    },
    "codex": {
        "filename": "AGENTS.md",
        "display_name": "OpenAI Codex CLI",
        "header": "<!-- OpenAI Codex CLI 設定；內容同 CLAUDE.md -->",
    },
}

DERIVED_PLATFORMS = [p for p in PLATFORMS if p != SOURCE_PLATFORM]


def read_source() -> str:
    """Read CLAUDE.md, the single source of truth."""
    source_path = BASE_DIR / SOURCE_FILENAME
    if not source_path.is_file():
        raise SystemExit(f"找不到權威來源 {source_path}——無法產生平台設定檔。")
    content = source_path.read_text(encoding="utf-8")
    if not content.strip():
        raise SystemExit(f"{source_path} 是空的——拒絕用空內容覆蓋平台設定檔。")
    return content


def generate_config(platform: str) -> str:
    """Generate the config content for a given platform (header + CLAUDE.md)."""
    if platform not in PLATFORMS:
        raise SystemExit(f"未知平台「{platform}」，須為 {sorted(PLATFORMS)}")
    header = PLATFORMS[platform]["header"]
    source = read_source()
    return source if header is None else f"{header}\n\n{source}"


def check_platform(platform: str) -> bool:
    """Return True if the on-disk file already matches what we would generate."""
    path = BASE_DIR / PLATFORMS[platform]["filename"]
    if not path.is_file():
        return False
    return path.read_text(encoding="utf-8") == generate_config(platform)


def write_config(platform: str, dry_run: bool = False) -> Path:
    """Write the config file for a platform. Returns the output path."""
    if platform == SOURCE_PLATFORM:
        raise SystemExit(
            f"{SOURCE_FILENAME} 是唯一權威來源，不由本工具產生——請直接編輯它，再重跑本工具同步其他平台。"
        )
    output_path = BASE_DIR / PLATFORMS[platform]["filename"]
    if dry_run:
        print(f"[DRY RUN] 會產生：{output_path}")
        return output_path
    content = generate_config(platform)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description=f"跨平台 AI 工具設定檔產生器（內容來源＝{SOURCE_FILENAME}）",
        epilog=(
            "範例：\n"
            "  python3 scripts/generate_platform_config.py                    # 全部衍生平台\n"
            "  python3 scripts/generate_platform_config.py --platform gemini  # 只產生 Gemini\n"
            "  python3 scripts/generate_platform_config.py --check            # 只檢查同步狀態\n"
            "  python3 scripts/generate_platform_config.py --list             # 列出支援的平台\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--platform",
        choices=DERIVED_PLATFORMS + ["all"],
        default="all",
        help="要產生的平台設定（預設：all；CLAUDE.md 是來源，不可產生）",
    )
    parser.add_argument("--list", action="store_true", help="列出所有支援的平台")
    # --check 與 --dry-run 都是「不寫檔」但語意不同，同時給會讓人誤以為兩者疊加，故互斥
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="只檢查各平台檔是否與 CLAUDE.md 同步（不寫檔）")
    mode.add_argument("--dry-run", action="store_true", help="只顯示會產生哪些檔案（不寫檔）")

    args = parser.parse_args()

    if args.list:
        print(f"內容權威來源：{SOURCE_FILENAME}\n")
        print("支援的平台：\n")
        for key, config in PLATFORMS.items():
            role = "（來源）" if key == SOURCE_PLATFORM else "（衍生）"
            print(f"  {key:10s} {role} → {config['filename']:40s} ({config['display_name']})")
        sys.exit(0)

    platforms = DERIVED_PLATFORMS if args.platform == "all" else [args.platform]

    if args.check:
        print(f"═══ 平台設定檔同步檢查（來源：{SOURCE_FILENAME}）═══\n")
        stale = [p for p in platforms if not check_platform(p)]
        for platform in platforms:
            mark = "✗ 不同步" if platform in stale else "✓ 同步"
            print(f"  {mark}  {PLATFORMS[platform]['filename']}")
        if stale:
            print(f"\n{len(stale)} 個檔案與 {SOURCE_FILENAME} 不同步——重跑本工具（不加 --check）即可修復。")
            sys.exit(1)
        print(f"\n全部 {len(platforms)} 個平台設定檔都與 {SOURCE_FILENAME} 同步。")
        sys.exit(0)

    print(f"═══ 跨平台設定檔產生器（來源：{SOURCE_FILENAME}）═══\n")
    for platform in platforms:
        path = write_config(platform, dry_run=args.dry_run)
        display = PLATFORMS[platform]["display_name"]
        print(f"  ✓ {display:20s} → {path.relative_to(BASE_DIR)}")

    if not args.dry_run:
        print(f"\n已產生 {len(platforms)} 個平台設定檔。")


if __name__ == "__main__":
    main()
