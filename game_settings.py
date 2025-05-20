import pygame
import os


class Settings:
    """Classe para armazenar todas as configurações do jogo"""

    def __init__(self):
        # Configurações da tela
        self.SCREEN_HEIGHT = 600
        self.SCREEN_WIDTH = 1100

        # Configurações de jogo
        self.INITIAL_GAME_SPEED = 20
        self.MAX_GAME_SPEED = 400000000000000000000000  # Limitar velocidade máxima para jogabilidade, original 40
        self.game_speed = self.INITIAL_GAME_SPEED

        # Quando introduzir os pássaros
        self.BIRD_INTRODUCTION_SCORE = 500

        # Configurações visuais
        self.DEBUG_VISUALS = True  # Mostrar hitboxes e linhas de detecção

        # Para passar referência aos obstáculos para desenho
        self.obstacles = []

        # Imagens serão carregadas pelo método load_images
        self.RUNNING = None
        self.JUMPING = None
        self.DUCKING = None
        self.SMALL_CACTUS = None
        self.LARGE_CACTUS = None
        self.BIRD = None

    def load_images(self):
        """Carrega todas as imagens do jogo"""
        # Imagens do dinossauro
        self.RUNNING = [
            pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
            pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))
        ]

        self.JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))

        self.DUCKING = [
            pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
            pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))
        ]

        # Imagens dos obstáculos
        self.SMALL_CACTUS = [
            pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
            pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
            pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))
        ]

        self.LARGE_CACTUS = [
            pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
            pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
            pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))
        ]

        self.BIRD = [
            pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
            pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))
        ]
