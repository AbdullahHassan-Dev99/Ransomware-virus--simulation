# 🛡️ Educational Ransomware & Remediation Simulator
### Academic Threat Simulation & Defensive Engineering Lab

An isolated, 100% reversible ransomware simulation system designed for academic cybersecurity demonstrations, malware analysis courses, and laboratory oral exams.

---

## 📁 Clean Project Structure (5 Core Files)

| File Name | Type | Description |
|:---|:---|:---|
| **`Ransomware GUI.py`** | Graphical Interface | The complete Attacker Control Console (Tkinter). Features target file monitoring, live entropy visualization, one-click encryption, 1-click auto recovery, and automatically hosts the localhost web extortion portal. |
| **`Ransomware With out GUI.py`** | Command-Line Interface | Interactive Terminal / CLI simulation interface. Perfect for automated, headless, or server demonstrations without opening desktop windows. |
| **`Ransomware.py`** | Core Cryptographic Engine | The backend engine (No GUI). Implements Fernet (AES-128-CBC + HMAC-SHA256) encryption, Shannon entropy calculation, dynamic file enumeration, and SHA-256 hash validation. |
| **`ransomware_report.html`** | Interactive Technical Report | Beautiful HTML manual with side-by-side syntax-highlighted code blocks and simple English explanations for presentations. Open directly in Chrome or print to PDF. |
| **`README.md`** | Academic Documentation | Project overview, architecture, MITRE ATT&CK mappings, and lab safety specifications. |

---

## 🚀 How to Run

### 1. Run with Graphical Interface (GUI):
```bash
python "Ransomware GUI.py"
```
* Launches the Hacker Console.
* Automatically hosts the victim extortion portal on **`http://localhost:8080`**.
* Click **`🌐 Open Victim Portal (Chrome)`** to view the live ticking 72-hour countdown.

### 2. Run without Graphical Interface (CLI / Terminal):
```bash
python "Ransomware With out GUI.py"
```
* Launches an interactive terminal menu with options to list files, encrypt, decrypt, and launch the web portal.

### 3. Open the Lab Report:
Double-click **`ransomware_report.html`** to open the technical report in Google Chrome / Edge.

---

## 🔒 Safety & Academic Boundaries
1. **100% Sandbox Confined:** Operations are strictly restricted to the `./sandbox_data/` folder.
2. **Synthetic Target Assets:** Generated test files only (.docx, .xlsx, .sql). User computer files are never modified.
3. **100% Reversible:** All files are decrypted and verified against original SHA-256 hashes with zero data loss.
4. **Zero Propagation:** No network propagation or persistence capabilities exist.
