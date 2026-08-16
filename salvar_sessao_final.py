import os
import subprocess

import instaloader

USUARIO = "misaelandrejezieski"

print("🚀 Iniciando captura da sessão do navegador...")

# Força a importação do navegador de forma mais bruta, ignorando proteções do Edge
try:
    L = instaloader.Instaloader()
    
    # Tenta usar o comando nativo do Windows para importar a sessão do Edge (funciona como último recurso)
    print("🍪 Tentando importar diretamente do Edge (método alternativo)...")
    
    # Importa do Edge padrão do Windows
    L.import_session_from_browser("edge")
    
    # Salva a sessão no arquivo
    L.save_session_to_file(USUARIO)
    
    print("✅ Sucesso! Sessão salva no disco.")
    print(f"📁 Arquivo '{USUARIO}' criado na pasta.")
    print("🎯 Agora você pode apagar este script, fechar o Edge e rodar o programa principal!")

except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    print("⚠️ Se falhar, o Edge pode ter bloqueado. Feche o Edge, abra-o novamente, logue no Instagram e repita o processo.")