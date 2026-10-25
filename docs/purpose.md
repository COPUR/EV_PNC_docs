> **Durum notu (25 Ekim 2026).** Pilot kapsamı Didim'den İstanbul–Bodrum koridoruna genişletildi ([kapsam](pilot/scope.md)) ve e-Devlet araç verisi entegrasyonu askıya alındı. Bu belge 24 Ekim sürümüdür ve değiştirilmemiştir; yeni sözler ürün sahibinin onayını bekliyor (kart R-02).

# Proje Amacı

## EV Charging & Payment Integration Platform  
**Türkiye Odaklı, Avrupa’ya Hazır Nötr Entegrasyon Katmanı**

**Proje Adı:** EV Charging Infrastructure & Seamless Payment Platform  
**Tarih:** 24 Ekim 2026  
**Versiyon:** 1.0  
**Durum:** Yeni Proje Başlangıcı  

---

## 1. Projenin Temel Amacı

Bu projenin amacı, Türkiye’de parçalanmış elektrikli araç (EV) şarj deneyimini birleştiren **nötr bir ara katman (intermediary / eMSP)** platformu geliştirmektir. Platform, sürücülerin araçlarını prize takar takmaz şarjın otomatik başlamasını ve ödemenin uçtan uca yetkilendirilmesini sağlar — ek uygulama üyeliği, kart okutma veya manuel işlem olmadan.

Platform **CPO (Charge Point Operator)** olarak istasyon işletmez ve **lisanslı ödeme kuruluşu** olarak fon tutmaz. Mevcut CPO’lar, ödeme sağlayıcıları ve sürücüler arasında entegrasyon sağlar.

### Temel Kullanıcı Vaadi
> Kabloyu tak, şarj başlasın, ödeme arka planda tamamlansın.

---

## 2. Stratejik Hedefler

| Hedef | Açıklama | Başarı Kriteri |
|-------|----------|----------------|
| **Seamless Plug&Charge** | ISO 15118 ile otomatik oturum başlatma ve ödeme | Kayıtlı kullanıcıda sıfır etkileşim |
| **Akıllı Navigasyon** | Dinamik programlama ile şarj durak optimizasyonu | SOC, hava, trafik, fiyat, politika entegrasyonu |
| **Türkiye Odaklı Başlangıç** | e-Devlet rıza, Masterpass, EPDK, KVKK uyumu | Didim / Ege turist koridorunda pilot başarı |
| **Misafir Deneyimi** | Tek seferlik kredi kartı + açık rıza (AD_HOC_USER) | Üyeliksiz, şeffaf ödeme akışı |
| **Politika Tabanlı Filtreleme** | Fiyat eşiği, operatör izin/engel listeleri | OCPI Token Authorization’da enforce |
| **Avrupa Hazırlığı** | OCPI 2.3.0, GIREVE / Hubject, AFIR uyumu | Tek entegrasyonla yüzlerce CPO’ya erişim |
| **Nötr Konum** | Ne CPO ne ödeme kuruluşu | Regülasyon ve operasyonel risk minimizasyonu |

---

## 3. Neden Bu Proje?

- Türkiye’de şarj deneyimi hâlâ parçalı (farklı uygulamalar, kartlar, fiyatlandırma).
- Plug&Charge yaygınlaşırken, entegre navigasyon + ödeme + politika yönetimi eksik.
- Turist yoğun bölgelerde (Didim vb.) yabancı sürücüler Avrupa standartlarına alışkın ancak yerel sürtünme yaşıyor.
- Avrupa’da AFIR (özellikle 1 Ocak 2027 temassız ödeme zorunluluğu) ve roaming hub’larının OCPI’ya geçişi fırsat yaratıyor.
- Girişimci olarak kendi oluşumunu kurma hedefiyle, teknik yetkinlik (yazılım geliştirme) bu alana odaklanabilir.

---

## 4. Kapsam Sınırları (Net)

**Kapsam içi:**
- Mobil uygulama + CarPlay / Android Auto
- OCPI tabanlı eMSP katmanı
- ISO 15118 Plug&Charge (Registration + Customization)
- EPDK telemetri + dinamik planlayıcı
- e-Devlet rıza + Masterpass entegrasyonu
- Misafir AD_HOC_USER akışı

**Kapsam dışı:**
- Şarj istasyonu işletmek (CPO)
- Ödeme kuruluşu olmak / fon tutmak
- Donanım üretmek

---

## 5. Fazlı Yol Haritası (Özet)

1. **Discovery & Tasarım** — Mimari, rıza akışları, partner eşleştirme
2. **Core Backend** — OCPI, EPDK, temel servisler
3. **Plug&Charge + Ödeme** — Sertifika yönetimi, politikalar, AD_HOC_USER
4. **Mobil + CarPlay + Planlayıcı** — Tam uygulama ve optimizasyon
5. **Didim Pilot** — Canlı test, geri bildirim, ticari sinyal
6. **Avrupa Hazırlığı** — GIREVE/Hubject, OCPI 2.3.0, AFIR
7. **Hardening & Lansman** — Ölçek, izleme, üretim

Detaylı RFP: `RFP_v2.md`

---

## 6. Başarı Ölçütleri (İlk 12–16 Ay)

- En az 1–2 CPO ile uçtan uca oturum (start → CDR → ödeme)
- Didim bölgesinde pilot kullanıcılarla ölçülebilir memnuniyet ve oturum sayısı
- Plug&Charge + politika filtrelemenin çalışması
- Avrupa roaming için teknik hazırlık (sertifikasyon yol haritası)
- KVKK ve ödeme uyumluluğu doğrulanmış

---

## 7. Sonraki Adımlar

- Bu amaç belgesini ve RFP’yi paydaşlarla (teknik, hukuki, ticari) gözden geçir
- Phase 0 Discovery için partner / vendor arama veya iç ekip planlaması
- e-Devlet, EPDK ve potansiyel CPO’larla erken temas

---

**Hazırlayan:** Proje başlatma notları (24 Ekim 2026)  
**İlgili belgeler:** RFP_EV_Charging_Platform_Turkey_Europe_v2.md
