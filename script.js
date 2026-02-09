const yearSlot = document.querySelector("#year");
if (yearSlot) {
  yearSlot.textContent = new Date().getFullYear();
}

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

  const link = document.createElement("a");
  link.href = file.download_url;
  link.target = "_blank";
  link.rel = "noopener";
  link.textContent = "Ouvrir";
  card.appendChild(link);

  return card;
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

function mountComments() {
  const commentsRoot = document.querySelector("#comments-root");
  if (!commentsRoot) return;

  const commentsScript = document.createElement("script");
  commentsScript.src = "https://utteranc.es/client.js";
  commentsScript.async = true;
  commentsScript.setAttribute("repo", siteConfig.commentsRepo);
  commentsScript.setAttribute("issue-term", "pathname");
  commentsScript.setAttribute("theme", "github-light");
  commentsScript.setAttribute("crossorigin", "anonymous");

  commentsRoot.appendChild(commentsScript);
}

loadMediaFromGitHub();
mountComments();
