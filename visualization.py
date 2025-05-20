import matplotlib.pyplot as plt
import numpy as np
import graphviz
import neat


def plot_stats(statistics, ylog=False, view=False, filename='neat-stats.svg'):
    """Plot the population's average and best fitness."""
    if plt is None:
        warnings.warn("This display is not available due to a missing optional dependency (matplotlib)")
        return

    generation = range(len(statistics.most_fit_genomes))
    best_fitness = [c.fitness for c in statistics.most_fit_genomes]
    avg_fitness = np.array(statistics.get_fitness_mean())
    stdev_fitness = np.array(statistics.get_fitness_stdev())

    plt.figure(figsize=(12, 8))
    plt.plot(generation, avg_fitness, 'b-', label="average")
    plt.plot(generation, avg_fitness - stdev_fitness, 'g-.', label="-1 sd")
    plt.plot(generation, avg_fitness + stdev_fitness, 'g-.', label="+1 sd")
    plt.plot(generation, best_fitness, 'r-', label="best")

    plt.title("Population's average and best fitness")
    plt.xlabel("Generations")
    plt.ylabel("Fitness")
    plt.grid()
    plt.legend(loc="best")
    if ylog:
        plt.gca().set_yscale('symlog')

    plt.savefig(filename)
    if view:
        plt.show()

    plt.close()


def draw_neural_network(config, genome, view=False, filename='network.gv', node_names=None):
    """Visualizar a rede neural"""
    if graphviz is None:
        warnings.warn("This display is not available due to a missing optional dependency (graphviz)")
        return

    node_names = {
        -1: 'Altura Dino',
        -2: 'Distância',
        -3: 'Diferença Altura',
        -4: 'Largura Obstáculo',
        -5: 'Altura Obstáculo',
        -6: 'Tipo Obstáculo',
        -7: 'Próximo Obstáculo',
        -8: 'Velocidade',
        -9: 'Pulando',
        -10: 'Agachando',
        0: 'Pular',
        1: 'Agachar'
    }

    # Criar gráfico
    dot = graphviz.Digraph(format='svg', node_attr={'shape': 'circle', 'fontsize': '9'})
    dot.attr('node', shape='circle')

    # Adicionar os nós de entrada
    for k in config.genome_config.input_keys:
        name = node_names.get(k, str(k))
        input_color = 'lightblue'
        dot.node(str(k), name, style='filled', fillcolor=input_color)

    # Adicionar os nós ocultos e de saída
    for k in set([n.key for n in genome.nodes.values()]):
        if k in config.genome_config.output_keys:
            name = node_names.get(k, str(k))
            output_color = 'lightgreen'
            dot.node(str(k), name, style='filled', fillcolor=output_color)
        elif k not in config.genome_config.input_keys:
            dot.node(str(k))

    # Adicionar conexões
    for cg in genome.connections.values():
        if cg.enabled:
            input_node, output_node = cg.key
            # Calcular cor e espessura baseada no peso
            weight = cg.weight
            color = 'green' if weight > 0 else 'red'
            width = str(0.1 + abs(weight / 5.0))
            dot.edge(str(input_node), str(output_node), color=color, penwidth=width)

    dot.render(filename, view=view)
    return dot


