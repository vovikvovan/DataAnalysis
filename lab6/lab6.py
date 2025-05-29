import numpy as np
import matplotlib.pyplot as plt

a = 2.5  # кутовий коефіцієнт
b = 1.0  # вільний член

np.random.seed(42)  # для відтворюваності результатів
x = np.linspace(0, 10, 50)  # 50 точок від 0 до 10
noise = np.random.normal(0, 1, size=x.shape)
y = a * x + b + noise  # значення y з шумом


def least_squares_fit(x, y):
    # Обчислюємо середні значення x та y
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    # Обчислюємо коефіцієнти для регресії
    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean)**2)
    beta1 = numerator / denominator
    beta0 = y_mean - beta1 * x_mean
    return beta0, beta1


beta0, beta1 = least_squares_fit(x, y)
print("Метод найменших квадратів (власна реалізація): β0 = {:.4f}, β1 = {:.4f}".format(beta0, beta1))


poly_slope, poly_intercept = np.polyfit(x, y, 1)  # повертає [slope, intercept]
print("Результати numpy.polyfit:")
print("β0 = {:.4f}, β1 = {:.4f}".format(poly_intercept, poly_slope))
print("Початкові параметри прямої: β0 = {:.4f}, β1 = {:.4f}".format(b, a))

plt.figure(figsize=(8, 6))
plt.scatter(x, y, color='blue', label='Згенеровані точки')

y_fit_own = beta1 * x + beta0
plt.plot(x, y_fit_own, color='red', linestyle='-', label='Регресія (власний метод)')

y_fit_poly = poly_slope * x + poly_intercept
plt.plot(x, y_fit_poly, color='green', linestyle='--', label='Регресія (numpy.polyfit)')

y_true = a * x + b
plt.plot(x, y_true, color='black', linestyle='-.', label='Початкова пряма')

plt.title('Регресія методом найменших квадратів')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.show()