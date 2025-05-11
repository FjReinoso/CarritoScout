document.addEventListener('DOMContentLoaded', function () {
    const formulario = document.querySelector('#mi-perfil form');
    const campoCorreo = document.querySelector('#email');
    const campoNombre = document.querySelector('#first_name');
    const campoApellidos = document.querySelector('#last_name');

    // Función para mostrar mensajes de error
    function mostrarError(input, mensaje) {
        const divError = input.nextElementSibling;
        if (divError && divError.classList.contains('invalid-feedback')) {
            divError.textContent = mensaje;
            input.classList.add('is-invalid');
        }
    }

    // Función para limpiar mensajes de error
    function limpiarError(input) {
        const divError = input.nextElementSibling;
        if (divError && divError.classList.contains('invalid-feedback')) {
            divError.textContent = '';
            input.classList.remove('is-invalid');
        }
    }

    // Validación del campo de nombre
    campoNombre.addEventListener('input', function () {
        if (campoNombre.value.trim() === '') {
            mostrarError(campoNombre, 'El nombre no puede estar vacío.');
        } else {
            limpiarError(campoNombre);
        }
    });

    // Validación del campo de apellidos
    campoApellidos.addEventListener('input', function () {
        if (campoApellidos.value.trim() === '') {
            mostrarError(campoApellidos, 'Los apellidos no pueden estar vacíos.');
        } else {
            limpiarError(campoApellidos);
        }
    });

    // Validación al enviar el formulario
    formulario.addEventListener('submit', function (evento) {
        let esValido = true;

        // Validar cada campo
        if (!campoCorreo.value || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(campoCorreo.value)) {
            mostrarError(campoCorreo, 'Por favor, introduce un correo electrónico válido.');
            esValido = false;
        }
        if (campoNombre.value.trim() === '') {
            mostrarError(campoNombre, 'El nombre no puede estar vacío.');
            esValido = false;
        }
        if (campoApellidos.value.trim() === '') {
            mostrarError(campoApellidos, 'Los apellidos no pueden estar vacíos.');
            esValido = false;
        }

        // Prevenir el envío del formulario si hay errores
        if (!esValido) {
            evento.preventDefault();
        }
    });
});
