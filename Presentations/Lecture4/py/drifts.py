import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


class Body:
    def __init__(self, w, v, v0, x0, y0, p):
        self.w = w
        self.v = v
        self.v0 = v0
        self.y0 = y0
        self.x0 = x0
        self.p = p

    def x(self, t):
        return self.x0 + (
            self.v0 / self.w * (np.sin(self.p) - np.sin(self.w * t + self.p))
            + self.v * t
        )

    def y(self, t):
        return self.y0 + self.v0 / self.w * (
            np.cos(self.w * t + self.p) - np.cos(self.p)
        )


if __name__ == "__main__":
    N = int(input("Количество частиц: "))
    TRAIL_LENGTH = 80   # длина хвоста в кадрах
    DT = 0.1
    FRAMES = 500

    fig, ax = plt.subplots()
    plt.title("Trajectories of particles")

    ax.set_xlim(-5, 5)
    ax.set_ylim(-2, 2)
    ax.set_aspect("equal")

    X0 = 0.0   # начальная x-координата
    Y0 = 0.0   # начальная y-координата

    angles = np.linspace(0, 360, N, endpoint=False)
    particles = [
        Body(w=-2, v=0.3, v0=1, x0=X0, y0=Y0, p=np.radians(angle))
        for angle in angles
    ]

    colors = plt.cm.hsv(np.linspace(0, 1, N, endpoint=False))

    particle_plots = [
        ax.plot([], [], "o", color=colors[i], ms=6)[0]
        for i in range(N)
    ]
    trail_plots = [
        ax.plot([], [], "-", color=colors[i], alpha=0.6, lw=1.5)[0]
        for i in range(N)
    ]

    def init():
        for plot in particle_plots + trail_plots:
            plot.set_data([], [])
        return particle_plots + trail_plots

    def update(frame):
        t_now = frame * DT
        t_start = max(0.0, t_now - TRAIL_LENGTH * DT)
        t_trail = np.linspace(t_start, t_now, TRAIL_LENGTH)

        for i, particle in enumerate(particles):
            particle_plots[i].set_data([particle.x(t_now)], [particle.y(t_now)])
            trail_plots[i].set_data(
                [particle.x(t) for t in t_trail],
                [particle.y(t) for t in t_trail],
            )

        return particle_plots + trail_plots

    ani = FuncAnimation(fig, update, frames=FRAMES, init_func=init, blit=True)

    ani.save("particle_trajectories.gif", writer="imagemagick", fps=30)
    plt.show()