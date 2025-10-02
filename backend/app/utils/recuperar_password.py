import secrets

codigos = {}

# Generar código
email = input("Email: ").strip()
codigo = str(secrets.randbelow(1000000)).zfill(6)
codigos[email] = codigo
print(f"\n📧 Código: {codigo}\n")

# Cambiar contraseña
email2 = input("Email: ").strip()
codigo_ing = input("Código: ").strip()

if codigos.get(email2) == codigo_ing:
    nueva = input("Nueva contraseña: ").strip()
    confirmar = input("Confirmar: ").strip()
    
    if nueva == confirmar:
        print(f"✅ Contraseña cambiada: {nueva}")
    else:
        print("❌ No coinciden")
else:
    print("❌ Código incorrecto")