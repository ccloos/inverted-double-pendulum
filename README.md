# Inverted Double Pendulum Demos

This repository contains two shareable Jupyter notebooks and a short demo-video generator for a simulated double inverted pendulum.

## What Is Included

- `double_inverted_pendulum_lqr.ipynb`
  Focused on the upright equilibrium study.
  It compares the free nonlinear system with an LQR controller designed around `(theta1, theta2, dtheta1, dtheta2) = (0, 0, 0, 0)`.

- `double_inverted_pendulum_swingup.ipynb`
  Extension notebook with a practical hybrid swing-up controller plus local LQR stabilization near the upright equilibrium.

- `make_lqr_demo_video.py`
  Generates a narrated local demo video that highlights:
  - the unstable free response near the upright equilibrium
  - the LQR-controlled response

- `double_pendulum_lqr_demo.mp4`
  Rendered demo video for presentation or quick sharing.

## Sources

The notebooks reference the following sources directly in their markdown sections:

- K. J. Astrom, K. Furuta, M. Iwashiro, T. Hoshino,
  *Energy Based Strategies for Swinging Up a Double Pendulum*,
  IFAC World Congress 1999.

- Practical reference repository:
  [jitendra825/Inverted-Pendulum-Simulink](https://github.com/jitendra825/Inverted-Pendulum-Simulink)

## Recommended Sharing Structure

- Share `double_inverted_pendulum_lqr.ipynb` when the goal is to explain instability and local stabilization with LQR.
- Share `double_inverted_pendulum_swingup.ipynb` when the goal is to discuss the extended swing-up controller.
- Share `double_pendulum_lqr_demo.mp4` when the goal is a short visual demo without equations.

## Notes

- The LQR notebook is the cleaner teaching/demo version.
- The swing-up notebook is the experimental extension.
- The video generator currently uses local Python dependencies and writes the MP4 in this folder.
