# ===================================================================
# main.py - BaixarYou + Instagram Anti-Checkpoint
# ===================================================================
# SUPORTA: YouTube, TikTok, Instagram (com login automático via Edge), 
# Twitter, Facebook, Vimeo, SoundCloud
# ===================================================================

import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
# ===================================================================
# IMPORTAÇÃO DO INSTALOADER (PARA O INSTAGRAM)
# ===================================================================
import instaloader
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================

def get_base_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

BASE_DIR = get_base_dir()
SAVE_DIR = BASE_DIR / "downloads"
SAVE_DIR.mkdir(exist_ok=True)

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

HISTORY_FILE = BASE_DIR / "download_history.json"
COOKIE_FILE = BASE_DIR / "cookies.txt"
CONFIG_FILE = BASE_DIR / "config.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "downloader.log", encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ===================================================================
# CONFIGURAÇÕES DO INSTAGRAM (SENHA FIXA)
# ===================================================================
INSTA_USER = "misaelandrejezieski"
INSTA_PASS = "SUA_SENHA_AQUI"  # <-- COLOQUE SUA SENHA AQUI

# ===================================================================
# CLASSE: Config
# ===================================================================
class Config:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config = self.load()
    
    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'save_dir': str(SAVE_DIR),
            'last_quality': 'best (recomendado)',
            'dark_mode': True,
            'max_history': 100,
            'auto_open_folder': False,
        }
    
    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()

# ===================================================================
# FUNÇÃO: validate_url
# ===================================================================
def validate_url(url: str) -> tuple:
    if not url or not url.strip():
        return False, None, "URL está vazia"
    url = url.strip()
    
    patterns = {
        'YouTube': [
            r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://(?:www\.)?youtu\.be/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
        ],
        'Instagram': [
            r'^https?://(?:www\.)?instagram\.com/p/[\w-]+/?',
            r'^https?://(?:www\.)?instagram\.com/reel/[\w-]+/?',
            r'^https?://(?:www\.)?instagram\.com/tv/[\w-]+/?',
        ],
        'TikTok': [
            r'^https?://(?:www\.)?tiktok\.com/@[\w.]+/video/\d+',
            r'^https?://(?:www\.)?tiktok\.com/[\w-]+',
            r'^https?://(?:www\.)?vm\.tiktok\.com/[\w-]+',
        ],
        'Twitter/X': [
            r'^https?://(?:www\.)?twitter\.com/\w+/status/\d+',
            r'^https?://(?:www\.)?x\.com/\w+/status/\d+',
        ],
    }
    
    for platform, regex_list in patterns.items():
        for regex in regex_list:
            if re.match(regex, url, re.IGNORECASE):
                return True, platform, None
    
    if re.match(r'^https?://[^\s]+$', url):
        return True, "Site Suportado", None
    
    return False, None, "URL inválida ou não suportada"

# ===================================================================
# CLASSE: DownloadHistory
# ===================================================================
class DownloadHistory:
    def __init__(self):
        self.history_file = HISTORY_FILE
        self.history = self.load_history()
    
    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def add_download(self, url: str, title: str, platform: str, status: str, error: str = ""):
        self.history.append({
            'url': url,
            'title': title,
            'platform': platform,
            'status': status,
            'error': error,
            'save_dir': str(SAVE_DIR),
            'timestamp': datetime.now().isoformat()
        })
        self.save_history()
    
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def clear(self):
        self.history = []
        self.save_history()

# ===================================================================
# CLASSE: DownloadWorker
# ===================================================================
class DownloadWorker:
    def __init__(self, status_callback, progress_callback, history: DownloadHistory):
        self.status_callback = status_callback
        self.progress_callback = progress_callback
        self.history = history
        self._app = None
        self.instagram_loader = None
        self.instagram_logado = False

    def _logar_instagram(self):
        """Tenta fazer o login do Instagram APENAS uma vez"""
        if self.instagram_logado:
            return True
        
        try:
            self.status_callback("🔐 Tentando logar no Instagram...")
            self.instagram_loader = instaloader.Instaloader()
            
            # Tenta carregar sessão salva
            try:
                self.instagram_loader.load_session_from_file(INSTA_USER)
                self.instagram_logado = True
                self.status_callback("✅ Instagram: Sessão carregada!")
                return True
            except:
                pass
            
            # Se não tiver sessão, faz login com a senha fixa
            if INSTA_PASS and INSTA_PASS != "SUA_SENHA_AQUI":
                self.instagram_loader.login(INSTA_USER, INSTA_PASS)
                self.instagram_loader.save_session_to_file(INSTA_USER)
                self.instagram_logado = True
                self.status_callback("✅ Instagram: Login feito com sucesso!")
                return True
            else:
                self.status_callback("⚠️ Coloque a senha do Instagram no código (INSTA_PASS)")
                return False

        except instaloader.exceptions.TwoFactorAuthRequiredException:
            self.status_callback("❌ Instagram pediu 2FA. Verifique o navegador.")
        except instaloader.exceptions.LoginException as e:
            self.status_callback(f"❌ Instagram: {e}")
        except Exception as e:
            self.status_callback(f"❌ Instagram: {e}")
        
        return False

    def _download_instagram(self, url: str):
        """Baixa usando INSTALOADER, não yt-dlp"""
        if not self._logar_instagram():
            self._show_error("Falha no login do Instagram. Verifique o código.")
            return False

        try:
            # Extrai o shortcode
            match = re.search(r'instagram\.com/(p|reel|tv)/([A-Za-z0-9_-]+)', url)
            if not match:
                self._show_error("Não foi possível extrair o código do post.")
                return False
            
            shortcode = match.group(2)
            self.status_callback(f"📸 Baixando post: {shortcode}...")
            
            post = instaloader.Post.from_shortcode(self.instagram_loader.context, shortcode)
            self.instagram_loader.dirname_pattern = str(SAVE_DIR)
            self.instagram_loader.download_post(post, target=str(SAVE_DIR))
            
            self.status_callback("✅ Instagram: Download concluído!")
            self.history.add_download(url, "Instagram Media", "Instagram", "SUCCESS")
            self._show_success("Download do Instagram concluído!")
            return True

        except Exception as e:
            erro = str(e)
            self.status_callback(f"❌ Instagram: {erro[:100]}")
            self.history.add_download(url, "Instagram Media", "Instagram", "FAILED", erro)
            self._show_error(f"Erro no Instagram:\n{erro}")
            return False

    def start_download(self, url: str, quality: str = "best", is_playlist: bool = False):
        thread = threading.Thread(
            target=self._download_video,
            args=(url, quality, is_playlist),
            daemon=True
        )
        thread.start()
        return thread
    
    def _progress_hook(self, d):
        try:
            if d['status'] == 'downloading':
                percent = 0
                if 'total_bytes' in d and d['total_bytes'] > 0:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif 'total_bytes_estimate' in d:
                    percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                
                speed = d.get('speed', 0)
                if speed and speed > 0:
                    if speed > 1024 * 1024:
                        speed_str = f"{speed / 1024 / 1024:.1f} MB/s"
                    elif speed > 1024:
                        speed_str = f"{speed / 1024:.1f} KB/s"
                    else:
                        speed_str = f"{speed:.0f} B/s"
                else:
                    speed_str = "calculando..."
                
                if self._app:
                    self._app.after(0, lambda p=percent, s=speed_str: self._app.update_progress_bar(p, s))
                    
            elif d['status'] == 'finished':
                if self._app:
                    self._app.after(0, lambda: self._app.update_progress_bar(100, "Finalizando..."))
        except Exception:
            pass
    
    def _get_ydl_options(self, quality: str, is_playlist: bool) -> dict:
        format_map = {
            "best": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "audio": "bestaudio/best",
        }
        
        format_spec = format_map.get(quality, "bestvideo+bestaudio/best")
        
        ydl_opts = {
            'outtmpl': str(SAVE_DIR / '%(title)s_%(id)s.%(ext)s'),
            'format': format_spec,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'extract_flat': is_playlist,
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
            'progress_hooks': [self._progress_hook],
            'verbose': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }
        return ydl_opts
    
    def _download_video(self, url: str, quality: str, is_playlist: bool):
        platform = self._detect_platform(url)
        
        # ==========================================================
        # SE FOR INSTAGRAM, USA O INSTALOADER (O QUE FUNCIONA)
        # ==========================================================
        if platform == "Instagram":
            self._download_instagram(url)
            if self._app:
                self._app.after(0, self._app.reset_progress_bar)
            return

        # ==========================================================
        # OUTRAS PLATAFORMAS (USAM O YT-DLP)
        # ==========================================================
        title = "Unknown"
        try:
            ydl_opts = self._get_ydl_options(quality, is_playlist)
            self.status_callback(f"🌐 Conectando a {platform}...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    entries = info.get('entries', [])
                    total = len(entries)
                    title = info.get('title', 'Playlist')
                    self.status_callback(f"📋 Playlist: {title} ({total} vídeos)")
                    ydl.download([url])
                    self.status_callback(f"✅ Playlist baixada: {title}")
                    self.history.add_download(url, title, platform, "SUCCESS")
                    self._show_success(f"Playlist baixada!\n{total} vídeos salvos em:\n{SAVE_DIR}")
                else:
                    title = info.get('title', 'Unknown')
                    self.status_callback(f"🎬 Baixando: {title[:50]}...")
                    ydl.download([url])
                    self.status_callback(f"✅ Download concluído: {title[:50]}")
                    self.history.add_download(url, title, platform, "SUCCESS")
                    self._show_success(f"Vídeo baixado com sucesso!\n\n📹 {title}\n📁 {SAVE_DIR}")
                    
        except DownloadError as e:
            error_msg = str(e)
            self.status_callback(f"❌ {error_msg[:150]}")
            self._show_error(error_msg[:300])
            logger.error(f"DownloadError: {url} - {e}")
            self.history.add_download(url, title, platform, "FAILED", str(e))
        except ExtractorError as e:
            error_msg = f"URL não suportada: {str(e)[:150]}"
            self.status_callback(f"❌ {error_msg}")
            logger.error(f"ExtractorError: {url} - {e}")
            self.history.add_download(url, title, platform, "FAILED", str(e))
            self._show_error(error_msg)
        except Exception as e:
            error_msg = f"Erro: {str(e)[:150]}"
            self.status_callback(f"❌ {error_msg}")
            logger.error(f"Unexpected error: {url} - {e}")
            self.history.add_download(url, title, platform, "FAILED", str(e))
            self._show_error(error_msg)
        finally:
            if self._app:
                self._app.after(0, self._app.reset_progress_bar)
    
    def _detect_platform(self, url: str) -> str:
        url_lower = url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return "YouTube"
        if 'tiktok.com' in url_lower:
            return "TikTok"
        if 'instagram.com' in url_lower:
            return "Instagram"
        if 'twitter.com' in url_lower or 'x.com' in url_lower:
            return "Twitter/X"
        if 'facebook.com' in url_lower or 'fb.com' in url_lower:
            return "Facebook"
        if 'vimeo.com' in url_lower:
            return "Vimeo"
        if 'soundcloud.com' in url_lower:
            return "SoundCloud"
        return "Site Suportado"
    
    def _show_success(self, message: str):
        if self._app:
            self._app.after(0, lambda: messagebox.showinfo("✅ Sucesso", message))
    
    def _show_error(self, message: str):
        if self._app:
            self._app.after(0, lambda: messagebox.showerror("❌ Erro", message))

# ===================================================================
# CLASSE: BaixarYouApp - INTERFACE GRÁFICA
# ===================================================================
class BaixarYouApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("📥 BaixarYou - Universal + Instagram Pro")
        self.geometry("720x680")
        self.resizable(True, True)
        
        self.config = Config()
        self.history = DownloadHistory()
        
        global SAVE_DIR
        saved_dir = self.config.get('save_dir')
        if saved_dir and Path(saved_dir).exists():
            SAVE_DIR = Path(saved_dir)
        
        self.worker = DownloadWorker(
            status_callback=self._update_status,
            progress_callback=self._update_progress,
            history=self.history
        )
        self.worker._app = self
        
        self.current_download = None
        self.downloading = False
        
        self.create_widgets()
    
    def create_widgets(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=15)
        
        ctk.CTkLabel(header_frame, text="📥 BaixarYou", font=("Arial", 28, "bold")).pack()
        ctk.CTkLabel(header_frame, text="Instagram, YouTube, TikTok, Twitter e mais", font=("Arial", 11), text_color="gray").pack()
        
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(main_frame, text="🔗 URL do vídeo:", font=("Arial", 13, "bold")).pack(anchor="w", pady=(10,0))
        
        self.url_entry = ctk.CTkEntry(main_frame, width=700, height=45, placeholder_text="Cole a URL aqui...")
        self.url_entry.pack(pady=5, fill="x")
        
        # Opções
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(options_frame, text="Qualidade:", font=("Arial", 12)).pack(side="left", padx=10)
        
        self.quality_var = ctk.StringVar(value=self.config.get('last_quality', 'best (recomendado)'))
        quality_menu = ctk.CTkOptionMenu(
            options_frame, 
            values=["best (recomendado)", "1080p", "720p", "480p", "Apenas Áudio (MP3)"],
            variable=self.quality_var,
            width=200
        )
        quality_menu.pack(side="left", padx=10)
        
        self.playlist_var = ctk.BooleanVar(value=False)
        playlist_check = ctk.CTkCheckBox(options_frame, text="📋 Playlist", variable=self.playlist_var)
        playlist_check.pack(side="left", padx=20)
        
        self.download_btn = ctk.CTkButton(
            main_frame, 
            text="⬇️ BAIXAR VÍDEO",
            command=self.start_download,
            width=300, height=50,
            font=("Arial", 16, "bold"),
            fg_color="#2e7d32"
        )
        self.download_btn.pack(pady=15)
        
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(progress_frame, text="📊 Progresso:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=500, height=20)
        self.progress_bar.pack(pady=5, padx=10, fill="x")
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="0% - Aguardando...", font=("Arial", 11))
        self.progress_label.pack(anchor="w", padx=10, pady=5)
        
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(status_frame, text="Status:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        
        self.status_label = ctk.CTkLabel(status_frame, text="✅ Pronto para baixar", font=("Arial", 12), text_color="green")
        self.status_label.pack(anchor="w", padx=10, pady=5)
        
        # Botões auxiliares
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=5)
        
        self.pasta_btn = ctk.CTkButton(buttons_frame, text="📂 Abrir Pasta", command=self.abrir_pasta, width=150)
        self.pasta_btn.pack(side="left", padx=5)
        
        self.mudar_pasta_btn = ctk.CTkButton(buttons_frame, text="🗂️ Mudar Pasta", command=self.mudar_pasta, width=150)
        self.mudar_pasta_btn.pack(side="left", padx=5)
        
        self.historico_btn = ctk.CTkButton(buttons_frame, text="📜 Histórico", command=self.ver_historico, width=150)
        self.historico_btn.pack(side="left", padx=5)
        
        self.label_pasta = ctk.CTkLabel(main_frame, text=f"📁 Pasta: {SAVE_DIR}", font=("Arial", 11), text_color="gray")
        self.label_pasta.pack(pady=10)
    
    def update_progress_bar(self, percent: float, speed: str):
        try:
            percent_value = min(100, max(0, float(percent))) / 100
            self.progress_bar.set(percent_value)
            percent_int = int(percent_value * 100)
            self.progress_label.configure(text=f"{percent_int}% - {speed}")
            self.update_idletasks()
        except:
            pass
    
    def reset_progress_bar(self):
        self.progress_bar.set(0)
        self.progress_label.configure(text="0% - Concluído!")
        self.after(2000, lambda: self.progress_label.configure(text="0% - Aguardando..."))
    
    def _update_status(self, message: str):
        def update():
            self.status_label.configure(text=message)
            if "✅" in message:
                self.status_label.configure(text_color="green")
            elif "❌" in message:
                self.status_label.configure(text_color="red")
            else:
                self.status_label.configure(text_color="blue")
        self.after(0, update)
    
    def _update_progress(self, message: str):
        def update():
            self.progress_label.configure(text=message)
        self.after(0, update)
    
    def start_download(self):
        url = self.url_entry.get().strip()
        
        is_valid, platform, error = validate_url(url)
        if not is_valid:
            messagebox.showwarning("URL Inválida", f"❌ {error}")
            return
        
        if self.downloading:
            messagebox.showinfo("Aviso", "Um download já está em andamento.")
            return
        
        self.progress_bar.set(0)
        self.progress_label.configure(text="0% - Iniciando...")
        
        quality_label = self.quality_var.get()
        quality_map = {
            "best (recomendado)": "best",
            "1080p": "1080p",
            "720p": "720p",
            "480p": "480p",
            "Apenas Áudio (MP3)": "audio"
        }
        quality = quality_map.get(quality_label, "best")
        is_playlist = self.playlist_var.get()
        
        self.config.set('last_quality', quality_label)
        
        self.downloading = True
        self.download_btn.configure(state="disabled", text="⏳ BAIXANDO...")
        
        self.current_download = self.worker.start_download(url, quality, is_playlist)
        self._monitor_download()
    
    def _monitor_download(self):
        if self.current_download and self.current_download.is_alive():
            self.after(500, self._monitor_download)
        else:
            self.downloading = False
            self.download_btn.configure(state="normal", text="⬇️ BAIXAR VÍDEO")
    
    def mudar_pasta(self):
        global SAVE_DIR
        pasta = filedialog.askdirectory(title="Escolha a pasta", initialdir=str(SAVE_DIR))
        if pasta:
            SAVE_DIR = Path(pasta)
            self.label_pasta.configure(text=f"📁 Pasta: {SAVE_DIR}")
            self.config.set('save_dir', str(SAVE_DIR))
    
    def abrir_pasta(self):
        try:
            if os.name == "nt":
                os.startfile(str(SAVE_DIR))
            else:
                subprocess.run(["xdg-open", str(SAVE_DIR)])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta:\n{e}")
    
    def ver_historico(self):
        if not self.history.history:
            messagebox.showinfo("Histórico", "Nenhum download realizado ainda.")
            return
        
        history_window = ctk.CTkToplevel(self)
        history_window.title("📜 Histórico de Downloads")
        history_window.geometry("700x550")
        
        main_frame = ctk.CTkFrame(history_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_box = ctk.CTkTextbox(main_frame, font=("Consolas", 10))
        text_box.pack(fill="both", expand=True, pady=(0, 10))
        
        for item in self.history.history[-20:]:
            status_icon = "✅" if item['status'] == "SUCCESS" else "❌"
            text_box.insert("end", f"{status_icon} [{item['platform']}] {item['title'][:60]}\n")
            text_box.insert("end", f"   📅 {item['timestamp'][:19]}\n")
            text_box.insert("end", "-" * 60 + "\n")
        
        text_box.configure(state="disabled")
        
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x")
        ctk.CTkButton(btn_frame, text="Fechar", command=history_window.destroy).pack(side="right", padx=5)

if __name__ == "__main__":
    app = BaixarYouApp()
    app.mainloop()