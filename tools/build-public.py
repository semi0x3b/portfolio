"""GitHub Pages에 필요한 문서와 공개 자산만 패키징한다."""
from pathlib import Path
import shutil
import json
import hashlib
import re
from urllib.parse import urlsplit
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / 'tools/build-service-pages.py'), run_name='__main__')
out = root / '_public'
if out.exists():
    shutil.rmtree(out)
out.mkdir(exist_ok=True)
for filename in ['index.html', 'career.html', 'designs.html', '404.html', 'site.css', 'site.js', 'tokens.css', 'sitemap.xml', 'og.png']:
    shutil.copy2(root / filename, out / filename)
for directory, pattern in [('work', '*.html'), ('content', '*.json')]:
    (out / directory).mkdir(exist_ok=True)
    for source in (root / directory).glob(pattern):
        shutil.copy2(source, out / directory / source.name)
(out / 'assets').mkdir(exist_ok=True)
shutil.copy2(root / 'assets/profile.jpg', out / 'assets/profile.jpg')
# 검수한 공개용 도식만 명시된 목록에서 가져온다. 원본 폴더 전체를 복사하지 않는다.
designs = json.loads((root / 'content/designs.json').read_text())
(out / 'services').mkdir(exist_ok=True)
for service in designs['services']:
    filename = service['id'] + '.html'
    shutil.copy2(root / 'services' / filename, out / 'services' / filename)
for diagram in designs['items']:
    source = root / diagram['image']
    target = out / diagram['image']
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
(out / '.nojekyll').touch()

# 이미지·스타일이 바뀌면 브라우저도 새 파일을 받도록 내용 해시를 붙인다.
# 원본 파일명과 다운로드 경로는 유지한다.
asset_reference = re.compile(r'((?:src|href)=["\'])([^"\']+\.(?:css|js|png|jpg))(["\'])')
for document in out.rglob('*.html'):
    def version_asset(match):
        prefix, url, quote = match.groups()
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            return match.group(0)
        if parsed.path.startswith('/portfolio/'):
            asset = out / parsed.path.removeprefix('/portfolio/')
        else:
            asset = document.parent / parsed.path
        asset = asset.resolve()
        if not asset.is_relative_to(out.resolve()) or not asset.is_file():
            return match.group(0)
        version = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        return f'{prefix}{url}?v={version}{quote}'

    document.write_text(asset_reference.sub(version_asset, document.read_text()))

# 배포 파일 자체에서 회사 원금액과 내부 구성도 경로가 섞이지 않았는지 확인한다.
for source in out.rglob('*'):
    if source.suffix not in {'.html', '.json', '.css', '.js'}:
        continue
    text = source.read_text()
    for term in ['2,400만원', '1,000만원', 'assets/diagrams/', 'assets/eks-to-oke.png']:
        if term in text:
            raise SystemExit('공개 제외 항목이 배포 파일에 있습니다: ' + str(source.relative_to(out)))
print('공개 페이지와 허용된 자산 패키징 완료')
