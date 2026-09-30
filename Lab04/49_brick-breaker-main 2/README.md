# Brick Breaker Game

This project is a terminal-based Brick Breaker (Breakout-style) clone using **Pygame**. It introduces students to interactive game design using object-oriented principles and real-time graphical rendering.

---

## What’s Provided

A partially working version of a Brick Breaker game with:

- A player-controlled paddle and a ball that bounces off walls, the paddle, and bricks
- A grid of destructible bricks
- Lives and score display

You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**

---

## Getting Started

### Setup

1. Clone the repo or download the project folder.
2. Make sure you have Python 3.10+ installed.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the game:

```bash
python main.py
```

---

## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Refine Collision Detection

> The ball always bounces vertically off the paddle and bricks, no matter which side it actually hit. Hitting a brick from the left or right should send the ball sideways, but instead it keeps moving in the same horizontal direction, which can look wrong or let it clip past a neighboring brick. Investigate and enhance collision accuracy so the bounce direction matches the side that was actually hit.

### Task 2: Implement Game Over Condition

> Add a screen that displays whether the player won (cleared all the bricks) or lost (ran out of lives), along with the final score, then gracefully waits for input instead of just printing to the console.

### Task 3: Add Replay Option

> After the end screen, allow the user to play again by choosing a difficulty (Easy, Medium, or Hard ball speed/paddle size), or exit.

### Task 4: Add Sound Feedback

> Add basic sound effects for a brick breaking, the ball hitting the paddle or a wall, and the game-over/win moment.

---

## Expected Behavior

- Smooth paddle movement using `Left`/`Right` or `A`/`D`
- The ball bounces off the side walls, the top wall, the paddle, and bricks
- Hitting a brick destroys it and increases the score
- Letting the ball fall past the paddle costs a life; losing all lives ends the game
- Destroying every brick wins the game

---

## Folder Structure

```
brick-breaker-main/
├── main.py
├── requirements.txt
├── game/
│   ├── game_engine.py
│   ├── paddle.py
│   ├── ball.py
│   └── brick.py
└── README.md
```

---

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history

