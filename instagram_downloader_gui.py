import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import instaloader
import threading
import os
import re
from datetime import datetime
from instaloader import ConnectionException, LoginRequiredException

# ============================================
# 👤 SEUS DADOS
# ============================================
USUARIO_INSTAGRAM = "misaelandrejezieski"
SENHA_INSTAGRAM = "SUA_SENHA_AQUI"  # <-- COLOCA SUA SENHA AQUI

class InstagramDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("📸 Baixador do Instagram")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a2e')
        
        self.loader = instaloader.Instaloader()
        self.logado = False
        
        self.criar_interface()
        
        # Tenta login automático
        self.root.after(500, self.login_automatico)
        
    def login_automatico(self):
        """Login automático usando cookies ou sessão salva"""
        
        # 1. Tenta carregar sessão salva
        try:
            self.loader.load_session_from_file(USUARIO_INSTAGRAM)
            self.logado = True
            self.status_login.config(text="✅ Logado!", fg='#25d366')
            self.log("✅ Sessão carregada automaticamente!")
            self.log("📥 Pronto para baixar!")
            return
        except:
            pass
        
        # 2. Tenta usar cookies do navegador (Edge/Chrome)
        try:
            self.log("🍪 Tentando usar cookies do navegador...")
            self.loader.load_session_from_file(USUARIO_INSTAGRAM, filename="session")
            self.logado = True
            self.status_login.config(text="✅ Logado!", fg='#25d366')
            self.log("✅ Sessão carregada do navegador!")
            self.log("📥 Pronto para baixar!")
            return
        except:
            pass
        
        # 3. Se não tem sessão, faz login com senha
        if not SENHA_INSTAGRAM:
            self.log("❌ Senha não configurada!")
            self.log("📌 Coloque sua senha em SENHA_INSTAGRAM")
            return
        
        def thread_login():
            try:
                self.log(f"🔐 Login automático como {USUARIO_INSTAGRAM}...")
                self.loader.login(USUARIO_INSTAGRAM, SENHA_INSTAGRAM)
                self.logado = True
                self.loader.save_session_to_file()
                self.status_login.config(text="✅ Logado!", fg='#25d366')
                self.log("✅ Login automático realizado com sucesso!")
                self.log("💾 Sessão salva!")
                self.log("📥 Pronto para baixar!")
                messagebox.showinfo("Sucesso", f"Login automático realizado!\n@{
USUARIO_INSTAGRAM}")
                
            except Exception as e:
                erro = str(e)
                self.log(f"❌ Erro: {erro}")
                self.status_login.config(text="❌ Falha", fg='#ff6b6b')
                
                if "Checkpoint" in erro:
                    match = re.search(r'/auth_platform/\?apc=[^\s]+', erro)
                    if match:
                        link = f"https://www.instagram.com{match.group(0)}"
                        self.log(f"🔗 Abra no navegador e confirme:")
                        self.log(f"{link}")
                        
                        # Copia o link pra área de transferência
                        self.root.clipboard_clear()
                        self.root.clipboard_append(link)
                        self.log("📋 Link copiado para a área de transferência!")
                        
                        self.root.after(0, lambda: messagebox.showwarning(
                            "Checkpoint necessário",
                            f"O link foi copiado para sua área de transferência!\n\nCole no navegador e confirme.\n\nDepois clique em 'OK' e tente novamente."
                        ))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erro no login",
                        f"{erro}"
                    ))
        
        threading.Thread(target=thread_login, daemon=True).start()
    
    def criar_interface(self):
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
            text=f"👤 @{USUARIO_INSTAGRAM}  |  Login automático ativado",
            font=("Segoe UI", 10),
            bg='#1a1a2e',
            fg='#25d366'
        )
        subtitulo.pack(pady=(0, 20))
        
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        login_frame = tk.LabelFrame(
            main_frame,
            text="🔐 Status do Login",
            font=("Segoe UI", 10, "bold"),
            bg='#16213e',
            fg='#ffffff',
            padx=10,
            pady=10
        )
        login_frame.pack(fill=tk.X, pady=(0, 15))
        
        row1 = tk.Frame(login_frame, bg='#16213e')
        row1.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(row1, text="Usuário:", bg='#16213e', fg='#ffffff', width=10, anchor='w').pack(side=tk.LEFT)
        self.user_entry = tk.Entry(row1, width=25, bg='#2a2a4a', fg='#25d366', insertbackground='white')
        self.user_entry.insert(0, USUARIO_INSTAGRAM)
        self.user_entry.config(state='readonly')
        self.user_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        row2 = tk.Frame(login_frame, bg='#16213e')
        row2.pack(fill=tk.X)
        
        tk.Label(row2, text="Senha:", bg='#16213e', fg='#ffffff', width=10, anchor='w').pack(side=tk.LEFT)
        self.pass_entry = tk.Entry(row2, width=25, show="*", bg='#2a2a4a', fg='white', insertbackground='white')
        if SENHA_INSTAGRAM:
            self.pass_entry.insert(0, SENHA_INSTAGRAM)
        self.pass_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.login_btn = tk.Button(
            row2,
            text="🔑 Logar",
            command=self.fazer_login_manual,
            bg='#25d366',
            fg='white',
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            width=10
        )
        self.login_btn.pack(side=tk.LEFT)
        
        self.status_login = tk.Label(
            row2,
            text="⏳ Conectando...",
            bg='#16213e',
            fg='#ffaa00',
            font=("Segoe UI", 9)
        )
        self.status_login.pack(side=tk.LEFT, padx=(15, 0))
        
        link_frame = tk.LabelFrame(
            main_frame,
            text="📎 Link do post ou perfil",
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
        self.log(f"👤 Usuário: @{USUARIO_INSTAGRAM}")
        self.log("🔄 Tentando login automático...")
    
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
    
    def fazer_login_manual(self):
        usuario = self.user_entry.get().strip()
        senha = self.pass_entry.get().strip()
        
        if not senha:
            messagebox.showwarning("Aviso", "Digite sua senha!")
            return
        
        def login_thread():
            try:
                self.log(f"🔐 Tentando login como {usuario}...")
                self.loader.login(usuario, senha)
                self.logado = True
                self.loader.save_session_to_file()
                self.status_login.config(text="✅ Logado!", fg='#25d366')
                self.log("✅ Login realizado com sucesso!")
                self.log("💾 Sessão salva!")
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            except Exception as e:
                self.log(f"❌ Erro: {str(e)}")
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
    
    def extrair_usuario(self, url):
        match = re.search(r'instagram\.com/([A-Za-z0-9_.]+)', url)
        if match:
            return match.group(1)
        return None
    
    def baixar_perfil(self, usuario, pasta):
        self.log(f"👤 Baixando perfil: {usuario}")
        self.log("⏳ Isso pode levar alguns minutos...")
        
        try:
            perfil = instaloader.Profile.from_username(self.loader.context, usuario)
            self.log(f"📊 Posts: {perfil.mediacount}")
            
            count = 0
            for post in perfil.get_posts():
                count += 1
                self.log(f"📥 Baixando post {count}/{perfil.mediacount}...")
                self.loader.download_post(post, target=pasta)
            
            self.log(f"✅ Perfil completo baixado! Total: {count} posts")
            return True
            
        except LoginRequiredException:
            self.log("❌ Perfil privado! Faça login para acessar.")
            return False
        except Exception as e:
            self.log(f"❌ Erro: {str(e)}")
            return False
    
    def iniciar_download(self):
        url = self.url_entry.get().strip()
        
        if not url or url == "https://www.instagram.com/p/...":
            messagebox.showwarning("Aviso", "Cole um link válido do Instagram!")
            return
        
        pasta = self.var_pasta.get()
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            self.log(f"📁 Pasta criada: {pasta}")
        
        usuario = self.extrair_usuario(url)
        if usuario and not re.search(r'/p/|/reel/|/tv/', url):
            self.download_btn.config(state=tk.DISABLED, text="⏳ Baixando perfil...")
            
            def thread_perfil():
                sucesso = self.baixar_perfil(usuario, pasta)
                self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL, text="⬇️ BAIXAR"))
                if sucesso:
                    self.root.after(0, lambda: messagebox.showinfo("Sucesso!", f"Perfil {usuario} baixado com sucesso!"))
            
            threading.Thread(target=thread_perfil, daemon=True).start()
            return
        
        shortcode = self.extrair_shortcode(url)
        if not shortcode:
            messagebox.showerror("Erro", "URL inválida!\nUse:\n- instagram.com/p/...\n- instagram.com/reel/...")
            return
        
        self.download_btn.config(state=tk.DISABLED, text="⏳ Baixando...")
        self.log(f"🎯 Iniciando download: {shortcode}")
        
        def download_thread():
            try:
                post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
                self.loader.dirname_pattern = pasta
                self.loader.download_post(post, target=pasta)
                
                self.log(f"✅ Download concluído!")
                self.log(f"📁 Arquivos salvos em: {pasta}")
                self.log(f"📊 Tipo: {post.typename}")
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso!",
                    f"Download concluído!\n📁 Pasta: {pasta}\n📊 Tipo: {post.typename}"
                ))
                
            except LoginRequiredException:
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

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramDownloader(root)
    root.mainloop()