import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

BLOCK_SIZE = 20
SPEED = 15

class SnakeGame:

    def __init__(self, w=None, h=None):
        if w is None or h is None:
            screen_info = pygame.display.Info()
            screen_height = screen_info.current_h
            size = screen_height - 100
            size = (size // BLOCK_SIZE) * BLOCK_SIZE
            self.w = size * 2
            self.h = size
        else:
            self.w = w
            self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT

        self.head = Point((self.w//2//BLOCK_SIZE)*BLOCK_SIZE, (self.h//2//BLOCK_SIZE)*BLOCK_SIZE)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self):
        paused = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if self.direction != Direction.RIGHT:
                        self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    if self.direction != Direction.LEFT:
                        self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    if self.direction != Direction.DOWN:
                        self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    if self.direction != Direction.UP:
                        self.direction = Direction.DOWN
                elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    paused = True

        if paused:
            return False, self.score, True

        self._move(self.direction)
        self.snake.insert(0, self.head)

        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score, False

        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(SPEED)
        return game_over, self.score, False

    def _is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        font = pygame.font.Font(None, 36)
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def _draw_game_over(self):
        self.display.fill(BLACK)

        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)

        game_over_text = font_large.render('GAME OVER', True, RED)
        game_over_rect = game_over_text.get_rect(center=(self.w/2, self.h/2 - 80))
        self.display.blit(game_over_text, game_over_rect)

        score_text = font_medium.render(f'Final Score: {self.score}', True, WHITE)
        score_rect = score_text.get_rect(center=(self.w/2, self.h/2))
        self.display.blit(score_text, score_rect)

        button_width = 200
        button_height = 60
        button_x = self.w/2 - button_width/2
        button_y = self.h/2 + 80

        self.restart_button = pygame.Rect(button_x, button_y, button_width, button_height)

        mouse_pos = pygame.mouse.get_pos()
        if self.restart_button.collidepoint(mouse_pos):
            pygame.draw.rect(self.display, GREEN, self.restart_button)
        else:
            pygame.draw.rect(self.display, GRAY, self.restart_button)

        pygame.draw.rect(self.display, WHITE, self.restart_button, 3)

        restart_text = font_small.render('RESTART', True, BLACK)
        restart_rect = restart_text.get_rect(center=self.restart_button.center)
        self.display.blit(restart_text, restart_rect)

        pygame.display.flip()

    def _wait_for_restart(self):
        waiting = True
        while waiting:
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.restart_button.collidepoint(event.pos):
                        waiting = False
                        return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        waiting = False
                        return True

            self._draw_game_over()

        return False

    def _draw_start_menu(self):
        self.display.fill(BLACK)

        font_title = pygame.font.Font(None, 96)
        font_subtitle = pygame.font.Font(None, 36)
        font_button = pygame.font.Font(None, 48)

        title_text = font_title.render('SNAKE GAME', True, GREEN)
        title_rect = title_text.get_rect(center=(self.w/2, self.h/2 - 120))
        self.display.blit(title_text, title_rect)

        subtitle_text = font_subtitle.render('Use arrow keys to control the snake', True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(self.w/2, self.h/2 - 40))
        self.display.blit(subtitle_text, subtitle_rect)

        button_width = 250
        button_height = 70
        button_x = self.w/2 - button_width/2
        button_y = self.h/2 + 40

        self.start_button = pygame.Rect(button_x, button_y, button_width, button_height)

        mouse_pos = pygame.mouse.get_pos()
        if self.start_button.collidepoint(mouse_pos):
            pygame.draw.rect(self.display, GREEN, self.start_button)
        else:
            pygame.draw.rect(self.display, GRAY, self.start_button)

        pygame.draw.rect(self.display, WHITE, self.start_button, 3)

        start_text = font_button.render('START GAME', True, BLACK)
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.display.blit(start_text, start_rect)

        hint_text = font_subtitle.render('Press SPACE or click button to start', True, GRAY)
        hint_rect = hint_text.get_rect(center=(self.w/2, self.h - 60))
        self.display.blit(hint_text, hint_rect)

        pygame.display.flip()

    def _wait_for_start(self):
        waiting = True
        while waiting:
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.collidepoint(event.pos):
                        waiting = False
                        return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        waiting = False
                        return True

            self._draw_start_menu()

        return False

    def _draw_pause_screen(self):
        overlay = pygame.Surface((self.w, self.h))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.display.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 96)
        font_small = pygame.font.Font(None, 36)

        pause_text = font_large.render('PAUSED', True, YELLOW)
        pause_rect = pause_text.get_rect(center=(self.w/2, self.h/2 - 60))
        self.display.blit(pause_text, pause_rect)

        resume_text = font_small.render('Press P or ESC to resume', True, WHITE)
        resume_rect = resume_text.get_rect(center=(self.w/2, self.h/2 + 20))
        self.display.blit(resume_text, resume_rect)

        quit_text = font_small.render('Press Q to quit', True, WHITE)
        quit_rect = quit_text.get_rect(center=(self.w/2, self.h/2 + 60))
        self.display.blit(quit_text, quit_rect)

        pygame.display.flip()

    def _handle_pause(self):
        paused = True
        while paused:
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        paused = False
                    elif event.key == pygame.K_q:
                        return False

            self._draw_pause_screen()

        return True


if __name__ == '__main__':
    game = SnakeGame()

    game._draw_start_menu()
    if not game._wait_for_start():
        pygame.quit()
        quit()

    while True:
        game_over, score, paused = game.play_step()

        if paused:
            if not game._handle_pause():
                break

        if game_over:
            game._draw_game_over()
            if game._wait_for_restart():
                game.reset()
            else:
                break

    pygame.quit()
