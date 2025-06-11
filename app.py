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



##Veri İşleme ve Analiz Modülü
Sensörlerden gelen ham veriler genellikle gürültülü veya tutarsız olabilir. Bu modülün amacı, bu ham verileri temizlemek, anlamlı hale getirmek ve belirlenen eşiklere veya basit istatistiksel analizlere göre "olayları" tanımlamaktır. Aşağıda Python kullanarak bu işlevleri nasıl uygulayacağına dair örnekler bulacaksın.

1. Ham Sensör Verilerini Temizleme, Filtreleme ve Normalleştirme
Sensör verilerinin kalitesini artırmak için çeşitli ön işleme teknikleri kullanabiliriz.

Temizleme: Eksik veya hatalı verileri (örn. NaN değerler) kaldırma veya doldurma.
Filtreleme: Gürültüyü azaltmak için hareketli ortalama gibi yöntemler kullanma.
Normalleştirme: Farklı sensörlerden gelen verileri ortak bir ölçeğe getirme (örn. 0-1 aralığına).

##Örnek Python Kodu:
import pandas as pd
import numpy as np

class SensorDataProcessor:
    def __init__(self):
        pass

    def clean_data(self, df):
        """
        DataFrame'deki NaN değerleri önceki geçerli değerlerle doldurur.
        İhtiyaca göre farklı temizleme stratejileri eklenebilir (örn. ortalama ile doldurma).
        """
        if isinstance(df, pd.Series):
            df = df.fillna(method='ffill')
            df = df.fillna(method='bfill') # Eğer ilk değer NaN ise
        elif isinstance(df, pd.DataFrame):
            df = df.fillna(method='ffill')
            df = df = df.fillna(method='bfill') # Eğer ilk değerler NaN ise
        return df

    def apply_moving_average_filter(self, series, window_size=5):
        """
        Bir Pandas Serisi'ne hareketli ortalama filtresi uygular.
        Gürültüyü azaltmak için kullanılır.
        """
        return series.rolling(window=window_size, min_periods=1).mean()

    def normalize_data(self, series):
        """
        Veri Serisi'ni Min-Max normalizasyonu kullanarak 0-1 aralığına ölçekler.
        """
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val: # Tüm değerler aynıysa sıfıra bölme hatasını önle
            return pd.Series([0.0] * len(series), index=series.index)
        return (series - min_val) / (max_val - min_val)

    def process_sensor_data(self, data_series, window_size=5):
        """
        Ham sensör verilerini temizleme, filtreleme ve normalleştirme işlemlerini sırayla uygular.
        """
        # Veriyi Pandas Serisi'ne dönüştür
        if not isinstance(data_series, pd.Series):
            data_series = pd.Series(data_series)

        # 1. Temizleme
        cleaned_data = self.clean_data(data_series)
        print(f"Temizlenmiş veri (ilk 5): {cleaned_data.head()}")

        # 2. Filtreleme
        filtered_data = self.apply_moving_average_filter(cleaned_data, window_size)
        print(f"Filtrelenmiş veri (ilk 5): {filtered_data.head()}")

        # 3. Normalleştirme
        normalized_data = self.normalize_data(filtered_data)
        print(f"Normalleştirilmiş veri (ilk 5): {normalized_data.head()}")

        return normalized_data
