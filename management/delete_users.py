import sys
import os
import getpass
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.db import SyncSessionLocal
from server.models import User

def list_users(session):
    users = session.query(User).order_by(User.created_at.desc()).all()
    print("\nUsuarios registrados:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.name or '-'} | {user.email} | ID: {user.id}")
    return users

def delete_user(session, user):
    session.delete(user)
    session.commit()
    print(f"Usuario {user.email} eliminado.")

def change_password(session, user):
    new_password = getpass.getpass("Nueva contraseña: ")
    confirm_password = getpass.getpass("Confirme la contraseña: ")
    if new_password != confirm_password:
        print("❌ Las contraseñas no coinciden.")
        return
    user.password = new_password
    session.commit()
    print(f"✅ Contraseña cambiada para {user.email}")

def main():
    session = SyncSessionLocal()
    users = list_users(session)
    if not users:
        print("No hay usuarios en la base de datos.")
        return

    try:
        print("\nOpciones:")
        print("1. Eliminar usuario")
        print("2. Cambiar contraseña de usuario")
        option = input("Seleccione una opción (1/2): ").strip()
        if option not in {"1", "2"}:
            print("Opción inválida.")
            return

        user_idx = int(input("Ingrese el número del usuario: ").strip()) - 1
        if user_idx < 0 or user_idx >= len(users):
            print("Número fuera de rango.")
            return

        user = users[user_idx]

        if option == "1":
            confirm = input(f"¿Seguro que desea eliminar a {user.email}? (s/N): ").strip().lower()
            if confirm == "s":
                delete_user(session, user)
            else:
                print("Operación cancelada.")
        else:
            change_password(session, user)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
