import os
import re
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk

import instaloader


class InstagramDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("📸 Baixador do Instagram")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a2e')
        
        # Inicializa o instaloader
        self.loader = instaloader.Instaloader()
        self.logado = False
        
        self.criar_interface()
        
    def criar_interface(self):
        # Título
        titulo = tk.Label(
            self.root,
            text="📸 Baixador do Instagram",
            font=("Segoe UI", 20, "bold"),
            bg='#1a1a2e',
            fg='#e1306c'
        )
        titulo.pack(pady=(20, 5))
        
        subtitulo = tk.Label(
            self.root,
            text="Baixe fotos, vídeos, reels e stories",
            font=("Segoe UI", 10),
            bg='#1a1a2e',
            fg='#a0a0b0'
        )
        subtitulo.pack(pady=(0, 20))
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # ========== ÁREA DE LOGIN ==========
        login_frame = tk.LabelFrame(
            main_frame,
            text="🔐 Login (opcional - para conteúdo privado)",
            font=("Segoe UI", 10, "bold"),
            bg='#16213e',
            fg='#ffffff',
            padx=10,
            pady=10
        )
        login_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Usuário
        row1 = tk.Frame(login_frame, bg='#16213e')
        row1.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(row1, text="Usuário:", bg='#16213e', fg='#ffffff', width=10, anchor='w').pack(side=tk.LEFT)
        self.user_entry = tk.Entry(row1, width=25, bg='#2a2a4a', fg='white', insertbackground='white')
        self.user_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Senha
        row2 = tk.Frame(login_frame, bg='#16213e')
        row2.pack(fill=tk.X)
        
        tk.Label(row2, text="Senha:", bg='#16213e', fg='#ffffff', width=10, anchor='w').pack(side=tk.LEFT)
        self.pass_entry = tk.Entry(row2, width=25, show="*", bg='#2a2a4a', fg='white', insertbackground='white')
        self.pass_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.login_btn = tk.Button(
            row2,
            text="🔑 Logar",
            command=self.fazer_login,
            bg='#25d366',
            fg='white',
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            width=10
        )
        self.login_btn.pack(side=tk.LEFT)
        
        self.status_login = tk.Label(
            row2,
            text="⭕ Deslogado",
            bg='#16213e',
            fg='#ff6b6b',
            font=("Segoe UI", 9)
        )
        self.status_login.pack(side=tk.LEFT, padx=(15, 0))
        
        # ========== ÁREA DO LINK ==========
        link_frame = tk.LabelFrame(
            main_frame,
            text="📎 Link do post",
            font=("Segoe UI", 10, "bold"),
            bg='#16213e',
            fg='#ffffff',
            padx=10,
            pady=10
        )
        link_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.url_entry = tk.Entry(
            link_frame,
            font=("Segoe UI", 11),
            bg='#2a2a4a',
            fg='white',
            insertbackground='white'
        )
        self.url_entry.pack(fill=tk.X, pady=(0, 10))
        self.url_entry.insert(0, "https://www.instagram.com/p/...")
        self.url_entry.bind("<FocusIn>", lambda e: self.url_entry.delete(0, tk.END) if self.url_entry.get() == "https://www.instagram.com/p/..." else None)
        
        # Botão baixar
        self.download_btn = tk.Button(
            link_frame,
            text="⬇️ BAIXAR",
            command=self.iniciar_download,
            bg='#e1306c',
            fg='white',
            font=("Segoe UI", 12, "bold"),
            height=1,
            cursor="hand2"
        )
        self.download_btn.pack(fill=tk.X)
        
        # ========== OPÇÕES ==========
        options_frame = tk.Frame(main_frame, bg='#1a1a2e')
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.var_pasta = tk.StringVar(value="downloads")
        
        tk.Label(
            options_frame,
            text="📁 Pasta:",
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.pasta_entry = tk.Entry(
            options_frame,
            textvariable=self.var_pasta,
            width=30,
            bg='#2a2a4a',
            fg='white',
            insertbackground='white'
        )
        self.pasta_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            options_frame,
            text="📂",
            command=self.escolher_pasta,
            bg='#2a2a4a',
            fg='white',
            cursor="hand2"
        ).pack(side=tk.LEFT)
        
        # ========== LOG DE SAÍDA ==========
        log_frame = tk.LabelFrame(
            main_frame,
            text="📋 Log",
            font=("Segoe UI", 10, "bold"),
            bg='#16213e',
            fg='#ffffff',
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg='#0d0d1a',
            fg='#00ff88',
            font=("Consolas", 10),
            height=10,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        self.log("🚀 Aplicação iniciada!")
        self.log("📌 Cole o link do Instagram e clique em Baixar")
        
    def log(self, mensagem):
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {mensagem}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Selecionar pasta para downloads")
        if pasta:
            self.var_pasta.set(pasta)
            self.log(f"📁 Pasta alterada: {pasta}")
    
    def fazer_login(self):
        usuario = self.user_entry.get().strip()
        senha = self.pass_entry.get().strip()
        
        if not usuario or not senha:
            messagebox.showwarning("Aviso", "Preencha usuário e senha!")
            return
        
        def login_thread():
            try:
                self.log(f"🔐 Tentando login como {usuario}...")
                self.loader.login(usuario, senha)
                self.logado = True
                self.status_login.config(text="✅ Logado!", fg='#25d366')
                self.log("✅ Login realizado com sucesso!")
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            except Exception as e:
                self.log(f"❌ Erro no login: {str(e)}")
                self.status_login.config(text="❌ Falha", fg='#ff6b6b')
                messagebox.showerror("Erro", f"Falha no login:\n{str(e)}")
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def extrair_shortcode(self, url):
        padroes = [
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
            r'instagram\.com/reel/([A-Za-z0-9_-]+)',
            r'instagram\.com/tv/([A-Za-z0-9_-]+)'
        ]
        
        for padrao in padroes:
            match = re.search(padrao, url)
            if match:
                return match.group(1)
        return None
    
    def iniciar_download(self):
        url = self.url_entry.get().strip()
        
        if not url or url == "https://www.instagram.com/p/...":
            messagebox.showwarning("Aviso", "Cole um link válido do Instagram!")
            return
        
        shortcode = self.extrair_shortcode(url)
        if not shortcode:
            messagebox.showerror("Erro", "URL inválida!\nUse links como:\n- instagram.com/p/...\n- instagram.com/reel/...")
            return
        
        self.download_btn.config(state=tk.DISABLED, text="⏳ Baixando...")
        self.log(f"🎯 Iniciando download: {shortcode}")
        
        def download_thread():
            try:
                pasta = self.var_pasta.get()
                if not os.path.exists(pasta):
                    os.makedirs(pasta)
                    self.log(f"📁 Pasta criada: {pasta}")
                
                post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
                
                # Salva na pasta escolhida
                self.loader.dirname_pattern = pasta
                self.loader.download_post(post, target=pasta)
                
                self.log(f"✅ Download concluído!")
                self.log(f"📁 Arquivos salvos em: {pasta}")
                self.log(f"📊 Tipo: {post.typename}")
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso!",
                    f"Download concluído!\n📁 Pasta: {pasta}\n📊 Tipo: {post.typename}"
                ))
                
            except instaloader.exceptions.LoginRequiredException:
                self.log("❌ Conteúdo privado! Faça login para acessar.")
                self.root.after(0, lambda: messagebox.showwarning(
                    "Login necessário",
                    "Este post é privado.\nFaça login para baixar."
                ))
                
            except Exception as e:
                self.log(f"❌ Erro: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Falha no download:\n{str(e)}"))
            
            finally:
                self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL, text="⬇️ BAIXAR"))
        
        threading.Thread(target=download_thread, daemon=True).start()

# ========== MAIN ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramDownloader(root)
    root.mainloop()