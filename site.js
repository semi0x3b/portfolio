// semi; portfolio: 헤더 경계선, 스크롤 commit, 프로젝트 미리보기, 영상, 그림 확대
window.__site = true;

const root = document.documentElement;
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
const finePointer = matchMedia("(hover: hover) and (pointer: fine)").matches;

// 홈으로 돌아갈 때 잇는 범위를 줄인다. 홈 맨 위로 가면 해당 행이 화면 밖이라 글자가 화면을 가로질러 날아가므로 아무것도 잇지 않고,
// 프로젝트 목록(#projects)으로 가면 이 프로젝트의 제목·수치만 잇는다(다음 프로젝트 제목까지 날아가지 않게).
addEventListener("pageswap", (event) => {
  if (!event.viewTransition || !event.activation) return;
  const destination = new URL(event.activation.entry.url);
  const toHome = /\/portfolio\/(index\.html)?$/.test(destination.pathname);
  if (!toHome) return;
  const scope = destination.hash ? ".next [style*='view-transition-name']" : "[style*='view-transition-name']";
  document.querySelectorAll(scope).forEach((element) => {
    element.style.viewTransitionName = "none";
  });
});

// 맨 위를 벗어나면 헤더 아래 선을 보인다
const header = document.querySelector(".site-header");
const topSentinel = document.createElement("div");
topSentinel.setAttribute("aria-hidden", "true");
topSentinel.style.cssText = "position:absolute;top:0;left:0;width:1px;height:8px;";
document.body.prepend(topSentinel);
new IntersectionObserver(([entry]) => {
  header.classList.toggle("is-stuck", !entry.isIntersecting);
}).observe(topSentinel);

// 화면에 든 행은 세미콜론이 떨어지고 뒤 절이 축에서 빠져나온다
if (root.classList.contains("motion")) {
  const commitObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add("is-in");
      commitObserver.unobserve(entry.target);
    }
  }, { rootMargin: "0px 0px -10% 0px" });
  document.querySelectorAll("[data-commit]").forEach((row) => commitObserver.observe(row));
}

// 프로젝트 행에 포인터를 올리면 썸네일이 오른쪽 빈 자리에서 포인터 높이를 따라온다 (마우스, 모션 허용일 때만)
const previewList = document.querySelector("[data-preview-list]");
if (previewList && finePointer && !reduceMotion) {
  const box = document.createElement("div");
  box.className = "preview";
  box.setAttribute("aria-hidden", "true");
  const image = document.createElement("img");
  image.alt = "";
  box.append(image);
  document.body.append(box);

  const links = [...previewList.querySelectorAll("a[data-preview]")];
  let pointerY = 0;
  let preloaded = false;

  // 전후 수치를 가리지 않도록 가로 위치는 화면 오른쪽 끝에 고정한다
  const place = () => {
    const edge = 32;
    const width = box.offsetWidth;
    const height = box.offsetHeight || width * 0.6;
    const x = innerWidth - width - edge;
    const y = Math.min(Math.max(pointerY - height / 2, 80), innerHeight - height - edge);
    box.style.setProperty("--x", `${x}px`);
    box.style.setProperty("--y", `${y}px`);
  };
  const show = (link) => {
    if (!image.src.endsWith(link.dataset.preview)) image.src = link.dataset.preview;
    box.classList.toggle("is-diagram", link.hasAttribute("data-diagram"));
    box.classList.add("is-on");
  };
  const hide = () => box.classList.remove("is-on");

  previewList.addEventListener("pointerenter", () => {
    if (preloaded) return;
    preloaded = true;
    for (const link of links) new Image().src = link.dataset.preview;
  });
  previewList.addEventListener("pointermove", (event) => {
    pointerY = event.clientY;
    const link = event.target.closest("a[data-preview]");
    if (link) {
      show(link);
    } else {
      hide();
    }
    place();
  });
  previewList.addEventListener("pointerleave", hide);
  // 포인터가 멈춘 채 페이지가 스크롤되면 pointerleave가 오지 않는다
  addEventListener("scroll", hide, { passive: true });
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

// 그림 확대
const zoomDialog = document.querySelector("dialog.zoom");
if (zoomDialog) {
  const zoomImage = zoomDialog.querySelector("img");
  document.querySelectorAll("[data-zoom]").forEach((button) => {
    button.addEventListener("click", () => {
      const thumb = button.querySelector("img");
      zoomImage.src = button.dataset.zoom;
      zoomImage.alt = thumb ? thumb.getAttribute("alt") || "" : "";
      zoomDialog.showModal();
    });
  });
  zoomDialog.addEventListener("click", (event) => {
    if (event.target === zoomDialog) zoomDialog.close();
  });
}
