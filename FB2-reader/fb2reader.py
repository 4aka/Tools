import sys
import re
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextBrowser, QDockWidget,
    QListWidget, QListWidgetItem, QToolBar, QStatusBar, QFileDialog,
    QSlider, QLabel,
)
from PyQt6.QtGui import QAction, QKeySequence, QPalette, QColor
from PyQt6.QtCore import Qt, QUrl, QSize

# ── FB2 парсер ──────────────────────────────────────────────────────────────

def tag(el):
    return el.tag.split('}', 1)[-1] if '}' in el.tag else el.tag

def escape(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def el_to_html(el):
    t = tag(el)
    text = escape(el.text)
    tail = escape(el.tail)
    ch = ''.join(el_to_html(c) for c in el)
    if t == 'p':
        return f'<p>{text}{ch}</p>{tail}'
    if t in ('emphasis', 'em'):
        return f'<em>{text}{ch}</em>{tail}'
    if t == 'strong':
        return f'<strong>{text}{ch}</strong>{tail}'
    if t == 'strikethrough':
        return f'<s>{text}{ch}</s>{tail}'
    if t == 'code':
        return f'<code>{text}{ch}</code>{tail}'
    if t == 'empty-line':
        return f'<br/>{tail}'
    if t == 'v':
        return f'{text}{ch}<br/>{tail}'
    if t in ('stanza', 'poem', 'epigraph', 'cite'):
        return f'<blockquote>{text}{ch}</blockquote>{tail}'
    if t == 'a':
        href = el.get('{http://www.w3.org/1999/xlink}href', '#')
        if href.startswith('#'):
            href = 'anchor:' + href[1:]
        return f'<a href="{href}">{text}{ch}</a>{tail}'
    if t == 'image':
        return tail
    return f'{text}{ch}{tail}'

def section_to_html(sec, level=1):
    parts = []
    sec_id = sec.get('id', '')

    # Якір завжди на початку секції
    if sec_id:
        parts.append(f'<a name="{sec_id}"></a>')

    for child in sec:
        t = tag(child)
        if t == 'title':
            heading_text = ''.join(
                escape(p.text) + ''.join(el_to_html(c) for c in p)
                for p in child if tag(p) == 'p'
            )
            h = min(level + 1, 4)
            parts.append(f'<h{h}>{heading_text}</h{h}>')
        elif t == 'section':
            parts.append(section_to_html(child, level + 1))
        else:
            parts.append(el_to_html(child))

    return '\n'.join(parts)

def parse_fb2(path):
    """Повертає (book_title, [(label, anchor_id)], html_string)."""
    tree = ET.parse(path)
    root = tree.getroot()

    # Назва книги
    title = 'FB2 Reader'
    ti_el = root.find('.//{http://www.gribuser.ru/xml/fictionbook/2.0}book-title')
    if ti_el is not None and ti_el.text:
        title = ti_el.text.strip()

    body = root.find('{http://www.gribuser.ru/xml/fictionbook/2.0}body')
    if body is None:
        return title, [], '<p>Не вдалося знайти body.</p>'

    toc = []
    html_parts = []

    for idx, sec in enumerate(body):
        t = tag(sec)
        if t == 'title':
            for p in sec:
                html_parts.append(f'<h1>{escape(p.text)}</h1>')
        elif t == 'section':
            # Гарантуємо наявність id
            if not sec.get('id'):
                sec.set('id', f'sec_{idx}')
            anchor_id = sec.get('id')

            # Заголовок для TOC
            title_el = sec.find('{http://www.gribuser.ru/xml/fictionbook/2.0}title')
            if title_el is not None:
                label = ' '.join(
                    (p.text or '') for p in title_el if tag(p) == 'p'
                ).strip() or f'Розділ {len(toc)+1}'
            else:
                label = f'Розділ {len(toc)+1}'

            toc.append((label, anchor_id))
            html_parts.append(section_to_html(sec, level=1))
        else:
            html_parts.append(el_to_html(sec))

    full_html = (
        '<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
        'body{font-family:Georgia,serif;line-height:1.7;margin:20px 30px}'
        'h1{font-size:1.5em;text-align:center;margin:.8em 0}'
        'h2{font-size:1.25em;margin:1.2em 0 .4em}'
        'h3{font-size:1.1em;margin:1em 0 .3em}'
        'p{margin:0;text-indent:1.5em}'
        'blockquote{border-left:3px solid #aaa;margin:1em 2em;padding-left:1em;color:#555}'
        'a{color:#2255aa;text-decoration:none}'
        'a:hover{text-decoration:underline}'
        'code{font-family:Consolas,monospace;background:#eee;padding:0 3px}'
        '</style></head><body>'
        + '\n'.join(html_parts)
        + '</body></html>'
    )
    return title, toc, full_html

# ── Головне вікно ───────────────────────────────────────────────────────────

class FB2Reader(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        if len(sys.argv) > 1:
            self._load_file(sys.argv[1])

    def _setup_ui(self):
        self.resize(540, 960)
        self.setMinimumSize(360, 640)

        self.browser = QTextBrowser()
        self.browser.setOpenLinks(False)
        self.browser.anchorClicked.connect(self._on_link)
        self.browser.setStyleSheet('QTextBrowser{border:none}')
        self.setCentralWidget(self.browser)

        # TOC dock
        self.toc_dock = QDockWidget('Зміст', self)
        self.toc_list = QListWidget()
        self.toc_list.itemClicked.connect(self._on_toc_click)
        self.toc_dock.setWidget(self.toc_list)
        self.toc_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.toc_dock)
        self.toc_dock.hide()

        # Toolbar
        tb = QToolBar('Панель', self)
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        act_open = QAction('📂 Відкрити', self)
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self._open_file)
        tb.addAction(act_open)

        tb.addSeparator()

        self.act_toc = QAction('☰ Зміст', self)
        self.act_toc.setCheckable(True)
        self.act_toc.triggered.connect(lambda v: self.toc_dock.setVisible(v))
        tb.addAction(self.act_toc)
        self.toc_dock.visibilityChanged.connect(
            lambda v: self.act_toc.setChecked(v))

        tb.addSeparator()

        act_zi = QAction('A＋', self)
        act_zi.setShortcut(QKeySequence.StandardKey.ZoomIn)
        act_zi.triggered.connect(lambda: self.browser.zoomIn(1))
        tb.addAction(act_zi)

        act_zo = QAction('A－', self)
        act_zo.setShortcut(QKeySequence.StandardKey.ZoomOut)
        act_zo.triggered.connect(lambda: self.browser.zoomOut(1))
        tb.addAction(act_zo)

        act_zr = QAction('A', self)
        act_zr.setShortcut('Ctrl+0')
        act_zr.triggered.connect(self._zoom_reset)
        tb.addAction(act_zr)


        tb.addSeparator()

        lbl_warm = QLabel(' 🌡 ')
        tb.addWidget(lbl_warm)
        self.warm_slider = QSlider(Qt.Orientation.Horizontal)
        self.warm_slider.setRange(0, 100)
        self.warm_slider.setValue(0)
        self.warm_slider.setFixedWidth(90)
        self.warm_slider.setToolTip('Теплота екрана')
        self.warm_slider.valueChanged.connect(self._apply_warmth)
        tb.addWidget(self.warm_slider)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage('Відкрийте файл: Ctrl+O')

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Відкрити FB2', '', 'FB2 файли (*.fb2);;Всі файли (*.*)'
        )
        if path:
            self._load_file(path)

    def _load_file(self, path):
        try:
            book_title, toc, html = parse_fb2(path)
        except Exception as e:
            self.status.showMessage(f'Помилка: {e}')
            return

        self._html = html
        self._apply_warmth(self.warm_slider.value())
        font = self.browser.document().defaultFont()
        font.setPointSize(13)
        self.browser.document().setDefaultFont(font)
        self.setWindowTitle(f'{book_title} — FB2 Reader')
        self.status.showMessage(f'{book_title}  ·  {len(toc)} розділів')

        self.toc_list.clear()
        for label, anchor in toc:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, anchor)
            self.toc_list.addItem(item)

    def _on_toc_click(self, item):
        anchor = item.data(Qt.ItemDataRole.UserRole)
        self.browser.scrollToAnchor(anchor)
        # Закрити TOC після вибору
        self.toc_dock.hide()

    def _on_link(self, url: QUrl):
        if url.scheme() == 'anchor':
            self.browser.scrollToAnchor(url.path() or url.host())
        else:
            import webbrowser
            webbrowser.open(url.toString())

    def _zoom_reset(self):
        font = self.browser.document().defaultFont()
        font.setPointSize(13)
        self.browser.document().setDefaultFont(font)

    def _apply_warmth(self, value):
        """value 0..100: 0=cold white, 100=warm sepia."""
        def lerp(a, b, t): return int(a + (b - a) * t)
        t = value / 100
        bg = (lerp(0xfa, 0xf4, t), lerp(0xfa, 0xdf, t), lerp(0xfa, 0xa8, t))
        tx = (lerp(0x1a, 0x2b, t), lerp(0x1a, 0x18, t), lerp(0x1a, 0x00, t))
        bg_hex = '#{:02x}{:02x}{:02x}'.format(*bg)
        tx_hex = '#{:02x}{:02x}{:02x}'.format(*tx)

        # Палітра — фон і текст самого документа
        pal = self.browser.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(bg_hex))
        pal.setColor(QPalette.ColorRole.Text, QColor(tx_hex))
        self.browser.setPalette(pal)

        # defaultStyleSheet — до reload HTML
        self.browser.document().setDefaultStyleSheet(
            f'body{{background:{bg_hex};color:{tx_hex}}}'
            'h1{font-size:1.5em;text-align:center;margin:.8em 0}'
            'h2{font-size:1.25em;margin:1.2em 0 .4em}'
            'h3{font-size:1.1em;margin:1em 0 .3em}'
            'p{margin:0;text-indent:1.5em}'
            'blockquote{border-left:3px solid #aaa;margin:1em 2em;padding-left:1em}'
            f'a{{color:#2255aa}}'
            'code{font-family:Consolas,monospace;padding:0 3px}'
        )

        # Перезавантажити HTML зі збереженням позиції
        if hasattr(self, '_html'):
            sb = self.browser.verticalScrollBar()
            pos = sb.value()
            self.browser.setHtml(self._html)
            # відновити шрифт
            font = self.browser.document().defaultFont()
            font.setPointSize(13)
            self.browser.document().setDefaultFont(font)
            sb.setValue(pos)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('FB2 Reader')
    win = FB2Reader()
    win.show()
    sys.exit(app.exec())
