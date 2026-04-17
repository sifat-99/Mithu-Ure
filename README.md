# Flappy Bird Game with PyOpenGL

A simple Flappy Bird clone implemented using PyOpenGL and GLUT.

## Requirements

- Python 3.x
- PyOpenGL
- PyOpenGL-accelerate

## Installation

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## How to Run

Use the project virtual environment to launch the game:

Windows batch:
```
.\run_game.bat
```

PowerShell:
```
.\run_game.ps1
```

If you prefer manual activation, run:
```
& .\.venv\Scripts\Activate.ps1
python main.py
```

## Controls

- **Spacebar**: Make the bird flap (jump)
- **R**: Restart the game when game over

## Gameplay

- Avoid the green pipes by flapping the bird.
- Score points by passing through the gaps.
- The game ends if the bird hits a pipe or goes out of bounds.

## Troubleshooting

- If you encounter issues with GLUT, ensure you have OpenGL drivers installed.
- On Windows, you may need to install freeglut if not included.