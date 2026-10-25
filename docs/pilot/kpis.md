# Koridor pilotu: operasyonel KPI'lar

**Tarih:** 25 Ekim 2026 · **Durum:** hedefler ürün sahibince verildi; tanımlar, formüller ve ölçüm kuralları bu belgede.
**Kullanım:** ara kontrol (9 Kasım 2026) için yalnız ölçüm altyapısı; hedefler go/no-go kapısı (7 Aralık 2026) sonrası pilot iterasyonlarında izlenir.

## Genel ölçüm kuralları

- Her KPI iki dönem için ayrı raporlanır: **normal** ve **yoğun** (yaz sezonu 15 Haziran–15 Eylül ve bayram tatili ±2 gün). Dönem takvimi `CP-PEAK-001` ile yapılandırılır.
- Her KPI güzergâh ailesine göre (M, A1–A4) ve Oksijen kümeleri ayrı kırılır.
- Ölçüm birimi oturum ya da yolculuktur; birim her KPI'da yazılı. Yolculuk = uygulamada planlanıp başlatılan, varışla biten tek rota.
- "Sorun tespiti" için ilk 4 hafta temel çizgi (baseline) toplanır: öneriler gösterilir ama sıralama optimizasyonu kapalıdır (kontrol grubu). Sonra kullanıcıların [%50]'si optimizasyonlu gruba alınır. Karşılaştırma iki grup arasında yapılır (I: önerilen yöntem; oran ürün sahibince onaylanır).
- Kişisel veri: KPI'lar takma adlı yolculuk kimliğiyle hesaplanır; konum izi 90 gün sonra hücre düzeyine (H3 çözünürlük 8) indirgenir (`CP-KPI-004`).

## KPI tanımları

| Kod | KPI | Formül | Hedef (pilot) | Veri kaynağı | Not |
|---|---|---|---|---|---|
| KPI-1 | Ortalama bekleme süresi | Σ(şarj başlangıcı − istasyona varış) / oturum sayısı; varış = araç konumunun istasyona 75 m içine girmesi | ≤ 8 dk (yoğun ≤ 15 dk) | Uygulama konumu + OCPI Session başlangıcı + kullanıcı geri bildirimi | Oksijen kümeleri ayrı |
| KPI-2 | Toplam yolculuk süresi sapması | \|gerçekleşen − planlanan\| / planlanan; süre = sürüş + şarj + bekleme | ≤ %12 | Planlayıcı çıktısı + yolculuk izi | Navigasyon optimizasyonunun ana çıktısı |
| KPI-3 | PnC oturum başarı oranı | Başarılı PnC başlatma / PnC denemesi; deneme = PnC yetkili EVSE'de kablo takılması ve ISO 15118 el sıkışmasının başlaması | ≥ %85 (üretim ≥ %95) | CPO oturum verisi (OCPI Session, auth_method=AUTH_REQUEST / token type), PNCP / OPCP olayları, uygulama geri bildirimi | GIREVE PNCP + CCP seçimine bağlı |
| KPI-4 | Alternatif sapma kullanım oranı | Önerilen alternatifin seçildiği yolculuk / alternatif önerilen yolculuk | ≥ %20 (yoğun dönemde) | Planlayıcı olayları | B planı ve dayanıklılık |
| KPI-5 | Misafir dönüşüm oranı | Tamamlanan AD_HOC_USER oturumu / gösterilen misafir teklifi | ≥ %40 | Ödeme ve oturum olayları | K8 ile birlikte okunur |
| KPI-6 | Güç paylaşımı etkisi | 1 − (çoklu araçta ortalama güç / tek araçta ortalama güç), aynı EVSE grubu | Ortalama düşüş ≤ %25 | OCPI Session charging_periods + CDR | Model iyileştirme girdisi |
| KPI-7 | Veri kapsama | Canlı doluluk ve güç verisi gelen EVSE / K1 kapsamındaki EVSE; canlı = son 15 dk içinde durum güncellemesi | ≥ %70 | Veri temeli (`CP-DATA`) | Navigasyon kalitesi için kritik |

## İkincil göstergeler (hedefsiz, izlenir)

- PnC başlatma süresi: kablo takılması → enerji akışı (sn).
- PnC hata dağılımı: sertifika bulunamadı, süresi dolmuş, CCP erişimi yok, EVSE yazılımı, diğer.
- Kuyruk tahmini hatası: tahmini − gerçekleşen bekleme (dk), MAE.
- Fiyat farkı: misafir fiyatı − aynı EVSE'nin doğrudan kart fiyatı (TL/kWh).
- İşgaliye uyarısı sonrası boşaltma süresi (dk).

## Kapı kararlarıyla ilişki

- K1 veya K3 geçmezse yedek E (hub'sız + ikili OCPI) güçlenir; KPI-1, KPI-2, KPI-4 ve KPI-7 yine önceliklidir.
- KPI-3 yalnız K2 ve K3 geçerse ölçülür; geçmezse yalnız test tezgâhı ve yurt dışı oturumlarda raporlanır.
- KPI-5 ve ikincil fiyat farkı K8'in pilot içi doğrulamasıdır.
