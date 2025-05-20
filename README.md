README: T-Rex Runner com NEAT AI
Este projeto implementa uma versão do famoso jogo do dinossauro T-Rex do Chrome, integrado com inteligência artificial usando o algoritmo NEAT (NeuroEvolution of Augmenting Topologies).
Funcionalidades

Jogo T-Rex Runner:

Sistema de pontuação baseado em distância percorrida
Obstáculos: cactos pequenos, cactos grandes e pássaros
Aumento progressivo de dificuldade


Inteligência Artificial com NEAT:

Evolução neural para aprender a jogar automaticamente
Visualização das redes neurais e estatísticas de treinamento
Possibilidade de salvar e carregar modelos treinados


Melhorias do Código Original:

Organização em classes separadas (MVC)
Física de jogo aprimorada
Sistema de colisão pixel-perfect
Balanceamento de obstáculos e dificuldade
Caching de máscaras para otimização



Estrutura do Projeto <br>
├── main.py            # Arquivo principal <br>
├── dinosaur.py        # Classe do dinossauro <br>
├── obstacles.py       # Classes de obstáculos <br>
├── game_settings.py   # Configurações do jogo <br>
├── visualization.py   # Ferramentas de visualização <br>
├── config.txt         # Configuração da rede neural NEAT <br>
└── Assets/            # Diretório de recursos <br>
    ├── Bird/ <br>
    ├── Cactus/ <br>
    ├── Dino/ <br>
    └── Other/ <br>
Entradas e Saídas da IA
Entradas (10 valores)

Altura normalizada do dinossauro
Distância normalizada ao obstáculo mais próximo
Diferença de altura normalizada
Largura do obstáculo normalizada
Altura do obstáculo normalizada
Tipo de obstáculo normalizado (0=Cacto Pequeno, 0.5=Cacto Grande, 1=Pássaro)
Distância para o próximo obstáculo
Velocidade do jogo normalizada
Estado de pulo (0 ou 1)
Estado de agachamento (0 ou 1)

Saídas (2 valores)

Pular (>0.5 para ativar)
Agachar (>0.5 para ativar)

Como Executar
Requisitos

Python 3.6+
Pygame
NEAT-Python
Matplotlib
Graphviz (opcional, para visualização)

Instalação
pip install pygame neat-python matplotlib graphviz
Executar Treinamento
python main.py
Executar Melhor Modelo Treinado
python main.py run_winner
Melhorias Implementadas
Física de Jogo

Ajuste dinâmico da gravidade baseado na velocidade do jogo
Sistema de pulo mais consistente e realista
Transição suave entre estados (correr, pular, agachar)

Sistema NEAT

Entradas expandidas e normalizadas
Sistema de recompensa mais sofisticado
Análise específica do tipo de obstáculo

Obstáculos

Balanceamento de frequência (mais pássaros em níveis avançados)
Alturas variadas para pássaros
Espaçamento dinâmico entre obstáculos

Interface e Visualização

Indicadores visuais de desempenho
Opção para visualizar redes neurais
Gráficos de evolução do fitness

Referências

NEAT-Python Documentation
Pygame Documentation
Chrome Dino Game
Paper: NEAT Algorithm

Autor
Este projeto foi melhorado com a assistência de Claude.