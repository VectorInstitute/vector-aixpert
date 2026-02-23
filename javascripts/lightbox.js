/* Gallery lightbox: click a .gallery-item to enlarge; one shared overlay for all galleries */
(function () {
  function init() {
    var overlay = document.getElementById("lightbox-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "lightbox-overlay";
      overlay.className = "lightbox lightbox-hidden";
      overlay.setAttribute("aria-hidden", "true");
      overlay.setAttribute("role", "dialog");
      overlay.setAttribute("aria-label", "Enlarge image");
      overlay.innerHTML =
        '<span class="lightbox-close" aria-label="Close">&times;</span><img class="lightbox-img" src="" alt="">';
      document.body.appendChild(overlay);
    }

    var lbImg = overlay.querySelector(".lightbox-img");
    var closeBtn = overlay.querySelector(".lightbox-close");
    if (!lbImg) return;

    function openLightbox(href, title) {
      lbImg.src = href;
      lbImg.alt = title || "";
      overlay.classList.remove("lightbox-hidden");
      overlay.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
    }

    function closeLightbox() {
      overlay.classList.add("lightbox-hidden");
      overlay.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }

    document.querySelectorAll(".remarkable-gallery a[href]").forEach(function (a) {
      var img = a.querySelector("img");
      if (!img || !/\.(png|jpe?g|gif|webp)(\?|$)/i.test(a.getAttribute("href") || "")) return;
      a.addEventListener("click", function (e) {
        e.preventDefault();
        openLightbox(a.getAttribute("href"), a.getAttribute("title") || (img && img.getAttribute("alt")) || "");
      });
    });

    if (closeBtn) closeBtn.addEventListener("click", closeLightbox);
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) closeLightbox();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !overlay.classList.contains("lightbox-hidden")) closeLightbox();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
