function populateTable(id, data) {
  const table = document.getElementById(id);
  if (data.length === 0) {
    table.innerHTML = '<tr><td>No data available</td></tr>';
    return;
  }
  const headers = Object.keys(data[0]);
  table.innerHTML = `
    <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
    ${data.map(row => `<tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>`).join('')}
  `;
  }


  async function findNearestHospitals() {
    const city = document.getElementById('city').value;
    const state = document.getElementById('state').value;
    const zip = document.getElementById('zip').value;
  
    if (!city || !state || !zip) {
      alert('Please enter city, state, and zip code');
      return;
    }
  
    try {
      const res = await fetch('/api/nearest-hospitals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          city,
          state,
          zip
        })
      });      
      const nearest = await res.json();
      populateTable('nearest-hospitals', nearest);

    } 
    catch (error) {
      console.error("Error fetching nearest hospitals:", error);
      alert("Failed to fetch nearest hospitals. Please check your input or try again.");
    }
  }

  async function findHospitalBySymptom(){
    const condition = document.getElementById('condition').value;

    console.log(condition);

    if(!condition){
      alert("Please enter the symptoms for us to suggest a doctor");
      return;
    }
    
    try
    {
      const res = await fetch('/api/condition-hospitals',{
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({condition})
      });
      const hospitals = await res.json();
      populateTable('symptom-hospitals',hospitals);
    }
    catch(error)
    {
      console.error("Error fetching the right hospitals:", error);
      alert("Failed to fetch the right hospitals. Please check your input or try again.");
    }
  }
  
  document.getElementById('location-form').addEventListener('submit', function (e) {
    e.preventDefault();
    findNearestHospitals();
  });
  

  document.getElementById('symptom-form').addEventListener('submit',function(e){
    e.preventDefault();
    findHospitalBySymptom();
  });