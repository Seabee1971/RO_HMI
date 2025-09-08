# space_invaders.py
# Handlers/space_invaders.py
import pygame
import sys

def run_game():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Red Oktober")

    BLACK, WHITE, GREEN, RED = (0,0,0), (255,255,255), (0,255,0), (255,0,0)
    clock = pygame.time.Clock()

    player_width, player_height = 50, 20
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - 50
    player_speed = 6

    bullet_width, bullet_height = 5, 15
    bullet_speed = -8
    bullets = []

    enemy_width, enemy_height = 40, 30
    enemies = [pygame.Rect(100 + col*(enemy_width+15), 50 + row*(enemy_height+15),
                           enemy_width, enemy_height)
               for row in range(5) for col in range(8)]
    enemy_speed, enemy_direction = 1, 1

    score, font = 0, pygame.font.SysFont("Arial", 24)

    def draw_player(x, y): pygame.draw.rect(screen, GREEN, (x, y, player_width, player_height))
    def draw_bullets(): [pygame.draw.rect(screen, WHITE, b) for b in bullets]
    def draw_enemies(): [pygame.draw.rect(screen, RED, e) for e in enemies]
    def draw_score(): screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))

    def game_over():
        screen.blit(font.render("GAME OVER", True, RED), (WIDTH//2 - 60, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player_x > 0: player_x -= player_speed
        if keys[pygame.K_d] and player_x < WIDTH - player_width: player_x += player_speed
        if keys[pygame.K_SPACE]:
            if len(bullets) < 5:
                bullets.append(pygame.Rect(player_x + player_width//2 - 2, player_y, bullet_width, bullet_height))

        for b in bullets[:]:
            b.y += bullet_speed
            if b.y < 0: bullets.remove(b)
            else:
                for e in enemies[:]:
                    if b.colliderect(e):
                        bullets.remove(b); enemies.remove(e); score += 10; break

        move_down = False
        for e in enemies:
            e.x += enemy_speed * enemy_direction
            if e.right >= WIDTH or e.left <= 0: move_down = True
        if move_down:
            enemy_direction *= -1
            for e in enemies:
                e.y += 20
                if e.bottom >= player_y: game_over()

        draw_player(player_x, player_y)
        draw_bullets()
        draw_enemies()
        draw_score()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
