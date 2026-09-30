import math
import pygame
from .paddle import Paddle
from .ball import Ball
from .brick import Brick
from .sound import SoundBank

# Game Engine

WHITE = (255, 255, 255)
BG = (15, 15, 25)
BRICK_COLORS = [
    (200, 60, 60),
    (200, 140, 60),
    (200, 200, 60),
    (80, 180, 80),
    (80, 140, 200),
]

MAX_BOUNCE_ANGLE = math.radians(60)  # from vertical, at paddle edges
MIN_VY_RATIO = 0.25                  # keep the ball from going near-horizontal

DIM = (180, 180, 200)
ACCENT_WIN = (90, 210, 120)
ACCENT_LOSE = (220, 80, 80)

# State machine
MENU, PLAYING, GAME_OVER = "menu", "playing", "game_over"

# key -> (name, ball speed px/frame, paddle width)
DIFFICULTIES = {
    pygame.K_1: ("Easy", 4.5, 130),
    pygame.K_2: ("Medium", 6.0, 100),
    pygame.K_3: ("Hard", 7.5, 70),
}
# number-pad aliases
DIFFICULTIES[pygame.K_KP1] = DIFFICULTIES[pygame.K_1]
DIFFICULTIES[pygame.K_KP2] = DIFFICULTIES[pygame.K_2]
DIFFICULTIES[pygame.K_KP3] = DIFFICULTIES[pygame.K_3]


def overlap(ball, x, y, w, h):
    """Return (depth_x, depth_y) of ball AABB vs rect, or None if not touching.
    Depths are always positive; sign/direction is decided by the caller."""
    bl, bt, br, bb = ball.bounds()
    ox = min(br, x + w) - max(bl, x)
    oy = min(bb, y + h) - max(bt, y)
    if ox <= 0 or oy <= 0:
        return None
    return ox, oy


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rows, self.cols = 5, 8

        self.font = pygame.font.SysFont("Arial", 28)
        self.big_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)

        self.sfx = SoundBank()

        self.state = MENU
        self.quit_requested = False
        self.result = None  # "win" or "lose"
        self.difficulty = "Medium"
        self.ball_speed = 6.0

        # Placeholder objects so render/update never see missing attributes
        self._new_game(*DIFFICULTIES[pygame.K_2])
        self.state = MENU

    # ------------------------------------------------------------------ setup

    def _new_game(self, name, ball_speed, paddle_width):
        self.difficulty = name
        self.ball_speed = ball_speed
        self.paddle = Paddle(self.width // 2 - paddle_width // 2, self.height - 30, paddle_width, 14)
        self.ball = Ball(self.width // 2, self.height - 50, radius=8)
        self._reset_ball()
        self.bricks = self._build_bricks(self.rows, self.cols)
        self.lives = 3
        self.score = 0
        self.result = None
        self.state = PLAYING

    def _build_bricks(self, rows, cols):
        bricks = []
        margin, gap, top = 30, 6, 60
        brick_w = (self.width - margin * 2 - gap * (cols - 1)) // cols
        brick_h = 22
        for r in range(rows):
            for c in range(cols):
                x = margin + c * (brick_w + gap)
                y = top + r * (brick_h + gap)
                bricks.append(Brick(x, y, brick_w, brick_h))
        return bricks

    # ------------------------------------------------------------------ input

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.state in (MENU, GAME_OVER):
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                self.quit_requested = True
            elif event.key in DIFFICULTIES:
                self._new_game(*DIFFICULTIES[event.key])
        elif self.state == PLAYING and event.key == pygame.K_ESCAPE:
            self.state = MENU  # abandon current game

    def handle_input(self):
        if self.state != PLAYING:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(-self.paddle.speed, self.width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(self.paddle.speed, self.width)

    # ------------------------------------------------------------------ update

    def update(self):
        if self.state != PLAYING:
            return

        # Sub-step so the ball never moves more than half its radius per step.
        # That makes tunnelling through a brick/paddle impossible.
        max_step = self.ball.radius / 2
        steps = max(1, math.ceil(self.ball.speed / max_step))
        frac = 1.0 / steps
        brick_hit = False  # at most one brick per frame

        for _ in range(steps):
            self.ball.move(frac)
            self._collide_walls()
            self._collide_paddle()
            if not brick_hit:
                brick_hit = self._collide_bricks()

        if self.ball.y - self.ball.radius > self.height:
            self.lives -= 1
            if self.lives <= 0:
                self._end("lose")
                return
            self._reset_ball()

        if all(not b.alive for b in self.bricks):
            self._end("win")

    def _end(self, result):
        self.result = result
        self.state = GAME_OVER
        self.sfx.play(result)  # "win" / "lose"

    def _collide_walls(self):
        b = self.ball
        hit = False
        if b.x - b.radius < 0:
            b.x = b.radius
            b.vx = abs(b.vx)
            hit = True
        elif b.x + b.radius > self.width:
            b.x = self.width - b.radius
            b.vx = -abs(b.vx)
            hit = True
        if b.y - b.radius < 0:
            b.y = b.radius
            b.vy = abs(b.vy)
            hit = True
        if hit:
            self.sfx.play("wall")

    def _collide_paddle(self):
        b, p = self.ball, self.paddle
        hit = overlap(b, p.x, p.y, p.width, p.height)
        if not hit:
            return
        ox, oy = hit
        self.sfx.play("paddle")

        if oy <= ox:
            # Top/bottom hit
            if b.y < p.y + p.height / 2:
                b.y = p.y - b.radius  # push out above
                # Angle depends on where it struck: -1 (left edge) .. +1 (right edge)
                rel = (b.x - (p.x + p.width / 2)) / (p.width / 2)
                rel = max(-1.0, min(1.0, rel))
                angle = rel * MAX_BOUNCE_ANGLE
                speed = b.speed
                b.vx = speed * math.sin(angle)
                b.vy = -speed * math.cos(angle)
            else:
                b.y = p.y + p.height + b.radius
                b.vy = abs(b.vy)
        else:
            # Side hit: push out horizontally, send ball away from paddle
            if b.x < p.x + p.width / 2:
                b.x = p.x - b.radius
                b.vx = -abs(b.vx)
            else:
                b.x = p.x + p.width + b.radius
                b.vx = abs(b.vx)

        self._enforce_min_vy()

    def _collide_bricks(self):
        """Resolve against the single deepest-overlapping brick. Returns True if one was hit."""
        b = self.ball
        best, best_hit, best_area = None, None, 0.0
        for brick in self.bricks:
            if not brick.alive:
                continue
            hit = overlap(b, brick.x, brick.y, brick.width, brick.height)
            if hit and hit[0] * hit[1] > best_area:
                best, best_hit, best_area = brick, hit, hit[0] * hit[1]

        if best is None:
            return False

        ox, oy = best_hit
        cx = best.x + best.width / 2
        cy = best.y + best.height / 2

        if ox < oy:
            # Side hit -> reverse x
            if b.x < cx:
                b.x -= ox
                b.vx = -abs(b.vx)
            else:
                b.x += ox
                b.vx = abs(b.vx)
        else:
            # Top/bottom hit (ties go vertical) -> reverse y
            if b.y < cy:
                b.y -= oy
                b.vy = -abs(b.vy)
            else:
                b.y += oy
                b.vy = abs(b.vy)

        best.alive = False
        self.score += 1
        self.sfx.play("brick")
        return True

    def _enforce_min_vy(self):
        b = self.ball
        speed = b.speed
        min_vy = speed * MIN_VY_RATIO
        if 0 < abs(b.vy) < min_vy:
            sign_y = 1 if b.vy > 0 else -1
            sign_x = 1 if b.vx >= 0 else -1
            b.vy = sign_y * min_vy
            b.vx = sign_x * math.sqrt(max(0.0, speed * speed - min_vy * min_vy))

    def _reset_ball(self):
        self.ball.x, self.ball.y = self.width / 2, self.height - 50
        # launch up-right at 45 degrees with the difficulty's speed
        c = self.ball_speed / math.sqrt(2)
        self.ball.vx, self.ball.vy = c, -c

    # ------------------------------------------------------------------ render

    def render(self, screen):
        screen.fill(BG)
        if self.state == MENU:
            self._render_menu(screen)
            return

        self._render_playfield(screen)
        if self.state == GAME_OVER:
            self._render_game_over(screen)

    def _render_playfield(self, screen):
        pygame.draw.rect(screen, WHITE, self.paddle.rect())
        pygame.draw.circle(screen, WHITE, (int(self.ball.x), int(self.ball.y)), self.ball.radius)

        for i, brick in enumerate(self.bricks):
            if brick.alive:
                row = i // self.cols
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                pygame.draw.rect(screen, color, brick.rect())

        screen.blit(self.font.render(f"Score: {self.score}", True, WHITE), (10, 10))
        lives = self.font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives, (self.width - lives.get_width() - 10, 10))

    def _center(self, screen, surf, y):
        screen.blit(surf, (self.width // 2 - surf.get_width() // 2, y))

    def _render_difficulty_options(self, screen, y):
        rows = [
            ("1", "Easy", "slow ball, wide paddle"),
            ("2", "Medium", "balanced"),
            ("3", "Hard", "fast ball, narrow paddle"),
        ]
        # Left-aligned columns, block centered as a whole
        col_key, col_name, col_desc = 0, 30, 120
        block_w = col_desc + max(self.small_font.size(d)[0] for _, _, d in rows)
        x0 = self.width // 2 - block_w // 2
        for i, (key, name, desc) in enumerate(rows):
            yy = y + i * 30
            screen.blit(self.small_font.render(key, True, WHITE), (x0 + col_key, yy))
            screen.blit(self.small_font.render(name, True, WHITE), (x0 + col_name, yy))
            screen.blit(self.small_font.render(desc, True, DIM), (x0 + col_desc, yy))
        self._center(screen, self.small_font.render("Q / Esc  Quit", True, DIM), y + 110)

    def _render_menu(self, screen):
        self._center(screen, self.big_font.render("BRICK BREAKER", True, WHITE), 130)
        self._center(screen, self.font.render("Choose difficulty", True, DIM), 230)
        self._render_difficulty_options(screen, 285)

    def _render_game_over(self, screen):
        veil = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 190))
        screen.blit(veil, (0, 0))

        won = self.result == "win"
        title = "YOU WIN" if won else "GAME OVER"
        color = ACCENT_WIN if won else ACCENT_LOSE
        self._center(screen, self.big_font.render(title, True, color), 130)
        self._center(screen, self.font.render(
            f"Final score: {self.score}   ({self.difficulty})", True, WHITE), 215)
        self._center(screen, self.font.render("Play again:", True, DIM), 265)
        self._render_difficulty_options(screen, 310)
