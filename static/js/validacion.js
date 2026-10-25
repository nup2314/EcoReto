// Confirmación antes de eliminar
document.querySelectorAll("form[data-confirmar]").forEach(function (f) {
  f.addEventListener("submit", function (e) {
    if (!confirm(f.dataset.confirmar)) e.preventDefault();
  });
});

// Validación simple del formulario: quita espacios y evita campos vacíos
document.querySelectorAll("form[data-validar]").forEach(function (f) {
  f.addEventListener("submit", function (e) {
    var vacio = false;
    f.querySelectorAll("input[required], textarea[required]").forEach(function (c) {
      c.value = c.value.trim();
      if (!c.value) { c.classList.add("invalido"); vacio = true; }
      else { c.classList.remove("invalido"); }
    });
    if (vacio) e.preventDefault();
  });
});
