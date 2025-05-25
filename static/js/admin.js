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
