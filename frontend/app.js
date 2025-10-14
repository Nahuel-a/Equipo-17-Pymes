document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("recuperarForm");
  const container = document.getElementById("formulario-container");

  if (form) {
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
  }

  // Registration form validation
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    const emailInput = document.getElementById('email');
    const emailError = document.getElementById('email-error');
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('password-strength');

    emailInput.addEventListener('input', () => {
        const email = emailInput.value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email.length > 0 && !emailRegex.test(email)) {
            emailError.textContent = 'Debe ser un email válido.';
            emailError.style.color = 'orange';
            emailError.style.display = 'block';
        } else {
            if (emailError.textContent === 'Debe ser un email válido.') {
                emailError.style.display = 'none';
            }
        }
    });

    emailInput.addEventListener('blur', () => {
        const email = emailInput.value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (email.length > 0 && !emailRegex.test(email)) {
            emailError.textContent = 'Debe ser un email válido.';
            emailError.style.color = 'orange';
            emailError.style.display = 'block';
            return;
        }

        if (email.length > 0) {
            fetch('/check-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    emailError.textContent = 'El email ya está registrado.';
                    emailError.style.color = 'red';
                    emailError.style.display = 'block';
                } else {
                    emailError.style.display = 'none';
                }
            });
        } else {
            emailError.style.display = 'none';
        }
    });

    passwordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        let strength = '';
        const regex = new RegExp("^(?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$");
        if(regex.test(password)) {
            strength = 'Segura';
            passwordStrength.style.color = 'green';
        } else {
            strength = 'Debe contener al menos un número, una mayúscula, una minúscula y al menos 8 caracteres.';
            passwordStrength.style.color = 'orange';
        }
        passwordStrength.textContent = strength;
    });
  }

  // Password recovery form
  const passwordForm = document.getElementById('passwordForm');
  if(passwordForm) {
    const newPasswordInput = document.getElementById('newPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const messageDisplay = document.getElementById('message');

    function checkPasswords(event) {
        event.preventDefault();
        messageDisplay.textContent = '';
        messageDisplay.className = 'message';
        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        if (!newPassword || !confirmPassword) {
            return; 
        }
        if (newPassword === confirmPassword) {
            messageDisplay.textContent = '¡Contraseñas coinciden! Procesando...';
            messageDisplay.classList.add('success');
            setTimeout(() => {
                passwordForm.submit();
            }, 2000);

        } else {
            messageDisplay.textContent = 'ERROR: Las contraseñas NO coinciden.';
            messageDisplay.classList.add('error');
            confirmPasswordInput.value = '';
            confirmPasswordInput.focus();
        }
    }

    passwordForm.addEventListener('submit', checkPasswords);
  }
});