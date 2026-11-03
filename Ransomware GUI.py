"""
RANSOMWARE SIMULATOR - GRAPHICAL USER INTERFACE (GUI VERSION)
============================================================
Complete standalone threat simulation console and recovery portal.
Automatically hosts the victim extortion web server on http://localhost:8080.
"""

# ==============================================================================
# 1. SYSTEM IMPORTS & PATH RESOLUTION
# Imports standard networking, concurrency, GUI libraries (Tkinter), and core engine.
# ==============================================================================
import os
import sys
import json
import time
import socket
import threading
import subprocess
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Ensure project root directory is on PYTHONPATH for clean module resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import backend engine and data model classes from Ransomware.py
from Ransomware import RansomwareEngine, SandboxFile


# ==============================================================================
# 2. UI VISUAL DESIGN SYSTEM & COLOR PALETTE
# Dark cybersecurity theme constants (backgrounds, borders, status accents).
# ==============================================================================
BG_ROOT = "#0a0c10"
BG_PANEL = "#11151c"
BG_CARD = "#1b202c"
BG_INPUT = "#0d1117"
BORDER_COLOR = "#2d3343"

TEXT_PRIMARY = "#f0f3f6"
TEXT_SECONDARY = "#8b949e"
TEXT_MUTED = "#57606a"

COLOR_DANGER = "#f85149"
COLOR_DANGER_DARK = "#b62324"
COLOR_DANGER_BG = "#3c1618"

COLOR_WARN = "#d29922"
COLOR_SUCCESS = "#238636"
COLOR_SUCCESS_BRIGHT = "#3fb950"

COLOR_INFO = "#58a6ff"
COLOR_PURPLE = "#bc8cff"
COLOR_CYAN = "#39c5cf"

FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"


# ==============================================================================
# 3. EMBEDDED VICTIM EXTORTION WEB PORTAL (HTML / CSS / JAVASCRIPT)
# Web interface served on http://localhost:8080 with live ticking 72h countdown,
# real-time infection status, simulated Bitcoin wallet, and decryption guide.
# ==============================================================================
HTML_PORTAL_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CRITICAL SECURITY ALERT: System Compromised</title>
  <style>
    :root {
      --bg-root: #0a0c10;
      --bg-panel: #11151c;
      --bg-card: #161b22;
      --bg-input: #0d1117;
      --border-color: #30363d;
      --text-primary: #f0f3f6;
      --text-secondary: #8b949e;
      --color-danger: #f85149;
      --color-danger-bg: #3c1618;
      --color-danger-border: #b62324;
      --color-warn: #d29922;
      --color-success: #238636;
      --color-success-bright: #3fb950;
      --color-info: #58a6ff;
      --color-cyan: #39c5cf;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg-root);
      color: var(--text-primary);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .banner {
      background: var(--color-danger-bg);
      border-bottom: 2px solid var(--color-danger-border);
      padding: 16px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: all 0.4s ease;
    }
    .banner.healthy { background: #13231b; border-bottom-color: var(--color-success); }
    .banner-content h1 { font-size: 1.25rem; font-weight: 700; color: var(--color-danger); display: flex; align-items: center; gap: 10px; }
    .banner.healthy .banner-content h1 { color: var(--color-success-bright); }
    .banner-content p { font-size: 0.85rem; color: #fca5a5; margin-top: 4px; }
    .banner.healthy .banner-content p { color: #86efac; }
    .badge-sim {
      font-size: 0.75rem;
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      padding: 4px 10px;
      border-radius: 999px;
      color: var(--text-secondary);
      font-family: monospace;
    }
    .container { max-width: 1100px; margin: 0 auto; padding: 24px 20px; width: 100%; flex: 1; }
    .grid { display: grid; grid-template-columns: 1fr 340px; gap: 20px; }
    @media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }
    .card {
      background: var(--bg-panel);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
    }
    .card-title {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .timer-container {
      background: var(--bg-input);
      border: 2px solid var(--color-danger-border);
      border-radius: 8px;
      padding: 24px;
      text-align: center;
      margin-bottom: 20px;
    }
    .timer-container.healthy { border-color: var(--color-success); }
    .timer-label { font-size: 0.85rem; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 1px; }
    .timer-digits {
      font-size: 3rem;
      font-weight: 800;
      color: var(--color-danger);
      font-family: monospace;
      letter-spacing: 4px;
      margin: 10px 0;
    }
    .timer-container.healthy .timer-digits { color: var(--color-success-bright); }
    .stat-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: var(--text-secondary); }
    .stat-val { font-weight: 600; font-family: monospace; }
    .stat-val.danger { color: var(--color-danger); }
    .stat-val.success { color: var(--color-success-bright); }
    .wallet-box {
      background: var(--bg-input);
      border: 1px dashed var(--border-color);
      border-radius: 6px;
      padding: 12px;
      font-family: monospace;
      font-size: 0.82rem;
      word-break: break-all;
      margin-top: 10px;
      color: var(--color-cyan);
    }
    .btn-copy {
      background: #21262d;
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 0.8rem;
      cursor: pointer;
      margin-top: 8px;
      width: 100%;
    }
    .btn-copy:hover { background: #30363d; }
    .note-text {
      background: var(--bg-input);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 14px;
      font-family: monospace;
      font-size: 0.8rem;
      line-height: 1.5;
      color: #94a3b8;
      white-space: pre-wrap;
      max-height: 320px;
      overflow-y: auto;
    }
  </style>
</head>
<body>
  <div id="banner" class="banner">
    <div class="banner-content">
      <h1 id="banner-title">⚠️ SYSTEM SECURITY ALERT: CRITICAL ENCRYPTION DETECTED</h1>
      <p id="banner-sub">Your critical documents, databases, and assets have been encrypted using high-grade cryptography.</p>
    </div>
    <span class="badge-sim">ACADEMIC SIMULATION PORTAL</span>
  </div>

  <div class="container">
    <div class="grid">
      <div>
        <div class="card">
          <div class="card-title">🚨 Incident Overview & What Happened</div>
          <p style="font-size:0.9rem; line-height:1.6; color:#cbd5e1; margin-bottom:12px;">
            A simulated high-grade ransomware lock has compromised files in the isolated <code>./sandbox_data/</code> test directory.
            All files are protected with Fernet authenticated encryption (AES-128 in CBC mode + HMAC-SHA256).
          </p>
          <p style="font-size:0.9rem; line-height:1.6; color:#cbd5e1;">
            To reverse this attack, enter the recovered Fernet key via the Attacker/Recovery GUI or submit it directly in your terminal console.
          </p>
        </div>

        <div class="card">
          <div class="card-title">📄 Dropped Extortion Note (README)</div>
          <div id="note-display" class="note-text">Loading extortion note artifact...</div>
        </div>
      </div>

      <div>
        <div id="timer-box" class="timer-container">
          <div class="timer-label">Time Remaining Until Key Destruction</div>
          <div id="timer-digits" class="timer-digits">72:00:00</div>
          <div style="font-size:0.75rem; color:var(--text-secondary);">Simulated Extortion Deadline</div>
        </div>

        <div class="card">
          <div class="card-title">📊 Live Telemetry</div>
          <div class="stat-row">
            <span class="stat-label">System State:</span>
            <span id="stat-state" class="stat-val danger">LOCKED</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Locked Assets:</span>
            <span id="stat-locked" class="stat-val danger">0</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Total Sandbox Assets:</span>
            <span id="stat-total" class="stat-val">8</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Encryption Algorithm:</span>
            <span class="stat-val" style="color:var(--color-info);">Fernet AES-128</span>
          </div>
        </div>

        <div class="card">
          <div class="card-title">💰 Decoy Extortion Demand</div>
          <div style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:6px;">Demanded Amount:</div>
          <div style="font-size:1.3rem; font-weight:700; color:#fbbf24;">0.50 BTC <span style="font-size:0.8rem; font-weight:normal; color:var(--text-secondary);">(~$32,000 USD)</span></div>
          <div style="font-size:0.85rem; color:var(--text-secondary); margin-top:10px;">Decoy Destination Address:</div>
          <div id="wallet-text" class="wallet-box">1EducationalSimulationSafeKey99</div>
          <button class="btn-copy" onclick="copyWallet()">Copy Decoy Address</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    let remainingSeconds = 72 * 3600;
    let timerRunning = false;

    function formatTime(secs) {
      const h = Math.floor(secs / 3600).toString().padStart(2, '0');
      const m = Math.floor((secs % 3600) / 60).toString().padStart(2, '0');
      const s = Math.floor(secs % 60).toString().padStart(2, '0');
      return `${h}:${m}:${s}`;
    }

    async function syncStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();

        const banner = document.getElementById('banner');
        const bannerTitle = document.getElementById('banner-title');
        const bannerSub = document.getElementById('banner-sub');
        const timerBox = document.getElementById('timer-box');
        const timerDigits = document.getElementById('timer-digits');
        const statState = document.getElementById('stat-state');
        const statLocked = document.getElementById('stat-locked');
        const statTotal = document.getElementById('stat-total');
        const noteDisplay = document.getElementById('note-display');

        statLocked.textContent = data.locked_count;
        statTotal.textContent = data.total_count;
        noteDisplay.textContent = data.ransom_note;

        if (data.is_encrypted) {
          banner.className = "banner";
          bannerTitle.textContent = "⚠️ SYSTEM SECURITY ALERT: CRITICAL ENCRYPTION DETECTED";
          bannerSub.textContent = "Your critical documents, databases, and assets have been encrypted using high-grade cryptography.";
          timerBox.className = "timer-container";
          statState.textContent = "COMPROMISED (LOCKED)";
          statState.className = "stat-val danger";
          statLocked.className = "stat-val danger";

          remainingSeconds = data.remaining_seconds;
          timerDigits.textContent = formatTime(remainingSeconds);
        } else {
          banner.className = "banner healthy";
          bannerTitle.textContent = "🛡️ SYSTEM STATUS: FULLY RECOVERED & HEALTHY";
          bannerSub.textContent = "All files have been restored and verified with zero data corruption.";
          timerBox.className = "timer-container healthy";
          statState.textContent = "NORMAL (RECOVERED)";
          statState.className = "stat-val success";
          statLocked.className = "stat-val success";
          timerDigits.textContent = "00:00:00";
          timerRunning = false;
          remainingSeconds = 0;
        }
      } catch (e) {}
    }

    function copyWallet() {
      const text = document.getElementById('wallet-text').textContent;
      navigator.clipboard.writeText(text).then(() => {
        alert('Decoy Bitcoin address copied to clipboard!');
      });
    }

    syncStatus();
    setInterval(syncStatus, 1500);
  </script>
</body>
</html>
"""


# ==============================================================================
# 4. EMBEDDED HTTP SERVER HANDLER (EmbeddedVictimHandler)
# Implements a lightweight HTTP server handling web portal requests and JSON API.
# Bound to localhost:8080 to support real-time web extortion display.
# ==============================================================================
class EmbeddedVictimHandler(BaseHTTPRequestHandler):
    """Serves the simulated victim portal on http://localhost:8080."""
    engine = RansomwareEngine()

    def log_message(self, format, *args):
        # Suppress noisy standard server logging in terminal
        pass

    # --------------------------------------------------------------------------
    # 4.1 HTTP GET ROUTER
    # Routes "/" to the portal HTML, and "/api/status" to dynamic JSON telemetry.
    # --------------------------------------------------------------------------
    def do_GET(self):
        # Serve main extortion web page
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(HTML_PORTAL_PAGE.encode("utf-8"))

        # Serve real-time telemetry API for the countdown timer and locked file counts
        elif self.path == "/api/status":
            self.engine.sync_from_disk()
            locked = sum(1 for f in self.engine.simulated_files if f.status == "LOCKED")
            is_encrypted = (locked > 0)

            timer_file = os.path.join(self.engine.sandbox_dir, ".attack_timer")
            if is_encrypted:
                attack_start = None
                if os.path.exists(timer_file):
                    try:
                        with open(timer_file, "r") as tf:
                            attack_start = float(tf.read().strip())
                    except Exception:
                        attack_start = None

                if attack_start is None:
                    attack_start = time.time()
                    try:
                        with open(timer_file, "w") as tf:
                            tf.write(str(attack_start))
                    except Exception:
                        pass

                elapsed = time.time() - attack_start
                remaining = max(0, int(72 * 3600 - elapsed))
            else:
                if os.path.exists(timer_file):
                    try:
                        os.remove(timer_file)
                    except Exception:
                        pass
                remaining = 0

            data = {
                "is_encrypted": is_encrypted,
                "locked_count": locked,
                "total_count": len(self.engine.simulated_files),
                "remaining_seconds": remaining,
                "ransom_note": self.engine.get_ransom_note_content()
            }

            payload = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(payload)

        else:
            self.send_response(404)
            self.end_headers()


# ==============================================================================
# 5. MAIN TKINTER GRAPHICAL USER INTERFACE (RansomwareGUI)
# Coordinates user controls, live treeview tables, non-blocking background threads,
# real-time disk auto-synchronization, and one-click incident remediation.
# ==============================================================================
class RansomwareGUI(tk.Tk):
    """Main graphical simulation console with attack controls & recovery portal."""

    # --------------------------------------------------------------------------
    # 5.1 WINDOW INITIALIZATION & BACKEND ENGINE LINKAGE
    # Sets window properties, instantiates RansomwareEngine, and configures auto-sync.
    # --------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.title("Ransomware Simulator [Fernet / AES-128] - Threat Console")
        self.geometry("1100x720")
        self.minsize(940, 620)
        self.configure(bg=BG_ROOT)

        # LINK: Instantiate core cryptographic engine
        self.engine = RansomwareEngine()
        self.is_running_task = False

        self._apply_styles()
        self._build_top_header()
        self._build_tabs()
        self._build_status_bar()

        # LINK: Initialize mock sandbox test files
        self.engine.initialize_sandbox()
        self.refresh_file_grid()

        # Real-time disk monitor (1-second polling interval)
        self.last_disk_sig = self._get_disk_signature()
        self.after(1000, self._auto_sync_with_disk)

        # Spawn background HTTP extortion server on localhost:8080
        self._ensure_web_server_running()

    # --------------------------------------------------------------------------
    # 5.2 TKINTER THEME & WIDGET STYLING
    # Configures dark themes for notebook tabs, treeview grids, and progress bars.
    # --------------------------------------------------------------------------
    def _apply_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=BG_PANEL)
        style.configure("TNotebook", background=BG_PANEL, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_PANEL, foreground=TEXT_SECONDARY, padding=[16, 8], font=(FONT_FAMILY, 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", BG_CARD), ("active", BORDER_COLOR)], foreground=[("selected", TEXT_PRIMARY), ("active", TEXT_PRIMARY)])
        style.configure("Treeview", background=BG_INPUT, foreground=TEXT_PRIMARY, fieldbackground=BG_INPUT, rowheight=28, font=(FONT_FAMILY, 9), borderwidth=0)
        style.configure("Treeview.Heading", background=BG_CARD, foreground=TEXT_PRIMARY, font=(FONT_FAMILY, 9, "bold"), relief="flat", padding=[6, 6])
        style.map("Treeview", background=[("selected", "#1f3b58")], foreground=[("selected", "#ffffff")])
        style.configure("Horizontal.TProgressbar", background=COLOR_DANGER, troughcolor=BG_INPUT, bordercolor=BORDER_COLOR)

    # --------------------------------------------------------------------------
    # 5.3 TOP NAVIGATION BAR & BROWSER LAUNCH BUTTON
    # Displays title header and one-click button to open http://localhost:8080.
    # --------------------------------------------------------------------------
    def _build_top_header(self):
        header = tk.Frame(self, bg=BG_PANEL, highlightbackground=BORDER_COLOR, highlightthickness=1)
        header.pack(fill="x")

        title_block = tk.Frame(header, bg=BG_PANEL)
        title_block.pack(side="left", padx=16, pady=10)

        lbl_main = tk.Label(title_block, text="⚡ RANSOMWARE SIMULATOR (ATTACKER & RECOVERY CONSOLE)", font=(FONT_FAMILY, 13, "bold"), fg=COLOR_DANGER, bg=BG_PANEL)
        lbl_main.pack(anchor="w")

        lbl_sub = tk.Label(title_block, text="Educational AES-128 Locking, Shannon Entropy Analysis & SHA-256 Remediation", font=(FONT_FAMILY, 8), fg=TEXT_SECONDARY, bg=BG_PANEL)
        lbl_sub.pack(anchor="w")

        btn_box = tk.Frame(header, bg=BG_PANEL)
        btn_box.pack(side="right", padx=16, pady=10)

        btn_launch = tk.Button(
            btn_box,
            text="🌐 Open Victim Portal (Chrome)",
            command=self._open_victim_portal,
            font=(FONT_FAMILY, 9, "bold"),
            bg="#21262d",
            fg=COLOR_INFO,
            activebackground=BORDER_COLOR,
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        btn_launch.pack(side="right")

    # --------------------------------------------------------------------------
    # 5.4 NOTEBOOK TAB NAVIGATION CONTAINER
    # Adds Tab 1 (Target Files & Encryption) and Tab 2 (Decryption & Recovery Portal).
    # --------------------------------------------------------------------------
    def _build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(4, 0))

        # Tab 1: Attack & File Grid
        self.tab_attack = ttk.Frame(self.notebook)
        self._build_attack_tab(self.tab_attack)
        self.notebook.add(self.tab_attack, text="  1. Target Files & Encryption  ")

        # Tab 2: Recovery Portal
        self.tab_recovery = ttk.Frame(self.notebook)
        self._build_recovery_tab(self.tab_recovery)
        self.notebook.add(self.tab_recovery, text="  2. Decryption & Recovery Portal  ")

    # --------------------------------------------------------------------------
    # 5.5 TAB 1: ATTACK CONTROLS & TARGET FILES GRID
    # Status KPI summary cards, attack action toolbar, live progress bar, and Treeview.
    # --------------------------------------------------------------------------
    def _build_attack_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

        # Status Summary KPI Cards
        cards_frame = tk.Frame(parent, bg=BG_PANEL)
        cards_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 6))
        for i in range(3):
            cards_frame.columnconfigure(i, weight=1)

        def make_card(col, title, var, col_accent):
            c = tk.Frame(cards_frame, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
            c.grid(row=0, column=col, sticky="nsew", padx=4, pady=2)
            tk.Label(c, text=title, font=(FONT_FAMILY, 8, "bold"), fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w", padx=12, pady=(6, 2))
            tk.Label(c, textvariable=var, font=(FONT_FAMILY, 13, "bold"), fg=col_accent, bg=BG_CARD).pack(anchor="w", padx=12, pady=(0, 6))

        self.var_total = tk.StringVar(value="8 Files")
        self.var_locked = tk.StringVar(value="0 Locked")
        self.var_health = tk.StringVar(value="SYSTEM HEALTHY")

        make_card(0, "TARGET ASSETS", self.var_total, COLOR_INFO)
        make_card(1, "ENCRYPTED ASSETS", self.var_locked, COLOR_DANGER)
        make_card(2, "SYSTEM STATUS", self.var_health, COLOR_SUCCESS_BRIGHT)

        # Action Toolbar Buttons
        toolbar = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
        toolbar.grid(row=1, column=0, sticky="ew", padx=16, pady=4)

        def btn(text, cmd, bg_col, fg_col="#ffffff"):
            b = tk.Button(toolbar, text=text, command=cmd, font=(FONT_FAMILY, 9, "bold"), bg=bg_col, fg=fg_col, activebackground=BORDER_COLOR, relief="flat", padx=10, pady=5, cursor="hand2")
            b.pack(side="left", padx=4, pady=6)
            return b

        self.btn_enc_all = btn("🔒 Encrypt All Files", self._action_encrypt_all, COLOR_DANGER)
        self.btn_enc_sel = btn("🔒 Encrypt Selected", self._action_encrypt_selected, "#881337")
        self.btn_add_file = btn("➕ Add / Import File", self._action_add_file, "#1f3b58", COLOR_CYAN)
        self.btn_preview = btn("👁 Preview File Content", self._action_preview_file, "#21262d", TEXT_PRIMARY)
        self.btn_open_dir = btn("📂 Open Sandbox Folder", self._action_open_folder, "#1e293b", COLOR_INFO)

        self.btn_reset = tk.Button(toolbar, text="↺ Reset Sandbox", command=self._action_reset, font=(FONT_FAMILY, 8), bg=BG_CARD, fg=TEXT_SECONDARY, relief="flat", padx=8, pady=4, cursor="hand2")
        self.btn_reset.pack(side="right", padx=8, pady=6)

        # Real-Time Progress Bar Row
        prog_frame = tk.Frame(parent, bg=BG_PANEL)
        prog_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=2)
        prog_frame.columnconfigure(0, weight=1)

        self.var_status_text = tk.StringVar(value="Ready. Select any file or click 'Encrypt All Files' to start.")
        tk.Label(prog_frame, textvariable=self.var_status_text, font=(FONT_FAMILY, 9), fg=TEXT_PRIMARY, bg=BG_PANEL).pack(anchor="w")

        self.progress_bar = ttk.Progressbar(prog_frame, orient="horizontal", mode="determinate", style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", pady=(2, 4))

        # Files Treeview Table
        table_frame = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
        table_frame.grid(row=3, column=0, sticky="nsew", padx=16, pady=(2, 12))
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("status", "filename", "current_name", "type", "size", "entropy")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("status", text="STATUS")
        self.tree.heading("filename", text="ORIGINAL FILE")
        self.tree.heading("current_name", text="ON-DISK FILENAME")
        self.tree.heading("type", text="TYPE")
        self.tree.heading("size", text="SIZE")
        self.tree.heading("entropy", text="ENTROPY (H)")

        self.tree.column("status", width=110, anchor="center")
        self.tree.column("filename", width=220, anchor="w")
        self.tree.column("current_name", width=260, anchor="w")
        self.tree.column("type", width=140, anchor="center")
        self.tree.column("size", width=90, anchor="center")
        self.tree.column("entropy", width=110, anchor="center")

        self.tree.tag_configure("NORMAL", foreground=COLOR_SUCCESS_BRIGHT)
        self.tree.tag_configure("LOCKED", foreground=COLOR_DANGER)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<Double-1>", lambda e: self._action_preview_file())

    # --------------------------------------------------------------------------
    # 5.6 TAB 2: DECRYPTION & INCIDENT REMEDIATION PORTAL
    # Provides key entry, 1-Click Auto Recovery, and shows the dropped ransom note.
    # --------------------------------------------------------------------------
    def _build_recovery_tab(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        # Remediation Header
        h = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
        h.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 8))
        tk.Label(h, text="🔓 DECRYPTION & REMEDIATION PORTAL", font=(FONT_FAMILY, 12, "bold"), fg=COLOR_SUCCESS_BRIGHT, bg=BG_CARD).pack(anchor="w", padx=16, pady=(8, 2))
        tk.Label(h, text="Verify key or use 1-Click Auto Recovery to safely restore all encrypted files with 100% SHA-256 match.", font=(FONT_FAMILY, 9), fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w", padx=16, pady=(0, 8))

        # Recovery Controls Box
        c_box = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
        c_box.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))

        key_row = tk.Frame(c_box, bg=BG_CARD)
        key_row.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(key_row, text="Decryption Key:", font=(FONT_FAMILY, 9, "bold"), fg=TEXT_SECONDARY, bg=BG_CARD).pack(side="left")
        self.entry_key = tk.Entry(key_row, font=(FONT_MONO, 10), bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, relief="flat", highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.entry_key.pack(side="left", fill="x", expand=True, padx=10, ipady=5)

        tk.Button(key_row, text="⚡ Auto Key", command=self._autofill_key, font=(FONT_FAMILY, 9, "bold"), bg="#21262d", fg=COLOR_PURPLE, relief="flat", padx=12, pady=4, cursor="hand2").pack(side="right")

        act_row = tk.Frame(c_box, bg=BG_CARD)
        act_row.pack(fill="x", padx=16, pady=(0, 14))

        tk.Button(act_row, text="⚡ 1-CLICK AUTO RECOVER", command=self._action_auto_recover, font=(FONT_FAMILY, 10, "bold"), bg=COLOR_SUCCESS, fg="#ffffff", relief="flat", pady=9, cursor="hand2").pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Button(act_row, text="VERIFY KEY & DECRYPT", command=self._action_manual_decrypt, font=(FONT_FAMILY, 9, "bold"), bg="#21262d", fg=TEXT_PRIMARY, relief="flat", pady=9, cursor="hand2").pack(side="left", fill="x", expand=True, padx=6)
        tk.Button(act_row, text="📂 View Target Files", command=lambda: self.notebook.select(self.tab_attack), font=(FONT_FAMILY, 9), bg=BG_INPUT, fg=TEXT_SECONDARY, relief="flat", pady=9, cursor="hand2").pack(side="left", padx=(6, 0))

        # Extortion Note Artifact Display Frame
        note_frame = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
        note_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 14))
        note_frame.rowconfigure(1, weight=1)
        note_frame.columnconfigure(0, weight=1)

        tk.Label(note_frame, text="EXTORTION NOTE ARTIFACT (README_RECOVER_FILES_SIMULATION.TXT)", font=(FONT_FAMILY, 9, "bold"), fg=TEXT_SECONDARY, bg=BG_CARD).grid(row=0, column=0, sticky="w", padx=16, pady=(8, 4))
        self.txt_note = tk.Text(note_frame, bg=BG_INPUT, fg="#94a3b8", font=(FONT_MONO, 9), wrap="word", relief="flat", padx=12, pady=10)
        self.txt_note.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        self._refresh_note_text()

    # --------------------------------------------------------------------------
    # 5.7 BOTTOM TELEMETRY STATUS BAR
    # Displays active sandbox path and victim portal URL.
    # --------------------------------------------------------------------------
    def _build_status_bar(self):
        bar = tk.Frame(self, bg=BG_PANEL, highlightbackground=BORDER_COLOR, highlightthickness=1)
        bar.pack(fill="x", side="bottom")
        tk.Label(bar, text=f"Target Directory: {self.engine.sandbox_dir}", font=(FONT_MONO, 8), fg=TEXT_MUTED, bg=BG_PANEL).pack(side="left", padx=14, pady=4)
        tk.Label(bar, text="Victim Web Portal: http://localhost:8080 (Chrome Ready)", font=(FONT_MONO, 8), fg=COLOR_WARN, bg=BG_PANEL).pack(side="right", padx=14, pady=4)

    # --------------------------------------------------------------------------
    # 5.8 TARGET FILES TREEVIEW GRID POPULATOR
    # Reads file list from self.engine, populates Treeview, and updates KPI cards.
    # --------------------------------------------------------------------------
    def refresh_file_grid(self):
        self.engine.sync_from_disk()
        for item in self.tree.get_children():
            self.tree.delete(item)

        files = self.engine.simulated_files
        locked = sum(1 for f in files if f.status == "LOCKED")
        for f in files:
            self.tree.insert("", "end", values=(f"[{f.status}]", f.original_name, f.filename, f.file_type, f"{f.size_bytes} B", f"{f.current_entropy:.2f} bits"), tags=(f.status,))

        self.var_total.set(f"{len(files)} Files")
        self.var_locked.set(f"{locked} Locked")
        if locked > 0:
            self.var_health.set("SYSTEM COMPROMISED (LOCKED)")
        else:
            self.var_health.set("SYSTEM HEALTHY")

    # --------------------------------------------------------------------------
    # 5.9 REAL-TIME DISK MONITOR & AUTO-SYNC LOOP
    # Checks disk directory signature every 1000ms to detect changes automatically.
    # --------------------------------------------------------------------------
    def _get_disk_signature(self):
        try:
            return tuple(sorted(os.listdir(self.engine.sandbox_dir)))
        except Exception:
            return ()

    def _auto_sync_with_disk(self):
        try:
            current_sig = self._get_disk_signature()
            if current_sig != self.last_disk_sig:
                self.last_disk_sig = current_sig
                self.refresh_file_grid()
                self._refresh_note_text()
                if self.engine.is_encrypted:
                    self._autofill_key()
                else:
                    self.var_status_text.set("All files successfully decrypted & restored.")
        except Exception:
            pass
        finally:
            self.after(1000, self._auto_sync_with_disk)

    # --------------------------------------------------------------------------
    # 5.10 BACKGROUND HTTP WEB SERVER MANAGER
    # Ensures port 8080 is listening on a background daemon thread.
    # --------------------------------------------------------------------------
    def _ensure_web_server_running(self):
        def is_port_in_use(port=8080):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.4)
                return s.connect_ex(('127.0.0.1', port)) == 0

        if not is_port_in_use(8080):
            def run_server():
                try:
                    server = HTTPServer(("0.0.0.0", 8080), EmbeddedVictimHandler)
                except Exception:
                    try:
                        server = HTTPServer(("127.0.0.1", 8080), EmbeddedVictimHandler)
                    except Exception:
                        return
                server.serve_forever()

            threading.Thread(target=run_server, daemon=True).start()

    # --------------------------------------------------------------------------
    # 5.11 EXTERNAL WEB BROWSER LAUNCHER
    # Opens default browser (Chrome/Edge) to view the victim extortion portal.
    # --------------------------------------------------------------------------
    def _open_victim_portal(self):
        self._ensure_web_server_running()
        url = "http://localhost:8080"
        def delayed_open():
            time.sleep(0.3)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        threading.Thread(target=delayed_open, daemon=True).start()

    # --------------------------------------------------------------------------
    # 5.12 BATCH ENCRYPTION EVENT HANDLER (MULTI-THREADED)
    # Runs engine.execute_encryption_simulation in background thread to avoid freezing.
    # --------------------------------------------------------------------------
    def _action_encrypt_all(self):
        if self.is_running_task:
            return
        self.is_running_task = True
        self.var_status_text.set("Executing Fernet Encryption Attack...")

        def task():
            # Real-time progress callback to update progress bar smoothly
            def on_progress(cur, tot, fname, pct):
                self.progress_bar["value"] = pct
                self.var_status_text.set(f"Encrypting ({cur}/{tot}): {fname}")
                self.after_idle(self.refresh_file_grid)

            try:
                # LINK: Calls encryption method in RansomwareEngine
                ok = self.engine.execute_encryption_simulation(on_progress)
            finally:
                self.is_running_task = False

            self.after_idle(self.refresh_file_grid)
            self.after_idle(self._refresh_note_text)
            self.after_idle(self._autofill_key)
            if ok:
                self.var_status_text.set("ENCRYPTION COMPLETE: All files locked! Check http://localhost:8080")
                messagebox.showinfo("Attack Complete", "All files in sandbox have been encrypted!\nOpen the Victim Portal to see the live countdown.")

        threading.Thread(target=task, daemon=True).start()

    # --------------------------------------------------------------------------
    # 5.13 INDIVIDUAL FILE ENCRYPTION HANDLER
    # Encrypts only the currently selected file in the Treeview table.
    # --------------------------------------------------------------------------
    def _action_encrypt_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select File", "Please select a file from the table first.")
            return
        orig_name = self.tree.item(sel[0], "values")[1]
        f_obj = next((f for f in self.engine.simulated_files if f.original_name == orig_name), None)
        if not f_obj or f_obj.status == "LOCKED":
            messagebox.showinfo("Already Encrypted", "File is already encrypted.")
            return

        ok = self.engine.encrypt_single_file(f_obj)
        self.refresh_file_grid()
        self._refresh_note_text()
        self._autofill_key()
        if ok:
            messagebox.showinfo("File Encrypted", f"'{f_obj.original_name}' has been encrypted!")

    # --------------------------------------------------------------------------
    # 5.14 CUSTOM FILE IMPORTATION HANDLER
    # Allows user to load an arbitrary test file into ./sandbox_data/ via dialog.
    # --------------------------------------------------------------------------
    def _action_add_file(self):
        fpath = filedialog.askopenfilename(title="Select File to Add to Simulator")
        if fpath:
            f_obj = self.engine.import_custom_file(fpath)
            if f_obj:
                self.refresh_file_grid()
                messagebox.showinfo("File Added", f"Loaded '{os.path.basename(fpath)}' into sandbox!")

    # --------------------------------------------------------------------------
    # 5.15 FILE CONTENT & HEX DUMP INSPECTOR
    # Displays preview window showing plain text or structured hexadecimal bytes.
    # --------------------------------------------------------------------------
    def _action_preview_file(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select File", "Please click on a file in the table first.")
            return
        orig_name = self.tree.item(sel[0], "values")[1]
        f_obj = next((f for f in self.engine.simulated_files if f.original_name == orig_name), None)
        if not f_obj:
            return

        preview = self.engine.read_file_preview(f_obj)
        d = tk.Toplevel(self)
        d.title(f"Preview: {f_obj.filename}")
        d.geometry("640x440")
        d.configure(bg=BG_CARD)
        tk.Label(d, text=f"File: {f_obj.filename} | Status: {f_obj.status} | Entropy: {f_obj.current_entropy:.2f} bits", font=(FONT_FAMILY, 9, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=12, pady=8)
        t = tk.Text(d, bg=BG_INPUT, fg="#cbd5e1", font=(FONT_MONO, 9), wrap="word", relief="flat")
        t.pack(fill="both", expand=True, padx=12, pady=4)
        t.insert("1.0", preview)
        t.config(state="disabled")

    # --------------------------------------------------------------------------
    # 5.16 SANDBOX DIRECTORY EXPLORER LAUNCHER
    # Opens Windows Explorer directly at ./sandbox_data/.
    # --------------------------------------------------------------------------
    def _action_open_folder(self):
        os.makedirs(self.engine.sandbox_dir, exist_ok=True)
        try:
            if sys.platform == "win32":
                os.startfile(self.engine.sandbox_dir)
            else:
                subprocess.Popen(["xdg-open", self.engine.sandbox_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory: {e}")

    # --------------------------------------------------------------------------
    # 5.17 SANDBOX RESET EVENT HANDLER
    # Purges all encrypted files and restores fresh unencrypted test assets.
    # --------------------------------------------------------------------------
    def _action_reset(self):
        if self.is_running_task:
            return
        self.engine.initialize_sandbox(force_clean=True)
        self.refresh_file_grid()
        self._refresh_note_text()
        self.entry_key.delete(0, tk.END)
        self.var_status_text.set("Sandbox reset to initial clean state.")
        self.progress_bar["value"] = 0
        messagebox.showinfo("Sandbox Reset", "All sandbox files restored to clean unencrypted state.")

    # --------------------------------------------------------------------------
    # 5.18 DECRYPTION KEY AUTOFILL HELPER
    # Reads the active Fernet key from the engine and populates the text field.
    # --------------------------------------------------------------------------
    def _autofill_key(self):
        key = self.engine.session_key if self.engine.session_key else self.engine.load_key().decode("utf-8")
        self.entry_key.delete(0, tk.END)
        self.entry_key.insert(0, key)

    # --------------------------------------------------------------------------
    # 5.19 1-CLICK AUTOMATIC INCIDENT REMEDIATION
    # Automatically retrieves the stored key and triggers full remediation.
    # --------------------------------------------------------------------------
    def _action_auto_recover(self):
        self._autofill_key()
        self._action_manual_decrypt()

    # --------------------------------------------------------------------------
    # 5.20 MANUAL KEY VERIFICATION & DECRYPTION HANDLER
    # Dispatches the key to self.engine.execute_decryption_simulation and verifies SHA-256.
    # --------------------------------------------------------------------------
    def _action_manual_decrypt(self):
        key = self.entry_key.get().strip()
        if not key:
            self._autofill_key()
            key = self.entry_key.get().strip()

        if not self.engine.is_encrypted:
            messagebox.showinfo("Safe", "Files are not currently encrypted.")
            return

        # LINK: Calls decryption method in RansomwareEngine
        ok, msg = self.engine.execute_decryption_simulation(key)
        self.refresh_file_grid()
        self._refresh_note_text()
        if ok:
            messagebox.showinfo("Recovery Success", msg)
            self.notebook.select(self.tab_attack)
        else:
            messagebox.showerror("Recovery Failed", msg)

    # --------------------------------------------------------------------------
    # 5.21 EXTORTION NOTE ARTIFACT VIEWER UPDATER
    # Reads note content from self.engine and displays it in the recovery tab.
    # --------------------------------------------------------------------------
    def _refresh_note_text(self):
        content = self.engine.get_ransom_note_content()
        self.txt_note.config(state="normal")
        self.txt_note.delete("1.0", tk.END)
        self.txt_note.insert("1.0", content)
        self.txt_note.config(state="disabled")


# ==============================================================================
# 6. GUI APPLICATION ENTRY POINT
# Instantiates and launches the Tkinter main event loop.
# ==============================================================================
def main():
    app = RansomwareGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
