import router from '@/router';

function handleRouterClick(e) {
  e.preventDefault();
  router.push(e.target.pathname);
}

const HAS_LISTENER = 'has-listener';

function bindRouterLink() {
  const routerLinks = document.querySelectorAll('.custom-router-link');

  routerLinks.forEach((link) => {
    if (!link.getAttribute(HAS_LISTENER)) {
      link.setAttribute(HAS_LISTENER, 'true');
      link.addEventListener('click', handleRouterClick);
    }
  });
}

export {
  handleRouterClick,
  bindRouterLink,
};
