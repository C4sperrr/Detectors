Python Tarafında Sensör Veri Okuma
Python tarafında, pyserial kütüphanesini kullanarak Arduino'dan gelen seri veriyi okuyacağız.

Gerekli Kütüphane:

pyserial: Python ile seri port iletişimi için kullanılır. Yüklü değilse: pip install pyserial

##Örnek Python Kodu:

import serial
import time

# Arduino'nun bağlı olduğu seri portu ve baud hızını belirt
# Port ismi işletim sistemine göre değişebilir (örn. 'COM3' Windows'ta, '/dev/ttyUSB0' Linux'ta)
SERIAL_PORT = 'COM3' # Kendi portuna göre ayarla!
BAUD_RATE = 9600

try:
    # Seri port bağlantısını aç
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Arduino'nun başlatılması için kısa bir bekleme süresi

    print(f"Seri port '{SERIAL_PORT}' başarıyla açıldı.")

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip() # Seri porttan bir satır oku ve decode et
            print(f"Alınan Veri: {line}")

            # Alınan veriyi parçala ve işle (örn. "Sicaklik:25.50,Nem:60.20")
            try:
                parts = line.split(',')
                data = {}
                for part in parts:
                    key_value = part.split(':')
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = float(key_value[1].strip())
                        data[key] = value

                if "Sicaklik" in data and "Nem" in data:
                    temperature = data["Sicaklik"]
                    humidity = data["Nem"]
                    print(f"Sıcaklık: {temperature}°C, Nem: {humidity}%")

                    # Burada sensör verilerini işleyebilir, kaydedebilir veya görselleştirebilirsin
                    # Örn: if temperature > 30: print("Sıcaklık çok yüksek!")

            except ValueError as e:
                print(f"Veri ayrıştırma hatası: {e} - Hatalı satır: {line}")
            except Exception as e:
                print(f"Genel hata: {e}")

        time.sleep(0.1) # CPU kullanımını azaltmak için kısa bir bekleme süresi

except serial.SerialException as e:
    print(f"Seri port hatası: {e}. Portun doğru olduğundan ve kullanılmadığından emin ol.")
except KeyboardInterrupt:
    print("Program kullanıcı tarafından sonlandırıldı.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Seri port kapatıldı.")


##Kodu Açıklama:
import serial: pyserial kütüphanesini dahil ediyoruz.
SERIAL_PORT = 'COM3': Bu satırı, Arduino'nun bilgisayarına bağlandığı doğru seri portla değiştirmelisin. Windows'ta "Aygıt Yöneticisi"nden (Portlar altında), Linux/macOS'ta ls /dev/tty* komutunu kullanarak bulabilirsin.
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1): Seri port bağlantısını açar. timeout parametresi, okuma işlemlerinin ne kadar süre bekleyeceğini belirtir.
ser.readline().decode('utf-8').strip(): Arduino'dan gelen bir satır veriyi okur, UTF-8 olarak çözer ve başındaki/sonundaki boşlukları kaldırır.
Veri Ayrıştırma: Alınan string ("Sicaklik:25.50,Nem:60.20") virgülle (',') parçalara ayrılır, ardından her parça iki nokta üst üste (':') ile anahtar ve değere ayrılır. Sayısal değerler float'a dönüştürülür.

Diğer Sensörler İçin Uygulama
PIR Hareket Sensörü: Arduino tarafında PIR sensörünün dijital çıkışını (HIGH/LOW) okuyup seri porttan "Hareket Algılandı" veya "Hareket Yok" gibi mesajlar gönderebilirsin. Python tarafında bu mesajları kontrol edersin.
MQ-2 Gaz Sensörü: Gaz sensörleri genellikle analog veri verir. Arduino'nun analogRead() fonksiyonu ile sensörden gelen voltaj değerini okuyup bu değeri Python'a gönderebilirsin. Python tarafında bu değeri gaz yoğunluğuna çevirebilirsin.
