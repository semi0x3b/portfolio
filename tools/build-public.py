"""GitHub Pages에 필요한 문서와 공개 자산만 패키징한다."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
out = root / '_public'
out.mkdir(exist_ok=True)
for filename in ['index.html', 'career.html', '404.html', 'site.css', 'site.js', 'tokens.css', 'sitemap.xml', 'og.png']:
    shutil.copy2(root / filename, out / filename)
for directory, pattern in [('work', '*.html'), ('content', '*.json')]:
    (out / directory).mkdir(exist_ok=True)
    for source in (root / directory).glob(pattern):
        shutil.copy2(source, out / directory / source.name)
(out / 'assets').mkdir(exist_ok=True)
shutil.copy2(root / 'assets/profile.jpg', out / 'assets/profile.jpg')
(out / '.nojekyll').touch()
# 배포 파일 자체에서 회사 원금액과 내부 구성도 경로가 섞이지 않았는지 확인한다.
for source in out.rglob('*'):
    if source.suffix not in {'.html', '.json', '.css', '.js'}:
        continue
    text = source.read_text()
    for term in ['2,400만원', '1,000만원', 'assets/diagrams/', 'assets/eks-to-oke.png']:
        if term in text:
            raise SystemExit('공개 제외 항목이 배포 파일에 있습니다: ' + str(source.relative_to(out)))
print('공개 페이지와 허용된 자산 패키징 완료')
