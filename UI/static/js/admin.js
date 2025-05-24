function showForm(formId) {
  const forms = ["add-form", "edit-form", "delete-form", "view"];
  forms.forEach((id) => {
    const element = document.getElementById(id);
    element.style.display = id === formId ? "block" : "none";
  });
  // If no form is selected, hide all
  if (formId === "none") {
    forms.forEach((id) => {
      document.getElementById(id).style.display = "none";
    });
  }
}
// Hide all forms by default
showForm("none");

// Example: Add course via AJAX
function addCourse(event) {
  event.preventDefault();
  const form = document.getElementById('add-form');
  const formData = new FormData(form);
  fetch('/add', {
    method: 'POST',
    body: formData
  })
    .then(response => {
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        return response.text();
      }
    })
    .then(data => {
      // Optionally handle response data
      // alert('Course added!');
      // location.reload();
    })
    .catch(error => {
      alert('Error adding course: ' + error);
    });
}

// Attach to form if it exists
const addForm = document.getElementById('add-form');
if (addForm) {
  addForm.addEventListener('submit', addCourse);
}
