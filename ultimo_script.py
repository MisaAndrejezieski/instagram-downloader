import instaloader

USUARIO = "misaelandrejezieski"
SENHA = "SUA_SENHA_AQUI"

L = instaloader.Instaloader()

# A "Mágica" está aqui: salvando a sessão ANTES de tentar logar.
# Isso faz o Instaloader entender que você quer o login padrão, sem ficar tentando 
# importar do navegador ou usar proxies que geram checkpoints.
try:
    L.save_session_to_file(USUARIO)
    L.login(USUARIO, SENHA)
    print("✅ Sessão salva com sucesso!")
except Exception as e:
    print(f"❌ Erro: {e}")