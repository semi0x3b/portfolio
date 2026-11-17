// semi; portfolio: 구성도 보기(dialog), 시연 영상, 장애 재현 그림 재생
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

// 이전 설계 모음의 북마크도 서비스 상세의 같은 그림으로 연결한다.
const followDesignBookmark = () => {
  const target = document.getElementById(location.hash.slice(1));
  if (target?.dataset.designRoute) location.replace(target.dataset.designRoute);
};
followDesignBookmark();
addEventListener('hashchange', followDesignBookmark);

// 그림을 누르면 뷰어를 연다. 뷰어의 이미지는 원본 파일 링크다.
const viewer = document.querySelector("dialog.viewer");
if (viewer) {
  const image = viewer.querySelector("img");
  const title = viewer.querySelector(".viewer__title");
  const originalLink = viewer.querySelector(".viewer__image-link");
  const body = viewer.querySelector(".viewer__body");
  let opener = null;

  document.querySelectorAll("a[data-diagram]").forEach((link) => {
    link.addEventListener("click", (event) => {
      const wantsNewTab = event.metaKey || event.ctrlKey || event.shiftKey || event.altKey;
      if (wantsNewTab) return;
      event.preventDefault();

      opener = link;
      title.textContent = link.dataset.title;
      originalLink.href = link.href;
      originalLink.setAttribute('aria-label', `${link.dataset.title} 원본 이미지`);
      image.alt = link.dataset.title;
      if (image.src !== link.href) {
        image.src = link.href;
      }
      viewer.showModal();
      body.scrollTo(0, 0);
    });
  });

  // 바깥(가림막)을 누르면 닫는다. Esc와 닫기 버튼은 dialog 기본 동작이다
  viewer.addEventListener("click", (event) => {
    if (event.target === viewer) viewer.close();
  });
  viewer.addEventListener("close", () => {
    opener?.focus();
  });
}

// 시연 영상은 화면에 보일 때만 재생한다
if (!reduceMotion) {
  const videoObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.play().catch(() => {});
      } else {
        entry.target.pause();
      }
    }
  }, { threshold: 0.4 });
  document.querySelectorAll("video[data-autoplay]").forEach((video) => videoObserver.observe(video));
}

// 장애 케이스: 끝 상태로 보여 주고, 재생을 누르면 수정 전·후 240초를 5초 동안 함께 재생한다
const loopSim = document.querySelector("[data-loop-sim]");
if (loopSim) {
  const clock = loopSim.querySelector("[data-clock]");
  const playButton = loopSim.querySelector("[data-replay]");
  const spanSeconds = 240;
  const playMs = 5000;
  let frame = 0;

  const setProgress = (progress) => {
    loopSim.style.setProperty("--p", progress);
    clock.textContent = Math.round(progress * spanSeconds);
  };
  const play = () => {
    cancelAnimationFrame(frame);
    const start = performance.now();
    loopSim.style.setProperty("--playing", 1);
    const step = (now) => {
      const progress = Math.min((now - start) / playMs, 1);
      setProgress(progress);
      if (progress < 1) {
        frame = requestAnimationFrame(step);
        return;
      }
      loopSim.style.setProperty("--playing", 0);
    };
    frame = requestAnimationFrame(step);
  };

  playButton.hidden = reduceMotion;
  playButton.addEventListener("click", play);
}

// 회사별 경력: 클릭, 키보드와 직접 링크에서 같은 탭 상태를 사용한다.
const companyTabs = [...document.querySelectorAll('[role="tab"][data-company]')];
if (companyTabs.length) {
  const activateCompany = (company, focus = false) => {
    const selected = companyTabs.find((tab) => tab.dataset.company === company) || companyTabs[0];
    for (const tab of companyTabs) {
      const active = tab === selected;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      document.getElementById(tab.getAttribute('aria-controls')).hidden = !active;
    }
    if (focus) selected.focus();
    return selected;
  };
  const companyFromHash = () => location.hash.slice(1).split('-')[0];
  activateCompany(companyFromHash());
  companyTabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
      const selected = activateCompany(tab.dataset.company);
      history.replaceState(null, '', '#' + selected.dataset.company);
      document.getElementById(selected.dataset.company).scrollIntoView({ block: 'start' });
    });
    tab.addEventListener('keydown', (event) => {
      let targetIndex;
      if (event.key === 'ArrowRight') targetIndex = (index + 1) % companyTabs.length;
      if (event.key === 'ArrowLeft') targetIndex = (index - 1 + companyTabs.length) % companyTabs.length;
      if (event.key === 'Home') targetIndex = 0;
      if (event.key === 'End') targetIndex = companyTabs.length - 1;
      if (targetIndex === undefined) return;
      event.preventDefault();
      const selected = activateCompany(companyTabs[targetIndex].dataset.company, true);
      history.replaceState(null, '', '#' + selected.dataset.company);
      document.getElementById(selected.dataset.company).scrollIntoView({ block: 'start' });
    });
  });
  addEventListener('hashchange', () => {
    activateCompany(companyFromHash());
    const target = document.getElementById(location.hash.slice(1));
    if (target) target.scrollIntoView();
  });
  const initialProject = document.getElementById(location.hash.slice(1));
  if (initialProject) requestAnimationFrame(() => initialProject.scrollIntoView());
}
