import pygame
import random
import time

# --- Constantes do Jogo ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_TITLE = "Nave Espacial"
FPS = 60

# --- Classes de Sprites ---


class NaveEspacial(pygame.sprite.Sprite):
    """Representa a nave espacial do jogador."""

    def __init__(self, name, position=(100, 100)):
        super().__init__()
        self.name = name
        self.alive = True
        self.position = pygame.Vector2(position)
        self.speed = 5
        self.shield = 100
        self.energy = 100
        self.image = pygame.image.load("nave_espacial.png")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=self.position)
        self.last_shield_time = -30
        self.shield_active = False
        self.shield_end_time = 0

    def update(self, keys):
        """Atualiza a posição da nave com base nas teclas pressionadas."""
        move = {
            pygame.K_LEFT: (-self.speed, 0),
            pygame.K_RIGHT: (self.speed, 0),
            pygame.K_UP: (0, -self.speed),
            pygame.K_DOWN: (0, self.speed),
        }

        for key, (dx, dy) in move.items():
            if keys[key]:
                self.position.x += dx
                self.position.y += dy

        # Garante que a nave permanece dentro dos limites da tela
        self.position.x = max(0, min(SCREEN_WIDTH, self.position.x))
        self.position.y = max(0, min(SCREEN_HEIGHT, self.position.y))
        self.rect.center = self.position

    def shoot(self):
        """Cria e retorna um novo objeto Tiro."""
        return Tiro(self.position)

    def back_shoot(self):
        """Cria e retorna um novo objeto TiroTras."""
        return TiroTras(self.position)

    def bubble_shoot(self):
        """Cria e retorna um novo objeto Bolha."""
        return Bolha(self.position)


class Tiro(pygame.sprite.Sprite):
    """Representa um projétil disparado pela nave para frente."""

    def __init__(self, position):
        super().__init__()
        self.position = pygame.Vector2(position)
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=self.position)
        self.speed = pygame.Vector2(0, -10)

    def update(self):
        """Atualiza a posição do tiro e o remove se sair da tela."""
        self.position += self.speed
        self.rect.center = self.position
        if self.position.y < 0:
            self.kill()


class TiroTras(pygame.sprite.Sprite):
    """Representa um projétil disparado pela nave para trás."""

    def __init__(self, position):
        super().__init__()
        self.position = pygame.Vector2(position)
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 100, 255))
        self.rect = self.image.get_rect(center=self.position)
        self.speed = pygame.Vector2(0, 10)

    def update(self):
        """Atualiza a posição do tiro e o remove se sair da tela."""
        self.position += self.speed
        self.rect.center = self.position
        if self.position.y > SCREEN_HEIGHT:
            self.kill()


class Bolha(pygame.sprite.Sprite):
    """Representa um projétil tipo bolha com movimento aleatório."""

    def __init__(self, position):
        super().__init__()
        self.position = pygame.Vector2(position)
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 200, 255), (10, 10), 10)
        self.rect = self.image.get_rect(center=self.position)
        self.speed = pygame.Vector2(random.uniform(-1, 1), -3)

    def update(self):
        """Atualiza a posição da bolha e a remove se sair da tela."""
        self.position += self.speed
        self.rect.center = self.position
        if self.position.y < 0:
            self.kill()


class CampoDeForca(pygame.sprite.Sprite):
    """Representa o escudo temporário da nave."""

    def __init__(self, nave):
        super().__init__()
        self.nave = nave
        self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 255, 100), (60, 60), 60)
        self.rect = self.image.get_rect(center=self.nave.position)

    def update(self):
        """Atualiza a posição do campo de força e o remove quando expira."""
        self.rect.center = self.nave.position
        if time.time() > self.nave.shield_end_time:
            self.nave.shield_active = False
            self.kill()


class Asteroide(pygame.sprite.Sprite):
    """Representa um asteroide com diferentes tamanhos e velocidades."""

    def __init__(self):
        super().__init__()
        self.image_original = pygame.image.load("asteroide.png").convert_alpha()
        self.size_type = random.choice(["P", "M", "G"])
        size_map = {"P": 30, "M": 60, "G": 100}
        size = size_map.get(self.size_type, 30)

        self.image = pygame.transform.scale(self.image_original, (size, size))
        self.rect = self.image.get_rect(
            center=(random.randint(0, SCREEN_WIDTH), random.randint(-100, -40))
        )
        self.speed = pygame.Vector2(random.uniform(-1, 1), random.uniform(2, 6))

    def update(self):
        """Atualiza a posição do asteroide e o remove se sair da tela."""
        self.rect.move_ip(self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# --- Funções do Jogo ---


def inicializar_jogo():
    """Inicializa o Pygame e as variáveis do jogo."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()

    bg_image = pygame.image.load("fundo_estrelado.jpg").convert()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    return screen, clock, bg_image


def criar_sprites():
    """Cria e retorna os grupos de sprites e a nave do jogador."""
    nave = NaveEspacial("Explorer")
    all_sprites = pygame.sprite.Group(nave)
    tiros = pygame.sprite.Group()
    tiros_tras = pygame.sprite.Group()
    bolhas = pygame.sprite.Group()
    asteroides = pygame.sprite.Group()
    escudo_sprite = pygame.sprite.Group()
    return nave, all_sprites, tiros, tiros_tras, bolhas, asteroides, escudo_sprite


def gerir_eventos(event, nave, all_sprites, tiros, tiros_tras, bolhas, escudo_sprite):
    """Lida com os eventos do teclado e do jogo."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            tiro = nave.shoot()
            all_sprites.add(tiro)
            tiros.add(tiro)
        elif event.key == pygame.K_o:
            tiro_tras = nave.back_shoot()
            all_sprites.add(tiro_tras)
            tiros_tras.add(tiro_tras)
        elif event.key == pygame.K_i:
            bolha = nave.bubble_shoot()
            all_sprites.add(bolha)
            bolhas.add(bolha)
        elif event.key == pygame.K_u:
            current_time = time.time()
            if current_time - nave.last_shield_time >= 30:
                nave.shield_active = True
                nave.shield_end_time = current_time + 10
                nave.last_shield_time = current_time
                escudo = CampoDeForca(nave)
                all_sprites.add(escudo)
                escudo_sprite.add(escudo)


def verificar_colisoes(nave, asteroides, tiros, tiros_tras, bolhas, score):
    """Verifica e lida com as colisões entre sprites."""
    if not nave.shield_active:
        hits = pygame.sprite.spritecollide(nave, asteroides, True)
        for _ in hits:
            nave.shield -= 20
            if nave.shield <= 0:
                nave.alive = False

    for grupo_tiro in [tiros, tiros_tras, bolhas]:
        hits = pygame.sprite.groupcollide(grupo_tiro, asteroides, True, True)
        for _, asts in hits.items():
            for ast in asts:
                if ast.size_type == "P":
                    score += 30
                elif ast.size_type == "M":
                    score += 20
                else:
                    score += 10
    return score


def desenhar_texto(screen, font, nave, score, start_time):
    """Renderiza e desenha o texto na tela."""
    tempo_ativo = int(time.time() - start_time)
    pontos_total = score + tempo_ativo

    texto_escudo = font.render(f"Escudo: {nave.shield}", True, (255, 255, 255))
    texto_pontuacao = font.render(f"Pontos: {pontos_total}", True, (255, 255, 0))
    screen.blit(texto_escudo, (10, 10))
    screen.blit(texto_pontuacao, (10, 35))


# --- Função Principal do Jogo ---


def main():
    """Função principal que executa o loop do jogo."""
    screen, clock, bg_image = inicializar_jogo()
    nave, all_sprites, tiros, tiros_tras, bolhas, asteroides, escudo_sprite = (
        criar_sprites()
    )

    score = 0
    start_time = time.time()
    bg_y = 0
    bg_speed = 1

    ADD_ASTEROID = pygame.USEREVENT + 1
    pygame.time.set_timer(ADD_ASTEROID, 1000)

    font = pygame.font.SysFont(None, 24)

    running = True
    while running:
        # Lógica para o fundo em movimento
        bg_y += bg_speed
        if bg_y >= SCREEN_HEIGHT:
            bg_y = 0
        screen.blit(bg_image, (0, bg_y))
        screen.blit(bg_image, (0, bg_y - SCREEN_HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == ADD_ASTEROID:
                asteroide = Asteroide()
                all_sprites.add(asteroide)
                asteroides.add(asteroide)
            gerir_eventos(
                event, nave, all_sprites, tiros, tiros_tras, bolhas, escudo_sprite
            )

        keys = pygame.key.get_pressed()
        nave.update(keys)
        tiros.update()
        tiros_tras.update()
        bolhas.update()
        asteroides.update()
        escudo_sprite.update()

        score = verificar_colisoes(nave, asteroides, tiros, tiros_tras, bolhas, score)
        if not nave.alive:
            running = False

        all_sprites.draw(screen)
        desenhar_texto(screen, font, nave, score, start_time)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
