<p align="center">
  <img src="assets/Logo.jpg" alt="RAMURI Logo" width="150" />
</p>

# RAMURI

**Aplikasi evaluasi posisi catur dan autoplayer offline untuk Windows — menggunakan ONNX dan Stockfish 19.**

---

## ⚡ Fitur Utama

- **100% Offline** — semua deteksi dan analisis berjalan secara lokal tanpa internet
- **Deteksi Papan Otomatis** — membaca papan catur 2D dari layar (Chess.com, Lichess, dll)
- **Analisis Stockfish 19** — saran langkah terbaik secara instan
- **Auto Move** — eksekusi langkah engine secara otomatis ke papan
- **Manual Play** — kontrol timing dengan tombol "Play Next Move"
- **Promosi Otomatis** — mengikuti pilihan Stockfish untuk promosi pion
- **Castling Rights** — konfigurasi hak rokade (Kingside/Queenside)
- **Depth Control** — atur kedalaman analisis sesuai kebutuhan
- **Retry Logic** — langkah yang gagal otomatis dicoba ulang
- **Move Mode** — pilih mode Drag atau Click untuk menggerakkan bidak
- **Human-Like Mouse** — gerakan mouse yang menyerupai manusia

---

## 🛠️ Konfigurasi Engine (engine_config.txt)

Letakkan file ini di samping executable untuk mengkustomisasi Stockfish:

```ini
# RAMURI Engine Configuration

# Memory dalam MB (64–1024 direkomendasikan)
setoption name Hash value 512

# Jumlah thread CPU
setoption name Threads value 2
```

Restart RAMURI setelah mengedit.

---

## ▶️ Cara Menjalankan

> **⚠️ PENTING: Download Engine Stockfish**
> Dikarenakan adanya batas maksimal upload file di GitHub (maks 25 MB), file engine `stockfish.exe` **tidak disertakan** di dalam repositori ini. 
> Anda harus mendownloadnya secara mandiri melalui situs resmi [stockfishchess.org](https://stockfishchess.org/download/) dan meletakkan file eksekusinya (`stockfish.exe`) ke dalam folder `src/` sebelum menjalankan aplikasi.

Setelah Stockfish siap di folder `src/`, jalankan perintah berikut:

```bash
pip install -r requirements.txt
python src/main.py
```

### Alur Penggunaan

1. Pilih **White** atau **Black**
2. Atur castling rights jika diperlukan
3. Atur kedalaman analisis (depth)
4. Pilih mode **Manual** atau **Auto**
5. Tekan **ESC** untuk kembali ke pilihan warna

### ⌨️ Keyboard Shortcuts

RAMURI memiliki shortcut keyboard untuk memudahkan kendali tanpa mouse:

| Mode          | Shortcut      | Fungsi                                       |
| ------------- | ------------- | -------------------------------------------- |
| **Selection** | **W** / **B** | Pilih warna White atau Black                 |
|               | **←** / **→** | Kurangi / tambah kedalaman analisis (depth)  |
|               | **↓** / **↑** | Kurangi / tambah delay screenshot            |
| **Play**      | **P**         | Eksekusi langkah terbaik selanjutnya         |
|               | **A**         | Aktifkan / matikan mode Auto-Play            |
|               | **K** / **Q** | Toggle hak rokade Kingside / Queenside       |
| **Global**    | **Esc**       | Kembali ke layar pemilihan warna             |

---

## 📦 Build ke Aplikasi Windows (EXE)

Project ini siap untuk dijadikan satu file eksekusi mandiri (`.exe`) menggunakan PyInstaller.

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Jalankan proses build:
   ```bash
   pyinstaller win.spec
   ```
3. Hasil build akan berada di folder `dist/RAMURI.exe`. Anda bisa memindahkan file ini ke mana saja (portable). File ini sudah mencakup Python, model ONNX, dan Stockfish.

---

## 💡 Tips Penggunaan (Best Practices)

Agar AI mendeteksi papan dan bidak dengan akurat, perhatikan hal berikut:
1. **Papan Terlihat Penuh:** Pastikan seluruh papan catur di browser/game terlihat jelas di layar monitor Anda. Jangan biarkan papan tertutup oleh jendela RAMURI atau aplikasi lain, karena RAMURI menggunakan tangkapan layar (screenshot) untuk mendeteksi posisi.
2. **Gunakan Bidak 2D Standar:** Model AI dilatih menggunakan tema bidak catur 2D standar (seperti Neo, Staunton, dll). Tema 3D, animasi, atau tema yang terlalu abstrak akan membuat model AI kesulitan mengenali bidak.
3. **Orientasi Papan:** Saat Anda memilih warna *White* atau *Black* di aplikasi, RAMURI mengasumsikan warna yang Anda pilih berada di bagian bawah layar. Pastikan posisi papan catur di layar Anda sesuai.

---

## 🔁 Troubleshooting

**Deteksi papan salah**
→ Geser jendela RAMURI agar detektor memiliki pandangan jelas ke papan catur.

**Stockfish tidak berjalan**
→ Pastikan file `stockfish.exe` ada di folder `src/` (jika dari source).

**Aplikasi Error/Crash**
→ Cek file log untuk detail masalah. File log tersimpan secara otomatis di:
`%LOCALAPPDATA%\RAMURI\ramuri.log` (contoh: `C:\Users\NamaUser\AppData\Local\RAMURI\ramuri.log`)

---

## 📁 Struktur Project

```text
RAMURI/
│
├── assets/                  # Gambar logo dan aset aplikasi
│   └── Logo.jpg
│
├── src/                     # Source code utama
│   ├── main.py              # Entry point aplikasi
│   ├── chess_detection.onnx # Model AI untuk mendeteksi bidak catur
│   ├── stockfish.exe        # Engine catur Stockfish 19
│   │
│   ├── board_detection/     # Modul deteksi papan catur dari layar
│   │   ├── fen_extractor.py
│   │   └── get_positions.py
│   │
│   ├── core/                # Logika inti dan state aplikasi
│   │   ├── board_utils.py
│   │   ├── config.py
│   │   ├── fen_utils.py
│   │   ├── game_state.py
│   │   └── notation.py
│   │
│   ├── game/                # Kontrol permainan dan eksekusi langkah
│   │   ├── auto_play.py
│   │   ├── board_analyzer.py
│   │   ├── move_execution.py
│   │   ├── move_processor.py
│   │   ├── move_validator.py
│   │   └── promotion.py
│   │
│   ├── gui/                 # Komponen antarmuka (PyQt6)
│   │   ├── button_and_checkboxes.py
│   │   ├── create_widget.py
│   │   ├── set_window_icon.py
│   │   ├── shortcuts.py
│   │   ├── shortcuts_dialog.py
│   │   └── update_depth_label.py
│   │
│   ├── services/            # Layanan background (Stockfish integration)
│   │   └── engine_service.py
│   │
│   ├── utils/               # Fungsi bantuan dan utilities
│   │   ├── chess_resources_manager.py
│   │   ├── downloader.py
│   │   ├── human_mouse.py
│   │   ├── logging_setup.py
│   │   ├── resource_path.py
│   │   ├── system_info.py
│   │   └── system_interaction.py
│   │
│   └── wayland_capture/     # Modul screenshot khusus Linux Wayland
│       ├── screen.py
│       └── wayland.py
│
├── requirements.txt         # Daftar dependency Python
├── engine_config.txt        # File konfigurasi engine Stockfish
└── win.spec                 # Konfigurasi build executable PyInstaller
```

---

## 📜 Lisensi

Project ini menggunakan **MIT License**.

---

## 🙏 Acknowledgments

- **Source Asli:** Project ini merupakan modifikasi dan pengembangan dari [ChessPilot oleh OTAKUWeBer](https://github.com/OTAKUWeBer/ChessPilot)
- Zai-Kun — ONNX 2D chess piece detector
- Stockfish Team — chess engine terkuat di dunia