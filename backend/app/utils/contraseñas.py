from email_validator import validate_email, EmailNotValidError


# Solicitud de datos al usuario
nombre_usuario = input("Ingrese su nombre: ").title().strip()
apellido_usuario = input("Ingrese su apellido: ").title().strip()
email = input("Ingrese su email: ").strip()
contraseña = input("Ingrese su contraseña: ").strip()
validacion_contraseña = input("Confirme su contraseña: ").strip()

if contraseña == validacion_contraseña:
    print("✔")
else:
    print("Las contraseñas no coinciden.")

# Validación y normalización de email
try:
    email_info = validate_email(email, check_deliverability=False)
    email_normalizado = email_info.normalized
    print("Email válido y normalizado:", email_normalizado)
except EmailNotValidError as e:
    print("Error en email:", str(e))
    exit(1)