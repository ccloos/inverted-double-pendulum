import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import imageio.v2 as imageio


WORKDIR = Path(__file__).resolve().parent
NOTEBOOK = WORKDIR / "double_inverted_pendulum.ipynb"
OUTPUT_GIF = WORKDIR / "double_pendulum_lqr_demo.gif"
OUTPUT_MP4 = WORKDIR / "double_pendulum_lqr_demo.mp4"


def load_notebook_symbols():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    ns = {}
    for idx in [6, 7, 8, 12]:
        cell = nb["cells"][idx]
        if cell.get("cell_type") != "code":
            continue
        exec(compile("".join(cell["source"]), f"<cell {idx}>", "exec"), ns)
    return ns


def fig_to_image(fig):
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    data = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(height, width, 4)
    image = Image.fromarray(data[..., :3], mode="RGB")
    plt.close(fig)
    return image


def draw_pendulum(ax, theta1, theta2, title, subtitle="", color="tab:blue"):
    l1 = 1.0
    l2 = 1.0
    x1 = l1 * np.sin(theta1)
    y1 = l1 * np.cos(theta1)
    x2 = x1 + l2 * np.sin(theta2)
    y2 = y1 + l2 * np.cos(theta2)

    ax.plot([0, 0], [0, 1.3], "--", color="gray", lw=1.5, alpha=0.7)
    ax.plot([0, x1, x2], [0, y1, y2], "o-", lw=4, color=color, markersize=8)
    ax.plot(x2, y2, "o", color="crimson", markersize=10)
    ax.set_xlim(-2.1, 2.1)
    ax.set_ylim(-2.1, 2.1)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    ax.set_title(title, fontsize=20, weight="bold")
    if subtitle:
        ax.text(0.5, -0.1, subtitle, ha="center", va="top", transform=ax.transAxes, fontsize=12)


def make_title_card():
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1.0])
    left = fig.add_subplot(gs[0, 0])
    right = fig.add_subplot(gs[0, 1])
    left.axis("off")
    left.text(
        0.02,
        0.85,
        "Double Pendulum Demo",
        fontsize=28,
        weight="bold",
        ha="left",
        va="top",
    )
    left.text(
        0.02,
        0.62,
        "This is a simulation of the double pendulum\n"
        "with unstable equilibrium at (0, 0, 0, 0).",
        fontsize=18,
        ha="left",
        va="top",
        linespacing=1.4,
    )
    left.text(
        0.02,
        0.34,
        "We first show the free system near the top position,\n"
        "then the same initial condition with LQR control.",
        fontsize=15,
        ha="left",
        va="top",
        linespacing=1.4,
    )
    draw_pendulum(
        right,
        theta1=0.55,
        theta2=-0.35,
        title="System Diagram",
        subtitle="Angles are measured from the upward vertical.",
        color="tab:blue",
    )
    fig.tight_layout()
    return fig_to_image(fig)


def make_text_card(title, body, footer=""):
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.05, 0.82, title, fontsize=28, weight="bold", ha="left", va="top")
    ax.text(0.05, 0.58, body, fontsize=18, ha="left", va="top", linespacing=1.5)
    if footer:
        ax.text(0.05, 0.14, footer, fontsize=14, ha="left", va="top", color="dimgray")
    return fig_to_image(fig)


def make_sim_frame(sol, frame_idx, title, caption, color):
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 0.85])
    ax_anim = fig.add_subplot(gs[0, 0])
    ax_info = fig.add_subplot(gs[0, 1])

    theta1 = sol["y"][0, frame_idx]
    theta2 = sol["y"][1, frame_idx]
    draw_pendulum(ax_anim, theta1, theta2, title=title, subtitle=f"t = {sol['t'][frame_idx]:.2f} s", color=color)

    ax_info.axis("off")
    ax_info.text(0.02, 0.88, caption, fontsize=18, ha="left", va="top", linespacing=1.5)
    ax_info.text(
        0.02,
        0.50,
        f"theta1 = {theta1:+.3f} rad\n"
        f"theta2 = {theta2:+.3f} rad\n"
        f"dtheta1 = {sol['y'][2, frame_idx]:+.3f} rad/s\n"
        f"dtheta2 = {sol['y'][3, frame_idx]:+.3f} rad/s",
        fontsize=15,
        ha="left",
        va="top",
        family="monospace",
    )
    if "u" in sol:
        ax_info.text(
            0.02,
            0.22,
            f"control torque = {sol['u'][frame_idx]:+.3f} Nm",
            fontsize=15,
            ha="left",
            va="top",
            family="monospace",
        )
    fig.tight_layout()
    return fig_to_image(fig)


def repeat_frame(image, count):
    return [image.copy() for _ in range(count)]


def sample_indices(length, count):
    if count <= 1:
        return np.array([0], dtype=int)
    return np.linspace(0, length - 1, count, dtype=int)


def main():
    ns = load_notebook_symbols()
    params = ns["DEFAULT_PARAMS"]
    K_demo, *_ = ns["lqr_gain"](params, [120.0, 150.0, 18.0, 20.0], 0.8)

    x0 = [0.10, -0.08, 0.0, 0.0]
    free_sol = ns["simulate"](x0, params=params, duration=6.0, fps=24, controller=None)
    lqr_sol = ns["simulate"](
        x0,
        params=params,
        duration=6.0,
        fps=24,
        controller=ns["make_lqr_controller"](K_demo),
        torque_limit=12.0,
    )

    frames = []
    frames += repeat_frame(make_title_card(), 92)
    frames += repeat_frame(
        make_text_card(
            "Free System",
            "A small perturbation near the top position is enough\n"
            "to make the uncontrolled system drift away.\n"
            "This shows that the equilibrium is unstable.",
        ),
        84,
    )
    for idx in sample_indices(len(free_sol["t"]), 54):
        frames.append(
            make_sim_frame(
                free_sol,
                idx,
                title="Free System Near the Upright Equilibrium",
                caption="Uncontrolled response:\nsmall errors grow instead of decaying.",
                color="tab:orange",
            )
        )

    frames += repeat_frame(
        make_text_card(
            "LQR Control",
            "Now we apply a linear quadratic regulator around\n"
            "the same equilibrium.\n"
            "The controller drives the state back to the top position.",
            footer="Q = diag(120, 150, 18, 20),    R = 0.8",
        ),
        84,
    )
    for idx in sample_indices(len(lqr_sol["t"]), 54):
        frames.append(
            make_sim_frame(
                lqr_sol,
                idx,
                title="LQR-Stabilized Response",
                caption="Controlled response:\nangles and velocities return to zero.",
                color="tab:green",
            )
        )

    frames += repeat_frame(
        make_text_card(
            "Result",
            "The same upright operating point is unstable in free motion,\n"
            "but locally stabilized by the LQR controller.",
        ),
        86,
    )

    rgb_arrays = [np.asarray(frame) for frame in frames]
    with imageio.get_writer(OUTPUT_MP4, fps=10, codec="libx264", quality=7) as writer:
        for frame in rgb_arrays:
            writer.append_data(frame)

    frames[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        optimize=False,
    )
    print(f"Saved demo to: {OUTPUT_MP4}")
    print(f"Saved fallback GIF to: {OUTPUT_GIF}")


if __name__ == "__main__":
    main()
