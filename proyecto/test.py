import serial
import time
import matplotlib.pyplot as plt

PORT = "COM7"      # cambia por tu puerto real
BAUD = 115200

print("Conectando con Arduino...")
arduino = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
arduino.reset_input_buffer()
print("Conectado correctamente")

# ==========================
# CALIBRACIÓN INICIAL
# ==========================

print("Calibrando MPU6050... no lo muevas")

az_samples = []

while len(az_samples) < 50:
    line = arduino.readline().decode("utf-8", errors="ignore").strip()
    datos = line.split(",")

    if len(datos) >= 3:
        try:
            az_samples.append(float(datos[1]))
        except:
            pass

az_ref = sum(az_samples) / len(az_samples)

print("Referencia AZ:", az_ref)
print("Iniciando gráfica...")

# ==========================
# VARIABLES
# ==========================

x = []
vib_raw = []
vib_filtered = []
servo_data = []

filtered = 0
alpha = 0.25

plt.ion()
fig, ax = plt.subplots(figsize=(12, 6))

i = 0

while True:
    line = arduino.readline().decode("utf-8", errors="ignore").strip()

    if "," not in line:
        continue

    datos = line.split(",")

    if len(datos) < 3:
        continue

    try:
        az = float(datos[1])
        servoPos = float(datos[2])

        # ==========================
        # VIBRACIÓN REAL DEL SENSOR
        # ==========================

        vibration = abs(az - az_ref)

        # Amplificación visual
        vibration_visual = vibration * 20

        # Señal filtrada / regulada visual
        filtered = alpha * vibration_visual + (1 - alpha) * filtered

        print(
            "AZ:", az,
            " Vib cruda:", vibration_visual,
            " Vib filtrada:", filtered,
            " Servo:", servoPos
        )

        x.append(i)
        vib_raw.append(vibration_visual)
        vib_filtered.append(filtered)
        servo_data.append(servoPos * 20)  # escala visual para verlo junto

        x = x[-100:]
        vib_raw = vib_raw[-100:]
        vib_filtered = vib_filtered[-100:]
        servo_data = servo_data[-100:]

        ax.clear()

        ax.plot(
            x,
            vib_raw,
            linewidth=2,
            label="Vibración MPU6050 cruda"
        )

        ax.plot(
            x,
            vib_filtered,
            linewidth=3,
            label="Vibración filtrada / regulada"
        )

        ax.plot(
            x,
            servo_data,
            linewidth=2,
            linestyle="--",
            label="Acción del servo x20"
        )

        ax.set_title("Regulación de vibración con MPU6050 y suspensión activa")
        ax.set_xlabel("Muestras")
        ax.set_ylabel("Amplitud visual")
        ax.grid(True)
        ax.legend(loc="upper right")

        ax.set_ylim(0, max(1000, max(vib_raw + vib_filtered + servo_data) * 1.2))

        plt.pause(0.1)

        i += 1

    except Exception as e:
        print("Error:", e)