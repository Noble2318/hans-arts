(() => {
  const root = document.documentElement;
  const themeButton = document.querySelector('#theme-toggle');
  const themeLabel = themeButton?.querySelector('.theme-toggle__label');
  const themeIcon = themeButton?.querySelector('.theme-toggle__icon');

  const setTheme = (theme) => {
    if (theme === 'light') {
      root.dataset.theme = 'light';
    } else {
      delete root.dataset.theme;
    }

    const isLight = theme === 'light';
    themeButton?.setAttribute('aria-pressed', String(isLight));
    themeButton?.setAttribute('aria-label', `Switch to ${isLight ? 'dark' : 'light'} theme`);
    themeButton?.setAttribute('title', `Switch to ${isLight ? 'dark' : 'light'} theme`);
    if (themeLabel) themeLabel.textContent = isLight ? 'Dark' : 'Light';
    if (themeIcon) themeIcon.textContent = isLight ? '☾' : '☼';
  };

  setTheme(root.dataset.theme === 'light' ? 'light' : 'dark');
  themeButton?.addEventListener('click', () => {
    const nextTheme = root.dataset.theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    try {
      localStorage.setItem('hans-arts-theme', nextTheme);
    } catch (error) {}
  });

  document.querySelectorAll('form').forEach((form) => {
    const inquiryType = form.querySelector('[name="inquiry_type"]');
    const orderDetails = form.querySelector('[name="order_details"]');
    const orderDetailsField = orderDetails?.closest('.form-field');
    if (!inquiryType || !orderDetails || !orderDetailsField) return;

    const updateOrderDetailsVisibility = () => {
      const isOrder = inquiryType.value === 'order';
      orderDetailsField.hidden = !isOrder;
      orderDetails.required = isOrder;
    };

    inquiryType.addEventListener('change', updateOrderDetailsVisibility);
    updateOrderDetailsVisibility();
  });

  const mainImage = document.querySelector('#main-image');
  const previewButton = document.querySelector('[data-lightbox-open]');
  const thumbnails = [...document.querySelectorAll('[data-artwork-thumbnail]')];
  const dialog = document.querySelector('#art-lightbox');

  if (mainImage && previewButton && dialog) {
    const previewImage = dialog.querySelector('#lightbox-image');
    const previewVideo = dialog.querySelector('#lightbox-video');
    const previewVideoContainer = dialog.querySelector('#lightbox-video-container');
    const previewVideoCaption = dialog.querySelector('#lightbox-video-caption');
    const caption = dialog.querySelector('#lightbox-caption');
    const previousButton = dialog.querySelector('[data-lightbox-previous]');
    const nextButton = dialog.querySelector('[data-lightbox-next]');
    let activeIndex = 0;

    const getImages = () => [
      { src: mainImage.dataset.originalSrc || mainImage.src, alt: mainImage.alt },
      ...thumbnails.map((thumbnail) => ({
        src: thumbnail.dataset.src,
        alt: thumbnail.dataset.alt || mainImage.alt,
      })),
    ];

    const showImage = (index) => {
      const images = getImages();
      activeIndex = (index + images.length) % images.length;
      previewImage.src = images[activeIndex].src;
      previewImage.alt = images[activeIndex].alt;
      caption.textContent = images[activeIndex].alt;
      const hasMultipleImages = images.length > 1;
      previousButton.hidden = !hasMultipleImages;
      nextButton.hidden = !hasMultipleImages;
    };

    mainImage.dataset.originalSrc = mainImage.src;
    previewButton.addEventListener('click', () => {
      const images = getImages();
      const currentIndex = images.findIndex((image) => image.src === mainImage.src);
      showImage(currentIndex < 0 ? 0 : currentIndex);
      if (previewButton.dataset.videoSrc) {
        previewVideo.src = previewButton.dataset.videoSrc;
        previewVideo.setAttribute('aria-label', previewButton.dataset.videoCaption);
        previewVideoCaption.textContent = previewButton.dataset.videoCaption;
        previewVideoContainer.hidden = false;
      }
      dialog.showModal();
    });

    thumbnails.forEach((thumbnail) => {
      thumbnail.addEventListener('click', () => {
        mainImage.src = thumbnail.dataset.src;
        mainImage.alt = thumbnail.dataset.alt || mainImage.alt;
        thumbnails.forEach((item) => item.setAttribute('aria-pressed', 'false'));
        thumbnail.setAttribute('aria-pressed', 'true');
      });
    });

    previousButton.addEventListener('click', () => showImage(activeIndex - 1));
    nextButton.addEventListener('click', () => showImage(activeIndex + 1));
    dialog.querySelector('[data-lightbox-close]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('close', () => {
      previewVideo.pause();
      previewVideo.removeAttribute('src');
      previewVideo.load();
      previewVideoContainer.hidden = true;
    });
    dialog.addEventListener('click', (event) => {
      if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft' && thumbnails.length) {
        event.preventDefault();
        showImage(activeIndex - 1);
      }
      if (event.key === 'ArrowRight' && thumbnails.length) {
        event.preventDefault();
        showImage(activeIndex + 1);
      }
    });
  }

  const cards = [...document.querySelectorAll('.painting-card')];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (cards.length && 'IntersectionObserver' in window && !reduceMotion) {
    root.classList.add('reveal-ready');
    const observer = new IntersectionObserver((entries, currentObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          currentObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    cards.forEach((card, index) => {
      card.style.setProperty('--reveal-delay', `${Math.min(index * 55, 220)}ms`);
      observer.observe(card);
    });
  }
})();