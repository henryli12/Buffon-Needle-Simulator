import math
import matplotlib.pyplot as plt

def factorial(x):
    if x == 0:
        return 1
    value = 1
    while x > 0:
        value *= x
        x -= 1
    return value

def poisson(t, l, n):
    top = (l*t)**n
    bot = factorial(n)
    right = math.e ** (-1 * l * t)
    return top / bot * right

def getValues(x, y, l, n):
    t = 0
    iterations = 1000
    step = 10/iterations
    for i in range(iterations):
        x.append(t)
        p = poisson(t,l,n)
        y.append(p)
        t += step
    return


if __name__ == "__main__":
    xValues0 = []
    yValue0 = []
    getValues(xValues0, yValue0, 2, 0)
    xValues1 = []
    yValue1 = []
    getValues(xValues1, yValue1, 2, 1)
    xValues2 = []
    yValue2 = []
    getValues(xValues2, yValue2, 2, 2)
    xValues3 = []
    yValue3 = []
    getValues(xValues3, yValue3, 2, 3)
    plt.plot(xValues0,yValue0)
    plt.plot(xValues1,yValue1)
    plt.plot(xValues2, yValue2)
    plt.plot(xValues3, yValue3)
    plt.show()