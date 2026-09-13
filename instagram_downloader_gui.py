import os
import re
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, scrolledtext


class InstagramDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("📸 Baixador Instagram (Sem Senha)")
        self.root.geometry("700x550")
        self.root.configure(bg='#1a1a2e')
        self.criar_interface()
        
    def criar_interface(self):
        titulo = tk.Label(self.root, text="📸 Baixador do Instagram", font=("Segoe UI", 20, "bold"), bg='#1a1a2e', fg='#e1306c')
        titulo.pack(pady=20)
        
        main = tk.Frame(self.root, bg='#1a1a2e')
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        tk.Label(main, text="Link do Post:", bg='#1a1a2e', fg='white').pack(anchor='w')
        
        input_frame = tk.Frame(main, bg='#1a1a2e')
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.url_entry = tk.Entry(input_frame, bg='#2a2a4a', fg='white', insertbackground='white', font=("Segoe UI", 11))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_entry.insert(0, "https://www.instagram.com/p/...")
        
        self.clear_btn = tk.Button(input_frame, text="✕", command=self.limpar_url, bg='#ff4444', fg='white', relief='flat', width=3, cursor='hand2')
        self.clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        frame_pasta = tk.Frame(main, bg='#1a1a2e')
        frame_pasta.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame_pasta, text="Pasta:", bg='#1a1a2e', fg='white').pack(side=tk.LEFT)
        self.pasta_entry = tk.Entry(frame_pasta, bg='#2a2a4a', fg='white', insertbackground='white')
        self.pasta_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.pasta_entry.insert(0, "downloads")
        
        tk.Button(frame_pasta, text="📂", command=self.escolher_pasta, bg='#2a2a4a', fg='white', relief='flat', cursor='hand2').pack(side=tk.RIGHT)
        
        self.download_btn = tk.Button(main, text="⬇️ BAIXAR", command=self.iniciar_download, bg='#e1306c', fg='white', font=("Segoe UI", 12, "bold"), relief='flat', cursor='hand2')
        self.download_btn.pack(fill=tk.X, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(main, bg='#0d0d1a', fg='#00ff88', font=("Consolas", 10), height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        self.log("🚀 Aplicação iniciada (sem senha).")
        self.log("📌 Cole o link e dê Enter.")
        
        self.url_entry.bind('<Return>', self.evento_enter)
        
    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def limpar_url(self):
        self.url_entry.delete(0, tk.END)
        self.url_entry.focus()

    def evento_enter(self, event):
        self.iniciar_download()
    
    def escolher_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_entry.delete(0, tk.END)
            self.pasta_entry.insert(0, pasta)
    
    def iniciar_download(self):
        url = self.url_entry.get().strip()
        if not url or url == "https://www.instagram.com/p/...":
            self.log("⚠️ Cole um link válido!")
            return
        
        pasta = self.pasta_entry.get().strip()
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        
        self.download_btn.config(state=tk.DISABLED, text="⏳ Baixando...")
        self.log(f"🎯 Baixando: {url}")
        
        def thread():
            try:
                # O comando que SEMPRE funcionou pra você
                comando = [
                    "yt-dlp",
                    "--no-playlist",
                    "--output", os.path.join(pasta, "%(title)s.%(ext)s"),
                    url
                ]
                
                resultado = subprocess.run(comando, capture_output=True, text=True)
                
                if resultado.returncode == 0:
                    self.log("✅ Download concluído com sucesso!")
                else:
                    self.log(f"❌ Erro: {resultado.stderr}")
                    
            except Exception as e:
                self.log(f"❌ Erro: {str(e)}")
            finally:
                self.download_btn.config(state=tk.NORMAL, text="⬇️ BAIXAR")
        
        threading.Thread(target=thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramDownloader(root)
    root.mainloop()