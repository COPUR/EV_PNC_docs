# İstanbul–Bodrum koridor pilotu

25 Ekim 2026'da Didim pilotu İstanbul–Bodrum koridoruna genişletildi. Bu klasör, ürün sahibinin kapsam metninden çıkarılan spec paketidir.

| Dosya | İçerik |
|---|---|
| `scope.md` | Ana güzergâh, dört alternatif ailesi (A1–A4), fonksiyonel kapsam, kapsam dışı, önceki kararlara etkisi |
| `kpis.md` | Yedi operasyonel KPI: formül, hedef, veri kaynağı, yoğun dönem ve kontrol grubu kuralları |
| `spec.md` | 32 EARS gereksinimi (`CP-GEO`, `NAV`, `IDLE`, `PNC`, `ACCESS`, `PEAK`, `PRICE`, `DATA`, `KPI`) |
| `acceptance/*.feature` | 7 Gherkin dosyası, her gereksinim etiketli |
| `tasks.md` | T-CP-01..21 |
| `traceability.csv` | 32 gereksinim, 32 hazır, 0 boşluk |

Go/no-go eşikleri [go-no-go.md](go-no-go.md) içinde (K1, K1-H, K3, K6, K8). Genel depo kopyasında K6 tavan tutarı yayımlanmaz.

Kapsam metnindeki istasyon bilgileri (ör. Bodrum Avenue AVM 400 kW) kullanıcı girdisidir ve doğrulanmadı; K1 kanıtı olarak sayılmaz.

Kaynak belgeler (`05-kararlar.md`, `03-turkiye-todo.md`, hub analizleri) bu depoda değil, proje dosyalarındadır; kararların özeti [ADR'lerde](../adr/index.md) durur.
