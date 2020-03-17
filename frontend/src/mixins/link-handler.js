function handleRouterClick(e) {
  e.preventDefault();
  this.$router.push(e.target.pathname);
}

const HAS_LISTENER = 'has-listener';

function bindRouterLink(_this) {
  const routerLinks = document.querySelectorAll('.custom-router-link');

  routerLinks.forEach((link) => {
    if (!link.getAttribute(HAS_LISTENER)) {
      link.setAttribute(HAS_LISTENER, 'true');
      link.addEventListener('click', _this.handleRouterClick);
    }
  });
}

export {
  handleRouterClick,
  bindRouterLink,
};
