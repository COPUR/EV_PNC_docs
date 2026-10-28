# Go/no-go ölçütleri (TR-16)

> **Genel depo notu.** Bu kopyada K6 tavan tutarı yayımlanmamıştır: hub pazarlığında vazgeçme sınırımızı açık depoda tutmak pazarlık gücümüzü zayıflatır. Tam sürüm ürün sahibinin proje dosyalarındadır. Diğer eşikler yayımlanmıştır; yayımlanmaması gerekenleri ürün sahibi belirler.

**Tarih:** 25 Ekim 2026 (koridor güncellemesi aynı gün) · **Dayanak:** `05-kararlar.md`, `06-eposta-taslaklari.md`, `03-turkiye-todo.md`
**Takvim (öneri):** hafta 0 = 26 Ekim 2026 (e-postalar) · ara kontrol = 9 Kasım 2026 (hafta 2) · **kapı = 7 Aralık 2026 (hafta 6)**

Eşik değerleri **öneridir**; köşeli parantezli olanları kapıdan önce siz belirlersiniz. Her ölçüt kanıtla kapanır: e-posta yanıtı, teklif, hukuk görüşü veya test sonucu. Kanıtı olmayan ölçüt "bilinmiyor" sayılır ve GO için yeterli değildir.

## Ölçütler

| No | Alan | Ölçüt | Önerilen eşik | Kanıt | Sahip | Türü |
|---|---|---|---|---|---|---|
| K1 | Kapsam | İstanbul–Bodrum koridoru ve alternatif ailelerinde erişilebilir EVSE (hub + ikili OCPI + misafir) | ≥ 120 EVSE, en az 45 DC (≥ 150 kW tercih) | Günlük K1 sayımı (`corridor-pilot` CP-ACCESS-003), CPO teklifleri, Hubject soru 6 | BD | Pilot için zorunlu |
| K1-H | Kapsam | K1'in Hubject (ZES) üzerinden erişilen kısmı | ≥ [__] EVSE (öneri: K1'in %20'si) | Hubject yanıtı, ZES teklifi | BD | Hubject için zorunlu |
| K2 | Plug&Charge | Pilot CPO'ların sorguladığı CCP'ye sertifikamız ulaşıyor mu | Evet, en az bir pilot CPO için yazılı teyit | GIREVE soru 8, Hubject soru 12, ZES soru 5 | PnC | PNCP için zorunlu |
| K3 | Plug&Charge | Koridor üzerinde ISO 15118-2 destekli EVSE ve araç durumu | ≥ 20 EVSE ve Togg/Trugo için yazılı teyit (TR-11) | CPO yanıtı, OEM teyidi | PnC | PNCP için zorunlu |
| K4 | Hukuk | eMSP'nin kendi fiyatıyla yeniden satış yapabilmesi (TR-01); hub sözleşmelerinde KVKK aktarımı (TR-05); GIREVE GTC Art. 14 | Yazılı hukuk görüşü olumlu; KVKK aktarım dayanağı belirlendi | Hukuk görüşü | Hukuk | **Tüm hub'lar için engelleyici** |
| K5 | Kimlik | TR provider ID ve EMAID öneki (TR-03) | Seçilen ID'nin kullanılabileceği teyit edildi | Hubject soru 5, mevzuat teyidi | Mevzuat | **Tüm hub'lar için engelleyici** |
| K6 | Ticari | Hub ücretleri ve asgari süre | İlk yıl toplam hub maliyeti ≤ [tutar bu kopyada yayımlanmaz] (iki hub toplamı olarak yorumlandı); asgari süre ≤ 12 ay | Yazılı teklif | BD + Finans | Hub başına, toplam sınırla |
| K7 | Finans | Türk tüzel kişiyle sözleşme, fatura para birimi, vergi (TR-04) | Sözleşme mümkün; EUR ödeme yolu var | Hub yanıtı, muhasebe | Finans | Hub başına |
| K8 | Fiyat | Misafir fiyat formülüyle (ADR-0006) rekabet | Ortalama misafir fiyat ≤ doğrudan kart fiyatı + %15; marj ≤ %20 (TR-06 doğrulanana kadar) | B2B tarifeler, haftalık kart fiyatı taraması (CP-PRICE-003) | Ürün | Karar 3 için |
| K9 | Teknik | Ortak katman hazır (kanonik model, mock hub'lar, hata enjeksiyonu) | Mock hub'larla `@happy` ve `@error` senaryoları yeşil | CI çıktısı, traceability.csv | Mühendislik | Sözleşme imzası için değil, takvim için |

## Karar kuralları

Kurallar sırayla uygulanır; ilk eşleşen kural geçerlidir.

1. **K4 veya K5 başarısız** → hiçbir hub sözleşmesi imzalanmaz. Mühendislik mock'larla devam eder. K4 yalnız yeniden satış maddesinde olumsuzsa Karar 3 E'ye (acente modeli) geçer ve K4 yeniden değerlendirilir.
2. **Hubject GO** = K1-H + K6 + K7 geçti → Hubject sözleşmesi imzalanır, ~3 aylık onboarding başlar.
3. **GIREVE PNCP GO** = K2 + K3 + K6 + K7 geçti → PNCP sözleşmesi imzalanır, ön üretimden sertifikasyona geçilir.
4. **K1-H başarısız, K2 geçti** → yalnız PNCP. Roaming kapsamı ikili OCPI ile sağlanır.
5. **K1-H ve K2 başarısız** → **E: hub'sız pilot.** Koridor ikili OCPI + misafir akışıyla açılır; hub'lar Faz 5'e kalır.
5a. **K1 (koridor toplamı) başarısız** → pilot kapsamı daraltılır (önce A2 + A4, yani Söke–Didim–Milas–Bodrum); navigasyon ve bekleme optimizasyonu yine önceliklidir.
6. **GIREVE roaming (BOOST!)** → kapıda karar verilmez, Faz 5'te Avrupa'ya giden Türk sürücüler için değerlendirilir.
7. **e-clearing.net** → Faz 5 (ADR-0004).

Plug&Charge üretim hub'ı kuralı (ADR-0003): K2'de hangi CCP pilot CPO'lara ulaşıyorsa o hub seçilir; ikisi de ulaşıyorsa K6'da ucuz olan.

## Ara kontrol (9 Kasım 2026)

| Kontrol | Beklenen | Yoksa |
|---|---|---|
| Hubject ve GIREVE yanıt verdi mi | Tanışma görüşmesi tarihi var | Hatırlatma; GIREVE için ikinci kanal olarak LinkedIn veya etkinlik |
| Hukuk görüşü (TR-01) başladı mı | Avukat atandı, soru listesi iletildi | Kapı tarihi riskte; rapor edilir |
| ZES ile temas | Görüşme planlandı | ZES'e Hubject üzerinden ulaşmayı deneyin |
| Ortak katman | Kanonik model ve ilk mock hub çalışıyor | Kapsam daraltılır (önce OICP mock) |

## Kapı çıktısı

Kapı toplantısında tek sayfalık karar notu yazılır: her ölçüt için geçti / kaldı / bilinmiyor, uygulanan kural ve sonucu. Not `analysis/` altına `gate-2026-12-07.md` olarak eklenir; ADR-0005 ve ADR-0006 gerekirse güncellenir.

## Güncelleme 25 Ekim 2026: koridor kapsamı ve operasyonel KPI'lar

Pilot kapsamı İstanbul–Bodrum ana güzergâhı ve dört alternatif ailesine genişletildi (`scope.md`). Ürün sahibinin verdiği eşikler K1, K3, K6 ve K8'e işlendi; K2, K4, K5, K7 ve K9 değişmedi, K4 ve K5 engelleyici kalıyor.

İki düzeltme yapıldı:

1. **K1 ikiye ayrıldı.** Yeni K1 tüm kanalları (hub, ikili OCPI, misafir) sayıyor. Bu yüzden "Hubject GO" kuralı artık Hubject'e özgü bir ölçüte (K1-H) bakıyor; aksi halde ikili OCPI kapsamı Hubject sözleşmesini gerekçelendirirdi. K1-H eşiği sizin onayınızı bekliyor.
2. **K6 toplam sınır olarak yorumlandı.** Tavan tutarı iki hubun ilk yıl toplamı olarak okundu. Hub başına sınır isteniyorsa değiştirin.

Pilot sonrası izlenecek operasyonel KPI'lar (ortalama bekleme ≤ 8 dk / yoğun ≤ 15 dk, yolculuk süresi sapması ≤ %12, PnC başarı ≥ %85, alternatif sapma ≥ %20, misafir dönüşüm ≥ %40, güç paylaşımı düşüşü ≤ %25, veri kapsama ≥ %70) formülleriyle `kpis.md` içinde. Ara kontrolde (9 Kasım) yalnız ölçüm altyapısı ve K1 sayımı kontrol edilir.
