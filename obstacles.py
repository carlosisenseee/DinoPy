import pygame
import random


class Obstacle:
    """Classe base para todos os obstáculos"""

    def __init__(self, image_list, type_idx=0):
        self.image_list = image_list
        self.type = type_idx
        self.rect = self.image_list[self.type].get_rect()
        self.rect.x = 1100  # Inicialmente fora da tela

        # Cache para máscara de colisão
        self._mask = None

    def update(self, game_speed):
        """Atualiza a posição do obstáculo baseado na velocidade do jogo"""
        self.rect.x -= game_speed

    def draw(self, screen):
        """Desenha o obstáculo na tela"""
        screen.blit(self.image_list[self.type], self.rect)

    def get_mask(self):
        """Retorna uma máscara de colisão para detecção precisa"""
        # Otimização: criar máscara apenas uma vez
        if self._mask is None:
            self._mask = pygame.mask.from_surface(self.image_list[self.type])
        return self._mask


class SmallCactus(Obstacle):
    """Classe para os cactos pequenos"""

    def __init__(self, image_list, type_idx=0):
        super().__init__(image_list, type_idx)
        self.rect.y = 325  # Posição Y fixa para cactos pequenos


class LargeCactus(Obstacle):
    """Classe para os cactos grandes"""

    def __init__(self, image_list, type_idx=0):
        super().__init__(image_list, type_idx)
        self.rect.y = 300  # Posição Y fixa para cactos grandes


class Bird(Obstacle):
    """Classe para os pássaros"""
    # Alturas possíveis para os pássaros
    HEIGHT_OPTIONS = [180, 220, 260]

    def __init__(self, image_list, height_type=None):
        super().__init__(image_list, 0)  # Pássaros começam com o primeiro frame

        # Determinar altura baseada no tipo ou aleatoriamente
        if height_type is not None and height_type < len(self.HEIGHT_OPTIONS):
            self.rect.y = self.HEIGHT_OPTIONS[height_type]
        else:
            self.rect.y = random.choice(self.HEIGHT_OPTIONS)

        self.step_index = 0

    def update(self, game_speed):
        """Atualiza a posição e animação do pássaro"""
        super().update(game_speed)

        # Animar o pássaro (alternar entre os dois sprites)
        self.step_index += 1
        if self.step_index >= 10:
            self.step_index = 0
            # Alternar entre os dois frames de animação
            self.type = 1 - self.type  # Alterna entre 0 e 1
            # Reset da máscara quando a imagem muda
            self._mask = None

    def draw(self, screen):
        """Desenha o pássaro na tela"""
        screen.blit(self.image_list[self.type], self.rect)

