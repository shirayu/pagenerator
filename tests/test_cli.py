import unittest

from pagenerator.cli import get_og_description, get_title


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


if __name__ == "__main__":
    unittest.main()
