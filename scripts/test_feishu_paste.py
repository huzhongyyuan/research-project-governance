"""Converter tests; never touch the clipboard."""
import unittest

import feishu_paste


class ToHtmlTests(unittest.TestCase):
    def test_table_becomes_html_table(self):
        out = feishu_paste.to_html('| 指标 ↓ | 值 |\n|---|---|\n| FID | **1.6** |\n')
        self.assertIn('<table', out)
        self.assertIn('<th', out)
        self.assertIn('<b>1.6</b>', out)
        self.assertNotIn('|---', out)

    def test_comments_removed(self):
        out = feishu_paste.to_html('# 标题\n<!-- 提示\n多行 -->\n正文\n')
        self.assertNotIn('提示', out)
        self.assertIn('<h1>标题</h1>', out)

    def test_inline_code_escaped_and_links(self):
        out = feishu_paste.to_html('路径 `/out/<a>.mp4` 见 [文档](https://x.y/z)\n')
        self.assertIn('<code>/out/&lt;a&gt;.mp4</code>', out)
        self.assertIn('<a href="https://x.y/z">文档</a>', out)

    def test_lists_quote_and_fence(self):
        out = feishu_paste.to_html('> 说明\n\n- a\n- b\n\n1. x\n2. y\n\n```\n| not | table |\n```\n')
        self.assertIn('<blockquote>说明</blockquote>', out)
        self.assertIn('<ul><li>a</li><li>b</li></ul>', out)
        self.assertIn('<ol><li>x</li><li>y</li></ol>', out)
        self.assertIn('<pre>| not | table |</pre>', out)

    def test_pipe_text_without_separator_is_paragraph(self):
        out = feishu_paste.to_html('更新｜A | B\n')
        self.assertNotIn('<table', out)
        self.assertIn('<p>', out)


if __name__ == '__main__':
    unittest.main()
