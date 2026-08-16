import os
import re
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext

import instaloader


class InstagramDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("📸 Baixador do Instagram")
        self.root.geometry("700x600")
        self.root.configure(bg='#1a1a2e')
        
        self.loader = instaloader.Instaloader()
        
        self.criar_interface()
        
    def criar_interface(self):
        titulo = tk.Label(self.root, text="📸 Baixador do Instagram", font=("Segoe UI", 20, "bold"), bg='#1a1a2e', fg='#e1306c')
        titulo.pack(pady=20)
        
        main = tk.Frame(self.root, bg='#1a1a2e')
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        tk.Label(main, text="Link do Post:", bg='#1a1a2e', fg='white').pack(anchor='w')
        self.url_entry = tk.Entry(main, bg='#2a2a4a', fg='white', insertbackground='white', font=("Segoe UI", 11))
        self.url_entry.pack(fill=tk.X, pady=(0, 10))
        self.url_entry.insert(0, "https://www.instagram.com/p/...")
        
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
        
        self.log("🚀 Aplicação iniciada! (Modo sem login automático)")
        self.log("📌 Cole o link do post ou reels e clique em Baixar.")
        self.log("⚠️ ATENÇÃO: Só funciona para perfis PÚBLICOS.")
        
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
        url = self.url_entry.get().strip()
        if not url or url == "https://www.instagram.com/p/...":
            messagebox.showwarning("Aviso", "Cole um link válido!")
            return
        
        shortcode = re.search(r'instagram\.com/(p|reel|tv)/([A-Za-z0-9_-]+)', url)
        if not shortcode:
            messagebox.showerror("Erro", "URL inválida!")
            return
        
        shortcode = shortcode.group(2)
        pasta = self.pasta_entry.get().strip()
        
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        
        self.download_btn.config(state=tk.DISABLED, text="⏳ Baixando...")
        self.log(f"🎯 Baixando post: {shortcode}")
        
        def thread():
            try:
                post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
                self.loader.dirname_pattern = pasta
                self.loader.download_post(post, target=pasta)
                self.log("✅ Download concluído!")
                messagebox.showinfo("Sucesso", "Download concluído!")
            except instaloader.exceptions.LoginRequiredException:
                self.log("❌ ERRO: O perfil é PRIVADO. O programa não está logado.")
                messagebox.showerror("Erro", "Perfil privado. Este programa não está logado.")
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