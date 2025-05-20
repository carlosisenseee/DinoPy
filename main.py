# main.py - Arquivo principal do jogo
import pygame
import os
import sys
import random
import neat
from dinosaur import Dinosaur
from obstacles import SmallCactus, LargeCactus, Bird
from game_settings import Settings
from visualization import plot_stats, draw_neural_network
import pickle


class Game:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        pygame.display.set_caption("T-Rex Runner NEAT")
        self.clock = pygame.time.Clock()

        # Carregar recursos uma única vez
        self.load_resources()

        # Estatísticas do jogo
        self.points = 0
        self.obstacles = []
        self.dinosaurs = []
        self.ge = []
        self.nets = []

        # Background
        self.x_pos_bg = 0
        self.y_pos_bg = 380

    def load_resources(self):
        """Carrega todos os recursos do jogo (imagens, sons)"""
        self.settings.load_images()
        # TODO: Adicionar carregamento de sons

        # Carregar fonte apenas uma vez
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.large_font = pygame.font.Font('freesansbold.ttf', 30)

        # Carregar fundo
        self.bg_image = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

    def draw_background(self):
        """Desenha o fundo em movimento"""
        image_width = self.bg_image.get_width()
        self.screen.blit(self.bg_image, (self.x_pos_bg, self.y_pos_bg))
        self.screen.blit(self.bg_image, (image_width + self.x_pos_bg, self.y_pos_bg))

        if self.x_pos_bg <= -image_width:
            self.x_pos_bg = 0
        self.x_pos_bg -= self.settings.game_speed

    def draw_statistics(self):
        """Mostra estatísticas do jogo na tela"""
        text_1 = self.font.render(f'Dinossauros Vivos: {str(len(self.dinosaurs))}', True, (0, 0, 0))
        text_2 = self.font.render(f'Geração: {self.population.generation + 1}', True, (0, 0, 0))
        text_3 = self.font.render(f'Velocidade: {str(self.settings.game_speed)}', True, (0, 0, 0))

        # Adicionar mais informações úteis
        highest_fitness = max([genome.fitness for genome in self.ge]) if self.ge else 0
        text_4 = self.font.render(f'Maior Fitness: {highest_fitness:.2f}', True, (0, 0, 0))

        self.screen.blit(text_1, (50, 450))
        self.screen.blit(text_2, (50, 480))
        self.screen.blit(text_3, (50, 510))
        self.screen.blit(text_4, (50, 540))

    def update_score(self):
        """Atualiza e mostra a pontuação"""
        self.points += 1

        # Aumentar a velocidade progressivamente (ajustado para ser menos abrupto)
        if self.points % 100 == 0:
            # Aumentar a velocidade conforme o jogo progride,
            # mas com um limite máximo para evitar que fique impossível
            if self.settings.game_speed < self.settings.MAX_GAME_SPEED:
                self.settings.game_speed += 1 #original 0.5

        # Mostrar pontuação
        score_text = self.font.render(f'Pontos: {str(self.points)}', True, (0, 0, 0))
        self.screen.blit(score_text, (950, 50))

        # Informações adicionais sobre velocidade e pássaros
        speed_text = self.font.render(f'Velocidade: {self.settings.game_speed:.1f}', True, (0, 100, 0))
        self.screen.blit(speed_text, (750, 110))

    def generate_obstacles(self):
        """Gera novos obstáculos com base na pontuação atual"""
        if len(self.obstacles) == 0:
            # Determinar quais tipos de obstáculos podem aparecer
            available_obstacles = []

            # Cactos sempre estão disponíveis
            available_obstacles.append(0)  # Small Cactus
            available_obstacles.append(1)  # Large Cactus

            # Pássaros aparecem apenas após certa pontuação
            if self.points >= self.settings.BIRD_INTRODUCTION_SCORE:
                available_obstacles.append(2)  # Bird

            # Escolher aleatoriamente entre os obstáculos disponíveis
            # Controle de frequência: mais cactos no início, mais pássaros depois
            if self.points > 1000:
                # Aumentar chance de pássaros em pontuações mais altas
                chance_modifier = min(0.4, (self.points - 1000) / 5000)
                weights = [0.3 - chance_modifier / 2, 0.3 - chance_modifier / 2, 0.4 + chance_modifier]
            else:
                weights = [0.4, 0.4, 0.2]

            # Filtrando pesos para apenas obstáculos disponíveis
            final_weights = []
            final_obstacles = []

            for i, obstacle_type in enumerate(available_obstacles):
                if i < len(weights):
                    final_weights.append(weights[i])
                    final_obstacles.append(obstacle_type)

            # Normalizar pesos
            total = sum(final_weights)
            final_weights = [w / total for w in final_weights]

            rand_int = random.choices(final_obstacles, weights=final_weights, k=1)[0]

            # Adicionar o obstáculo escolhido
            if rand_int == 0:
                self.obstacles.append(SmallCactus(
                    self.settings.SMALL_CACTUS,
                    random.randint(0, 2)
                ))
            elif rand_int == 1:
                self.obstacles.append(LargeCactus(
                    self.settings.LARGE_CACTUS,
                    random.randint(0, 2)
                ))
            elif rand_int == 2:
                self.obstacles.append(Bird(
                    self.settings.BIRD,
                    height_type=random.randint(0, 2)  # Diferentes alturas para o pássaro
                ))

            # Adicionar distância mínima entre obstáculos baseada na velocidade
            min_distance = 50 + (self.settings.game_speed * 5)

            # Ajustar posição X do obstáculo para garantir distância mínima
            self.obstacles[-1].rect.x = self.settings.SCREEN_WIDTH + min_distance

    def remove_dinosaur(self, index):
        """Remove um dinossauro e seus dados associados quando ele colide"""
        self.dinosaurs.pop(index)
        self.ge.pop(index)
        self.nets.pop(index)

    def eval_genomes(self, genomes, config):
        """Função principal de avaliação dos genomas"""
        self.points = 0
        self.obstacles = []
        self.dinosaurs = []
        self.ge = []
        self.nets = []
        self.population = neat.Population(config) if not hasattr(self, 'population') else self.population

        # Reiniciar a velocidade do jogo
        self.settings.game_speed = self.settings.INITIAL_GAME_SPEED

        # Configurar os genomas e redes
        for genome_id, genome in genomes:
            self.dinosaurs.append(Dinosaur(self.settings.RUNNING[0], self.settings))
            self.ge.append(genome)
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            genome.fitness = 0

        run = True
        while run:
            # Verificar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                    elif event.key == pygame.K_s:
                        # Salvar o melhor genoma
                        self.save_best_genome()

            # Limpar a tela
            self.screen.fill((255, 255, 255))

            # Atualizar e desenhar dinossauros
            for dinosaur in self.dinosaurs:
                dinosaur.update()
                dinosaur.draw(self.screen)

            # Verificar se todos os dinossauros morreram
            if len(self.dinosaurs) == 0:
                break

            # Gerar obstáculos se necessário
            self.generate_obstacles()

            # Atualizar e desenhar obstáculos
            for obstacle in list(self.obstacles):  # Usar uma cópia para evitar modificação durante iteração
                obstacle.draw(self.screen)
                obstacle.update(self.settings.game_speed)

                # Remover obstáculos que saíram da tela
                if obstacle.rect.x < -obstacle.rect.width:
                    self.obstacles.remove(obstacle)
                    continue

                # Verificar colisões
                for i, dinosaur in enumerate(list(self.dinosaurs)):  # Usar uma cópia para evitar problemas
                    if i >= len(self.ge):  # Verificação de segurança
                        continue

                    if dinosaur.check_collision(obstacle):
                        # Penalizar por colisão
                        self.ge[i].fitness -= 1
                        self.remove_dinosaur(i)
                        break  # Sair do loop interno após remover

            # Atualizar redes neurais
            self.update_neural_networks()

            # Desenhar informações do jogo
            self.draw_statistics()
            self.update_score()
            self.draw_background()

            # Limitação de framerate para consistência
            self.clock.tick(30)
            pygame.display.update()

    def update_neural_networks(self):
        """Atualiza as redes neurais para cada dinossauro"""
        for i, dinosaur in enumerate(list(self.dinosaurs)):
            if i >= len(self.ge):  # Verificação de segurança
                continue

            # Recompensar o dinossauro por permanecer vivo
            self.ge[i].fitness += 0.1

            # Encontrar o obstáculo mais próximo
            closest_obstacle = None
            closest_distance = float('inf')

            for obstacle in self.obstacles:
                # Calcular apenas obstáculos que estão à frente do dinossauro
                if obstacle.rect.x > dinosaur.rect.x:
                    distance = obstacle.rect.x - dinosaur.rect.x
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_obstacle = obstacle

            # Definir valores padrão caso não haja obstáculos
            obstacle_type = 0
            obstacle_width = 0
            obstacle_height = 0
            height_diff = 0
            distance_x = self.settings.SCREEN_WIDTH
            distance_normalized = 1.0  # Normalizado entre 0 e 1
            next_obstacle_distance = self.settings.SCREEN_WIDTH * 2  # Distância para o segundo obstáculo
            game_speed_normalized = self.settings.game_speed / self.settings.MAX_GAME_SPEED

            # Se temos um obstáculo próximo, obter suas informações
            if closest_obstacle:
                if isinstance(closest_obstacle, Bird):
                    obstacle_type = 2
                elif isinstance(closest_obstacle, LargeCactus):
                    obstacle_type = 1
                else:
                    obstacle_type = 0

                obstacle_width = closest_obstacle.rect.width
                obstacle_height = closest_obstacle.rect.height
                height_diff = dinosaur.rect.y - closest_obstacle.rect.y
                distance_x = closest_obstacle.rect.x - dinosaur.rect.x

                # Normalizar a distância (ajuda a rede neural)
                distance_normalized = max(0, min(1, distance_x / self.settings.SCREEN_WIDTH))

                # Encontrar a distância para o próximo obstáculo (se houver)
                if len(self.obstacles) > 1:
                    next_obstacles = [o for o in self.obstacles if o.rect.x > closest_obstacle.rect.x]
                    if next_obstacles:
                        next_obstacle_distance = next_obstacles[0].rect.x - dinosaur.rect.x

            # Inputs expandidos para a rede neural
            output = self.nets[i].activate((
                dinosaur.rect.y / self.settings.SCREEN_HEIGHT,  # Altura normalizada
                distance_normalized,  # Distância normalizada para o obstáculo mais próximo
                height_diff / self.settings.SCREEN_HEIGHT,  # Diferença de altura normalizada
                obstacle_width / self.settings.SCREEN_WIDTH,  # Largura do obstáculo normalizada
                obstacle_height / self.settings.SCREEN_HEIGHT,  # Altura do obstáculo normalizada
                obstacle_type / 2,  # Tipo de obstáculo normalizado (0, 0.5, ou 1)
                next_obstacle_distance / (self.settings.SCREEN_WIDTH * 2),  # Distância para o próximo obstáculo
                game_speed_normalized,  # Velocidade do jogo normalizada
                dinosaur.jumping / 1,  # Estado atual de pulo (0 ou 1)
                dinosaur.ducking / 1  # Estado atual de agachamento (0 ou 1)
            ))

            # Interpretar as saídas da rede neural
            if closest_obstacle:
                # Lógica melhorada para pássaros:
                if isinstance(closest_obstacle, Bird):
                    # Verificar a altura do pássaro para decidir entre pular ou agachar
                    bird_y = closest_obstacle.rect.y
                    bird_height = closest_obstacle.rect.height

                    # Pássaros mais baixos requerem pulo
                    if bird_y + bird_height > dinosaur.NORMAL_Y - 30:
                        if output[0] > 0.5 and dinosaur.rect.y == dinosaur.NORMAL_Y and not dinosaur.jumping:
                            dinosaur.duck()
                            # Recompensar o pulo correto para pássaros baixos
                            self.ge[i].fitness += 0.3 #original = 0.3
                    # Pássaros mais altos requerem agachamento
                    else:
                        if output[1] > 0.5 and not dinosaur.jumping:
                            dinosaur.duck()
                            # Recompensar o agachamento correto para pássaros altos
                            self.ge[i].fitness += 0.5 #original = 0.3
                        elif output[1] <= 0.5 and dinosaur.ducking:
                            dinosaur.stop_duck()
                # Lógica para cactos (sempre pular):
                else:
                    # Decidir pular baseado na distância e largura do cacto
                    jump_threshold = max(0.4, 0.7 - (self.settings.game_speed / 100))

                    # Pular apenas se o obstáculo estiver próximo o suficiente
                    if distance_x < 250 and output[0] > jump_threshold and dinosaur.rect.y == dinosaur.NORMAL_Y:
                        dinosaur.jump()
                        # Recompensar por pular obstáculos corretamente
                        if not isinstance(closest_obstacle, Bird):
                            self.ge[i].fitness += 0.2

                    # Penalizar por agachar com cactos (deve pular)
                    if output[1] > 0.5 and not dinosaur.jumping:
                        dinosaur.duck()
                        # Pequena penalização por agachar com cactos
                        self.ge[i].fitness -= 0.05
                    elif output[1] <= 0.5 and dinosaur.ducking:
                        dinosaur.stop_duck()

            # Se não há obstáculos próximos, voltar a correr normalmente
            else:
                if dinosaur.ducking:
                    dinosaur.stop_duck()

    def save_best_genome(self):
        """Salva o melhor genoma da geração atual"""
        if not self.ge:
            return

        best_genome = max(self.ge, key=lambda g: g.fitness)

        with open('best_genome.pkl', 'wb') as f:
            pickle.dump(best_genome, f)

        print(f"Melhor genoma salvo! Fitness: {best_genome.fitness:.2f}")

    def run_neat(self, config_path, num_generations=50):
        """Executa o algoritmo NEAT"""
        # Configurar NEAT
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )

        # Criar população
        self.population = neat.Population(config)

        # Adicionar reporters para estatísticas
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)

        # Executar NEAT
        winner = self.population.run(self.eval_genomes, num_generations)

        # Salvar o melhor genoma
        with open('winner.pkl', 'wb') as f:
            pickle.dump(winner, f)

        print(f"Melhor genoma: {winner}")

        # Visualizar estatísticas
        plot_stats(stats, ylog=False, view=True)
        draw_neural_network(config, winner, view=True)

        return winner

    def run_winner(self, config_path, genome_path='winner.pkl'):
        """Executa o melhor genoma"""
        # Carregar configuração
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )

        # Carregar genoma
        with open(genome_path, 'rb') as f:
            genome = pickle.load(f)

        # Criar rede neural
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Criar dinossauro
        dinosaur = Dinosaur(self.settings.RUNNING[0], self.settings)

        # Configuração inicial
        self.points = 0
        self.obstacles = []
        self.settings.game_speed = self.settings.INITIAL_GAME_SPEED

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Limpar a tela
            self.screen.fill((255, 255, 255))

            # Atualizar e desenhar dinossauro
            dinosaur.update()
            dinosaur.draw(self.screen)

            # Gerar obstáculos
            self.generate_obstacles()

            # Atualizar e desenhar obstáculos
            for obstacle in list(self.obstacles):
                obstacle.draw(self.screen)
                obstacle.update(self.settings.game_speed)

                if obstacle.rect.x < -obstacle.rect.width:
                    self.obstacles.remove(obstacle)

                # Verificar colisão
                if dinosaur.check_collision(obstacle):
                    run = False
                    break

            # Encontrar o obstáculo mais próximo
            closest_obstacle = None
            closest_distance = float('inf')

            for obstacle in self.obstacles:
                if obstacle.rect.x > dinosaur.rect.x:
                    distance = obstacle.rect.x - dinosaur.rect.x
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_obstacle = obstacle

            # Definir valores padrão
            obstacle_type = 0
            obstacle_width = 0
            obstacle_height = 0
            height_diff = 0
            distance_normalized = 1.0
            next_obstacle_distance = self.settings.SCREEN_WIDTH * 2
            game_speed_normalized = self.settings.game_speed / self.settings.MAX_GAME_SPEED

            # Se temos um obstáculo próximo
            if closest_obstacle:
                if isinstance(closest_obstacle, Bird):
                    obstacle_type = 2
                elif isinstance(closest_obstacle, LargeCactus):
                    obstacle_type = 1
                else:
                    obstacle_type = 0

                obstacle_width = closest_obstacle.rect.width
                obstacle_height = closest_obstacle.rect.height
                height_diff = dinosaur.rect.y - closest_obstacle.rect.y
                distance_x = closest_obstacle.rect.x - dinosaur.rect.x

                # Normalizar a distância
                distance_normalized = max(0, min(1, distance_x / self.settings.SCREEN_WIDTH))

                # Próximo obstáculo
                if len(self.obstacles) > 1:
                    next_obstacles = [o for o in self.obstacles if o.rect.x > closest_obstacle.rect.x]
                    if next_obstacles:
                        next_obstacle_distance = next_obstacles[0].rect.x - dinosaur.rect.x

            # Ativar a rede neural
            output = net.activate((
                dinosaur.rect.y / self.settings.SCREEN_HEIGHT,
                distance_normalized,
                height_diff / self.settings.SCREEN_HEIGHT,
                obstacle_width / self.settings.SCREEN_WIDTH,
                obstacle_height / self.settings.SCREEN_HEIGHT,
                obstacle_type / 2,
                next_obstacle_distance / (self.settings.SCREEN_WIDTH * 2),
                game_speed_normalized,
                dinosaur.jumping / 1,
                dinosaur.ducking / 1
            ))

            # Executar ações baseadas na saída da rede
            if output[0] > 0.5 and dinosaur.rect.y == dinosaur.NORMAL_Y and not dinosaur.jumping:
                dinosaur.jump()

            if output[1] > 0.5 and not dinosaur.jumping:
                dinosaur.duck()
            elif output[1] <= 0.5 and dinosaur.ducking:
                dinosaur.stop_duck()

            # Desenhar informações do jogo
            score_text = self.large_font.render(f'Pontuação: {self.points}', True, (0, 0, 0))
            speed_text = self.font.render(f'Velocidade: {self.settings.game_speed:.1f}', True, (0, 100, 0))

            self.screen.blit(score_text, (self.settings.SCREEN_WIDTH // 2 - 100, 50))
            self.screen.blit(speed_text, (self.settings.SCREEN_WIDTH // 2 - 100, 100))

            # Atualizar pontuação
            self.points += 1
            if self.points % 100 == 0 and self.settings.game_speed < self.settings.MAX_GAME_SPEED:
                self.settings.game_speed += 0.5

            # Desenhar fundo
            self.draw_background()

            # Atualizar tela
            self.clock.tick(30)
            pygame.display.update()


# dinosaur.py - Classe do dinossauro
# obstacles.py - Classes para os obstáculos
# game_settings.py - Configurações do jogo
# visualization.py - Ferramentas para visualização e estatísticas
# Arquivo principal para executar o jogo
if __name__ == '__main__':
    import os

    # Inicializar o jogo
    game = Game()

    # Verificar argumentos de linha de comando
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'run_winner':
            # Executar o melhor genoma treinado
            config_path = os.path.join(os.path.dirname(__file__), 'config.txt')
            game.run_winner(config_path)
        else:
            print("Comando não reconhecido")
            print("Uso: python main.py [run_winner]")
            sys.exit(1)
    else:
        # Treinar novo modelo
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config.txt')
        game.run_neat(config_path, num_generations=50)
