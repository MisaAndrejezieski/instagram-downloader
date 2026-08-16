import os

import instaloader

USUARIO = "misaelandrejezieski"
# COLOQUE SUA SENHA AQUI NOVAMENTE (pois o checkpoint já foi confirmado no navegador)
SENHA = "#Sonho1313" 

print(f"🚀 Iniciando login para {USUARIO}...")

try:
    L = instaloader.Instaloader()
    
    # Tenta fazer o login. Como você já confirmou o checkpoint no navegador,
    # o Instagram não vai mais bloquear agora.
    L.login(USUARIO, SENHA)
    
    # Salva a sessão
    L.save_session_to_file(USUARIO)
    
    print("✅ SESSÃO SALVA COM SUCESSO!")
    print(f"📁 Arquivo de sessão '{USUARIO}' criado.")
    print("🎯 Agora pode rodar o programa principal, ele vai abrir logado!")

except instaloader.exceptions.TwoFactorAuthRequiredException:
    print("⚠️ O Instagram pediu código 2FA. Verifique seu app e tente novamente.")
except Exception as e:
    print(f"❌ Erro: {e}")