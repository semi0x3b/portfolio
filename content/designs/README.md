# 구성도 편집

포트폴리오의 구성도와 플로우는 [stack-diagram](https://github.com/caru-ini/stack-diagram)의 로고 타일·직교 연결선 형식을 공유한다.

- `stack-diagrams.json`: 서비스 역할, 노드, 연결과 좌표.
- `stack-theme.css`: 공통 서체, 색, 크기와 간격.
- 각 HTML: 아이콘과 CSS가 포함된 렌더 원본. 외부 요청 없이 열린다.
- `assets/designs/*.png`: HTML을 브라우저에서 2배 크기로 캡처한 게시 이미지.
- 기존 `.drawio`: 이전 편집 원본.

아이콘 캐시를 준비한 뒤 `python3 tools/build-diagrams.py --icons <캐시 경로>`로 HTML을 만든다. 브랜드 로고는 기존 stack-diagram 원본의 공식 로고를 사용하고, 일반 개념은 Lucide 아이콘을 쓴다. Jitsi의 밝은 로고에는 어두운 타일을 적용한다. 로고 색은 바꾸지 않는다.

PNG를 교체할 때 브라우저에서 글자·아이콘·연결선 겹침과 잘림을 확인하고 `content/designs.json` 및 HTML의 이미지 크기를 함께 맞춘다. 공개 목록의 PNG만 `tools/build-public.py`가 게시한다.

템플릿은 MIT 라이선스의 stack-diagram을 바탕으로 한다. 원문은 `STACK-DIAGRAM-LICENSE`에 보관한다. 각 브랜드 로고의 권리는 원 소유자에게 있으며 Lucide 아이콘의 라이선스는 `LUCIDE-LICENSE`에 보관한다.
