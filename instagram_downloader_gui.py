import os
import re
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext

import instaloader

# ============================================
# 👤 SEUS DADOS - SÓ ALTERE A SENHA AQUI
# ============================================
USUARIO = "misaelandrejezieski"
SENHA = "#Sonho1313" # <--- COLOQUE SUA SENHA AQUI, COM AS ASPAS
# ============================================

class InstagramDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("📸 Baixador do Instagram")
        self.root.geometry("700x600")
        self.root.configure(bg='#1a1a2e')
        
        self.loader = instaloader.Instaloader()
        self.logado = False
        
        self.criar_interface()
        
        # Tenta carregar do Edge automaticamente, ou salva a sessão
        self.root.after(500, self.login_automatico_ou_salvar)
    
    def login_automatico_ou_salvar(self):
        def thread_login():
            try:
                self.log("🔐 Tentando login com sessão salva ou navegador...")
                
                # 1. Tenta carregar sessão salva (se já rodou antes)
                try:
                    self.loader.load_session_from_file(USUARIO)
                    self.logado = True
                    self.status_login.config(text="✅ Logado! (Sessão)", fg='#25d366')
                    self.log("✅ Sessão carregada com sucesso!")
                    return
                except:
                    pass

                # 2. Tenta importar sessão do Edge (AQUI ESTÁ A MÁGICA)
                try:
                    self.log("🍪 Importando cookies do Microsoft Edge...")
                    # Usa o navegador padrão do Windows para pegar os cookies do Instagram
                    self.loader.import_session_from_browser("edge")
                    self.logado = True
                    self.loader.save_session_to_file(USUARIO) # Salva para não precisar repetir
                    self.status_login.config(text="✅ Logado! (Edge)", fg='#25d366')
                    self.log("✅ Sessão importada do Microsoft Edge!")
                    return
                except:
                    pass

                # 3. Se não tiver sessão e não conseguir importar do Edge, faz o login com senha
                if SENHA:
                    self.log(f"🔐 Fazendo login com senha para {USUARIO}...")
                    self.loader.login(USUARIO, SENHA)
                    self.loader.save_session_to_file(USUARIO)
                    self.logado = True
                    self.status_login.config(text="✅ Logado!", fg='#25d366')
                    self.log("✅ Login com senha realizado com sucesso!")
                else:
                    self.log("❌ Falha: Nenhuma sessão, senha não configurada.")
                    self.status_login.config(text="❌ Deslogado", fg='#ff6b6b')

            except Exception as e:
                erro = str(e)
                self.log(f"❌ Erro no login: {erro}")
                self.status_login.config(text="❌ Falha", fg='#ff6b6b')
                
                if "Checkpoint" in erro:
                    self.log("⚠️ O Instagram ainda pede verificação.")
                    self.log("💡 Abra o Edge, faça login manualmente e DEIXE ABERTO.")
                    self.log("🔄 Depois feche e abra este programa novamente.")

        threading.Thread(target=thread_login, daemon=True).start()
    
    def criar_interface(self):
        titulo = tk.Label(self.root, text="📸 Baixador do Instagram", font=("Segoe UI", 20, "bold"), bg='#1a1a2e', fg='#e1306c')
        titulo.pack(pady=20)
        
        self.status_login = tk.Label(self.root, text="⏳ Conectando...", bg='#1a1a2e', fg='#ffaa00', font=("Segoe UI", 10))
        self.status_login.pack()
        
        main = tk.Frame(self.root, bg='#1a1a2e')
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        tk.Label(main, text="Link do Post ou Perfil:", bg='#1a1a2e', fg='white').pack(anchor='w')
        self.url_entry = tk.Entry(main, bg='#2a2a4a', fg='white', insertbackground='white', font=("Segoe UI", 11))
        self.url_entry.pack(fill=tk.X, pady=(0, 10))
        self.url_entry.insert(0, "https://www.instagram.com/p/... ou @usuario")
        
        frame_pasta = tk.Frame(main, bg='#1a1a2e')
        frame_pasta.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame_pasta, text="Pasta:", bg='#1a1a2e', fg='white').pack(side=tk.LEFT)
        self.pasta_entry = tk.Entry(frame_pasta, bg='#2a2a4a', fg='white', insertbackground='white')
        self.pasta_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.pasta_entry.insert(0, "downloads")
        
        tk.Button(frame_pasta, text="📂", command=self.escolher_pasta, bg='#2a2a4a', fg='white', relief='flat').pack(side=tk.RIGHT)
        
        self.download_btn = tk.Button(main, text="⬇️ BAIXAR", command=self.iniciar_download, bg='#e1306c', fg='white', font=("Segoe UI", 12, "bold"), relief='flat', cursor='hand2')
        self.download_btn.pack(fill=tk.X, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(main, bg='#0d0d1a', fg='#00ff88', font=("Consolas", 10), height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        self.log("🚀 Aplicação iniciada!")
        self.log("📌 Cole o link do post, reels, ou @usuario e clique em Baixar")
    
    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def escolher_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_entry.delete(0, tk.END)
            self.pasta_entry.insert(0, pasta)
    
    def iniciar_download(self):
        entrada = self.url_entry.get().strip()
        if not entrada or entrada in ["https://www.instagram.com/p/... ou @usuario", "https://www.instagram.com/p/..."]:
            messagebox.showwarning("Aviso", "Cole um link ou usuário válido!")
            return
        
        # Verifica se é um perfil (@usuario)
        usuario = re.search(r'@([A-Za-z0-9_.]+)', entrada)
        if not usuario:
            usuario = re.search(r'instagram\.com/([A-Za-z0-9_.]+)', entrada)
            if usuario:
                usuario = usuario.group(1)
        else:
            usuario = usuario.group(1)
        
        # Verifica se é um shortcode (post individual)
        shortcode = re.search(r'instagram\.com/(p|reel|tv)/([A-Za-z0-9_-]+)', entrada)
        if shortcode:
            shortcode = shortcode.group(2)
        
        pasta = self.pasta_entry.get().strip()
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        
        self.download_btn.config(state=tk.DISABLED, text="⏳ Baixando...")
        
        def thread():
            try:
                # Se for um perfil
                if usuario and not shortcode:
                    self.log(f"👤 Baixando perfil: {usuario}")
                    perfil = instaloader.Profile.from_username(self.loader.context, usuario)
                    count = 0
                    for post in perfil.get_posts():
                        count += 1
                        self.log(f"📥 Baixando post {count}/{perfil.mediacount}...")
                        self.loader.download_post(post, target=pasta)
                    self.log("✅ Perfil baixado!")
                    messagebox.showinfo("Sucesso", f"Perfil {usuario} baixado!")
                
                # Se for post único
                elif shortcode:
                    self.log(f"🎯 Baixando post: {shortcode}")
                    post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
                    self.loader.dirname_pattern = pasta
                    self.loader.download_post(post, target=pasta)
                    self.log("✅ Download concluído!")
                    messagebox.showinfo("Sucesso", "Download concluído!")
                
                else:
                    raise ValueError("Link ou usuário não reconhecido.")
                
            except instaloader.LoginRequiredException:
                self.log("❌ Privado. Faça login manualmente no Edge e tente de novo.")
                messagebox.showerror("Erro", "Conteúdo privado. Faça login no Edge e tente novamente.")
            except Exception as e:
                self.log(f"❌ Erro: {str(e)}")
                messagebox.showerror("Erro", str(e))
            finally:
                self.download_btn.config(state=tk.NORMAL, text="⬇️ BAIXAR")
        
        threading.Thread(target=thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramDownloader(root)
    root.mainloop()