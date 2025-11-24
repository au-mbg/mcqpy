from scipy.optimize import curve_fit

curve_fit(lambda x, a, b: a * x + b, xdata, ydata)