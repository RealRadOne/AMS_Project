let hospitalsData = []; // Full fetched data
let currentlyDisplayed = []; // Current view

// Fetch hospitals using location and distance
async function fetchHospitalsByDistance(latitude, longitude, distance) {
  try {
    const res = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude, longitude, distance })
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
  const table = document.getElementById(id).getElementsByTagName('tbody')[0];
  table.innerHTML = ''; // Clear the table

  data.forEach(hospital => {
    const row = table.insertRow();
    Object.values(hospital).forEach(value => {
      const cell = row.insertCell();
      cell.textContent = value;
    });
  });
}

// Populate dropdown filters dynamically
function populateFilters() {
  const insuranceFilter = document.getElementById('table-filter-insurance');
  const conditionFilter = document.getElementById('table-filter-condition');

  // Populate filters with unique values from hospitalsData
  const insuranceOptions = new Set();
  const conditionOptions = new Set();

  hospitalsData.forEach(hospital => {
    insuranceOptions.add(hospital['insurance_provider']);
    conditionOptions.add(hospital['medical_condition']);
  });

  // Populate insurance dropdown
  insuranceFilter.innerHTML = '<option value="">Filter by Insurance Provider</option>';
  insuranceOptions.forEach(option => {
    const opt = document.createElement('option');
    opt.value = option;
    opt.textContent = option;
    insuranceFilter.appendChild(opt);
  });

  // Populate condition dropdown
  conditionFilter.innerHTML = '<option value="">Filter by Medical Condition</option>';
  conditionOptions.forEach(option => {
    const opt = document.createElement('option');
    opt.value = option;
    opt.textContent = option;
    conditionFilter.appendChild(opt);
  });
}

// Filter hospitals in the table based on dropdown selections
function applyTableFilters() {
  const insurance = document.getElementById('table-filter-insurance').value.toLowerCase();
  const condition = document.getElementById('table-filter-condition').value.toLowerCase();

  currentlyDisplayed = hospitalsData.filter(hospital => {
    return (!insurance || hospital.insurance_provider.toLowerCase() === insurance) &&
           (!condition || hospital.medical_condition.toLowerCase() === condition);
  });

  populateTable('results-table', currentlyDisplayed);
}

// Handle Locate Me button
const locateBtn = document.getElementById('locate-btn');
locateBtn.addEventListener('click', () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(position => {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;

      document.getElementById('latitude').value = latitude;
      document.getElementById('longitude').value = longitude;
      document.getElementById('latitude-visible').value = latitude;
      document.getElementById('longitude-visible').value = longitude;

      // Immediately fetch hospitals after locating
      const distance = document.getElementById('distance-slider').value;
      fetchHospitalsByDistance(latitude, longitude, distance);

    }, error => {
      alert('Unable to retrieve your location');
    });
  } else {
    alert('Geolocation is not supported by your browser');
  }
});

// Distance Slider change
const distanceSlider = document.getElementById('distance-slider');
const distanceValue = document.getElementById('distance-value');

distanceSlider.addEventListener('input', () => {
  distanceValue.textContent = distanceSlider.value;
});

distanceSlider.addEventListener('change', () => {
  const latitude = document.getElementById('latitude').value;
  const longitude = document.getElementById('longitude').value;
  const distance = distanceSlider.value;

  if (latitude && longitude) {
    fetchHospitalsByDistance(latitude, longitude, distance);
  } else {
    alert('Please click Locate Me first to get your location!');
  }
});

// Filter changes
['table-filter-insurance', 'table-filter-condition'].forEach(id => {
  document.getElementById(id).addEventListener('change', applyTableFilters);
});
