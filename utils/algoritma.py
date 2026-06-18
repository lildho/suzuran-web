"""
utils/algoritma.py
Kelas SearchEngine & SortEngine — implementasi algoritma pencarian & pengurutan.

SearchEngine:
  - linear_search   : Linear / Sequential Search  → O(n)
  - binary_search   : Binary Search (by NIM)       → O(log n)

SortEngine:
  - bubble_sort     : Bubble Sort    → O(n²)
  - selection_sort  : Selection Sort → O(n²)
"""

import math


# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class SearchEngine:
    """Kelas pencarian data mahasiswa dengan berbagai algoritma."""

    def __init__(self, data):
        # Konversi sqlite3.Row → list of dict agar bisa dimanipulasi
        self.data = [dict(row) for row in data]

    # ── Linear / Sequential Search ─────────────────────────────────────────────
    def linear_search(self, keyword: str, field: str = "nama") -> tuple[list, int]:
        """
        Linear Search: iterasi setiap elemen satu per satu.
        Time Complexity : O(n)
        Space Complexity: O(1)

        Kelebihan : tidak perlu data terurut, bisa cari di semua field
        Kekurangan: lambat untuk data besar (n besar)
        """
        keyword_lower = keyword.lower()
        hasil   = []
        langkah = 0

        for item in self.data:
            langkah += 1   # Setiap iterasi = 1 langkah
            nilai = str(item.get(field, "")).lower()
            if keyword_lower in nilai:
                hasil.append(item)

        return hasil, langkah

    # ── Binary Search ──────────────────────────────────────────────────────────
    def binary_search(self, keyword: str) -> tuple[list, int]:
        """
        Binary Search: membagi data menjadi dua bagian berulang kali.
        Data HARUS terurut berdasarkan NIM (ascending).
        Time Complexity : O(log n)
        Space Complexity: O(1)

        Kelebihan : sangat cepat untuk data besar
        Kekurangan: data harus terurut, hanya bisa exact-match / prefix
        """
        # Urutkan berdasarkan NIM dulu
        sorted_data = sorted(self.data, key=lambda x: x["nim"])

        keyword_upper = keyword.upper()
        kiri   = 0
        kanan  = len(sorted_data) - 1
        langkah = 0
        hasil  = []

        while kiri <= kanan:
            langkah += 1
            tengah = (kiri + kanan) // 2
            nim_tengah = sorted_data[tengah]["nim"]

            if nim_tengah == keyword_upper:
                # Ketemu exact match — kumpulkan juga yang bersebelahan (duplikat NIM tidak ada, tapi siaga)
                hasil.append(sorted_data[tengah])
                break
            elif nim_tengah < keyword_upper:
                kiri = tengah + 1
            else:
                kanan = tengah - 1

        # Jika tidak ketemu exact, lakukan prefix search di seluruh data (fallback)
        if not hasil:
            for item in sorted_data:
                langkah += 1
                if item["nim"].startswith(keyword_upper):
                    hasil.append(item)

        return hasil, langkah

    # ── Estimasi Kompleksitas ──────────────────────────────────────────────────
    def estimasi_complexity(self, n: int, algoritma: str) -> dict:
        """
        Estimasi jumlah operasi dan waktu teoritis berdasarkan n.
        Asumsi: 1 operasi ≈ 0.000001 detik (1 μs)
        """
        ops_per_sec   = 1_000_000   # 1 juta operasi/detik (estimasi modern CPU)
        if algoritma == "binary":
            ops = math.log2(n) if n > 0 else 1
            label = "O(log n)"
        else:
            ops = n
            label = "O(n)"

        waktu_teori_s = ops / ops_per_sec
        return {
            "label"          : label,
            "estimasi_ops"   : round(ops, 2),
            "estimasi_waktu_s": round(waktu_teori_s, 8),
            "keterangan"     : f"Dengan n={n} data, {label} butuh ≈{round(ops,1)} operasi"
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  SORT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class SortEngine:
    """Kelas pengurutan data mahasiswa dengan berbagai algoritma."""

    def __init__(self, data):
        self.data = [dict(row) for row in data]

    # ── Bubble Sort ────────────────────────────────────────────────────────────
    def bubble_sort(self, field: str = "nama", order: str = "asc") -> tuple[list, int]:
        """
        Bubble Sort: bandingkan pasangan elemen bersebelahan, tukar jika perlu.
        Time Complexity  : O(n²) worst/average, O(n) best (sudah terurut)
        Space Complexity : O(1)
        Stable           : Ya

        Cocok untuk: dataset kecil, data yang hampir terurut
        """
        arr     = [item.copy() for item in self.data]
        n       = len(arr)
        steps   = 0
        reverse = (order == "desc")

        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                steps += 1
                val_j   = self._get_val(arr[j],   field)
                val_j1  = self._get_val(arr[j+1], field)
                should_swap = (val_j > val_j1) if not reverse else (val_j < val_j1)
                if should_swap:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    swapped = True
            if not swapped:
                break   # Optimasi: hentikan jika sudah terurut

        return arr, steps

    # ── Selection Sort ─────────────────────────────────────────────────────────
    def selection_sort(self, field: str = "nama", order: str = "asc") -> tuple[list, int]:
        """
        Selection Sort: temukan elemen minimum/maksimum, letakkan di posisi benar.
        Time Complexity  : O(n²) semua kasus
        Space Complexity : O(1)
        Stable           : Tidak (pada implementasi array)

        Cocok untuk: dataset kecil, meminimalkan jumlah penukaran (swap)
        """
        arr     = [item.copy() for item in self.data]
        n       = len(arr)
        steps   = 0
        reverse = (order == "desc")

        for i in range(n):
            idx_ekstrem = i
            for j in range(i + 1, n):
                steps += 1
                val_ekstrem = self._get_val(arr[idx_ekstrem], field)
                val_j       = self._get_val(arr[j],           field)
                if (not reverse and val_j < val_ekstrem) or (reverse and val_j > val_ekstrem):
                    idx_ekstrem = j
            if idx_ekstrem != i:
                arr[i], arr[idx_ekstrem] = arr[idx_ekstrem], arr[i]

        return arr, steps

    # ── Helper ─────────────────────────────────────────────────────────────────
    @staticmethod
    def _get_val(item: dict, field: str):
        """Ambil nilai untuk perbandingan (lowercase string / float)."""
        val = item.get(field, "")
        try:
            return float(val)
        except (ValueError, TypeError):
            return str(val).lower()

    def estimasi(self, n: int) -> dict:
        ops           = n * n
        ops_per_sec   = 1_000_000
        waktu_teori_s = ops / ops_per_sec
        return {
            "label"          : "O(n²)",
            "estimasi_ops"   : ops,
            "estimasi_waktu_s": round(waktu_teori_s, 6),
            "keterangan"     : f"Dengan n={n} data, O(n²) butuh ≈{ops:,} operasi"
        }
