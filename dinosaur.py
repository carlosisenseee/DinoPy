import pygame
import math
import random


class Dinosaur:
    def __init__(self, image, settings):
        # Configurações
        self.settings = settings
        self.X_POS = 80
        self.NORMAL_Y = 310  # Posição Y normal
        self.DUCK_Y = 340  # Posição Y agachado
        self.JUMP_VEL = 8.5  # Velocidade inicial do pulo

        # Estado do dinossauro
        self.image = image
        self.running = True
        self.jumping = False
        self.ducking = False
        self.jump_vel = self.JUMP_VEL
        self.step_index = 0

        # Configurar retângulo para colisão
        self.rect = pygame.Rect(self.X_POS, self.NORMAL_Y, image.get_width(), image.get_height())

        # Cor para visualização da IA
        self.color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

        # Otimizar a máscara de colisão
        self._mask = None
        self._last_image = None

    def update(self):
        """Atualiza o estado do dinossauro"""

        if self.running:
            self.run()
        if self.jumping:
            self.jump()
        if self.ducking:
            self.duck()

        # Garantir que o passo de animação não ultrapasse o limite
        if self.step_index >= 10:
            self.step_index = 0

    def jump(self):
        """Faz o dinossauro pular"""
        if not self.jumping:
            self.jumping = True
            self.running = False
            self.ducking = False

        # Ajusta o sprite para pulo
        self.image = self.settings.JUMPING

        #RELER LINHAS ABAIXO PARA TENTAR ARRUMAR O PULO NAS ALTURAS

        # Sistema de pulo melhorado com física mais realista
        # Calcular fator de velocidade com base logarítmica para evitar crescimento excessivo
        base_speed = self.settings.INITIAL_GAME_SPEED
        speed_ratio = self.settings.game_speed / base_speed
        speed_factor = 1 + (speed_ratio - 1) * 0.3  # Crescimento mais controlado

        # Movimento vertical ajustado dinamicamente
        jump_multiplier = 4 * min(speed_factor, 2)  # Limitar o multiplicador máximo Original é 2.5
        self.rect.y -= self.jump_vel * jump_multiplier

        # Gravidade ajustada dinamicamente com balanceamento
        base_gravity = 0.8
        gravity_adjustment = base_gravity * (1 + (speed_factor - 1) * 0.4)  # Crescimento proporcional mas controlado
        self.jump_vel -= gravity_adjustment

        # Verificar se o pulo acabou
        if self.jump_vel <= -self.JUMP_VEL:
            # Se chegou ou passou do chão, resetar posição e estados
            if self.rect.y >= self.NORMAL_Y:
                self.rect.y = self.NORMAL_Y
                self.jumping = False
                self.running = True
                self.jump_vel = self.JUMP_VEL

        # Invalidar a máscara atual quando muda de imagem
        self._mask = None

    def duck(self):
        """Faz o dinossauro se agachar"""
        self.ducking = True
        self.running = False
        self.jumping = False

        # Alterna entre sprites de agachamento
        self.image = self.settings.DUCKING[(self.step_index // 5) % len(self.settings.DUCKING)]
        self.rect.y = self.DUCK_Y
        self.step_index += 1

        # Ajusta o retângulo para a colisão correta
        self.rect = pygame.Rect(
            self.X_POS,
            self.DUCK_Y,
            self.image.get_width(),
            self.image.get_height()
        )

        # Invalidar a máscara atual quando muda de imagem
        self._mask = None

    def stop_duck(self):
        """Para de agachar"""
        self.ducking = False
        self.running = True

        # Ajustar retângulo para posição normal
        self.rect.y = self.NORMAL_Y
        self.rect = pygame.Rect(
            self.X_POS,
            self.NORMAL_Y,
            self.settings.RUNNING[0].get_width(),
            self.settings.RUNNING[0].get_height()
        )

    def run(self):
        """Animação de corrida do dinossauro"""
        self.image = self.settings.RUNNING[self.step_index // 5]

        # Garantir posição correta
        self.rect.x = self.X_POS
        self.rect.y = self.NORMAL_Y
        self.step_index += 1

        # Redefinir retângulo para garantir dimensões corretas
        self.rect = pygame.Rect(
            self.X_POS,
            self.NORMAL_Y,
            self.image.get_width(),
            self.image.get_height()
        )

        # Invalidar a máscara atual quando muda de imagem
        self._mask = None

    def draw(self, screen):
        """Desenha o dinossauro na tela"""
        screen.blit(self.image, (self.rect.x, self.rect.y))

        # Para depuração visual, mostrar hitbox e linhas para os obstáculos
        if self.settings.DEBUG_VISUALS:
            # Desenhar retângulo de colisão
            pygame.draw.rect(screen, self.color, self.rect, 2)

            # Desenhar linhas para obstáculos próximos (até 2)
            for obstacle in self.settings.obstacles[:2]:  # Limitar a 2 obstáculos
                pygame.draw.line(
                    screen,
                    self.color,
                    (self.rect.x + 54, self.rect.y + 12),
                    obstacle.rect.center,
                    2
                )

    def get_mask(self):
        """Retorna uma máscara de colisão para detecção precisa"""
        # Otimização: cria a máscara apenas quando a imagem muda
        if self._mask is None or self._last_image != self.image:
            self._mask = pygame.mask.from_surface(self.image)
            self._last_image = self.image
        return self._mask

    def check_collision(self, obstacle):
        """Verifica colisão com obstáculo usando máscara (pixel-perfect)"""
        dino_mask = self.get_mask()
        obstacle_mask = obstacle.get_mask()

        # Calcular offset entre os dois objetos
        offset = (
            obstacle.rect.x - self.rect.x,
            obstacle.rect.y - self.rect.y
        )

        # Verificar sobreposição de máscaras
        collision_point = dino_mask.overlap(obstacle_mask, offset)
        return collision_point is not None
