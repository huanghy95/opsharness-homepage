(() => {
  "use strict";

  const STORAGE_KEY = "opsharness-language";
  const motionQuery = window.matchMedia
    ? window.matchMedia("(prefers-reduced-motion: reduce)")
    : { matches: false };
  const prefersReducedMotion = motionQuery.matches;

  function catalogFor(language) {
    const catalog = window.OPSHARNESS_I18N || {};
    return catalog[language] || catalog.en || {};
  }

  function readSavedLanguage() {
    try {
      return localStorage.getItem(STORAGE_KEY) === "zh" ? "zh" : "en";
    } catch (_) {
      return "en";
    }
  }

  function saveLanguage(language) {
    try {
      localStorage.setItem(STORAGE_KEY, language);
    } catch (_) {
      /* Storage may be disabled; the current page still switches language. */
    }
  }

  function applyLanguage(language) {
    const supported = language === "zh" ? "zh" : "en";
    const catalog = catalogFor(supported);

    document.querySelectorAll("[data-i18n]").forEach((node) => {
      const value = catalog[node.dataset.i18n];
      if (typeof value === "string") node.textContent = value;
    });

    document.querySelectorAll("[data-i18n-success]").forEach((node) => {
      const value = catalog[node.dataset.i18nSuccess];
      if (typeof value === "string") node.dataset.successLabel = value;
    });

    document.querySelectorAll("[data-i18n-failure]").forEach((node) => {
      const value = catalog[node.dataset.i18nFailure];
      if (typeof value === "string") node.dataset.failureLabel = value;
    });

    document.querySelectorAll("[data-i18n-aria-label]").forEach((node) => {
      const value = catalog[node.dataset.i18nAriaLabel];
      if (typeof value === "string") node.setAttribute("aria-label", value);
    });

    document.documentElement.lang = supported === "zh" ? "zh-CN" : "en";
    saveLanguage(supported);
    return supported;
  }

  function initLanguage() {
    let language = applyLanguage(readSavedLanguage());
    const toggle = document.querySelector("[data-language-toggle]");
    if (!toggle) return;

    toggle.addEventListener("click", () => {
      language = applyLanguage(language === "en" ? "zh" : "en");
    });
  }

  function initNavigation() {
    const button = document.querySelector("[data-nav-toggle]");
    const menu = document.getElementById("primary-navigation");
    if (!button || !menu) return;

    const setOpen = (open) => {
      button.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("is-open", open);
    };

    button.addEventListener("click", () => {
      setOpen(button.getAttribute("aria-expanded") !== "true");
    });

    menu.addEventListener("click", (event) => {
      if (event.target.closest("a")) setOpen(false);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") setOpen(false);
    });
  }

  function initTabs() {
    const tabs = [...document.querySelectorAll('[role="tab"]')];
    if (!tabs.length) return;

    const activate = (tab, moveFocus = false) => {
      tabs.forEach((candidate) => {
        const selected = candidate === tab;
        candidate.setAttribute("aria-selected", String(selected));
        candidate.tabIndex = selected ? 0 : -1;
        const panel = document.getElementById(candidate.getAttribute("aria-controls"));
        if (panel) panel.hidden = !selected;
      });
      if (moveFocus) tab.focus();
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => activate(tab));
      tab.addEventListener("keydown", (event) => {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        const offset = event.key === "ArrowRight" ? 1 : -1;
        activate(tabs[(index + offset + tabs.length) % tabs.length], true);
      });
    });

    const selectedTab = tabs.find((tab) => tab.getAttribute("aria-selected") === "true") || tabs[0];
    activate(selectedTab);
    selectedTab.closest(".terminal-card")?.classList.add("tabs-ready");
  }

  function fallbackCopy(text) {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.append(area);
    area.select();
    const copied = document.execCommand("copy");
    area.remove();
    if (!copied) throw new Error("Copy command was rejected");
  }

  function initCopyButtons() {
    const status = document.querySelector("[data-copy-status]");
    document.querySelectorAll("[data-copy-target]").forEach((button) => {
      button.addEventListener("click", async () => {
        const target = document.getElementById(button.dataset.copyTarget);
        if (!target) return;

        const original = button.textContent;
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(target.textContent);
          } else {
            fallbackCopy(target.textContent);
          }
          button.textContent = button.dataset.successLabel || "Copied";
        } catch (_) {
          button.textContent = button.dataset.failureLabel || "Select and copy manually";
        }
        if (status) status.textContent = button.textContent;

        window.setTimeout(() => {
          button.textContent = original;
          if (status) status.textContent = "";
        }, 1800);
      });
    });
  }

  function initLightbox() {
    const dialog = document.querySelector("[data-lightbox]");
    const target = dialog && dialog.querySelector("[data-lightbox-target]");
    const closeButton = dialog && dialog.querySelector("[data-lightbox-close]");
    if (!dialog || !target || !closeButton) return;

    let trigger = null;
    let inertedNodes = [];

    const setBackgroundInert = (inert) => {
      if (inert) {
        inertedNodes = [...document.body.children].filter(
          (node) => node !== dialog && !node.hasAttribute("inert"),
        );
        inertedNodes.forEach((node) => node.setAttribute("inert", ""));
        return;
      }
      inertedNodes.forEach((node) => node.removeAttribute("inert"));
      inertedNodes = [];
    };

    const close = () => {
      dialog.setAttribute("aria-hidden", "true");
      target.removeAttribute("src");
      target.alt = "";
      document.body.classList.remove("lightbox-open");
      setBackgroundInert(false);
      if (trigger) trigger.focus();
    };

    document.querySelectorAll("[data-lightbox-image]").forEach((button) => {
      button.addEventListener("click", () => {
        const image = button.querySelector("img");
        if (!image) return;
        trigger = button;
        target.src = image.currentSrc || image.src;
        target.alt = image.alt;
        dialog.setAttribute("aria-hidden", "false");
        document.body.classList.add("lightbox-open");
        setBackgroundInert(true);
        closeButton.focus();
      });
    });

    closeButton.addEventListener("click", close);
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) close();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Tab" && dialog.getAttribute("aria-hidden") === "false") {
        event.preventDefault();
        closeButton.focus();
        return;
      }
      if (event.key === "Escape" && dialog.getAttribute("aria-hidden") === "false") {
        close();
      }
    });
  }

  function animateCounter(node) {
    const target = Number(node.dataset.countTo);
    const decimals = Number(node.dataset.decimals || 0);
    const prefix = node.dataset.prefix || "";
    const suffix = node.dataset.suffix || "";

    const render = (value) => {
      node.textContent = `${prefix}${value.toFixed(decimals)}${suffix}`;
    };

    if (!Number.isFinite(target) || prefersReducedMotion) {
      render(target);
      return;
    }

    const start = performance.now();
    const tick = (now) => {
      const elapsed = Math.min((now - start) / 950, 1);
      const eased = 1 - Math.pow(1 - elapsed, 3);
      render(target * eased);
      if (elapsed < 1) window.requestAnimationFrame(tick);
    };
    window.requestAnimationFrame(tick);
  }

  function initRevealsAndCounters() {
    document.querySelectorAll("[data-count-to]").forEach(animateCounter);
    const nodes = [...document.querySelectorAll("[data-reveal]")];
    if (!nodes.length) return;

    const reveal = (node) => {
      node.classList.add("is-visible");
      node.classList.remove("reveal-ready");
    };

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      nodes.forEach(reveal);
      return;
    }

    nodes.forEach((node) => node.classList.add("reveal-ready"));
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        reveal(entry.target);
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    nodes.forEach((node) => observer.observe(node));
  }

  function initSectionNavigation() {
    if (!("IntersectionObserver" in window)) return;
    const links = [...document.querySelectorAll('#primary-navigation a[href^="#"]')];
    const byId = new Map(
      links.map((link) => [link.getAttribute("href").slice(1), link]),
    );

    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((left, right) => right.intersectionRatio - left.intersectionRatio)[0];
      if (!visible) return;
      links.forEach((link) => link.removeAttribute("aria-current"));
      const current = byId.get(visible.target.id);
      if (current) current.setAttribute("aria-current", "location");
    }, { rootMargin: "-25% 0px -62%", threshold: [0, 0.25, 0.6] });

    byId.forEach((_, id) => {
      const section = document.getElementById(id);
      if (section) observer.observe(section);
    });
  }

  function initHeaderState() {
    const header = document.querySelector("[data-site-header]");
    if (!header) return;
    const update = () => header.classList.toggle("is-scrolled", window.scrollY > 12);
    update();
    window.addEventListener("scroll", update, { passive: true });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initLanguage();
    initNavigation();
    initTabs();
    initCopyButtons();
    initLightbox();
    initRevealsAndCounters();
    initSectionNavigation();
    initHeaderState();
  });
})();
