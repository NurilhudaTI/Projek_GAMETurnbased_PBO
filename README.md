Deskripsi Project

**Monstera Eclipse** adalah sebuah game RPG berbasis giliran (*turn-based RPG*) bertemakan dunia fantasi gelap yang dipenuhi tanaman mistis dan kegelapan eclipse. Konsepnya sederhana namun strategis: pemain memimpin sebuah tim hero untuk melawan gelombang musuh yang semakin kuat di setiap level.

Setiap pertarungan berlangsung secara bergantian — hero dan musuh saling menggunakan skill di setiap giliran mereka. Kemenangan di setiap level memberikan reward berupa heal HP, lalu pertarungan berlanjut ke level berikutnya dengan musuh yang lebih kuat dan lebih banyak. Tujuan permainan adalah menyelesaikan seluruh **12 level** sebelum semua hero jatuh kalah.

Game ini dibuat menggunakan **Python 3.13** dan **Pygame 2.6** sebagai library utama. Project ini merupakan tugas akhir dari mata kuliah *Object-Oriented Programming* yang menerapkan konsep **Inheritance**, **Polymorphism**, **Encapsulation**, dan **Abstraction** secara menyeluruh dalam setiap bagian kodenya.

# Anggota Kelompok
 M. Ikliluddin Al Wafi 
 Mochamat Nurilhuda
 Valentinus Satrio Dewanto
 Kevin Ahmadinejad

# Fitur Utama

## Hero System

Game memiliki tiga jenis hero yang bisa dipilih saat memulai permainan, masing-masing dengan peran dan skill yang berbeda:

**Warrior** *(Verdant Knight)* — Hero frontliner dengan HP tinggi dan defense kuat. Cocok untuk menahan serangan musuh. Memiliki skill fisik seperti *Vine Slash* untuk single target, *Thorn Burst* untuk menyerang semua musuh, *Root Shield* untuk menaikkan DEF, dan *Earth Smash* sebagai serangan brutal.

**Mage** *(Flora Sorceress)* — Hero damage dealer dengan ATK tertinggi namun DEF rendah. Unggul dalam serangan sihir. Memiliki skill seperti *Petal Storm*, *Spore Cloud* untuk AOE, dan *Arcane Bloom* sebagai ultimate attack.

**Healer** *(Bloom Sage)* — Hero support yang menjaga ketahanan tim. Bisa menyembuhkan satu ally, menyembuhkan seluruh tim sekaligus, atau memfokuskan heal ke ally dengan HP paling rendah lewat *Revitalize*.

Setiap hero memiliki **4 skill unik** yang bisa digunakan setiap giliran, dengan tipe skill berupa: *attack*, *aoe*, *defense*, dan *heal*.

## Enemy System

Game memiliki tiga jenis musuh dengan tingkat bahaya yang meningkat:

**Shadow** *(Demon)* — Musuh cepat dengan HP rendah. Selalu menyerang hero dengan HP paling sedikit. Memiliki skill *Dark Slash* dan *Void Strike* untuk serangan brutal single target.

**DarkMage** *(Frost Golem)* — Musuh bertipe sihir yang berbahaya karena bisa melakukan serangan AOE (*Eclipse Blast*) ke seluruh tim hero sekaligus.

**BossEclipse** *(Frost Titan)* — Boss dengan HP sangat tinggi dan sistem **fase bertarung** yang dinamis. Perilaku AI-nya berubah berdasarkan sisa HP: fase *normal* → *enraged* → *berserk* → *desperate*. Semakin kritis HP-nya, semakin agresif dan semakin sering menggunakan AOE dan skill *Permafrost* yang menyerang dua hero terkuat sekaligus.

Setiap musuh memiliki method `ai_turn()` dengan logika keputusan yang berbeda, sehingga setiap pertarungan terasa unik dan menantang.

## Game Features

**Level System** — Game terdiri dari 12 level yang dibagi dalam 4 tier kesulitan: *Hijau* (level 1–3), *Redup* (4–6), *Gelap* (7–9), dan *Eclipse* (10–12). Semakin tinggi tier, semakin banyak musuh yang muncul dan semakin kecil heal reward yang diterima setelah menang.

**Heal Reward System** — Setiap kali menang, hero yang masih hidup mendapatkan heal sebesar persentase tertentu dari Max HP mereka. Heal reward semakin kecil di level yang lebih tinggi (40% → 30% → 20% → 15%) untuk menjaga tantangan tetap seimbang.

**Particle System** — Setiap serangan, skill, dan momen kemenangan menghasilkan efek partikel berwarna yang membuat pertarungan terasa lebih hidup dan dinamis.

**Sprite & Animasi** — Karakter didukung sistem animasi berbasis sprite sheet dengan state *idle*, *run*, *attack*, *hurt*, dan *die* yang dikelola oleh `AssetManager` dan `CharacterAnimator`.

**Audio System** — Musik background untuk menu dan battle, serta sound effects untuk setiap aksi karakter dikelola oleh `SFXManager`.

**Multiple Screen** — Game memiliki layar `MenuScreen`, `SettingsScreen`, `PartySelectScreen`, `BattleScreen`, `LevelUpScreen`, dan `GameClearScreen` dengan transisi yang mulus.

# Cara Menjalankan Project

**Prasyarat:**
- Python 3.13 atau lebih baru
- pip (Python package manager)

**Langkah instalasi:**

```bash
# Step 1: Clone atau download repository
git clone <url-repository-kamu>
cd monstera-eclipse

# Step 2: Install dependencies
pip install pygame>=2.6

# Step 3: Jalankan game
python main.py
```

Game akan langsung terbuka. Pilih hero tim kamu dan mulai bertarung!

# Kontrol Game

| Tombol | Fungsi |
|---|---|
| Klik kiri pada hero | Pilih hero untuk bertindak |
| Klik pada musuh | Ganti target serangan |
| Klik tombol skill | Gunakan skill yang dipilih |
| Klik skill saat musuh dipilih | Eksekusi serangan |

---

# Penjelasan Implementasi OOP

## Abstraction

`Character` adalah *abstract base class* yang mendefinisikan interface dasar untuk semua karakter dalam game. Method seperti `use_skill()`, `get_description()`, dan `get_role_icon()` dideklarasikan di sini tapi tidak diimplementasikan — setiap subclass wajib mengisinya sendiri. Ini memastikan semua karakter punya kontrak yang seragam tanpa memaksakan satu implementasi tertentu.

## Inheritance

Hierarki class dibangun berlapis. `Hero` dan `Enemy` mewarisi semua atribut dasar dari `Character` (`_hp`, `_attack`, `_defense`, dll.) tanpa menulis ulang. `Warrior`, `Mage`, `Healer` kemudian mewarisi dari `Hero`, sedangkan `Shadow`, `DarkMage`, `BossEclipse` mewarisi dari `Enemy`. Setiap level hirarki hanya menambahkan apa yang spesifik untuknya.

## Encapsulation

Semua atribut sensitif karakter disimpan sebagai private (`_hp`, `_attack`, `_defense`, `_alive`) dan hanya bisa diakses dari luar lewat `@property` yang read-only. Tidak ada kode di luar class yang bisa mengubah HP secara langsung — semua modifikasi harus lewat method resmi seperti `take_damage()` atau `heal()`.

## Polymorphism

Method `use_skill()` dipanggil dengan cara yang **identik** untuk semua karakter, namun menghasilkan efek yang **sama sekali berbeda** tergantung subclass-nya. Begitu juga `ai_turn()` pada musuh — `Shadow` selalu menyerang hero dengan HP paling rendah, `DarkMage` sering memilih AOE, dan `BossEclipse` mengubah pola serangannya secara dinamis berdasarkan sisa HP. Ini adalah polymorphism murni: satu interface, banyak perilaku.


Repository GitHub:
