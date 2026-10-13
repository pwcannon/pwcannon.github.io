(() => {
  const filters = document.querySelector('.writing-filters');
  if (!filters) return;
  const buttons = [...filters.querySelectorAll('button')];
  const categories = buttons.map(button => button.dataset.writingFilter).filter(category => category !== 'all');
  const labels = Object.fromEntries(buttons.map(button => [button.dataset.writingFilter, button.querySelector('.writing-filter-label').textContent]));
  const items = [...document.querySelectorAll('.writing-item')];
  const years = [...document.querySelectorAll('.writing-year')];
  const status = document.querySelector('.writing-filter-status');
  const empty = document.querySelector('.writing-filter-empty');

  function render() {
    const type = new URL(window.location.href).searchParams.get('type');
    const selected = categories.includes(type) ? type : 'all';
    let count = 0;
    items.forEach(item => {
      item.hidden = selected !== 'all' && item.dataset.writingCategory !== selected;
      if (!item.hidden) count += 1;
    });
    years.forEach(year => {
      year.hidden = ![...year.querySelectorAll('.writing-item')].some(item => !item.hidden);
    });
    buttons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.writingFilter === selected));
    });
    empty.hidden = count > 0 || items.length === 0;
    const selection = selected === 'all' ? 'All writing' : labels[selected];
    status.textContent = `${selection}: ${count} ${count === 1 ? 'post' : 'posts'}.`;
  }

  buttons.forEach(button => button.addEventListener('click', () => {
    const category = button.dataset.writingFilter;
    const url = new URL(window.location.href);
    if (category === 'all') url.searchParams.delete('type');
    else url.searchParams.set('type', category);
    if (url.href !== window.location.href) window.history.pushState(null, '', url);
    render();
  }));
  window.addEventListener('popstate', render);
  render();
  filters.hidden = false;
})();
