import re

def parse_markdown(markdown):
    def parse_inline(text):
        # Escape HTML special chars
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # Strong
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        # Em
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        # Code
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        # Image
        text = re.sub(r'!\[([^\]]*)\]\(([^)]*)\)', r'<img src="\2" alt="\1" />', text)
        # Link
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        return text

    lines = markdown.split('\n')
    html = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Blank line
        if line.strip() == '':
            i += 1
            continue

        # ATX Heading
        m = re.match(r'^(#{1,6})(\s+)(.*?)(\s+#+\s*)?$', line)
        if m:
            level = len(m.group(1))
            content = m.group(3).strip()
            content = re.sub(r'\s+#+\s*$', '', content).strip()
            html.append(f'<h{level}>{parse_inline(content)}</h{level}>')
            i += 1
            continue

        # Fenced code block
        m = re.match(r'^(`{3,}|~{3,})(.*)', line)
        if m:
            fence = m.group(1)
            info = m.group(2).strip()
            code_lines = []
            i += 1
            while i < len(lines) and not re.match(r'^' + re.escape(fence[:3]) + r'+\s*$', lines[i]):
                code_lines.append(lines[i])
                i += 1
            i += 1
            code = '\n'.join(code_lines) + '\n'
            lang = f' class="language-{info}"' if info else ''
            html.append(f'<pre><code{lang}>{code}</code></pre>')
            continue

        # Indented code block
        if line.startswith('    ') or line.startswith('\t'):
            code_lines = []
            while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t') or lines[i].strip() == ''):
                if lines[i].strip() == '':
                    code_lines.append('')
                else:
                    code_lines.append(lines[i][4:] if lines[i].startswith('    ') else lines[i][1:])
                i += 1
            # strip trailing blank lines
            while code_lines and code_lines[-1] == '':
                code_lines.pop()
            code = '\n'.join(code_lines) + '\n'
            html.append(f'<pre><code>{code}</code></pre>')
            continue

        # Blockquote
        if re.match(r'^>\s?', line):
            bq_lines = []
            while i < len(lines) and re.match(r'^>\s?', lines[i]):
                bq_lines.append(re.sub(r'^>\s?', '', lines[i]))
                i += 1
            inner = parse_markdown('\n'.join(bq_lines))
            html.append(f'<blockquote>\n{inner}\n</blockquote>')
            continue

        # Thematic break
        if re.match(r'^\s{0,3}(\*\s*){3,}\s*$|^\s{0,3}(-\s*){3,}\s*$|^\s{0,3}(_\s*){3,}\s*$', line):
            html.append('<hr />')
            i += 1
            continue

        # Setext heading
        if i + 1 < len(lines):
            if re.match(r'^=+\s*$', lines[i+1]):
                html.append(f'<h1>{parse_inline(line.strip())}</h1>')
                i += 2
                continue
            if re.match(r'^-+\s*$', lines[i+1]) and not re.match(r'^(-\s*){3,}\s*$', lines[i+1]):
                html.append(f'<h2>{parse_inline(line.strip())}</h2>')
                i += 2
                continue

        # Unordered list
        if re.match(r'^[-*+] ', line):
            items = []
            while i < len(lines) and re.match(r'^[-*+] ', lines[i]):
                items.append(parse_inline(lines[i][2:]))
                i += 1
            lis = '\n'.join(f'<li>{item}</li>' for item in items)
            html.append(f'<ul>\n{lis}\n</ul>')
            continue

        # Ordered list
        if re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                content = re.sub(r'^\d+\. ', '', lines[i])
                items.append(parse_inline(content))
                i += 1
            lis = '\n'.join(f'<li>{item}</li>' for item in items)
            html.append(f'<ol>\n{lis}\n</ol>')
            continue

        # Paragraph
        para_lines = []
        while i < len(lines) and lines[i].strip() != '' and \
              not re.match(r'^#{1,6}\s', lines[i]) and \
              not re.match(r'^[-*+] ', lines[i]) and \
              not re.match(r'^\d+\. ', lines[i]) and \
              not re.match(r'^>\s?', lines[i]) and \
              not re.match(r'^(`{3,}|~{3,})', lines[i]) and \
              not re.match(r'^\s{0,3}(\*\s*){3,}\s*$|^\s{0,3}(-\s*){3,}\s*$|^\s{0,3}(_\s*){3,}\s*$', lines[i]):
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            para = '\n'.join(para_lines)
            html.append(f'<p>{parse_inline(para)}</p>')

    return '\n'.join(html) + '\n'
