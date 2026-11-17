"""공개 서비스 목록과 상세 페이지를 하나의 데이터에서 생성한다."""
import json
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
VIEWER = '''<dialog class="viewer" aria-labelledby="viewer-title">
  <div class="viewer__bar"><h2 class="viewer__title" id="viewer-title">구성도</h2>
    <form method="dialog"><button class="viewer__close" aria-label="닫기">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>
    </button></form>
  </div>
  <div class="viewer__body"><a class="viewer__image-link" target="_blank" rel="noopener"><img alt=""></a></div>
</dialog>'''


def figure(diagram, eager=False):
    image = escape('../' + diagram['image'], quote=True)
    title = escape(diagram['title'], quote=True)
    loading = 'eager' if eager else 'lazy'
    return f'''<figure class="figure service-figure" id="{diagram['id']}">
  <a class="figure__zoom" href="{image}" data-diagram data-title="{title}" aria-label="{title} 보기">
    <img src="{image}" width="{diagram['width']}" height="{diagram['height']}" alt="{escape(diagram['alt'], quote=True)}" loading="{loading}" decoding="async">
  </a>
  <figcaption>{escape(diagram['caption'])}</figcaption>
</figure>'''


def render_pages(manifest, template):
    items = {item['id']: item for item in manifest['items']}
    pages = {}
    cards = []
    for service in manifest['services']:
        slug = service['id']
        path = f'services/{slug}.html'
        title = escape(service['title'])
        description = escape(service['description'])
        architecture = items[service['architecture']]
        details = [items[item_id] for item_id in service['items'] if item_id != architecture['id']]

        # 기존 설계 앵커는 JS 없이도 해당 서비스 카드로 이동할 수 있게 남긴다.
        aliases = [(slug + '-title', path)]
        aliases += [(item_id, path + '#' + item_id) for item_id in service['items']]
        anchors = ''.join(
            f'<span class="service-anchor" id="{anchor}" data-design-route="{target}" aria-hidden="true"></span>'
            for anchor, target in aliases
        )
        cards.append(f'''<li id="{slug}" data-design-route="{path}">{anchors}
  <a class="service-card" href="{path}"><h2>{title}</h2><p>{description}</p></a>
</li>''')

        links = ''.join(
            f'<a class="link" href="{escape("../" + link["href"], quote=True)}">{escape(link["label"])}</a>'
            for link in service['links']
        )
        related = f'<nav class="design-links" aria-label="관련 경험">{links}</nav>' if links else ''
        detail_content = ''
        if details:
            articles = '\n'.join(
                f'<article class="service-design"><h3>{escape(item["title"])}</h3>{figure(item)}</article>'
                for item in details
            )
            detail_content = f'''<section class="service-designs" aria-labelledby="details-title">
  <h2 class="section__title" id="details-title">세부 설계</h2>
  {articles}
</section>'''
        content = f'''<div class="wrap service-page">
  <a class="back link" href="../designs.html">서비스 목차</a>
  <h1 class="case__title" id="{slug}-title">{title}</h1>
  {figure(architecture, eager=True)}
  <div class="service-summary"><p>{description}</p>{related}</div>
  {detail_content}
</div>'''
        pages[path] = template.substitute(
            title=title, description=description, path=path, prefix='../', content=content, viewer=VIEWER
        )

    content = '''<div class="wrap design-intro">
  <a class="back link" href="./#projects">포트폴리오 목록</a>
  <h1 class="case__title">서비스별 아키텍처·설계</h1>
  <nav aria-label="서비스 목차"><ul class="service-directory">''' + '\n'.join(cards) + '</ul></nav></div>'
    pages['designs.html'] = template.substitute(
        title='서비스별 아키텍처·설계',
        description='교육·채용 서비스의 아키텍처와 ALEX, LION, 미래이력서의 세부 설계를 서비스별로 정리했습니다.',
        path='designs.html', prefix='./', content=content, viewer=''
    )
    return pages


def build():
    manifest = json.loads((ROOT / 'content/designs.json').read_text())
    template = Template((ROOT / 'templates/service-page.html').read_text())
    pages = render_pages(manifest, template)
    for path, html in pages.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html)
    print(f'서비스 목차와 상세 페이지 {len(pages)}개 생성 완료')


if __name__ == '__main__':
    build()
