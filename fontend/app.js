document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("recuperarForm");
  const container = document.getElementById("formulario-container");

    //Solo ejecuta esta lógica si el formulario 'recuperarForm' existe en la página donde se esta haciendo foco.
    if (form && container) {
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
                    </button>
                </a>
            `;
        });
    } else {
    }
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


if (passwordForm && newPasswordInput && confirmPasswordInput && messageDisplay) {
    // Esta función se ejecuta ANTES de que el formulario intente enviarse
    passwordForm.addEventListener('submit', checkPasswords);
} else {
}











// Esta función permite ver o no la contraseña 
const passwordInput = document.getElementById('password');
const toggleButton = document.getElementById('togglePassword');

if(passwordForm && toggleButton){
    togglePassword.addEventListener('click', function (e) {
        // 1. Alternar el tipo de input (password <-> text)
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // 2. Alternar el icono (ojo abierto <-> ojo tachado)
        this.querySelector('i').classList.toggle('fa-eye');
        this.querySelector('i').classList.toggle('fa-eye-slash');
    });
} else{

}









document.addEventListener("DOMContentLoaded", function() {
    const hamburgerMenu = document.getElementById('hamburgerMenu');
    const navLinksContainer = document.getElementById('navLinksContainer');

    if (hamburgerMenu && navLinksContainer) {
        hamburgerMenu.addEventListener("click", function() {
            navLinksContainer.classList.toggle("active");
            // Opcional: Cambiar el ícono de hamburguesa a una 'X'
            const icon = this.querySelector('i');
            if (navLinksContainer.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times'); // 'fa-times' es el ícono de una 'X'
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });

        // Opcional: Cerrar el menú si se hace clic fuera de él (para mejorar la UX)
        document.addEventListener("click", function(event) {
            const isClickInsideMenu = navLinksContainer.contains(event.target);
            const isClickOnHamburger = hamburgerMenu.contains(event.target);

            if (!isClickInsideMenu && !isClickOnHamburger && navLinksContainer.classList.contains("active")) {
                navLinksContainer.classList.remove("active");
                hamburgerMenu.querySelector('i').classList.remove('fa-times');
                hamburgerMenu.querySelector('i').classList.add('fa-bars');
            }
        });
    }
});