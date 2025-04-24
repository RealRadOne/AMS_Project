document.getElementById('search-form').addEventListener('submit', async e => {
  e.preventDefault();
  const params = new URLSearchParams(new FormData(e.target));
  const res = await fetch(`/api/search?${params}`);
  const data = await res.json();
  const tbody = document.querySelector('#results-table tbody');
  tbody.innerHTML = '';
  if (data.error) {
    alert(data.error);
    return;
  }
  data.forEach(h => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${h.name}</td>
      <td>${h.address}</td>
      <td>${h.city}, ${h.state}</td>
      <td>${h.distance_miles}</td>
      <td>${h.avg_duration}</td>
      <td>${h.avg_cost}</td>
      <td>${h.status}</td>
      <td>${h.helipad}</td>
    `;
    tbody.appendChild(tr);
  });
});
