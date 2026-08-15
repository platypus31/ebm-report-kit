"""Tests for generate_platform_config.py — cross-platform config generation.

契約：`CLAUDE.md` 是唯一權威，其他平台檔＝「該平台 header 一行 ＋ CLAUDE.md 全文」。
"""

from pathlib import Path

import pytest

from scripts.generate_platform_config import (
    BASE_DIR,
    DERIVED_PLATFORMS,
    PLATFORMS,
    SOURCE_FILENAME,
    SOURCE_PLATFORM,
    check_platform,
    generate_config,
    write_config,
)

SOURCE_TEXT = (BASE_DIR / SOURCE_FILENAME).read_text(encoding="utf-8")


class TestGenerateConfig:
    def test_all_platforms_generate(self):
        for platform in PLATFORMS:
            content = generate_config(platform)
            assert len(content) > 100, f"{platform} config is too short"

    def test_source_platform_is_claude_md_verbatim(self):
        assert generate_config(SOURCE_PLATFORM) == SOURCE_TEXT

    def test_derived_platforms_are_header_plus_source(self):
        for platform in DERIVED_PLATFORMS:
            header = PLATFORMS[platform]["header"]
            assert header, f"{platform} 缺 header"
            assert generate_config(platform) == f"{header}\n\n{SOURCE_TEXT}"

    def test_derived_headers_point_back_to_source(self):
        for platform in DERIVED_PLATFORMS:
            assert SOURCE_FILENAME in PLATFORMS[platform]["header"]

    def test_unknown_platform_rejected(self):
        with pytest.raises(SystemExit):
            generate_config("not-a-platform")

    def test_all_platforms_have_shared_content(self):
        for platform in PLATFORMS:
            content = generate_config(platform)
            assert "EBM Report Kit" in content
            assert "6A" in content
            assert "PICO" in content
            assert "projects/<name>/" in content
            assert "init_project.py" in content
            assert "繁體中文" in content

    def test_claude_has_slash_commands(self):
        content = generate_config("claude")
        assert "/ebm-from-paper" in content
        assert "/ebm" in content
        assert "/pico" in content


class TestPlatformDefinitions:
    def test_platform_filenames(self):
        assert PLATFORMS["claude"]["filename"] == "CLAUDE.md"
        assert PLATFORMS["gemini"]["filename"] == "GEMINI.md"
        assert PLATFORMS["cursor"]["filename"] == ".cursorrules"
        assert PLATFORMS["copilot"]["filename"] == ".github/copilot-instructions.md"
        assert PLATFORMS["codex"]["filename"] == "AGENTS.md"

    def test_derived_excludes_source(self):
        assert SOURCE_PLATFORM not in DERIVED_PLATFORMS
        assert set(DERIVED_PLATFORMS) | {SOURCE_PLATFORM} == set(PLATFORMS)

    def test_source_platform_refuses_to_be_written(self):
        """不能用本工具覆寫 CLAUDE.md——它是來源，覆寫它等於自我循環。"""
        with pytest.raises(SystemExit):
            write_config(SOURCE_PLATFORM)


class TestOnDiskSync:
    """漂移偵測：實際檔案必須與 CLAUDE.md 同步。

    這是本檔最重要的一條——曾發生過「commit 訊息宣稱同步了四平台檔、實際只改到 CLAUDE.md」
    而數日無人察覺的情況；有這條測試就會當場紅燈。
    """

    def test_all_derived_files_in_sync(self):
        stale = [PLATFORMS[p]["filename"] for p in DERIVED_PLATFORMS if not check_platform(p)]
        assert not stale, (
            f"以下平台檔與 {SOURCE_FILENAME} 不同步：{stale}；"
            f"跑 `python3 scripts/generate_platform_config.py` 重新產生。"
        )

    def test_derived_files_exist(self):
        for platform in DERIVED_PLATFORMS:
            path = Path(BASE_DIR) / PLATFORMS[platform]["filename"]
            assert path.is_file(), f"{path} 不存在"
