# İstanbul–Bodrum koridor pilotu: kapsam

**Tarih:** 25 Ekim 2026 · **Durum:** kabul edildi (ürün sahibi, 25 Ekim 2026) · **Önceki kapsam:** yalnız Didim
**Dayanak:** ürün sahibinin 25 Ekim 2026 tarihli kapsam genişletmesi; `(hub analysis) 05-kararlar.md`; `go-no-go.md`

Pilot, Didim'den İstanbul–Bodrum koridoruna genişletildi. Amaç sorunu (bekleme, sürtünme, kapsama boşluğu) ve çözümün etkisini koridor ölçeğinde ölçülebilir kılmak.

Etiketler: **F** kaynaklı olgu · **K** kullanıcı girdisi, doğrulanmalı · **I** çıkarım · **U** bilinmiyor.

## 1. Coğrafi kapsam

### Ana güzergâh (M)

İstanbul → O-5 (Osmangazi Köprüsü / İstanbul–İzmir Otoyolu) → Manisa / İzmir çevresi → Aydın (Söke) → Milas → Bodrum, Didim bağlantısıyla.

### Alternatif aileleri (en az üçü gerçek yolculukla test edilir)

| Kod | Aile | Güzergâh özeti | Şarj yoğunluğu | Ana test değeri | PnC potansiyeli | Yoğun dönem riski |
|---|---|---|---|---|---|---|
| A1 | Çanakkale yönü | İstanbul → Tekirdağ / Malkara → O-6 (1915 Çanakkale Köprüsü) veya Gelibolu feribotu → Çanakkale → (isteğe bağlı) Biga / Bandırma üzerinden güney | Seyrek | Dayanıklılık, B planı, "en yakın değil en uygun" | Düşük | Feribot ve köprü kuyruğu |
| A2 | Güney varyantları | Söke → Didim (veya Akbük) → Milas → Bodrum; Söke–Milas doğrudan + Didim sapması; Milas–Bodrum Havalimanı | Orta | Turist kuyruğu, misafir akışı, Didim sürekliliği | Orta | Yüksek (yaz) |
| A3 | İç / kısa sapma | O-5 üzerinde veya 1–20 km dışında: Manisa (Turgutlu, Salihli), Aydın (OPS Mall, Aydın–Denizli Otoyolu 7. km), Oksijen dışı dinlenme noktaları | Yüksek–orta | Güç + doluluk + sapma optimizasyonu, çoklu operatör | Yüksek | Orta (Oksijen kümeleri) |
| A4 | Bodrum son segment + Didim | Milas → Bodrum (AVM, otel, marina, merkez) ve Didim geri bağlantısı | Orta–yüksek | Varış segmenti, misafir dönüşümü, fiyat rekabeti, işgaliye | Orta | Yüksek (yaz) |

Şehir içi son segmentler (İstanbul çıkışı, Bodrum / Didim varışı) isteğe bağlıdır ama ölçüme dahildir.

### Kullanıcının verdiği istasyon bilgileri (K)

Aşağıdakiler kapsam metninden alındı ve henüz doğrulanmadı. K1 kanıtı olarak sayılmazlar; Şarj@TR, CPO teklifleri ve EPDK istasyon listesiyle karşılaştırılır (spec `CP-DATA-004`).

- A1: Gelibolu servis alanı ve Çanakkale çevresinde Eşarj, Wat, Aksa, En Yakıt noktaları, yaklaşık 180 kW.
- A2: Söke (Novada AVM, Shell, Trugo); Didim (ZES, HIZZLAN, Otojet, otel ve AVM noktaları, 180 kW'a kadar); Milas (Pomelon AVM, havalimanı, ZES / Trugo).
- A3: ZES, Trugo, Astor, 5 Şarj, Eşarj kümeleri; 180–400 kW noktalar.
- A4: Bodrum'da ZES (Avenue AVM, 400 kW), Trugo, otel ve AVM noktaları; Didim'de 9'dan fazla DC.

## 2. Fonksiyonel kapsam

| Kod | Yetenek | Ne ölçülür | Spec alanı |
|---|---|---|---|
| F1 | Navigasyon süresi optimizasyonu | Toplam süre = sürüş + tahmini şarj + beklenen kuyruk | `CP-NAV` |
| F2 | Atıl bekleme azaltma | Canlı ve tarihsel doluluk, güç paylaşımı, işgaliye uyarısı | `CP-IDLE` |
| F3 | PnC başlatma sürtünmesi ve başarı oranı | Deneme, başarı, hata nedeni, süre | `CP-PNC` |
| F4 | Çoklu operatör erişimi | Hubject / ZES, ikili OCPI, misafir AD_HOC_USER | `CP-ACCESS` |
| F5 | Yoğun dönem (yaz, bayram) modeli ve sapma önerisi | Kuyruk tahmini, alternatif öneri ve kabul | `CP-PEAK` |
| F6 | Misafir fiyat rekabet testi | B2B + sabit marj + KDV, TL/kWh; doğrudan kart fiyatıyla karşılaştırma | `CP-PRICE` |
| F7 | Veri temeli | Canlı doluluk, güç müsaitliği, arıza, tarihsel kuyruk, mevsimsel desen | `CP-DATA` |
| F8 | KPI ölçümü | Operasyonel KPI'lar, yoğun dönem ayrı | `CP-KPI` |

## 3. Kapsam dışı (şimdilik)

Tam ülke ağı, şehir içi günlük şarj, OCPP 2.1 arka uç ayrıntısı, e-clearing.net (Faz 5).

## 4. Bu genişlemenin önceki kararlara etkisi

- **Karar 1 (hub sırası) değişmedi.** Koridordaki CPO'ların çoğu yine hub'da değil (Hubject'te yalnız ZES, **F**). Kapsamın ana kaynağı ikili OCPI ve misafir akışı olarak kalıyor; K1 artık tüm kanalları sayıyor (bkz. `07-go-no-go.md`).
- **Karar 2 (PnC) değişmedi.** K3 eşiği koridor üzerinde ≥ 20 ISO 15118-2 EVSE oldu.
- **Karar 3 (misafir fiyatı) değişmedi.** K8 eşiği: doğrudan kart fiyatı + %15'i geçmeyen ortalama, marj ≤ %20.
- **Yeni bağımlılık:** navigasyon ve bekleme optimizasyonu canlı doluluk verisine bağlı. EPDK Şarj@TR'nin üçüncü taraflara açık bir API'si yayımlanmış değil (**F**: EPDK web servis sayfası yalnız istasyon listesi ve lisans sorgusu REST servislerini listeliyor). Canlı veri ikili OCPI ve hub'lardan gelecek; EPDK kaynağı için bkz. `../national-hub-service/`.
