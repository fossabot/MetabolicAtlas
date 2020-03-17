function handleRouterClick(e) {
  e.preventDefault();
  this.$router.push(e.target.pathname);
}

export default handleRouterClick;
