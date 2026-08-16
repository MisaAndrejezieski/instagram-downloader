import instaloader

# Seu usuário
USUARIO = "misaelandrejezieski"

# Inicializa o loader
L = instaloader.Instaloader()

# ==========================================================
# COLE OS VALORES EXATOS QUE VOCÊ ME MANDOU AQUI
# ==========================================================

L.context._session.cookies.set("sessionid", "17098757153%3A0mz8qJFEp9cyG4%3A16%3AAYiQrp24FLK-TfZOdtmKpmsNdirgI486WMAib5ggFw")

L.context._session.cookies.set("csrftoken", "3uiterCtxZje3caXGqn5nW0JDJSzE")

L.context._session.cookies.set("ds_user_id", "17098757153")

# ==========================================================

# Salva a sessão no disco
L.save_session_to_file(USUARIO)

print("✅ SESSÃO SALVA COM SUCESSO!")
print("🎯 Agora rode o programa principal!")