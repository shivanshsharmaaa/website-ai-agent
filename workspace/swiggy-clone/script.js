document.addEventListener('DOMContentLoaded', () => {
  const categories = document.querySelectorAll('#categories li');
  const cards = document.querySelectorAll('.card');
  const searchInput = document.getElementById('search');

  function filterCards() {
    const activeCat = document.querySelector('#categories li.active').dataset.cat;
    const query = searchInput.value.toLowerCase();
    cards.forEach(card => {
      const catMatch = activeCat === 'all' || card.dataset.cat === activeCat;
      const textMatch = card.textContent.toLowerCase().includes(query);
      card.style.display = catMatch && textMatch ? 'block' : 'none';
    });
  }

  categories.forEach(li => {
    li.addEventListener('click', () => {
      categories.forEach(c => c.classList.remove('active'));
      li.classList.add('active');
      filterCards();
    });
  });

  searchInput.addEventListener('input', filterCards);
});
