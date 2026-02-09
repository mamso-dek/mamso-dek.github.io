const yearSlot = document.querySelector("#year");
if (yearSlot) {
  yearSlot.textContent = new Date().getFullYear();
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
    const isOpen = header.classList.contains("is-open");
    if (isOpen) {
      closeMenu();
      return;
    }
    openMenu();
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => closeMenu());
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
    }
  });

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Node)) return;
    if (!header.contains(target)) {
      closeMenu();
    }
  });

  const mediaQuery = window.matchMedia("(min-width: 761px)");
  const handleResize = () => {
    if (mediaQuery.matches) {
      closeMenu();
    }
  };

  if (typeof mediaQuery.addEventListener === "function") {
    mediaQuery.addEventListener("change", handleResize);
  } else {
    mediaQuery.addListener(handleResize);
  }
}

bindMobileMenu();

const revealItems = document.querySelectorAll(".reveal");

const observer = new IntersectionObserver(
  (entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        obs.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.18 }
);

revealItems.forEach((item) => observer.observe(item));

const siteConfig = {
  githubOwner: "mamso-dek",
  githubRepo: "mamso-dek.github.io",
  mediaFolder: "media",
  commentsRepo: "mamso-dek/mamso-dek.github.io",
};

const mediaTypeByExt = {
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
  const dotIdx = filename.lastIndexOf(".");
  if (dotIdx === -1) return "";
  return filename.slice(dotIdx + 1).toLowerCase();
}

function getMediaType(filename) {
  const ext = getExtension(filename);
  if (mediaTypeByExt.image.includes(ext)) return "image";
  if (mediaTypeByExt.video.includes(ext)) return "video";
  if (mediaTypeByExt.document.includes(ext)) return "document";
  return "other";
}

function createCommentButton(scope, term, titleText) {
  const button = document.createElement("button");
  button.className = "comment-btn";
  button.type = "button";
  button.dataset.commentScope = scope;
  button.dataset.commentTerm = term;
  button.dataset.commentTitle = titleText;
  button.textContent = scope === "project" ? "Commenter ce projet" : "Commenter cette publication";
  return button;
}

function makePreview(file, mediaType) {
  if (mediaType === "image") {
    const img = document.createElement("img");
    img.className = "media-preview";
    img.src = file.download_url;
    img.alt = file.name;
    img.loading = "lazy";
    return img;
  }

  if (mediaType === "video") {
    const video = document.createElement("video");
    video.className = "media-preview";
    video.controls = true;
    video.preload = "metadata";
    video.src = file.download_url;
    return video;
  }

  const doc = document.createElement("div");
  doc.className = "media-doc";
  doc.textContent = "Document";
  return doc;
}

function createMediaCard(file) {
  const mediaType = getMediaType(file.name);
  const card = document.createElement("article");
  card.className = "card media-card";
  card.appendChild(makePreview(file, mediaType));

  const typeTag = document.createElement("p");
  typeTag.className = "media-type";
  typeTag.textContent = mediaType.toUpperCase();
  card.appendChild(typeTag);

  const title = document.createElement("h3");
  title.className = "media-title";
  title.textContent = file.name;
  card.appendChild(title);

  const actions = document.createElement("div");
  actions.className = "card-actions";

  const link = document.createElement("a");
  link.href = file.download_url;
  link.target = "_blank";
  link.rel = "noopener";
  link.textContent = "Ouvrir";
  actions.appendChild(link);

  const term = `publication-${slugify(file.name)}`;
  const commentTitle = `Commentaires: ${file.name}`;
  actions.appendChild(createCommentButton("publication", term, commentTitle));

  card.appendChild(actions);
  return card;
}

function mountUtterances(root, issueTerm) {
  root.innerHTML = "";

  const commentsScript = document.createElement("script");
  commentsScript.src = "https://utteranc.es/client.js";
  commentsScript.async = true;
  commentsScript.setAttribute("repo", siteConfig.commentsRepo);
  commentsScript.setAttribute("issue-term", issueTerm);
  commentsScript.setAttribute("theme", "github-light");
  commentsScript.setAttribute("crossorigin", "anonymous");

  root.appendChild(commentsScript);
}

function openCommentsFor(scope, term, title) {
  const panelId =
    scope === "project" ? "#project-comments-panel" : "#publication-comments-panel";
  const titleId =
    scope === "project" ? "#project-comments-title" : "#publication-comments-title";
  const rootId =
    scope === "project" ? "#project-comments-root" : "#publication-comments-root";

  const panel = document.querySelector(panelId);
  const titleNode = document.querySelector(titleId);
  const root = document.querySelector(rootId);

  if (!panel || !titleNode || !root) return;

  titleNode.textContent = title;
  panel.hidden = false;
  mountUtterances(root, term);
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function bindProjectComments() {
  const projectButtons = document.querySelectorAll(
    ".comment-btn[data-comment-scope='project']"
  );

  projectButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const term = button.dataset.commentTerm;
      const title = button.dataset.commentTitle;
      if (!term || !title) return;
      openCommentsFor("project", term, title);
    });
  });
}

function bindPublicationComments() {
  const mediaGrid = document.querySelector("#media-grid");
  if (!mediaGrid) return;

  mediaGrid.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    const button = target.closest(".comment-btn[data-comment-scope='publication']");
    if (!button) return;

    const term = button.dataset.commentTerm;
    const title = button.dataset.commentTitle;
    if (!term || !title) return;
    openCommentsFor("publication", term, title);
  });
}

async function loadMediaFromGitHub() {
  const grid = document.querySelector("#media-grid");
  const status = document.querySelector("#media-status");
  if (!grid || !status) return;

  const apiUrl = `https://api.github.com/repos/${siteConfig.githubOwner}/${siteConfig.githubRepo}/contents/${siteConfig.mediaFolder}`;
  status.textContent = "Chargement des publications depuis GitHub...";

  try {
    const res = await fetch(apiUrl, {
      headers: { Accept: "application/vnd.github+json" },
    });
    if (!res.ok) {
      throw new Error(`GitHub API status ${res.status}`);
    }

    const payload = await res.json();
    const files = Array.isArray(payload) ? payload : [];
    const mediaFiles = files.filter((file) => {
      return file.type === "file" && getMediaType(file.name) !== "other";
    });

    if (mediaFiles.length === 0) {
      status.textContent =
        "Aucun média publié pour le moment. Utilisez le bouton 'Publier un fichier'.";
      grid.innerHTML = "";
      return;
    }

    mediaFiles.sort((a, b) => b.name.localeCompare(a.name, "fr"));
    grid.innerHTML = "";
    mediaFiles.forEach((file) => grid.appendChild(createMediaCard(file)));
    status.textContent = `${mediaFiles.length} publication(s) chargée(s).`;
  } catch (error) {
    status.textContent =
      "Impossible de charger automatiquement. Vérifiez que le dossier media/ existe et contient des fichiers.";
    grid.innerHTML = "";
  }
}

bindProjectComments();
bindPublicationComments();
loadMediaFromGitHub();
