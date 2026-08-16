import instaloader

# Seu usuário (já configurado)
USUARIO = "misaelandrejezieski"

# Inicializa o Instaloader
L = instaloader.Instaloader()

# ==========================================================
# ATENÇÃO: COPIE OS VALORES EXATOS DO SEU PRINT AQUI!
# Lembre-se de colocar as aspas duplas no começo e no fim.
# ==========================================================

# 1. O valor do sessionid é gigante (tem "..." no seu print). 
#    Você precisa pegar ele inteiro no navegador e colar entre as aspas.
L.context._session.cookies.set("sessionid", "17098757153%3A0mz8qIFEpKyG4%3A16%3AAYQ...") 

# 2. Coloque o csrftoken exato do seu print
L.context._session.cookies.set("csrftoken", "3uiterCtxZje3caXGqn5nW0JDJSzE")

# 3. Coloque o ds_user_id exato do seu print
L.context._session.cookies.set("ds_user_id", "17098757153")

# ==========================================================

# Salva a sessão no disco
L.save_session_to_file(USUARIO)

print("✅ SESSÃO SALVA COM SUCESSO!")
print(f"📁 Arquivo de sessão criado para o usuário: {USUARIO}")
print("🎯 Agora você pode fechar este programa e rodar o principal!")