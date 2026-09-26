# MOVIE

Website video + panel admin dalam satu repository.

## Aturan inti
- Kategori: Indonesia, Papua, Barat.
- Slug otomatis dari judul + Part.
- Part otomatis dihitung per kategori saat video baru dibuat.
- Edit video tidak mengubah slug/Part.
- Urutan website berdasarkan tanggal + jam publikasi, bukan waktu terakhir diedit.
- Cover: `covers/[slug].jpg`.
- OG cover: `covers/og/[slug].jpg`, 1200x630 px.
- Google Drive player tetap digunakan.
- `videos.json` adalah source of truth.
- GitHub Actions menjalankan generator dan deploy ke GitHub Pages.

## Admin
Buka `/admin/`. Panel memakai GitHub Personal Access Token yang dimasukkan sendiri oleh admin. Token hanya disimpan di sessionStorage browser. Token harus memiliki akses Contents: Read and write pada repository yang dikonfigurasi di Website Settings.

## Data publikasi
```json
{
  "tanggal": "2026-09-19",
  "jam": "21:30"
}
```

## Migrasi
Data lama dapat diimpor melalui `scripts/import_legacy.py` setelah URL legacy diisi secara manual jika diperlukan. Script hanya membaca `videos.json` lama; folder `covers/` lama tidak dibaca.

## GitHub Pages
Setelah upload ke branch `main`, buka Settings → Pages dan pilih GitHub Actions sebagai Source.

## Copy ke repository baru (testing)

Source ini dirancang agar dapat disalin ke repository GitHub baru tanpa mengedit `generate.py`, template HTML, atau player.

Setelah source disalin:
1. Pastikan branch yang digunakan adalah `main`.
2. Buka `/admin/`.
3. Masukkan GitHub Owner, Repository, Branch, dan token milik repository tersebut.
4. Pada **Website Settings**, isi Nama Website dan URL Website, lalu simpan.
5. Pada **Adsterra Settings**, masukkan kode iklan milik website tersebut jika ingin mengaktifkan iklan.

`config.json` menyimpan identitas website, repository, dan pengaturan Adsterra. `templates/video.html` dan player Google Drive tidak diubah oleh mekanisme konfigurasi ini.
