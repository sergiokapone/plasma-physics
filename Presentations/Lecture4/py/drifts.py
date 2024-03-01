import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


class Body:
    def __init__(self, w, v, v0, y0, p):
        self.w = w
        self.v = v
        self.v0 = v0
        self.y0 = y0
        self.p = p

    def x(self, t):
        return (
            self.v0 / self.w * (np.sin(self.p) - np.sin(self.w * t + self.p))
            + self.v * t
        )

    def y(self, t):
        return self.y0 + self.v0 / self.w * (
            np.cos(self.w * t + self.p) - np.cos(self.p)
        )


if __name__ == "__main__":
    fig, ax = plt.subplots()
    plt.title("Trajectories of particles")

    ax.set_xlim(0, 10)
    ax.set_ylim(-2, 2)
    ax.set_aspect("equal")

    # Создаем список частиц с разными параметрами p
    particles = [
        Body(w=-2, v=0.3, v0=1, p=np.radians(angle), y0=0)
        for angle in range(0, 360, 30)
    ]

    # Creating blank graphics for animation
    particle_plots = [ax.plot([], [], "bo")[0] for _ in particles]

    # Graphs for trajectories
    t_values = np.linspace(0, 100, 500)
    trajectory_plots = [
        ax.plot([], [], label=f"Trajectory {i}", alpha=0.7)[0]
        for i in range(len(particles))
    ]

    # Adding a legend
    # ax.legend()

    # Animation initialization function
    def init():
        for plot in particle_plots + trajectory_plots:
            plot.set_data([], [])
        return particle_plots + trajectory_plots

    # Animation refresh function
    def update(frame):
        for i, particle in enumerate(particles):
            t = frame * 0.1
            particle_plots[i].set_data(particle.x(t), particle.y(t))

            # Обновляем траектории
            x_values = [particle.x(t) for t in t_values]
            y_values = [particle.y(t) for t in t_values]
            trajectory_plots[i].set_data(x_values, y_values)

        return particle_plots + trajectory_plots

    ani = FuncAnimation(fig, update, frames=500, init_func=init, blit=True)

    # ani.save("particle_trajectories.gif", writer="imagemagick", fps=30)
    plt.show()
