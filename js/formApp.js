
    document.addEventListener('DOMContentLoaded', function() {
        const toggleButton = document.getElementById('theme-toggle');
        const body = document.body;
        toggleButton.innerHTML = '🌙 Modo Oscuro';

        toggleButton.addEventListener('click', function() {
            body.classList.toggle('dark-theme');
            if (body.classList.contains('dark-theme')) {
                this.innerHTML = '☀️ Modo Claro';
            } else {
                this.innerHTML = '🌙 Modo Oscuro';
            }
        });
    });
