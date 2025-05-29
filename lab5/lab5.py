import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import iirfilter, filtfilt

# Початкові параметри сигналу
t = np.linspace(0, 2 * np.pi, 500)  # часовий масив
A0, f0, phi0 = 1.0, 1.0, 0.0  # амплітуда, частота (Гц), фаза
noise_mean0, noise_var0 = 0.0, 0.0  # початкові середнє та дисперсія шуму
cutoff0 = 2.0  # початкова частота зрізу фільтру (Гц)
filter_order = 4  # порядок фільтру

y_clean = A0 * np.sin(2 * np.pi * f0 * t + phi0)
noise = np.random.normal(noise_mean0, np.sqrt(noise_var0), size=t.shape)
y_noisy = y_clean + noise

fs = 1 / (t[1] - t[0])  # частота дискретизації (Гц)
b, a = iirfilter(filter_order, cutoff0 / (fs / 2), btype='low')
y_filtered = filtfilt(b, a, y_noisy)

fig, (ax_wave, ax_filt) = plt.subplots(1, 2, figsize=(10, 6))
plt.subplots_adjust(bottom=0.4)

# Початкове відображення сигналів
line_wave, = ax_wave.plot(t, y_noisy, color='C0', label='Зашумлений сигнал')
ax_wave.plot(t, y_clean, color='C0', linestyle='--', label='Чистий сигнал')
ax_wave.set_title('Гармоніка')
ax_wave.legend()

line_filt, = ax_filt.plot(t, y_filtered, color='C1', label='Фільтрований сигнал')
ax_filt.set_title('Після фільтрації')
ax_filt.legend()

ax_amp = plt.axes((0.15, 0.35, 0.7, 0.03))
ax_freq = plt.axes((0.15, 0.30, 0.7, 0.03))
ax_phase = plt.axes((0.15, 0.25, 0.7, 0.03))
ax_noise_mean = plt.axes((0.15, 0.20, 0.7, 0.03))
ax_noise_var = plt.axes((0.15, 0.15, 0.7, 0.03))
ax_filter_cutoff = plt.axes((0.15, 0.10, 0.7, 0.03))

slider_amp = Slider(ax_amp, "A (амплітуда)", 0.1, 5.0, valinit=A0)
slider_freq = Slider(ax_freq, "f (Гц)", 0.1, 5.0, valinit=f0)
slider_phase = Slider(ax_phase, "Фаза (рад)", 0.0, 2 * np.pi, valinit=phi0)
slider_noise_mean = Slider(ax_noise_mean, "Шум: середнє", -1.0, 1.0, valinit=noise_mean0)
slider_noise_var = Slider(ax_noise_var, "Шум: дисперсія", 0.0, 1.0, valinit=noise_var0)
slider_filter = Slider(ax_filter_cutoff, "Фільтр: зріз f (Гц)", 0.1, 5.0, valinit=cutoff0)

ax_check = plt.axes([0.82, 0.45, 0.15, 0.15])
check = CheckButtons(ax_check, ['Шум', 'Фільтр'], [False, False])

for ax_slider in [ax_amp, ax_freq, ax_phase, ax_noise_mean, ax_noise_var, ax_filter_cutoff]:
    ax_slider.tick_params(axis='x', labelbottom=False)


def update(val):
    A = slider_amp.val
    f = slider_freq.val
    phi = slider_phase.val
    noise_mean = slider_noise_mean.val
    noise_var = slider_noise_var.val
    cutoff = slider_filter.val

    y_clean = A * np.sin(2 * np.pi * f * t + phi)
    if check.get_status()[0]:  # якщо чекбокс "Шум" активний
        noise = np.random.normal(noise_mean, np.sqrt(noise_var), size=t.shape)
    else:
        noise = np.zeros_like(t)
    y_noisy = y_clean + noise
    line_wave.set_ydata(y_noisy)

    fs = 1 / (t[1] - t[0])
    b, a = iirfilter(filter_order, cutoff / (fs / 2), btype='low')
    y_filtered = filtfilt(b, a, y_noisy)
    line_filt.set_ydata(y_filtered)

    if check.get_status()[1]:  # якщо чекбокс "Фільтр" активний
        line_filt.set_visible(True)
        ax_filt.set_title("Після фільтрації")
    else:
        line_filt.set_visible(False)
        ax_filt.set_title("Після фільтрації (відключено)")

    fig.canvas.draw_idle()


ax_reset = plt.axes([0.8, 0.02, 0.1, 0.04])
button = Button(ax_reset, 'Скинути')


def reset(event):
    slider_amp.reset()
    slider_freq.reset()
    slider_phase.reset()
    slider_noise_mean.reset()
    slider_noise_var.reset()
    slider_filter.reset()
    # Скидаємо чекбокси до початкового стану
    current = list(check.get_status())
    defaults = [False, False]
    for i, state in enumerate(current):
        if state != defaults[i]:
            check.set_active(i)
    update(None)


button.on_clicked(reset)

# Зв'язування оновлення з подіями віджетів
for s in [slider_amp, slider_freq, slider_phase, slider_noise_mean, slider_noise_var, slider_filter]:
    s.on_changed(update)
check.on_clicked(update)

plt.show()