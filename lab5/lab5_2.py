from bokeh.plotting import figure, show
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, CheckboxGroup, Button
import numpy as np
from scipy.signal import iirfilter, filtfilt

t = np.linspace(0, 2 * np.pi, 500)
A0, f0, phi0 = 1.0, 1.0, 0.0
noise_mean0, noise_var0 = 0.0, 0.0
cutoff0, filter_order = 2.0, 4

fs = 1 / (t[1] - t[0])
y_clean = A0 * np.sin(2 * np.pi * f0 * t + phi0)
y_noisy = y_clean.copy()
b, a = iirfilter(filter_order, cutoff0 / (fs / 2), btype='low')
y_filtered = filtfilt(b, a, y_noisy)

source = ColumnDataSource(data=dict(x=t, original=y_noisy, filtered=y_filtered))

plot_orig = figure(title="Гармоніка", width=700, height=400)
plot_orig.line('x', 'original', source=source, color="blue", legend_label="Сигнал")
plot_orig.legend.location = "top_left"

plot_filt = figure(title="Після фільтрації", width=700, height=400)
plot_filt.line('x', 'filtered', source=source, color="orange", legend_label="Фільтрований")
plot_filt.legend.location = "top_left"

amp_slider = Slider(start=0.1, end=5.0, value=A0, step=0.1, title="A (амплітуда)")
freq_slider = Slider(start=0.1, end=5.0, value=f0, step=0.1, title="f (Гц)")
phase_slider = Slider(start=0.0, end=2 * np.pi, value=phi0, step=0.1, title="Фаза (рад)")
mean_slider = Slider(start=-1.0, end=1.0, value=noise_mean0, step=0.1, title="Шум: середнє")
var_slider = Slider(start=0.0, end=1.0, value=noise_var0, step=0.1, title="Шум: дисперсія")
cutoff_slider = Slider(start=0.1, end=5.0, value=cutoff0, step=0.1, title="Фільтр: зріз f (Гц)")
checkbox = CheckboxGroup(labels=["Шум", "Фільтр"], active=[])
reset_button = Button(label="Скинути")


def update_data(attr, old, new):
    A = amp_slider.value
    f = freq_slider.value
    phi = phase_slider.value
    noise_mean = mean_slider.value
    noise_var = var_slider.value
    cutoff = cutoff_slider.value

    y_clean = A * np.sin(2 * np.pi * f * t + phi)
    if 0 in checkbox.active:  # шум увімкнено
        noise = np.random.normal(noise_mean, np.sqrt(noise_var), size=t.shape)
    else:
        noise = np.zeros_like(t)
    y_noisy = y_clean + noise

    b, a = iirfilter(filter_order, cutoff / (fs / 2), btype='low')
    y_filtered = filtfilt(b, a, y_noisy)

    source.data = dict(x=t, original=y_noisy, filtered=y_filtered)


def reset_callback():
    amp_slider.value = A0
    freq_slider.value = f0
    phase_slider.value = phi0
    mean_slider.value = noise_mean0
    var_slider.value = noise_var0
    cutoff_slider.value = cutoff0
    checkbox.active = []
    update_data(None, None, None)


for widget in [amp_slider, freq_slider, phase_slider, mean_slider, var_slider, cutoff_slider]:
    widget.on_change('value', update_data)
checkbox.on_change('active', update_data)
reset_button.on_click(reset_callback)

layout = column(
    row(plot_orig, plot_filt),
    row(amp_slider, freq_slider, phase_slider, mean_slider, var_slider, cutoff_slider),
    checkbox,
    reset_button
)

from bokeh.io import curdoc

curdoc().add_root(layout)
curdoc().title = "Інтерактивна гармоніка"
