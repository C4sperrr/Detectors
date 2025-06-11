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


Kullanıcı Arayüzü

1. Konsol Tabanlı Arayüz
En basit kullanıcı arayüzü, verileri doğrudan konsola yazdırmaktır. Bu, özellikle hata ayıklama ve projenin başlangıç aşamalarında hızlı geri bildirim almak için kullanışlıdır.

Önceki bölümlerdeki SensorDataProcessor ve EventDetector sınıflarını varsayarak, ana döngüde bu çıktıları nasıl gösterebileceğine dair bir örnek:

import serial
import time
import pandas as pd
import numpy as np # SensorDataProcessor için gerekli

# Önceki bölümlerden SensorDataProcessor ve EventDetector sınıflarını buraya kopyala veya import et
# Basitlik adına burada doğrudan tanımlıyorum:

class SensorDataProcessor:
    def clean_data(self, df):
        if isinstance(df, pd.Series):
            df = df.fillna(method='ffill')
            df = df.fillna(method='bfill')
        elif isinstance(df, pd.DataFrame):
            df = df.fillna(method='ffill')
            df = df.fillna(method='bfill')
        return df

    def apply_moving_average_filter(self, series, window_size=5):
        return series.rolling(window=window_size, min_periods=1).mean()

    def normalize_data(self, series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([0.0] * len(series), index=series.index)
        return (series - min_val) / (max_val - min_val)

    def process_sensor_data(self, data_series, window_size=5):
        if not isinstance(data_series, pd.Series):
            data_series = pd.Series(data_series)
        cleaned_data = self.clean_data(data_series)
        filtered_data = self.apply_moving_average_filter(cleaned_data, window_size)
        normalized_data = self.normalize_data(filtered_data)
        return normalized_data

class EventDetector:
    def detect_temperature_event(self, current_temperature, threshold_high=28.0, threshold_low=10.0):
        if current_temperature > threshold_high:
            return "YuksekSicaklikAlarm", f"Sıcaklık eşiği aşıldı: {current_temperature}°C"
        elif current_temperature < threshold_low:
            return "DusukSicaklikAlarm", f"Sıcaklık çok düşük: {current_temperature}°C"
        return None, None

    def detect_motion_event(self, current_motion_value, motion_threshold=0.5):
        if current_motion_value > motion_threshold:
            return "HareketAlgilandi", "Hareket algılandı!"
        return None, None

    def detect_gas_event(self, current_gas_level, safe_threshold=0.3):
        if current_gas_level > safe_threshold:
            return "GazSizintisiAlarm", f"Tehlikeli gaz seviyesi algılandı: {current_gas_level}"
        return None, None

    def monitor_data_stream(self, processed_data_dict):
        events = []
        # Not: Burada tek bir EventDetector instance'ı kullanıyoruz
        # Eğer bu sınıfın metotları statik olsaydı self. yerine EventDetector.method() kullanabilirdik.
        # Basitlik adına, doğrudan metotları çağırıyorum.
        
        if "Sicaklik" in processed_data_dict:
            event_type, message = self.detect_temperature_event(processed_data_dict["Sicaklik"])
            if event_type:
                events.append({'type': event_type, 'message': message, 'value': processed_data_dict["Sicaklik"]})
        
        if "Hareket" in processed_data_dict:
            # Hareket sensörü genellikle 0 veya 1 döndürür. Normalleştirme sonrası 0-1 aralığında olacaktır.
            event_type, message = self.detect_motion_event(processed_data_dict["Hareket"])
            if event_type:
                events.append({'type': event_type, 'message': message, 'value': processed_data_dict["Hareket"]})
        
        if "Gaz" in processed_data_dict:
            event_type, message = self.detect_gas_event(processed_data_dict["Gaz"])
            if event_type:
                events.append({'type': event_type, 'message': message, 'value': processed_data_dict["Gaz"]})
                
        return events


# Seri port ayarları
SERIAL_PORT = 'COM3'  # Kendi portuna göre ayarla!
BAUD_RATE = 9600

processor = SensorDataProcessor()
detector = EventDetector()

def run_console_interface():
    ser = None
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Seri port '{SERIAL_PORT}' başarıyla açıldı. Veriler okunuyor...")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(f"\nHam Veri: {line}")

                processed_data_dict = {}
                try:
                    parts = line.split(',')
                    for part in parts:
                        key_value = part.split(':')
                        if len(key_value) == 2:
                            key = key_value[0].strip()
                            value = float(key_value[1].strip())
                            
                            # Burada işleme mantığını uygula
                            # Tek bir değer için basit işleme yapılıyor, daha karmaşık senaryolar için bir geçmiş tutulmalı
                            # Örnek: sıcaklık için hareketli ortalama, ama tek değer için etkisi sınırlı.
                            processed_value_series = processor.process_sensor_data(pd.Series([value]), window_size=1)
                            processed_data_dict[key] = processed_value_series.iloc[-1] # En son işlenmiş değeri al
                            
                            print(f"  -> İşlenmiş {key}: {processed_data_dict[key]:.2f}")

                    # Olay tespiti
                    detected_events = detector.monitor_data_stream(processed_data_dict)
                    if detected_events:
                        for event in detected_events:
                            print(f"*** [OLAY] {event['type']}: {event['message']} ***")

                except ValueError as e:
                    print(f"Veri ayrıştırma hatası: {e} - Hatalı satır: {line}")
                except Exception as e:
                    print(f"Genel hata işleme: {e}")

            time.sleep(0.1)

    except serial.SerialException as e:
        print(f"Hata: Seri port açılamadı '{SERIAL_PORT}'. {e}")
        print("Lütfen portun doğru olduğundan ve başka bir uygulama tarafından kullanılmadığından emin olun.")
    except KeyboardInterrupt:
        print("Program kullanıcı tarafından sonlandırıldı.")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Seri port kapatıldı.")

# run_console_interface() # Konsol arayüzünü çalıştırmak için bu satırı etkinleştir

Konsol Arayüzünün Çalışma Mantığı:

Arduino'dan gelen ham veri satırını okur.
Her bir sensör verisini (örn. "Sicaklik", "Nem") ayrıştırır.
SensorDataProcessor kullanarak her bir sensör verisini (örneğin sadece temizleme ve normalleştirme) işler.
EventDetector kullanarak işlenmiş verilere göre olayları tespit eder.
Hem işlenmiş sensör değerlerini hem de algılanan olayları konsola yazdırır.

2. Basit Grafiksel Kullanıcı Arayüzü (Tkinter)
Tkinter, Python'ın standart GUI kütüphanesidir ve basit arayüzler oluşturmak için oldukça uygundur. Bu örnekte, sıcaklık ve hareket durumunu gösteren etiketler ile algılanan olayları listeleyen bir metin alanı kullanacağız.

import tkinter as tk
from tkinter import scrolledtext
import threading
import serial
import time
import pandas as pd
import numpy as np

# Önceki bölümlerden SensorDataProcessor ve EventDetector sınıflarını buraya kopyala veya import et
# (Yukarıdaki konsol örneğindeki gibi bu dosya içinde tanımlandığını varsayıyorum)

# Seri port ayarları
SERIAL_PORT = 'COM3'  # Kendi portuna göre ayarla!
BAUD_RATE = 9600

processor = SensorDataProcessor()
detector = EventDetector()

class SensorApp:
    def __init__(self, master):
        self.master = master
        master.title("Dedektör Sistemi")

        self.is_running = True
        self.serial_port = None
        
        # UI Bileşenleri
        self.lbl_temp = tk.Label(master, text="Sıcaklık: N/A", font=("Helvetica", 16))
        self.lbl_temp.pack(pady=10)

        self.lbl_motion = tk.Label(master, text="Hareket Durumu: N/A", font=("Helvetica", 16))
        self.lbl_motion.pack(pady=10)

        self.events_label = tk.Label(master, text="Algılanan Olaylar:", font=("Helvetica", 14))
        self.events_label.pack(pady=5)

        self.events_text = scrolledtext.ScrolledText(master, width=50, height=10, font=("Helvetica", 12))
        self.events_text.pack(pady=10)
        self.events_text.config(state=tk.DISABLED) # Kullanıcının yazmasını engelle

        self.status_label = tk.Label(master, text="Durum: Bağlantı bekleniyor...", font=("Helvetica", 10), fg="blue")
        self.status_label.pack(pady=5)

        self.btn_exit = tk.Button(master, text="Çıkış", command=self.on_closing, font=("Helvetica", 12))
        self.btn_exit.pack(pady=10)

        # Seri port okuma işlemini ayrı bir thread'de başlat
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()

    def update_ui(self, temp=None, motion=None, events=None):
        if temp is not None:
            self.lbl_temp.config(text=f"Sıcaklık: {temp:.2f}°C")
        if motion is not None:
            status = "Algılandı" if motion > 0.5 else "Yok" # Normalleştirilmiş değer için
            self.lbl_motion.config(text=f"Hareket Durumu: {status}")
        
        if events:
            self.events_text.config(state=tk.NORMAL)
            for event in events:
                self.events_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {event['type']}: {event['message']}\n")
            self.events_text.yview(tk.END) # En alta kaydır
            self.events_text.config(state=tk.DISABLED)

    def read_serial_data(self):
        try:
            self.serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
            self.status_label.config(text=f"Durum: '{SERIAL_PORT}' bağlı.", fg="green")

            while self.is_running:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    # print(f"Raw: {line}") # Debug
                    
                    processed_data_dict = {}
                    try:
                        parts = line.split(',')
                        current_temp = None
                        current_motion = None
                        
                        for part in parts:
                            key_value = part.split(':')
                            if len(key_value) == 2:
                                key = key_value[0].strip()
                                value = float(key_value[1].strip())
                                
                                # Veri işleme (tek bir değer için basit)
                                processed_value_series = processor.process_sensor_data(pd.Series([value]), window_size=1)
                                processed_value = processed_value_series.iloc[-1]
                                
                                processed_data_dict[key] = processed_value
                                
                                if key == "Sicaklik":
                                    current_temp = processed_value
                                elif key == "Hareket":
                                    current_motion = processed_value
                        
                        # Olay tespiti
                        detected_events = detector.monitor_data_stream(processed_data_dict)
                        
                        # UI güncellemesini ana thread'de yap (thread safe)
                        self.master.after(0, self.update_ui, current_temp, current_motion, detected_events)

                    except ValueError as e:
                        print(f"Veri ayrıştırma hatası (thread): {e} - Satır: {line}")
                    except Exception as e:
                        print(f"Genel hata (thread): {e}")
                
                time.sleep(0.1) # CPU kullanımını azalt

        except serial.SerialException as e:
            self.status_label.config(text=f"Hata: Seri port açılamadı. {e}", fg="red")
            print(f"Seri port hatası: {e}")
        except Exception as e:
            self.status_label.config(text=f"Uygulama hatası: {e}", fg="red")
            print(f"Uygulama hatası: {e}")
        finally:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                print("Seri port thread kapatıldı.")
            self.status_label.config(text="Durum: Bağlantı kesildi.", fg="red")


    def on_closing(self):
        self.is_running = False
        if self.serial_thread.is_alive():
            self.serial_thread.join(timeout=2) # Thread'in bitmesini bekle
        self.master.destroy() # GUI'yi kapat

# Uygulamayı başlat
if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.mainloop() # GUI'nin olay döngüsünü başlat

##Tkinter Arayüzünün Çalışma Mantığı:

1. SensorApp Sınıfı:
Ana pencereyi ve UI bileşenlerini (etiketler, kaydırılabilir metin alanı, düğme) oluşturur.
read_serial_data fonksiyonunu ayrı bir iş parçacığında (threading.Thread) başlatır. Bu önemlidir çünkü seri port okuma işlemi bloklayıcı olabilir ve GUI'nin donmasına neden olabilir.
on_closing metodu, pencere kapatıldığında iş parçacığını güvenli bir şekilde sonlandırmak için çağrılır.

2. read_serial_data Metodu (Ayrı Thread):
Seri portu açar ve sürekli olarak veri okur.
Okunan veriyi ayrıştırır ve SensorDataProcessor ile işler.
EventDetector ile olayları tespit eder.
self.master.after(0, self.update_ui, ...): Burası kritik! GUI güncellemelerinin ana iş parçacığında (main thread) yapılması gerekir. after() metodu, belirtilen fonksiyonu (burada update_ui) ana iş parçacığında belirli bir gecikmeden sonra (0ms yani hemen) çalıştırmasını sağlar.

3. update_ui Metodu (Ana Thread):
lbl_temp ve lbl_motion etiketlerini günceller.
events_text kaydırılabilir metin alanına algılanan olayları ekler ve otomatik olarak en alta kaydırır.
Metin alanına kullanıcının yazmasını engellemek için config(state=tk.DISABLED) kullanılır.

Kurulum ve Çalıştırma:

1. pyserial ve pandas: Bu kütüphanelerin kurulu olduğundan emin ol: pip install pyserial pandas numpy

2. Arduino Kodu: Arduino'na yukarıdaki DHT11 örneğindeki seri veri gönderen kodu yükle.

3. Seri Port Ayarı: Python kodundaki SERIAL_PORT = 'COM3' kısmını, Arduino'nun bağlı olduğu seri port adıyla değiştir.

4. Çalıştırma: Python dosyasını çalıştır.
