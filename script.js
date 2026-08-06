const siteConfig = {
  githubOwner: "mamso-dek",
  githubRepo: "mamso-dek.github.io",
  mediaFolder: "media",
  commentsRepo: "mamso-dek/mamso-dek.github.io",
  themeStorageKey: "massavo-theme",
};

const siteSearchIndex = [
  {
    title: "À propos",
    type: "Page",
    description: "Profil, parcours, compétences et outils.",
    url: "/index.html",
    keywords: "massavo salako parcours cv compétences outils génie mathématique modélisation",
  },
  {
    title: "Travaux",
    type: "Page",
    description: "Projets, publications, documents et médias.",
    url: "/publications.html",
    keywords: "travaux projets publications documents médias recherche",
  },
  {
    title: "Décomposition du Profit & Loss (BRVM)",
    type: "Projet",
    description: "Explication du P&L à partir de facteurs de risque.",
    url: "/projets/decomposition-pnl-brvm.html",
    keywords: "finance quantitative risque brvm pnl profit loss intelligence artificielle explicabilité",
  },
  {
    title: "Modélisation et simulation de prix d’options",
    type: "Projet",
    description: "Valorisation de produits dérivés et simulation numérique.",
    url: "/projets/simulation-prix-options.html",
    keywords: "option simulation valorisation produits dérivés finance mathématiques",
  },
  {
    title: "Modélisation de la volatilité avec GARCH",
    type: "Projet",
    description: "Estimation de la variance conditionnelle sur données financières.",
    url: "/projets/modelisation-volatilite-garch.html",
    keywords: "garch volatilité économétrie variance conditionnelle données financières",
  },
  {
    title: "Enseignement",
    type: "Page",
    description: "Cours, TD, TP, ateliers et ressources pédagogiques.",
    url: "/enseignement.html",
    keywords: "enseignement cours formation atelier tutorat td tp ressources pédagogiques",
  },
  {
    title: "Python pour le calcul scientifique",
    type: "Enseignement",
    description: "Atelier pratique en préparation.",
    url: "/enseignement.html",
    keywords: "python calcul scientifique programmation atelier",
  },
  {
    title: "Introduction à la modélisation mathématique",
    type: "Enseignement",
    description: "Cours et travaux dirigés en préparation.",
    url: "/enseignement.html",
    keywords: "cours modélisation mathématique td licence",
  },
  {
    title: "Analyse de données avec R",
    type: "Enseignement",
    description: "Atelier d’exploration et de visualisation des données.",
    url: "/enseignement.html",
    keywords: "R analyse données visualisation atelier",
  },
  {
    title: "Contact",
    type: "Page",
    description: "Email, LinkedIn, GitHub et CV.",
    url: "/contact.html",
    keywords: "contact email linkedin github cv cotonou bénin",
  },
];

document.querySelectorAll("[data-year]").forEach((slot) => {
  slot.textContent = new Date().getFullYear();
});

function normalizeSearchText(value) {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9&]+/g, " ")
    .trim();
}

function getSearchResults(query) {
  const words = normalizeSearchText(query).split(/\s+/).filter(Boolean);
  if (!words.length) return siteSearchIndex.slice(0, 7);

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
    const query = input.value;
    const results = getSearchResults(query);

    if (!results.length) {
      resultsRoot.innerHTML = `
        <p class="search-hint">Aucun résultat</p>
        <p class="search-empty">Essayez un domaine, une méthode ou le nom d’un projet.</p>
      `;
      return;
    }

    const label = query.trim() ? `${results.length} résultat${results.length > 1 ? "s" : ""}` : "Accès rapides";
    resultsRoot.innerHTML = `
      <p class="search-hint">${label}</p>
      ${results
        .map(
          (item) => `
            <a class="search-result" href="${item.url}">
              <span class="search-result-type">${item.type}</span>
              <div>
                <strong>${item.title}</strong>
                <small>${item.description}</small>
              </div>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6"></path></svg>
            </a>
          `
        )
        .join("")}
    `;
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

  const openMenu = () => {
    header.classList.add("is-open");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Fermer le menu");
  };

  toggle.addEventListener("click", () => {
    if (header.classList.contains("is-open")) {
      closeMenu();
    } else {
      openMenu();
    }
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

  sections.forEach((section) => {
    section.hidden =
      value !== "all" && section.dataset.filterCategory !== value;
  });

  let visibleItems = 0;
  items.forEach((item) => {
    const visible =
      value === "all" || item.dataset.filterCategory === value;
    item.hidden = !visible;
    if (visible) visibleItems += 1;
  });

  if (group === "teaching") {
    const listSection = document.querySelector(".teaching-section");
    if (listSection) {
      listSection.hidden = value === "resources";
    }
  }

  document.querySelectorAll(`[data-filter-empty="${group}"]`).forEach((empty) => {
    empty.hidden =
      value === "all" || value === "resources" || visibleItems > 0;
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

const mediaTypeByExtension = {
  image: ["jpg", "jpeg", "png", "webp", "gif", "svg", "avif"],
  video: ["mp4", "webm", "ogg", "mov", "m4v"],
  document: ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "txt", "csv"],
};

function slugify(value) {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function getExtension(filename) {
  const dotIndex = filename.lastIndexOf(".");
  return dotIndex === -1 ? "" : filename.slice(dotIndex + 1).toLowerCase();
}

function getMediaType(filename) {
  const extension = getExtension(filename);
  if (mediaTypeByExtension.image.includes(extension)) return "image";
  if (mediaTypeByExtension.video.includes(extension)) return "video";
  if (mediaTypeByExtension.document.includes(extension)) return "document";
  return "other";
}

function createCommentButton(scope, term, title) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "comment-btn";
  button.dataset.commentScope = scope;
  button.dataset.commentTerm = term;
  button.dataset.commentTitle = title;
  button.textContent = "Commenter";
  return button;
}

function makeMediaPreview(file, mediaType) {
  if (mediaType === "image") {
    const image = document.createElement("img");
    image.className = "media-preview";
    image.src = file.download_url;
    image.alt = "";
    image.loading = "lazy";
    return image;
  }

  if (mediaType === "video") {
    const video = document.createElement("video");
    video.className = "media-preview";
    video.controls = true;
    video.preload = "metadata";
    video.src = file.download_url;
    return video;
  }

  const documentPreview = document.createElement("div");
  documentPreview.className = "media-doc";
  documentPreview.textContent = getExtension(file.name).toUpperCase() || "DOC";
  return documentPreview;
}

function createMediaItem(file) {
  const mediaType = getMediaType(file.name);
  const item = document.createElement("article");
  item.className = "media-item";
  item.appendChild(makeMediaPreview(file, mediaType));

  const content = document.createElement("div");
  const type = document.createElement("p");
  type.className = "media-type";
  type.textContent = mediaType.toUpperCase();
  content.appendChild(type);

  const title = document.createElement("h3");
  title.className = "media-title";
  title.textContent = file.name;
  content.appendChild(title);
  item.appendChild(content);

  const actions = document.createElement("div");
  actions.className = "media-actions";

  const openLink = document.createElement("a");
  openLink.href = file.download_url;
  openLink.target = "_blank";
  openLink.rel = "noopener";
  openLink.textContent = "Ouvrir";
  actions.appendChild(openLink);

  actions.appendChild(
    createCommentButton(
      "publication",
      `publication-${slugify(file.name)}`,
      `Commentaires : ${file.name}`
    )
  );
  item.appendChild(actions);

  return item;
}

function utterancesTheme() {
  return currentTheme() === "dark" ? "github-dark" : "github-light";
}

function mountUtterances(root, issueTerm) {
  root.innerHTML = "";
  const script = document.createElement("script");
  script.src = "https://utteranc.es/client.js";
  script.async = true;
  script.setAttribute("repo", siteConfig.commentsRepo);
  script.setAttribute("issue-term", issueTerm);
  script.setAttribute("theme", utterancesTheme());
  script.setAttribute("crossorigin", "anonymous");
  root.appendChild(script);
}

function openComments(scope, term, title) {
  const project = scope === "project";
  const panel = document.querySelector(
    project ? "#project-comments-panel" : "#publication-comments-panel"
  );
  const heading = document.querySelector(
    project ? "#project-comments-title" : "#publication-comments-title"
  );
  const root = document.querySelector(
    project ? "#project-comments-root" : "#publication-comments-root"
  );
  if (!panel || !heading || !root) return;

  heading.textContent = title;
  panel.hidden = false;
  mountUtterances(root, term);
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function bindComments() {
  document.addEventListener("click", (event) => {
    if (!(event.target instanceof HTMLElement)) return;

    const commentButton = event.target.closest(".comment-btn");
    if (commentButton) {
      const { commentScope, commentTerm, commentTitle } = commentButton.dataset;
      if (commentScope && commentTerm && commentTitle) {
        openComments(commentScope, commentTerm, commentTitle);
      }
      return;
    }

    const closeButton = event.target.closest(".comments-close");
    if (!closeButton) return;
    const panel = closeButton.closest(".comments-panel");
    if (!panel) return;
    panel.hidden = true;
    panel.querySelectorAll('[id$="-comments-root"]').forEach((root) => {
      root.innerHTML = "";
    });
  });
}

function openDiscussionFromHash() {
  if (window.location.hash !== "#discussion") return;
  const button = document.querySelector("#discussion .comment-btn");
  if (button instanceof HTMLButtonElement) {
    window.setTimeout(() => button.click(), 200);
  }
}

async function loadMediaFromGitHub() {
  const list = document.querySelector("#media-grid");
  const status = document.querySelector("#media-status");
  if (!list || !status) return;

  const endpoint =
    `https://api.github.com/repos/${siteConfig.githubOwner}/${siteConfig.githubRepo}/contents/${siteConfig.mediaFolder}`;

  try {
    const response = await fetch(endpoint, {
      headers: { Accept: "application/vnd.github+json" },
    });
    if (!response.ok) throw new Error(`GitHub API status ${response.status}`);

    const payload = await response.json();
    const files = Array.isArray(payload)
      ? payload.filter(
          (file) => file.type === "file" && getMediaType(file.name) !== "other"
        )
      : [];

    if (!files.length) {
      status.textContent =
        "Aucun média publié pour le moment. Les prochains fichiers apparaîtront automatiquement ici.";
      return;
    }

    files.sort((a, b) => b.name.localeCompare(a.name, "fr"));
    list.innerHTML = "";
    files.forEach((file) => list.appendChild(createMediaItem(file)));
    status.textContent = `${files.length} média${files.length > 1 ? "s" : ""} publié${files.length > 1 ? "s" : ""}.`;
  } catch (error) {
    status.textContent =
      "Les médias ne peuvent pas être chargés pour le moment. Le dossier GitHub reste accessible ci-dessus.";
  }
}

bindThemeToggle();
bindSiteSearch();
bindMobileMenu();
bindRevealAnimations();
bindFilters();
bindComments();
openDiscussionFromHash();
loadMediaFromGitHub();
