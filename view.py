import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import numpy as np

DEBUG = False

def start_progress_plot(title, count):
    print("Staring view %s with %d" % (title, count))
    if DEBUG:
        return
    x = np.arange(count)
    y = [0] * count
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    f = open(title, "w+")
    def animate(_):
        pullData = f.read()
        dataArray = pullData.split('\n')
        for x_var in dataArray:
            if len(x_var) > 0:
                y[int(x_var)] = 1
        ax1.clear()
        ax1.plot(x, y)
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.title(title)
    plt.show()

def add_progress(title, segment):
    print("Adding view progress %s : %d" % (title, segment))
    if DEBUG:
        return
    with open(title, 'a') as f:
        f.write('%d\n' % segment)
        f.flush()
