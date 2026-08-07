const siteConfig = {
  commentsRepo: "manusalako/manusalako.github.io",
  themeStorageKey: "massavo-theme",
};

const searchData = document.querySelector("#site-search-index");
let siteSearchIndex = [];

try {
  siteSearchIndex = JSON.parse(searchData?.textContent || "[]");
} catch (error) {
  console.warn("L’index de recherche n’a pas pu être chargé.", error);
}

document.querySelectorAll("[data-year]").forEach((slot) => {
  slot.textContent = new Date().getFullYear();
});

function normalizeSearchText(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9&]+/g, " ")
    .trim();
}

function getSearchResults(query) {
  const words = normalizeSearchText(query).split(/\s+/).filter(Boolean);
  if (!words.length) return [];

  return siteSearchIndex
    .map((item) => {
      const title = normalizeSearchText(item.title);
      const description = normalizeSearchText(item.description);
      const keywords = normalizeSearchText(item.keywords);
      const matches = words.every(
        (word) =>
          title.includes(word) ||
          description.includes(word) ||
          keywords.includes(word)
      );
      if (!matches) return null;

      const score = words.reduce((total, word) => {
        if (title.includes(word)) return total + 4;
        if (keywords.includes(word)) return total + 2;
        return total + 1;
      }, 0);
      return { item, score };
    })
    .filter(Boolean)
    .sort((a, b) => b.score - a.score)
    .map(({ item }) => item)
    .slice(0, 8);
}

function createSearchResult(item) {
  const link = document.createElement("a");
  link.className = "search-result";
  link.href = item.url;

  const type = document.createElement("span");
  type.className = "search-result-type";
  type.textContent = item.type;

  const content = document.createElement("div");
  const title = document.createElement("strong");
  const description = document.createElement("small");
  title.textContent = item.title;
  description.textContent = item.description;
  content.append(title, description);

  const arrow = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  arrow.setAttribute("viewBox", "0 0 24 24");
  arrow.setAttribute("aria-hidden", "true");
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", "M5 12h13M13 6l6 6-6 6");
  arrow.appendChild(path);

  link.append(type, content, arrow);
  return link;
}

function bindSiteSearch() {
  const toggles = document.querySelectorAll(".search-toggle");
  if (!toggles.length) return;

  const dialog = document.createElement("dialog");
  dialog.className = "search-dialog";
  dialog.setAttribute("aria-label", "Recherche sur le site");
  dialog.innerHTML = `
    <div class="search-panel">
      <div class="search-input-row">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.4"></circle><path d="m16 16 4.2 4.2"></path></svg>
        <input class="search-input" type="search" autocomplete="off" placeholder="Rechercher un projet, une méthode, un cours…" aria-label="Votre recherche" />
        <button class="search-close" type="button" aria-label="Fermer la recherche">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"></path></svg>
        </button>
      </div>
      <div class="search-results" aria-live="polite"></div>
    </div>
  `;
  document.body.appendChild(dialog);

  const input = dialog.querySelector(".search-input");
  const resultsRoot = dialog.querySelector(".search-results");
  const closeButton = dialog.querySelector(".search-close");

  const renderResults = () => {
    resultsRoot.replaceChildren();
    const query = input.value.trim();
    if (!query) return;

    const results = getSearchResults(query);
    const hint = document.createElement("p");
    hint.className = "search-hint";

    if (!results.length) {
      hint.textContent = "Aucun résultat";
      const empty = document.createElement("p");
      empty.className = "search-empty";
      empty.textContent =
        "Essayez un domaine, une méthode ou le nom d’un projet.";
      resultsRoot.append(hint, empty);
      return;
    }

    hint.textContent = `${results.length} résultat${results.length > 1 ? "s" : ""}`;
    resultsRoot.appendChild(hint);
    results.forEach((item) => resultsRoot.appendChild(createSearchResult(item)));
  };

  const openSearch = () => {
    if (!dialog.open) dialog.showModal();
    renderResults();
    window.setTimeout(() => input.focus(), 0);
  };

  toggles.forEach((toggle) => toggle.addEventListener("click", openSearch));
  closeButton.addEventListener("click", () => dialog.close());
  input.addEventListener("input", renderResults);
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", () => {
    input.value = "";
    renderResults();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && dialog.open) {
      dialog.close();
      return;
    }

    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openSearch();
    }
  });
}

function currentTheme() {
  return document.documentElement.dataset.theme === "dark" ? "dark" : "light";
}

function updateThemeUi() {
  const dark = currentTheme() === "dark";
  const themeColor = document.querySelector('meta[name="theme-color"]');

  document.querySelectorAll(".theme-toggle").forEach((button) => {
    button.setAttribute(
      "aria-label",
      dark ? "Activer le mode clair" : "Activer le mode sombre"
    );
    button.setAttribute("title", dark ? "Mode clair" : "Mode sombre");
  });

  if (themeColor) {
    themeColor.setAttribute("content", dark ? "#111216" : "#ffffff");
  }
}

function syncCommentTheme() {
  const theme = currentTheme() === "dark" ? "github-dark" : "github-light";
  document.querySelectorAll("iframe.utterances-frame").forEach((frame) => {
    frame.contentWindow?.postMessage(
      { type: "set-theme", theme },
      "https://utteranc.es"
    );
  });
}

function bindThemeToggle() {
  updateThemeUi();

  document.querySelectorAll(".theme-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const nextTheme = currentTheme() === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = nextTheme;
      localStorage.setItem(siteConfig.themeStorageKey, nextTheme);
      updateThemeUi();
      syncCommentTheme();
    });
  });
}

function bindMobileMenu() {
  const header = document.querySelector(".site-header");
  if (!header) return;

  const toggle = header.querySelector(".menu-toggle");
  const nav = header.querySelector("nav");
  if (!toggle || !nav) return;

  const closeMenu = () => {
    header.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Ouvrir le menu");
  };

  toggle.addEventListener("click", () => {
    const open = header.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });

  document.addEventListener("click", (event) => {
    if (event.target instanceof Node && !header.contains(event.target)) {
      closeMenu();
    }
  });

  const desktopQuery = window.matchMedia("(min-width: 821px)");
  const handleViewportChange = () => {
    if (desktopQuery.matches) closeMenu();
  };

  if (typeof desktopQuery.addEventListener === "function") {
    desktopQuery.addEventListener("change", handleViewportChange);
  } else {
    desktopQuery.addListener(handleViewportChange);
  }
}

function bindRevealAnimations() {
  const items = document.querySelectorAll(".reveal");
  if (!items.length) return;

  if (
    !("IntersectionObserver" in window) ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries, activeObserver) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        activeObserver.unobserve(entry.target);
      });
    },
    { threshold: 0.12 }
  );

  items.forEach((item) => observer.observe(item));
}

function applyFilter(group, value) {
  const buttons = document.querySelectorAll(
    `[data-filter-group="${group}"]`
  );
  const sections = document.querySelectorAll(
    `[data-filter-section="${group}"]`
  );
  const items = document.querySelectorAll(`[data-filter-item="${group}"]`);

  buttons.forEach((button) => {
    const selected = button.dataset.filterValue === value;
    button.classList.toggle("is-selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });

  let visibleSections = 0;
  sections.forEach((section) => {
    const visible =
      value === "all" || section.dataset.filterCategory === value;
    section.hidden = !visible;
    if (visible) visibleSections += 1;
  });

  let visibleItems = 0;
  items.forEach((item) => {
    const visible =
      value === "all" || item.dataset.filterCategory === value;
    item.hidden = !visible;
    if (visible) visibleItems += 1;
  });

  document.querySelectorAll(`[data-filter-empty="${group}"]`).forEach((empty) => {
    empty.hidden = value === "all" || visibleSections + visibleItems > 0;
  });
}

function bindFilters() {
  document.querySelectorAll("[data-filter-group]").forEach((button) => {
    button.addEventListener("click", () => {
      const group = button.dataset.filterGroup;
      const value = button.dataset.filterValue;
      if (!group || !value) return;
      applyFilter(group, value);
    });
  });
}

function utterancesTheme() {
  return currentTheme() === "dark" ? "github-dark" : "github-light";
}

function mountUtterances(root, issueTerm) {
  root.replaceChildren();
  const script = document.createElement("script");
  script.src = "https://utteranc.es/client.js";
  script.async = true;
  script.setAttribute("repo", siteConfig.commentsRepo);
  script.setAttribute("issue-term", issueTerm);
  script.setAttribute("theme", utterancesTheme());
  script.setAttribute("crossorigin", "anonymous");
  root.appendChild(script);
}

function bindComments() {
  const roots = Array.from(
    document.querySelectorAll(".comments-root[data-comment-term]")
  );
  if (!roots.length) return;

  const mount = (root) => {
    if (root.dataset.commentsMounted === "true") return;
    const issueTerm = root.dataset.commentTerm;
    if (!issueTerm) return;

    root.dataset.commentsMounted = "true";
    mountUtterances(root, issueTerm);
  };

  if (!("IntersectionObserver" in window)) {
    roots.forEach(mount);
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        mount(entry.target);
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "320px 0px" }
  );

  roots.forEach((root) => observer.observe(root));
}

bindThemeToggle();
bindSiteSearch();
bindMobileMenu();
bindRevealAnimations();
bindFilters();
bindComments();
