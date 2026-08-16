import instaloader

USUARIO = "misaelandrejezieski"
SENHA = "SUA_SENHA_AQUI"  # <-- COLOCA SUA SENHA

L = instaloader.Instaloader()
L.login(USUARIO, SENHA)
L.save_session_to_file()
print("✅ Sessão salva com sucesso!")