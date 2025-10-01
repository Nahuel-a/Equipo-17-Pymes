document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("recuperarForm");
  const container = document.getElementById("formulario-container");

  if (!form) {
    console.error("No se encontró el formulario #recuperarForm");
    return;
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    container.innerHTML = `
      <h2>Se ha enviado un correo de recuperación a tu email.</h2>
      <p style="color:white; font-size:16px; margin-top:20px; text-align: center;">
        No recibí el correo
      </p>
        <a href="/password-recovery">
        <button id="reenviarForm" 
              style="padding:10px 20px; border:none; border-radius:20px; background:#ff5722; color:white; font-weight:bold; cursor:pointer;">
        Reenviar
      </button> </a>
    `;
  });
});

// Obtengo los elementos del DOM
const passwordForm = document.getElementById('passwordForm');
const newPasswordInput = document.getElementById('newPassword');
const confirmPasswordInput = document.getElementById('confirmPassword');
const messageDisplay = document.getElementById('message');


//Función que maneja el envío del formulario y la validación de contraseñas

function checkPasswords(event) {
    // Evito el envio del formulario
    event.preventDefault();

    // Limpia los mensajes anteriores
    messageDisplay.textContent = '';
    messageDisplay.className = 'message';

    // Obtiene los valores
    const newPassword = newPasswordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    
    // Si la nueva contraseña o la confirmación están vacías, no hacemos nada 
    // y dejamos que el "required" del HTML entre en acción
    if (!newPassword || !confirmPassword) {
        // Esto solo para asegurar que los campos tienen contenido
        return; 
    }

    // Verifica si las contraseñas coinciden
    if (newPassword === confirmPassword) {
        messageDisplay.textContent = '¡Contraseñas coinciden! Procesando...';
        messageDisplay.classList.add('success');
        setTimeout(() => {
            passwordForm.submit();
        }, 6000);

    } else {
        messageDisplay.textContent = 'ERROR: Las contraseñas NO coinciden.';
        messageDisplay.classList.add('error');
        confirmPasswordInput.value = '';
        confirmPasswordInput.focus();
    }
}

// Esta función se ejecuta ANTES de que el formulario intente enviarse
passwordForm.addEventListener('submit', checkPasswords);