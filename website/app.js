// Updated app.js

let hospitalsData = []; // Full data from backend
let currentlyDisplayed = []; // What is currently shown after backend search

// Fetch hospitals initially
async function fetchHospitals(zip = '', insurance = '', condition = '') {
  try {
    const res = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ zip, insurance, condition, age_group: '' })
    });

    hospitalsData = await res.json();
    currentlyDisplayed = hospitalsData;
    populateFilters();
    populateTable('results-table', currentlyDisplayed);
  } catch (error) {
    console.error('Error loading hospitals:', error);
  }
}

// Populate the hospital table
function populateTable(id, data) {
  const table = document.getElementById(id);
  if (!table) return;
  if (data.length === 0) {
    table.querySelector('tbody').innerHTML = '<tr><td colspan="11" class="text-center">No hospitals found</td></tr>';
    return;
  }

  table.querySelector('tbody').innerHTML = data.map(h => `
    <tr>
      <td>${h.name}</td>
      <td>${h.address}</td>
      <td>${h.city}</td>
      <td>${h.state}</td>
      <td>${h.zip}</td>
      <td>${h.telephone}</td>
      <td>${h.type}</td>
      <td>${h.status}</td>
      <td>${h.helipad}</td>
      <td>${h.insurance_provider || '-'}</td>
      <td>${h.medical_condition || '-'}</td>
    </tr>
  `).join('');
}

// Populate dropdown filters dynamically
function populateFilters() {
  const insuranceSet = new Set();
  const conditionSet = new Set();

  hospitalsData.forEach(h => {
    if (h.insurance_provider) insuranceSet.add(h.insurance_provider);
    if (h.medical_condition) conditionSet.add(h.medical_condition);
  });

  populateDropdown('table-filter-insurance', insuranceSet);
  populateDropdown('table-filter-condition', conditionSet);
}

function populateDropdown(id, values) {
  const select = document.getElementById(id);
  select.innerHTML = '<option value="">All</option>'; // Reset first
  values.forEach(val => {
    const option = document.createElement('option');
    option.value = val;
    option.textContent = val;
    select.appendChild(option);
  });
}

// Filter hospitals in the table only based on dropdowns
function applyTableFilters() {
  const insuranceInput = document.getElementById('table-filter-insurance').value.trim().toLowerCase();
  const conditionInput = document.getElementById('table-filter-condition').value.trim().toLowerCase();

  let filtered = currentlyDisplayed;

  if (insuranceInput) {
    filtered = filtered.filter(h => h.insurance_provider && h.insurance_provider.toLowerCase() === insuranceInput);
  }
  if (conditionInput) {
    filtered = filtered.filter(h => h.medical_condition && h.medical_condition.toLowerCase() === conditionInput);
  }

  populateTable('results-table', filtered);
}

// When user submits the top search form
const searchForm = document.getElementById('search-form');
searchForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const zip = searchForm.zip.value.trim();
  const insurance = searchForm.insurance.value.trim();
  const condition = searchForm.condition.value.trim();

  await fetchHospitals(zip, insurance, condition);
});

// When user changes table filters
['table-filter-insurance', 'table-filter-condition'].forEach(id => {
  document.getElementById(id).addEventListener('change', applyTableFilters);
});

// Initial load
fetchHospitals();
