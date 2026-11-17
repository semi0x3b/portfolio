"""배포 HTML의 링크·이미지·서비스 순서와 이전 북마크를 검사한다."""
import hashlib
import json
import struct
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1] / '_public'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.elements = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attributes):
        self.elements.append((tag, dict(attributes)))


pages = {path: Page(path) for path in ROOT.rglob('*.html')}
errors = []
references = 0
for path, page in pages.items():
    ids = [attrs['id'] for _, attrs in page.elements if 'id' in attrs]
    if len(ids) != len(set(ids)):
        errors.append(f'{path.relative_to(ROOT)}: 중복 ID')
    for tag, attributes in page.elements:
        for attribute in ['href', 'src', 'data-design-route']:
            url = attributes.get(attribute)
            if not url:
                continue
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                continue
            if not parts.path:
                target = path
            elif parts.path.startswith('/portfolio/'):
                target = ROOT / parts.path.removeprefix('/portfolio/')
            else:
                target = path.parent / parts.path
            target = target.resolve()
            if target.is_dir():
                target /= 'index.html'
            references += 1
            if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
                errors.append(f'{path.relative_to(ROOT)}: 없는 파일 {parts.path}')
                continue
            if parts.fragment and target in pages:
                target_ids = {attrs.get('id') for _, attrs in pages[target].elements}
                if unquote(parts.fragment) not in target_ids:
                    errors.append(f'{path.relative_to(ROOT)}: 없는 앵커 {parts.fragment}')
            version = parse_qs(parts.query).get('v')
            if version and version != [hashlib.sha256(target.read_bytes()).hexdigest()[:12]]:
                errors.append(f'{path.relative_to(ROOT)}: 자산 해시 불일치')
            if tag == 'img' and attribute == 'src' and target.suffix == '.png':
                data = target.read_bytes()
                size = struct.unpack('>II', data[16:24])
                declared = (int(attributes['width']), int(attributes['height']))
                if data[:8] != b'\x89PNG\r\n\x1a\n' or size != declared:
                    errors.append(f'{path.relative_to(ROOT)}: 이미지 형식·크기 불일치')

manifest = json.loads((ROOT / 'content/designs.json').read_text())
home = pages[ROOT / 'index.html']
entry = [attrs for tag, attrs in home.elements if tag == 'a' and 'design-feature' in attrs.get('class', '').split()]
if len(entry) != 1 or entry[0].get('href') != 'designs.html':
    errors.append('홈의 설계 모음 카드는 서비스 목차로 연결해야 함')
if len(entry) == 1 and entry[0].get('aria-label') != '서비스별 아키텍처·설계 보기':
    errors.append('홈의 설계 모음 카드 이름이 이동 대상과 다름')
directory = pages[ROOT / 'designs.html']
routes = {attrs.get('id'): attrs['data-design-route'] for _, attrs in directory.elements if 'data-design-route' in attrs}
sitemap = {node.text for node in ElementTree.parse(ROOT / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
covered = set()
for service in manifest['services']:
    relative = 'services/' + service['id'] + '.html'
    page = pages[ROOT / relative]
    h1 = next(i for i, (tag, _) in enumerate(page.elements) if tag == 'h1')
    if page.elements[h1 + 1] != ('figure', {'class': 'figure service-figure', 'id': service['architecture']}):
        errors.append(f'{relative}: 서비스명 바로 아래 아키텍처 필요')
    images = {attrs['id'] for tag, attrs in page.elements if tag == 'figure'}
    if images != {service['architecture'], *service['items']}:
        errors.append(f'{relative}: 누락·중복 설계')
    if routes.get(service['id']) != relative:
        errors.append(f'{relative}: 기존 서비스 링크 누락')
    for item in service['items']:
        if routes.get(item) != relative + '#' + item:
            errors.append(f'{relative}: 기존 설계 링크 누락 {item}')
    if 'https://semi0x3b.github.io/portfolio/' + relative not in sitemap:
        errors.append(f'{relative}: 사이트맵 누락')
    covered.update(images)
if covered != {item['id'] for item in manifest['items']}:
    errors.append('공개 설계 목록과 상세 이미지 불일치')

print(json.dumps({'pages': len(pages), 'services': len(manifest['services']), 'diagrams': len(covered), 'references': references, 'errors': errors}, ensure_ascii=False))
raise SystemExit(bool(errors))
