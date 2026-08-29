"""Tests for gen_teaching_figures.py — 六張自繪教學圖與 gen_journal_svg 的 asset 頁型。"""

import re

import pytest

from scripts import gen_teaching_figures as gtf
from scripts.gen_journal_svg import H, W, build

EXPECTED = [
    "evidence-pyramid-6s",
    "ocebm-2011-levels-en",
    "ocebm-2011-levels-zh",
    "appraisal-tool-selection",
    "appraisal-workflow",
    "appraisal-vip",
]


@pytest.fixture(scope="module")
def figures(tmp_path_factory):
    """跑一次生成器，把產出與 stderr 一起交給下面所有測試。"""
    out = tmp_path_factory.mktemp("assets")
    import io
    import sys
    err = io.StringIO()
    orig, sys.stderr = sys.stderr, err
    try:
        paths = gtf.build(str(out))
    finally:
        sys.stderr = orig
    return out, paths, err.getvalue()


class TestBuild:
    def test_generates_all_six(self, figures):
        out, paths, _ = figures
        assert len(paths) == 6
        assert sorted(p.name for p in out.iterdir()) == sorted(f"{n}.svg" for n in EXPECTED)

    def test_no_layout_warnings(self, figures):
        """版面契約破了（圖本體壓到 caption 帶／表格縮到最小字級仍塞不下）會印 WARN。"""
        _out, _paths, err = figures
        assert "WARN" not in err, err

    def test_full_page_viewbox(self, figures):
        """asset 頁型只認 1280x720 全頁 SVG，尺寸跑掉會靜默退回佔位框。"""
        out, _paths, _ = figures
        for name in EXPECTED:
            svg = (out / f"{name}.svg").read_text(encoding="utf-8")
            assert f'viewBox="0 0 {W} {H}"' in svg, name
            assert svg.rstrip().endswith("</svg>"), name

    def test_has_source_note(self, figures):
        """每張圖底部都要有出處註記——這是它能隨公開 repo 散布的依據。"""
        out, _paths, _ = figures
        for name in EXPECTED:
            svg = (out / f"{name}.svg").read_text(encoding="utf-8")
            assert "自繪" in svg or "自行翻譯" in svg, name

    def test_no_raster_image_embedded(self, figures):
        """全向量：不得有 <image>／base64（有的話代表混進了外部點陣圖）。"""
        out, _paths, _ = figures
        for name in EXPECTED:
            svg = (out / f"{name}.svg").read_text(encoding="utf-8")
            assert "<image" not in svg, name
            assert "base64" not in svg, name

    def test_text_within_canvas(self, figures):
        """所有 <text> 的估算邊界都要落在畫布內。

        直向由生成器的 check_overflow 顧，橫向出血它看不見——但 ppt-master 的 svg_quality_checker
        會判 blocking error，所以在這裡用同一套字寬估算先擋住（CI 沒有 ppt-master 可跑）。
        每單位寬取 0.53×字級（全形 2 單位／半形 1 單位），比 svg_quality_checker 實測反推的
        0.511 保守一點，才不會估太鬆漏抓。
        """
        pat = re.compile(
            r'<text x="([-\d.]+)" y="([-\d.]+)" font-family="[^"]*" font-size="([\d.]+)"'
            r'[^>]*text-anchor="(\w+)"[^>]*>(.*?)</text>')
        out, _paths, _ = figures
        for name in EXPECTED:
            svg = (out / f"{name}.svg").read_text(encoding="utf-8")
            assert len(pat.findall(svg)) == svg.count("<text "), f"{name}: <text> 正則沒吃到全部"
            for x, y, fs, anchor, body in pat.findall(svg):
                x, y, fs = float(x), float(y), float(fs)
                width = sum(2 if ord(ch) > 0x2E80 else 1 for ch in body) * fs * 0.53
                left = x - width / 2 if anchor == "middle" else x
                assert 0 <= left and left + width <= W, f"{name}: 「{body[:20]}」橫向出血"
                assert 0 <= y <= H, f"{name}: y={y}"


class TestWrap:
    def test_no_orphan_closing_punct(self):
        """禁則：收尾標點不得落在行首（否則「）」會孤零零自成一行）。"""
        lines = gtf.wrap("這個介入治療有幫助嗎？（治療益處）", 16)
        assert len(lines) > 1
        assert not any(ln[0] in gtf._NO_LINE_START for ln in lines[1:]), lines

    def test_no_orphan_opening_punct(self):
        """禁則：起始括號不得落在行尾。"""
        lines = gtf.wrap("評定證據等級（對照 OCEBM 2011 的等級表）", 14)
        assert not any(ln[-1] in gtf._NO_LINE_END for ln in lines[:-1]), lines

    def test_footnote_marker_not_orphaned(self):
        lines = gtf.wrap("切合當地環境普查的系統性回顧**", 14)
        assert not any(ln.startswith("*") for ln in lines[1:]), lines

    def test_terminates_on_consecutive_punct(self):
        """連續標點不能讓推字迴圈打轉。"""
        assert gtf.wrap("測試」）。」）。」）", 4)

    def test_short_text_untouched(self):
        assert gtf.wrap("短句", 20) == ["短句"]

    def test_second_shift_is_actually_needed(self):
        """連續禁則（如「，」後接「**」）要能連搬兩次——KINSOKU_MAX_SHIFT 不是白設的。"""
        assert gtf.KINSOKU_MAX_SHIFT >= 2
        lines = gtf.wrap("系列病例報告，病例對照試驗，或歷史對照試驗**", 12)
        assert not any(ln[0] in gtf._NO_LINE_START for ln in lines[1:]), lines


class TestWrapFit:
    CASES = [
        "非隨機控制的世代／追蹤研究（上市後監測）**",
        "系列病例報告，病例對照試驗，或歷史對照試驗**",
        "這個介入治療有幫助嗎？（治療益處）",
        "評定證據等級（對照 OCEBM 2011 的等級表）",
        "（（（測試）））、、。**",
        "Mechanism-based reasoning",
        "SR of randomized trials, SR of nested case-control studies, n-of-1 trial",
        "a",
        "",
    ]

    def test_never_exceeds_width(self):
        """行寬保證：禁則推字會讓下一行變長，wrap_fit 必須把它壓回欄寬內。

        超寬是橫向出血——check_overflow 只驗直向、完全沒有訊號，而 ppt-master 的
        svg_quality_checker 會判 blocking error。units=1 排除在外：一個全形字就是 2 單位，
        任何斷行法都塞不進 1 單位。
        """
        for units in range(2, 60):
            for s in self.CASES:
                for ln in gtf.wrap_fit(s, units):
                    assert gtf.text_units(ln) <= units, f"units={units} 行={ln!r}"

    def test_no_upfront_slack_penalty_on_narrow_columns(self):
        """窄欄不該因為「預留餘裕」被逼到逐字硬切（舊 KINSOKU_SLACK 作法的病灶）。"""
        assert gtf.wrap_fit("Mechanism-based reasoning", 15) == ["Mechanism-based", "reasoning"]


class TestSourceNote:
    def test_single_line_at_note_baseline(self):
        s = []
        gtf.source_note(s, "t", "短短的出處")
        assert f'y="{gtf.NOTE_Y}"' in s[0]

    def test_warns_when_wrapping_into_caption_band(self):
        """出處註記往上長會壓到 caption 帶，check_overflow 只驗往下那一邊，這裡要自己出聲。"""
        import io
        import sys
        err = io.StringIO()
        orig, sys.stderr = sys.stderr, err
        try:
            gtf.source_note([], "t", "依" + "很長的出處說明" * 20)
        finally:
            sys.stderr = orig
        assert "壓到 caption 帶" in err.getvalue()


class TestAssetSlide:
    def _content(self, path):
        return {"cover": {"title": ["T"]},
                "slides": [{"kind": "asset", "title": "等級表", "caption": "本文 Level 3",
                            "path": str(path)}]}

    def test_passthrough_and_caption(self, figures, tmp_path):
        """合格素材原樣輸出，caption 疊在版面契約留給它的位置。"""
        out, _paths, _ = figures
        src = out / "ocebm-2011-levels-zh.svg"
        deck = tmp_path / "svg_output"
        build_json = tmp_path / "content.json"
        import json
        build_json.write_text(json.dumps(self._content(src)), encoding="utf-8")
        build(str(build_json), str(deck))
        page = deck / "02_as_等級表.svg"
        assert page.exists(), sorted(p.name for p in deck.iterdir())
        got = page.read_text(encoding="utf-8")
        assert "本文 Level 3" in got
        assert got.count("</svg>") == 1
        # 素材本體原封不動：疊 caption 只在結尾加一行
        assert src.read_text(encoding="utf-8").rstrip()[:-len("</svg>")] in got

    def test_missing_asset_falls_back_to_placeholder(self, tmp_path):
        """素材缺失要退回佔位框並留下 WARN，不能靜默產出空白頁。"""
        import io
        import json
        import sys
        deck = tmp_path / "svg_output"
        cj = tmp_path / "content.json"
        cj.write_text(json.dumps(self._content(tmp_path / "nope.svg")), encoding="utf-8")
        err = io.StringIO()
        orig, sys.stderr = sys.stderr, err
        try:
            build(str(cj), str(deck))
        finally:
            sys.stderr = orig
        got = (deck / "02_as_等級表.svg").read_text(encoding="utf-8")
        assert "[ Teaching Figure ]" in got
        assert "WARN" in err.getvalue()

    def test_non_utf8_asset_falls_back(self, tmp_path):
        """壞編碼的素材要退回佔位框，不能讓整個 build() 崩掉。

        UnicodeDecodeError 不是 OSError 的子類，只攔 OSError 會漏掉這條路徑。
        """
        import io
        import json
        import sys
        bad = tmp_path / "latin1.svg"
        bad.write_bytes(b'<svg viewBox="0 0 1280 720">\xff\xfe not utf-8</svg>')
        deck = tmp_path / "svg_output"
        cj = tmp_path / "content.json"
        cj.write_text(json.dumps(self._content(bad)), encoding="utf-8")
        err = io.StringIO()
        orig, sys.stderr = sys.stderr, err
        try:
            build(str(cj), str(deck))   # 不得拋例外
        finally:
            sys.stderr = orig
        assert "[ Teaching Figure ]" in (deck / "02_as_等級表.svg").read_text(encoding="utf-8")
        assert "編碼不對" in err.getvalue()

    def test_wrong_size_svg_rejected(self, tmp_path):
        """非 1280x720 的 SVG 不能被當全頁素材貼上去（會變成半張圖）。"""
        import io
        import json
        import sys
        bad = tmp_path / "bad.svg"
        bad.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"></svg>',
                       encoding="utf-8")
        deck = tmp_path / "svg_output"
        cj = tmp_path / "content.json"
        cj.write_text(json.dumps(self._content(bad)), encoding="utf-8")
        err = io.StringIO()
        orig, sys.stderr = sys.stderr, err
        try:
            build(str(cj), str(deck))
        finally:
            sys.stderr = orig
        assert "[ Teaching Figure ]" in (deck / "02_as_等級表.svg").read_text(encoding="utf-8")
        assert "viewBox 不符" in err.getvalue()
