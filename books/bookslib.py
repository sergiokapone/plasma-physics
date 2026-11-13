"""Спільні функції для make_toc.py і search_books.py: djvu і pdf.

Книга = файл .djvu або .pdf у цій теці. Номери сторінок скрізь 1-based (індекс сторінки файлу).
PDF: текст і закладки через PyMuPDF (fitz); сторінка → PNG теж через fitz.
DJVU: djvutxt/djvused з DjVuLibre.
OCR (лише PDF без текстового шару): tesseract (rus+ukr+eng), повільно, результат кешується.
"""
import re
import subprocess
import tempfile
from pathlib import Path

BOOKS = Path(__file__).resolve().parent
DJVUTXT = r'D:\Programs\BookShop\DjVuLibre\djvutxt.exe'
DJVUSED = r'D:\Programs\BookShop\DjVuLibre\djvused.exe'
TESSERACT = r'D:\Programs\Utility\Tesseract-OCR\tesseract.exe'


def list_books(folder: Path = BOOKS):
    return sorted(list(folder.glob('*.djvu')) + list(folder.glob('*.pdf')))


def is_pdf(p: Path) -> bool:
    return p.suffix.lower() == '.pdf'


def _fitz():
    import fitz  # PyMuPDF
    return fitz


def page_count(p: Path) -> int:
    if is_pdf(p):
        with _fitz().open(p) as d:
            return d.page_count
    out = subprocess.run([DJVUSED, '-e', 'n', str(p)], capture_output=True).stdout.decode().strip()
    return int(out or 0)


def page_texts(p: Path):
    """Список текстів сторінок (індекс 0 = сторінка 1). Порожні рядки, якщо текстового шару нема."""
    if is_pdf(p):
        with _fitz().open(p) as d:
            return [pg.get_text() for pg in d]
    raw = subprocess.run([DJVUTXT, str(p)], capture_output=True).stdout.decode('utf-8', errors='replace')
    pages = raw.split('\x0c')
    n = page_count(p)
    return pages[:n] if n else pages


def has_text_layer(pages) -> bool:
    """Груба оцінка: на сторінку в середньому щонайменше ~40 символів."""
    if not pages:
        return False
    return sum(len(t.strip()) for t in pages) >= 40 * len(pages) * 0.3


def ocr_pdf(p: Path, dpi=200, lang='rus+ukr+eng', progress=True):
    """OCR сторінок PDF через tesseract; повертає список текстів. Повільно (секунди на сторінку)."""
    fitz = _fitz()
    texts = []
    with fitz.open(p) as d, tempfile.TemporaryDirectory() as tmp:
        for i, pg in enumerate(d, start=1):
            img = Path(tmp) / ('p%d.png' % i)
            pg.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72)).save(str(img))
            r = subprocess.run([TESSERACT, str(img), 'stdout', '-l', lang], capture_output=True)
            texts.append(r.stdout.decode('utf-8', errors='replace'))
            img.unlink(missing_ok=True)
            if progress and i % 10 == 0:
                print('  OCR %d/%d' % (i, d.page_count), flush=True)
    return texts


def outline(p: Path):
    """[(depth, title, page)] або None, якщо закладок нема. depth з 0, page — int."""
    if is_pdf(p):
        with _fitz().open(p) as d:
            toc = d.get_toc()
        if not toc:
            return None
        return [(lvl - 1, title.strip(), pg) for lvl, title, pg in toc]
    raw = subprocess.run([DJVUSED, '-e', 'print-outline', str(p)], capture_output=True).stdout.decode('latin-1')
    if not raw.strip().startswith('(bookmarks'):
        return None
    return [(d_, t, int(pg.lstrip('#')) if pg.lstrip('#').isdigit() else -1)
            for d_, t, pg in _parse_djvu_outline(raw)]


def _unescape(s: str) -> str:
    out = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            n = s[i + 1]
            if n in '0123' and i + 3 < len(s) + 1:
                out.append(int(s[i + 1:i + 4], 8)); i += 4; continue
            if n in '"\\':
                out += n.encode(); i += 2; continue
            if n == 'n':
                out += b'\n'; i += 2; continue
        out += c.encode('utf-8'); i += 1
    return out.decode('utf-8', errors='replace')


def _parse_djvu_outline(txt: str):
    tokens = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"', txt)
    res = []

    def walk(i, depth):
        i += 1
        title = _unescape(tokens[i][1:-1]).strip(); i += 1
        page = _unescape(tokens[i][1:-1]); i += 1
        res.append((depth, title, page))
        while tokens[i] == '(':
            i = walk(i, depth + 1)
        return i + 1
    i = 1
    while i < len(tokens) and tokens[i] == '(':
        i = walk(i, 0)
    return res


def render_png(p: Path, page: int, out_dir: Path, scale_pct=100):
    """Зберегти сторінку як PNG і повернути шлях. PDF — fitz; DJVU — ddjvu через djvu2png.py."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if is_pdf(p):
        fitz = _fitz()
        with fitz.open(p) as d:
            z = max(scale_pct, 10) / 100 * 2  # 100% = ~144 dpi
            pix = d[page - 1].get_pixmap(matrix=fitz.Matrix(z, z))
            target = out_dir / ('%s_%04d.png' % (re.sub(r'[^\w\-]+', '_', p.stem)[:30], page))
            pix.save(str(target))
            return target
    import sys
    script = r'D:\Programs\BookShop\Script\djvu2png.py'
    subprocess.run([sys.executable, script, str(p), '-p', str(page), '-o', str(out_dir), '-s', str(scale_pct)],
                   capture_output=True)
    cands = sorted(out_dir.glob('*_%03d.png' % page)) or sorted(out_dir.glob('*%d.png' % page))
    return cands[-1] if cands else None
