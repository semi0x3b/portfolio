# 포트폴리오 작업 안내

화면을 바꾸기 전에 `DESIGN.md`를 읽는다. GitHub Pages에는 `_public`의 정적 파일만 배포한다.

- 서비스 분류·설명·대표 아키텍처·세부 설계: `content/designs.json`
- 서비스 목차·상세 페이지 양식: `templates/service-page.html`
- 생성 코드: `tools/build-service-pages.py`
- 생성 결과: `designs.html`, `services/*.html`. 직접 수정하지 않고 데이터·양식을 고친 뒤 빌드한다.
- 그림 원본: `content/designs/stack-diagrams.json`, `stack-theme.css`. 이미지 재생성은 같은 폴더의 `README.md`를 따른다.

`python3 tools/build-public.py`는 페이지 생성과 공개 파일 패키징을 함께 한다. 이어서 `python3 tools/check-public.py`, `node --check site.js`, `git diff --check`로 검사한다.

서비스·도식 ID는 기존 공유 링크에 사용된다. ID를 바꿀 때는 이전 주소에서 새 상세로 이동하는 경로도 유지한다. 서비스명 바로 아래에는 아키텍처를 놓고, 세부 설계는 설명 아래에 둔다. 이미지 클릭·× 닫기·Esc·포커스 복귀와 경력기술서 회사 탭은 브라우저에서도 확인한다.

화면에는 구현 도구·작업 시점·중복 소개 문구를 덧붙이지 않는다. 내부 구성 원본·접속 정보는 공개 자산에 추가하지 않는다.
