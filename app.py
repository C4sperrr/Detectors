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

##Örnek Kullanım:
# Örnek ham sıcaklık verisi (NaN değerler ve gürültü içeriyor)
raw_temperature_data = [22.1, 22.3, np.nan, 22.8, 23.0, 22.9, 28.5, 23.2, 23.1, 23.0]
processor = SensorDataProcessor()
processed_temp_data = processor.process_sensor_data(raw_temperature_data, window_size=3)

# Örnek ham hareket sensörü verisi (0 ve 1'lerden oluşan, gürültülü olabilir)
# Genellikle hareket sensörleri zaten temiz dijital veri verir, ancak burada örnek amaçlı gürültü ekleyelim.
raw_motion_data = [0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0]
# Motion sensörleri için normalizasyon ve filtreleme genellikle anlamsızdır,
# ancak temizleme fonksiyonu yine de kullanılabilir (örneğin -1 gibi hatalı değerler için).
# processor.clean_data(pd.Series(raw_motion_data))

2. Eşik Değer Tabanlı veya Basit İstatistiksel Analizlerle Olay Tanımlama
Veriler temizlenip işlendikten sonra, belirli koşullar altında "olayları" tespit edebiliriz.

class EventDetector:
    def __init__(self):
        pass

    def detect_temperature_event(self, current_temperature, threshold_high=28.0, threshold_low=10.0):
        """
        Sıcaklık eşik değerlerine göre olayları algılar.
        """
        if current_temperature > threshold_high:
            return "YuksekSicaklikAlarm", f"Sıcaklık eşiği aşıldı: {current_temperature}°C"
        elif current_temperature < threshold_low:
            return "DusukSicaklikAlarm", f"Sıcaklık çok düşük: {current_temperature}°C"
        return None, None # Olay yok

    def detect_motion_event(self, current_motion_value, motion_threshold=0.5):
        """
        Hareket sensörü verisine göre hareket olayını algılar.
        Dijital sensörler için 0 veya 1 doğrudan kontrol edilebilir.
        Analog sensörler veya işlenmiş veriler için eşik kullanılabilir.
        """
        if current_motion_value > motion_threshold: # PIR için 1 ise hareket var
            return "HareketAlgilandi", "Hareket algılandı!"
        return None, None

    def detect_gas_event(self, current_gas_level, safe_threshold=0.3):
        """
        Gaz sensörü verisine göre gaz sızıntısı olayını algılar (normalleştirilmiş değerler için).
        """
        if current_gas_level > safe_threshold:
            return "GazSizintisiAlarm", f"Tehlikeli gaz seviyesi algılandı: {current_gas_level}"
        return None, None

    def monitor_data_stream(self, processed_data_stream):
        """
        Gelen işlenmiş veri akışını sürekli izler ve olayları raporlar.
        processed_data_stream: dictionary of sensor_name: value
        """
        events = []
        event_detector = EventDetector()

        for sensor_name, value in processed_data_stream.items():
            if sensor_name == "Sicaklik":
                event_type, message = event_detector.detect_temperature_event(value)
                if event_type:
                    events.append({'type': event_type, 'message': message, 'value': value})
            elif sensor_name == "Hareket":
                event_type, message = event_detector.detect_motion_event(value)
                if event_type:
                    events.append({'type': event_type, 'message': message, 'value': value})
            elif sensor_name == "Gaz":
                event_type, message = event_detector.detect_gas_event(value)
                if event_type:
                    events.append({'type': event_type, 'message': message, 'value': value})
            # Daha fazla sensör tipi eklenebilir

        return events

 ##Örnek Kullanım:

 event_detector = EventDetector()

# Tek bir sıcaklık değeri için olay tespiti
temp_value_1 = 29.1
event_type, message = event_detector.detect_temperature_event(temp_value_1)
if event_type:
    print(f"Olay: {event_type} - Mesaj: {message}")
else:
    print(f"Sıcaklık ({temp_value_1}°C) eşikler içinde.")

temp_value_2 = 25.0
event_type, message = event_detector.detect_temperature_event(temp_value_2)
if event_type:
    print(f"Olay: {event_type} - Mesaj: {message}")
else:
    print(f"Sıcaklık ({temp_value_2}°C) eşikler içinde.")


# Gerçek zamanlı akış simülasyonu
print("\nGerçek Zamanlı Veri Akışı İzleme:")
sample_data_stream_1 = {"Sicaklik": 27.5, "Nem": 0.65, "Hareket": 0.0, "Gaz": 0.2}
detected_events = event_detector.monitor_data_stream(sample_data_stream_1)
if detected_events:
    for event in detected_events:
        print(f"[{event['type']}] {event['message']} (Değer: {event['value']})")
else:
    print("Herhangi bir olay algılanmadı.")

sample_data_stream_2 = {"Sicaklik": 29.5, "Nem": 0.60, "Hareket": 1.0, "Gaz": 0.4}
detected_events = event_detector.monitor_data_stream(sample_data_stream_2)
if detected_events:
    for event in detected_events:
        print(f"[{event['type']}] {event['message']} (Değer: {event['value']})")
else:
    print("Herhangi bir olay algılanmadı.")

Entegrasyon Notları:
Veri Akışı: Yukarıdaki SensorDataProcessor sınıfını, Arduino'dan pyserial ile okuduğun verilere uygulayabilirsin. Okuduğun her sensör değerini SensorDataProcessor'ın process_sensor_data metoduna göndererek temizlenmiş, filtrelenmiş ve normalleştirilmiş halini alırsın.
Olay Tetikleme: İşlenmiş bu değerleri daha sonra EventDetector sınıfının ilgili metotlarına veya monitor_data_stream metoduna göndererek olayları algılayabilirsin.
Sürekli Çalışma: Bu modülleri, veri toplama modülünden gelen verileri sürekli dinleyen bir ana döngü (örneğin while True döngüsü) içinde kullanmalısın.


