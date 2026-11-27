(() => {
  "use strict";

  const root = document.documentElement;
  const language = document.getElementById("language");
  const menu = document.getElementById("menu-toggle");
  const nav = document.getElementById("site-nav");
  const compact = matchMedia("(max-width: 900px)");
  const dialog = document.getElementById("figure-dialog");
  const figureImage = document.getElementById("figure-full");
  const originalImage = document.getElementById("figure-original");
  const caption = document.getElementById("figure-caption");
  const closeFigure = document.getElementById("figure-close");
  const feedback = document.getElementById("feedback");
  const form = document.getElementById("publication-filters");
  const rows = Array.from(document.querySelectorAll(".publication"));
  const groups = Array.from(document.querySelectorAll("[data-publication-group]"));
  const count = document.getElementById("publication-count");
  const empty = document.getElementById("publication-empty");
  let currentFigure;

  const inChinese = () => root.lang === "zh-CN";
  const message = (en, zh) => inChinese() ? zh : en;
  const normalize = value => value.normalize("NFKC").toLowerCase().replace(/\s+/gu, " ").trim();
  const searchable = rows.map(row => ({
    row,
    text: normalize([...row.querySelectorAll("h4, .authors, .journal, .paper-translation")]
      .map(node => node.textContent).join(" ") + " " + row.dataset.doi),
  }));

  function filterPublications() {
    if (!form) return;
    const filters = new FormData(form);
    const terms = normalize(filters.get("query")).split(" ").filter(Boolean);
    const year = filters.get("year");
    const status = filters.get("status");
    const theme = filters.get("theme");
    const role = filters.get("role");
    let shown = 0;
    for (const { row, text } of searchable) {
      const paper = row.dataset;
      const matchesRole = (
        !role || role === paper.role
        || role === "listed-first" && ["first", "cofirst"].includes(paper.role)
        || role === "equal" && paper.role === "cofirst"
      );
      row.hidden = !(
        (!year || year === paper.year)
        && (!status || status === paper.status)
        && (!theme || paper.themes.split(" ").includes(theme))
        && matchesRole && terms.every(term => text.includes(term))
      );
      if (!row.hidden) shown += 1;
    }
    for (const group of groups) {
      group.hidden = !group.querySelector(".publication:not([hidden])");
    }
    count.textContent = message(
      `${shown} of ${rows.length} publications`,
      `显示 ${rows.length} 篇论文中的 ${shown} 篇`,
    );
    empty.hidden = shown !== 0;
  }

  function showLinkedPublication() {
    // A direct link from a system, project or software card must remain usable while filters are active.
    const target = rows.find(row => "#" + row.id === location.hash);
    if (!target || !target.hidden) return;
    form.reset();
    form.elements.status.value = "";
    filterPublications();
    target.scrollIntoView({ block: "start" });
  }

  function updateImageDialog() {
    if (!currentFigure) return;
    const source = currentFigure.querySelector("img");
    figureImage.src = currentFigure.href;
    figureImage.alt = source.alt;
    originalImage.href = currentFigure.href;
    caption.textContent = currentFigure.parentElement.querySelector(
      message("figcaption .en", "figcaption .zh"),
    ).textContent;
  }

  const localizedAttributes = [
    ["img[data-alt-zh]", "alt", "altZh"],
    ["[data-label-zh]", "aria-label", "labelZh"],
    ["[data-placeholder-zh]", "placeholder", "placeholderZh"],
  ];
  for (const [selector, attribute, key] of localizedAttributes) {
    for (const element of document.querySelectorAll(selector)) {
      element.dataset[key.replace(/Zh$/u, "En")] = element.getAttribute(attribute);
    }
  }

  function setLanguage(locale) {
    root.lang = locale;
    language.textContent = message("中文", "English");
    language.lang = message("zh-CN", "en");
    document.title = document.body.dataset[message("titleEn", "titleZh")];
    for (const [selector, attribute, key] of localizedAttributes) {
      for (const element of document.querySelectorAll(selector)) {
        element.setAttribute(attribute, element.dataset[message(key.replace(/Zh$/u, "En"), key)]);
      }
    }
    for (const option of document.querySelectorAll("option[data-en]")) {
      option.textContent = option.dataset[message("en", "zh")];
    }
    updateImageDialog();
    filterPublications();
  }

  let stored;
  try {
    stored = localStorage.getItem("baoding-language");
  } catch {
    // The language switch also runs when storage is unavailable.
  }
  setLanguage(stored === "zh-CN" ? "zh-CN" : "en");
  language.hidden = false;
  language.addEventListener("click", () => {
    const next = message("zh-CN", "en");
    setLanguage(next);
    try {
      localStorage.setItem("baoding-language", next);
    } catch {
      // Keep the selected language for the current page.
    }
  });

  function closeMenu() {
    nav.classList.remove("is-open");
    menu.setAttribute("aria-expanded", "false");
  }

  function updateMenu() {
    closeMenu();
    menu.hidden = !compact.matches;
  }

  root.classList.add("js");
  updateMenu();
  compact.addEventListener("change", updateMenu);
  menu.addEventListener("click", () => {
    if (nav.classList.toggle("is-open")) {
      menu.setAttribute("aria-expanded", "true");
      nav.querySelector("a").focus({ preventScroll: true });
    } else {
      closeMenu();
    }
  });
  nav.addEventListener("click", event => {
    if (compact.matches && event.target.closest("a")) closeMenu();
  });
  document.addEventListener("keydown", event => {
    if (event.key !== "Escape" || !nav.classList.contains("is-open")) return;
    closeMenu();
    menu.focus();
  });

  if (form) {
    form.hidden = false;
    count.hidden = false;
    form.addEventListener("submit", event => event.preventDefault());
    form.addEventListener("input", filterPublications);
    form.addEventListener("change", filterPublications);
    window.addEventListener("hashchange", showLinkedPublication);
    showLinkedPublication();
  }

  if (typeof dialog.showModal === "function") {
    for (const figureLink of document.querySelectorAll("[data-figure]")) {
      figureLink.addEventListener("click", event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        currentFigure = figureLink;
        updateImageDialog();
        dialog.showModal();
        closeFigure.focus();
      });
    }
    closeFigure.addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", event => {
      if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener("close", () => {
      currentFigure?.focus({ preventScroll: true });
      currentFigure = undefined;
    });
  }

  for (const button of document.querySelectorAll("[data-copy]")) {
    const label = button.querySelector("[data-copy-label]");
    const confirmation = button.querySelector("[data-copy-confirmation]");
    let resetTimer;
    button.hidden = false;
    button.addEventListener("click", async () => {
      const citation = document.getElementById(button.dataset.copy);
      try {
        await navigator.clipboard.writeText(citation.textContent);
        feedback.textContent = message("BibTeX copied.", "已复制 BibTeX。");
        clearTimeout(resetTimer);
        label.hidden = true;
        confirmation.hidden = false;
        resetTimer = setTimeout(() => {
          label.hidden = false;
          confirmation.hidden = true;
        }, 1600);
      } catch {
        const range = document.createRange();
        range.selectNodeContents(citation);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        citation.focus({ preventScroll: true });
        feedback.textContent = message(
          "BibTeX selected. Use your browser’s copy command.",
          "已选中 BibTeX，请使用浏览器的复制命令。",
        );
      }
    });
  }
})();
