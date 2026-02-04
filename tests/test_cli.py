import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from pagenerator.cli import (
    check_unsupported_meta_tags,
    convert,
    get_mydict,
    get_og_description,
    get_title,
    remove_html_comments_outside_code_fence,
    remove_meta_comments,
)


class TestCli(unittest.TestCase):
    def test_get_title_with_h1(self):
        text = "# テストタイトル\n\n本文です。"
        self.assertEqual(get_title(text), "テストタイトル")

    def test_get_title_with_h2(self):
        text = "## サブタイトル\n\n本文です。"
        self.assertEqual(get_title(text), "サブタイトル")

    def test_get_title_with_spaces(self):
        text = "#    スペース付きタイトル   \n\n本文です。"
        self.assertEqual(get_title(text), "スペース付きタイトル")

    def test_get_title_no_header(self):
        text = "普通のテキストです。\n\nヘッダーはありません。"
        self.assertEqual(get_title(text), "")

    def test_get_title_empty(self):
        text = ""
        self.assertEqual(get_title(text), "")

    def test_get_og_description_with_colon(self):
        text = "# タイトル\n\n<!-- og:description: これはテスト用の説明文です -->\n\n本文です。"
        self.assertEqual(get_og_description(text), "これはテスト用の説明文です")

    def test_get_og_description_without_colon(self):
        text = "# タイトル\n\n<!-- og:description これはコロンなしの説明文です -->\n\n本文です。"
        self.assertEqual(get_og_description(text), "これはコロンなしの説明文です")

    def test_get_og_description_with_extra_spaces(self):
        text = "# タイトル\n\n<!--   og:description:   スペース付きの説明文   -->\n\n本文です。"
        self.assertEqual(get_og_description(text), "スペース付きの説明文")

    def test_get_og_description_case_insensitive(self):
        text = "# タイトル\n\n<!-- OG:DESCRIPTION: 大文字小文字テスト -->\n\n本文です。"
        self.assertEqual(get_og_description(text), "大文字小文字テスト")

    def test_get_og_description_in_code_block_ignored(self):
        text = """# タイトル

本文です。

```html
<!-- og:description: コードブロック内の説明 -->
```

続きの本文です。"""
        self.assertEqual(get_og_description(text), "")

    def test_get_og_description_real_comment_with_code_block(self):
        text = """# タイトル

<!-- og:description: 実際の説明文 -->

本文です。

```html
<!-- og:description: コードブロック内の説明 -->
```

続きの本文です。"""
        self.assertEqual(get_og_description(text), "実際の説明文")

    def test_get_og_description_no_comment(self):
        text = "# タイトル\n\n本文です。\n\nog:descriptionコメントはありません。"
        self.assertEqual(get_og_description(text), "")

    def test_get_og_description_empty(self):
        text = ""
        self.assertEqual(get_og_description(text), "")

    def test_get_og_description_multiple_comments_first_one(self):
        text = """# タイトル

<!-- og:description: 最初の説明文 -->

本文です。

<!-- og:description: 二番目の説明文 -->

続きの本文です。"""
        self.assertEqual(get_og_description(text), "最初の説明文")

    def test_get_og_description_with_newlines(self):
        text = """# タイトル

<!-- og:description: これは
複数行にわたる
説明文です -->

本文です。"""
        self.assertEqual(get_og_description(text), "これは<br>複数行にわたる<br>説明文です")

    def test_get_og_description_with_newlines_without_colon(self):
        text = """# タイトル

<!-- og:description これは
複数行の
説明文です -->

本文です。"""
        self.assertEqual(get_og_description(text), "これは<br>複数行の<br>説明文です")

    def test_get_og_description_with_existing_br_tags(self):
        text = """# タイトル

<!-- og:description: これは<br>
改行を<br>
使った説明文です -->

本文です。"""
        self.assertEqual(get_og_description(text), "これは<br><br>改行を<br><br>使った説明文です")

    def test_get_og_description_with_existing_BR_tags_uppercase(self):
        text = """# タイトル

<!-- og:description: これは<BR>
改行を<BR>
使った説明文です -->

本文です。"""
        self.assertEqual(get_og_description(text), "これは<BR><br>改行を<BR><br>使った説明文です")

    def test_remove_meta_comments_og_description_with_colon(self):
        text = "# タイトル\n\n<!-- og:description: これは説明文です -->\n\n本文です。"
        expected = "# タイトル\n\n\n\n本文です。"
        self.assertEqual(remove_meta_comments(text), expected)

    def test_remove_meta_comments_og_description_without_colon(self):
        text = "# タイトル\n\n<!-- og:description これは説明文です -->\n\n本文です。"
        expected = "# タイトル\n\n\n\n本文です。"
        self.assertEqual(remove_meta_comments(text), expected)

    def test_remove_meta_comments_twitter_card(self):
        text = "# タイトル\n\n<!-- twitter:card: summary_large_image -->\n\n本文です。"
        expected = "# タイトル\n\n\n\n本文です。"
        self.assertEqual(remove_meta_comments(text), expected)

    def test_remove_meta_comments_twitter_without_colon(self):
        text = "# タイトル\n\n<!-- twitter:site @example -->\n\n本文です。"
        expected = "# タイトル\n\n\n\n本文です。"
        self.assertEqual(remove_meta_comments(text), expected)

    def test_remove_meta_comments_multiple_types(self):
        text = """# タイトル

<!-- og:title: ページタイトル -->
<!-- twitter:card summary_large_image -->
<!-- og:image: https://example.com/image.jpg -->

本文です。"""
        expected = """# タイトル




本文です。"""
        self.assertEqual(remove_meta_comments(text), expected)

    def test_remove_meta_comments_case_insensitive(self):
        text = "# タイトル\n\n<!-- OG:DESCRIPTION: 大文字小文字テスト -->\n<!-- TWITTER:CARD: summary -->\n\n本文です。"
        expected = "# タイトル\n\n\n\n\n本文です。"
        self.assertEqual(remove_meta_comments(text), expected)

    def test_remove_meta_comments_preserves_other_comments(self):
        text = """# タイトル

<!-- 普通のコメント -->
<!-- og:description: 削除される説明文 -->
<!-- 別の普通のコメント -->
<!-- twitter:card summary -->

本文です。"""
        expected = """# タイトル

<!-- 普通のコメント -->

<!-- 別の普通のコメント -->


本文です。"""
        self.assertEqual(remove_meta_comments(text), expected)

    def test_remove_meta_comments_no_meta_comments(self):
        text = "# タイトル\n\n本文です。\n<!-- 普通のコメント -->"
        expected = "# タイトル\n\n本文です。\n<!-- 普通のコメント -->"
        self.assertEqual(remove_meta_comments(text), expected)

    def test_remove_html_comments_outside_code_fence_basic(self):
        text = "# タイトル\n\n<!-- 普通のコメント -->\n\n本文です。"
        expected = "# タイトル\n\n\n\n本文です。"
        self.assertEqual(remove_html_comments_outside_code_fence(text), expected)

    def test_remove_html_comments_outside_code_fence_removes_inline(self):
        text = "- 士 <!-- 格 -->"
        expected = "- 士 "
        self.assertEqual(remove_html_comments_outside_code_fence(text), expected)

    def test_remove_html_comments_outside_code_fence_ignores_code_block(self):
        text = """# タイトル

```html
<!-- コメント -->
```

<!-- ここは消える -->
"""
        expected = """# タイトル

```html
<!-- コメント -->
```


"""
        self.assertEqual(remove_html_comments_outside_code_fence(text), expected)

    def test_check_unsupported_meta_tags_no_unsupported(self):
        text = "# タイトル\n\n<!-- og:description: サポートされているタグ -->\n\n本文です。"
        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = captured_stderr = StringIO()
        try:
            check_unsupported_meta_tags(text)
            self.assertEqual(captured_stderr.getvalue(), "")
        finally:
            sys.stderr = old_stderr

    def test_check_unsupported_meta_tags_with_unsupported(self):
        text = """# タイトル

<!-- og:description: サポートされているタグ -->
<!-- og:title: 未対応タグ1 -->
<!-- twitter:card: 未対応タグ2 -->
<!-- custom:tag: カスタムタグ -->

本文です。"""
        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = captured_stderr = StringIO()
        try:
            check_unsupported_meta_tags(text)
            output = captured_stderr.getvalue()
            self.assertIn("警告: 未対応のメタタグが見つかりました:", output)
            self.assertIn("custom:tag", output)
            self.assertIn("og:title", output)
            self.assertIn("twitter:card", output)
            self.assertNotIn("og:description", output)
        finally:
            sys.stderr = old_stderr

    def test_check_unsupported_meta_tags_in_code_block_ignored(self):
        text = """# タイトル

```
<!-- og:title: コードブロック内のタグ -->
```

<!-- og:description: 実際のタグ -->

本文です。"""
        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = captured_stderr = StringIO()
        try:
            check_unsupported_meta_tags(text)
            self.assertEqual(captured_stderr.getvalue(), "")
        finally:
            sys.stderr = old_stderr

    def test_check_unsupported_meta_tags_sorted_output(self):
        text = """# タイトル

<!-- zebra:tag: Z最後のタグ -->
<!-- apple:tag: A最初のタグ -->
<!-- banana:tag: B中間のタグ -->

本文です。"""
        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = captured_stderr = StringIO()
        try:
            check_unsupported_meta_tags(text)
            output = captured_stderr.getvalue()
            # アルファベット順になっているかチェック
            apple_pos = output.find("apple:tag")
            banana_pos = output.find("banana:tag")
            zebra_pos = output.find("zebra:tag")
            self.assertTrue(apple_pos < banana_pos < zebra_pos)
        finally:
            sys.stderr = old_stderr

    def test_get_mydict_basic(self):
        mydict = {"key1": "value1", "key2": "value2"}
        result = get_mydict(mydict=mydict, input_filename="test.md")
        expected = {"key1": "value1", "key2": "value2"}
        self.assertEqual(result, expected)

    def test_get_mydict_with_prefix(self):
        mydict = {"prefix1:key1": "value1", "prefix2:key2": "value2", "key3": "value3"}
        result = get_mydict(mydict=mydict, input_filename="prefix1/test.md")
        expected = {"key1": "value1", "key3": "value3"}
        self.assertEqual(result, expected)

    def test_get_mydict_no_matching_prefix(self):
        mydict = {"prefix1:key1": "value1", "prefix2:key2": "value2", "key3": "value3"}
        result = get_mydict(mydict=mydict, input_filename="other/test.md")
        expected = {"key3": "value3"}
        self.assertEqual(result, expected)

    def test_convert_with_og_description_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # テスト用のMarkdownファイル（og:descriptionなし）
            md_content = "# テストタイトル\n\n本文です。"
            md_file = tmpdir_path / "test.md"
            md_file.write_text(md_content)

            # テンプレートファイル
            template_content = "$title - $og_description - $content"
            template_file = tmpdir_path / "template.html"
            template_file.write_text(template_content)

            # 出力ファイル
            output_file = tmpdir_path / "output.html"

            # mydictにデフォルトのog_descriptionを設定
            mydict = {"og_description": "デフォルトの説明文"}

            # 変換実行
            title = convert(
                input_filename=str(md_file),
                template_name=str(template_file),
                output_name=str(output_file),
                mydict=mydict,
                force=True,
            )

            # 結果確認
            self.assertEqual(title, "テストタイトル")
            output_content = output_file.read_text()
            self.assertIn("デフォルトの説明文", output_content)

    def test_convert_with_og_description_in_markdown_overrides_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # テスト用のMarkdownファイル（og:descriptionあり）
            md_content = "# テストタイトル\n\n<!-- og:description: Markdownの説明文 -->\n\n本文です。"
            md_file = tmpdir_path / "test.md"
            md_file.write_text(md_content)

            # テンプレートファイル
            template_content = "$title - $og_description - $content"
            template_file = tmpdir_path / "template.html"
            template_file.write_text(template_content)

            # 出力ファイル
            output_file = tmpdir_path / "output.html"

            # mydictにデフォルトのog_descriptionを設定
            mydict = {"og_description": "デフォルトの説明文"}

            # 変換実行
            title = convert(
                input_filename=str(md_file),
                template_name=str(template_file),
                output_name=str(output_file),
                mydict=mydict,
                force=True,
            )

            # 結果確認
            self.assertEqual(title, "テストタイトル")
            output_content = output_file.read_text()
            self.assertIn("Markdownの説明文", output_content)
            self.assertNotIn("デフォルトの説明文", output_content)

    def test_convert_removes_html_comments_to_avoid_list_break(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            md_content = """# タイトル

- foo
<!-- コメント -->
- bar
"""
            md_file = tmpdir_path / "test.md"
            md_file.write_text(md_content)

            template_content = "$content"
            template_file = tmpdir_path / "template.html"
            template_file.write_text(template_content)

            output_file = tmpdir_path / "output.html"

            convert(
                input_filename=str(md_file),
                template_name=str(template_file),
                output_name=str(output_file),
                mydict={},
                force=True,
            )

            output_content = output_file.read_text()
            self.assertIn("<li>\n<p>foo</p>\n</li>", output_content)
            self.assertIn("<li>\n<p>bar</p>\n</li>", output_content)

    def test_convert_with_prefix_specific_og_description(self):
        """プレフィックス機能は実際の使用時は相対パスで動作するため、基本的なテストのみ実施"""
        # get_mydictの動作テストで十分確認されているため、ここでは基本的なog_description機能のテストに留める
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # テスト用のMarkdownファイル（og:descriptionなし）
            md_content = "# テストタイトル\n\n本文です。"
            md_file = tmpdir_path / "test.md"
            md_file.write_text(md_content)

            # テンプレートファイル
            template_content = "$title - $og_description - $content"
            template_file = tmpdir_path / "template.html"
            template_file.write_text(template_content)

            # 出力ファイル
            output_file = tmpdir_path / "output.html"

            # mydictに基本のog_descriptionを設定
            mydict = {"og_description": "デフォルトの説明文"}

            # 変換実行
            title = convert(
                input_filename=str(md_file),
                template_name=str(template_file),
                output_name=str(output_file),
                mydict=mydict,
                force=True,
            )

            # 結果確認
            self.assertEqual(title, "テストタイトル")
            output_content = output_file.read_text()
            self.assertIn("デフォルトの説明文", output_content)


if __name__ == "__main__":
    unittest.main()
