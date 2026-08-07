# TurKMedBench Public Data Card v1

Tarih: 2026-08-07

Durum: Araştırma adayı paketinin self contained veri kartı. Bu kart public release, klinik kullanım veya klinik doğruluk onayı değildir.

## Kısa tanım

TurKMedBench, Türkiye bağlamında klinik yapay zekâ sistemlerinin görev davranışını, güvenlik sınırlarını, belirsizlik iletişimini ve yerel uygulanabilirlik gereksinimlerini incelemek üzere tasarlanan çok branşlı bir araştırma benchmark'ıdır. Paket, klinisyen incelemesi için tasarlanmıştır; mevcut aday klinik olarak adjudicate edilmiş gold standard değildir.

## Aday kapsam

* 22 sentetik vaka.
* 11 branş: Kardiyoloji, Acil Tıp, Aile Hekimliği, Enfeksiyon Hastalıkları, İç Hastalıkları, Nöroloji, Tıbbi Onkoloji, Pediatri, Psikiyatri, Genel Cerrahi ve Kadın Hastalıkları veya Doğum.
* Vaka metinleri Türkiye bağlamını, sağlık sistemi yolunu, sevk yolunu, güvenlik sınırını ve yerel uygulanabilirlik boyutlarını taşır.
* Görev yüzeyleri triyaj, kırmızı bayrak tanıma, belirsizlik, güvenli eskalasyon, ilaç veya işlem sınırı, iletişim ve yerel kapasite doğrulamasını kapsar.

## Veri ve mahremiyet

* Tüm aday vakalar sentetiktir.
* Hasta düzeyi veri, doğrudan tanımlayıcı, gerçek klinik kayıt ve model çıktısı bu pakete dahil değildir.
* Beklenen yanıt, scoring key, kaynak ayrıntısı, reviewer kimliği, credential bilgisi ve adjudication kaydı bu pakete dahil değildir.
* Paket içindeki dosyalar başka bir veri kaynağıyla birleştirilerek gerçek hasta yönetimi üretmek için tasarlanmamıştır.

## Değerlendirme sınırı

Bu aday paket klinik doğruluk, model sıralaması, leaderboard, public metric, gerçek hasta performansı veya klinik kullanım iddiası taşımaz. İnsan klinisyen incelemesi gereklidir. Kaynak güncelliği, görev eşleşmeli quorum, güvenlik kararları ve anlaşmazlık çözümü ayrı kontrollü kapılardır.

## Yerel uygulanabilirlik

Yanıtlar Türkiye'deki kurum kapasitesi, sevk yolu, bakım düzeyi, ilaç erişimi, geri ödeme doğrulaması ve hasta iletişimi bağlamını kesin olmayan noktaları açıkça belirterek ele almalıdır. Yerel bir kurumun kapasitesi veya güncel uygulaması bu paket tarafından otomatik olarak varsayılmaz.

## Kullanım sınırı

Bu paket araştırma ve yöntem geliştirme içindir. Hasta bakımı, tedavi seçimi, ilaç dozu, işlem emri, transfüzyon kararı veya acil klinik yönlendirme için kullanılamaz. Lisans, atıf, katkı ve dış dağıtım kararları ayrıca verilmeden paket yayımlanmış sayılmaz.

## Yeniden üretilebilirlik

Paket dosyalarının bütünlüğü birlikte verilen SHA256 checksum listesiyle kontrol edilebilir. Dosya evreni değişirse paket yeniden üretilmeli ve önceki aday snapshot'ı yeni snapshot ile karıştırılmamalıdır.
