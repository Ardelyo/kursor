# AuraMouse - Kontrol Mouse dengan Gestur Tangan & Kepala

AuraMouse adalah aplikasi Python yang memungkinkan Anda mengontrol kursor mouse komputer menggunakan gestur tangan atau gerakan kepala melalui webcam.

## Fitur Utama

*   **Dua Mode Kontrol:**
    *   **Mode Tangan:** Menggunakan deteksi tangan MediaPipe untuk melacak jari dan mengenali gestur.
    *   **Mode Kepala (Wajah):** Menggunakan deteksi wajah MediaPipe untuk melacak fitur wajah (misalnya, hidung) sebagai pointer.
*   **Aksi Mouse:**
    *   Gerakan Pointer
    *   Klik Kiri (Pinch tangan, Dwell wajah)
    *   Klik Kanan (Pinch tangan)
    *   Double Klik (Gestur tangan)
    *   Toggle Drag (Gestur tangan)
    *   Scroll Atas/Bawah (Gestur tangan)
    *   Aksi kustom melalui kedipan mata (Mode Wajah)
*   **Keyboard Virtual:**
    *   Keyboard QWERTY yang dapat ditampilkan di layar.
    *   Input melalui dwell-hover atau gestur klik utama.
    *   Dapat di-toggle dengan tombol fisik atau mekanisme aksesibel (direncanakan).
*   **Konfigurasi Fleksibel:**
    *   Pengaturan disimpan dalam file `settings.json`.
    *   GUI Pengaturan (Tkinter) untuk mengubah parameter dengan mudah.
    *   Parameter meliputi sensitivitas, durasi dwell, threshold gestur, pilihan kamera, dll.

## Persyaratan

*   Python 3.7+
*   OpenCV (`opencv-python`)
*   MediaPipe (`mediapipe`)
*   PyAutoGUI (`pyautogui`)
*   NumPy (`numpy`)

Anda dapat menginstal dependensi dengan:
`pip install -r requirements.txt`

## Cara Menjalankan

1.  Pastikan webcam Anda terhubung.
2.  Jalankan `main.py`:
    `python main.py`
3.  Jendela pratinjau kamera akan muncul dengan informasi status.
4.  Gunakan tombol pintas untuk mengontrol aplikasi (lihat bagian "Kontrol Umum").
5.  Untuk mengubah pengaturan, jalankan `gui_settings.py`:
    `python gui_settings.py`
    Simpan pengaturan, lalu restart `main.py` agar perubahan diterapkan.

## Kontrol Umum (Default)

*   **`q`**: Keluar dari aplikasi.
*   **`s`**: Start/Stop kontrol mouse aktual.
*   **`h`**: Beralih ke Mode Deteksi TANGAN.
*   **`f`**: Beralih ke Mode Deteksi KEPALA (Wajah).
*   **`p`**: Tampilkan instruksi ini lagi di konsol.
*   **`k`**: Toggle Keyboard Virtual (atau sesuai pengaturan `keyboard_toggle_key`).

## Deskripsi Gestur Tangan (Umum)

Berikut adalah deskripsi postur tangan yang diharapkan untuk gestur umum. Akurasi dapat dipengaruhi oleh pencahayaan, latar belakang, dan kualitas kamera. Sesuaikan threshold di pengaturan jika perlu.

*   **Pointer Bergerak:** Ujung jari telunjuk (landmark #8) adalah pointer default. Gerakkan tangan Anda.
*   **Klik Kiri (Pinch Telunjuk-Jempol):**
    *   Pertemukan ujung jari telunjuk dengan ujung ibu jari.
    *   Jari-jari lain idealnya tetap terbuka atau tidak mengganggu.
*   **Klik Kanan (Pinch Tengah-Jempol):**
    *   Pertemukan ujung jari tengah dengan ujung ibu jari.
    *   Jari telunjuk dan jari-jari lain idealnya tetap terbuka.
*   **Toggle Drag (Pinch Manis-Jempol):**
    *   Pertemukan ujung jari manis dengan ujung ibu jari.
    *   Jari-jari lain idealnya tetap terbuka.
*   **Scroll Atas:**
    *   Ibu jari, jari telunjuk, dan jari tengah terangkat (lurus ke atas).
    *   Jari manis dan kelingking tertutup/ke bawah.
    *   (Contoh: seperti menunjukkan angka '3' dengan jempol juga ikut serta, tangan menghadap ke depan)
*   **Scroll Bawah:**
    *   Ibu jari tertutup/ke bawah.
    *   Jari telunjuk, jari tengah, dan jari manis terangkat (lurus ke atas).
    *   Kelingking tertutup/ke bawah.
    *   (Contoh: seperti menunjukkan angka '3' tanpa jempol, tangan menghadap ke depan)

*Catatan: Definisi gestur scroll di atas adalah contoh. Implementasi aktual di `tracker.py` berdasarkan `fingers_up()` mungkin sedikit berbeda. Periksa `HandTracker.fingers_up()` dan `HandTracker.get_gestures()` untuk detailnya.*

## Rencana Pengembangan (Roadmap)

*   **Fase Saat Ini:** Stabilisasi gestur, integrasi dasar keyboard virtual.
*   **Selanjutnya:**
    *   Fungsionalitas penuh keyboard virtual (termasuk penekanan tombol).
    *   Mekanisme pemanggilan keyboard yang aksesibel (tanpa keyboard fisik).
    *   Peningkatan GUI pengaturan.
    *   Polesan keyboard (estetika, suara).
    *   Layout keyboard tambahan/kustom.
    *   Dokumentasi pengguna yang lebih komprehensif.

## Kontribusi

Kontribusi, laporan bug, dan saran fitur sangat diterima! Silakan buat *issue* atau *pull request* di repositori GitHub (jika tersedia).