import random

import time

from collections import deque
from viewer import MazeViewer
from math import inf, sqrt


def gera_labirinto(n_linhas, n_colunas, inicio, goal):
    # cria labirinto vazio
    labirinto = [[0] * n_colunas for _ in range(n_linhas)]

    # adiciona celulas ocupadas em locais aleatorios de
    # forma que 50% do labirinto esteja ocupado
    numero_de_obstaculos = int(0.50 * n_linhas * n_colunas)
    for _ in range(numero_de_obstaculos):
        linha = random.randint(0, n_linhas-1)
        coluna = random.randint(0, n_colunas-1)
        labirinto[linha][coluna] = 1

    # remove eventuais obstaculos adicionados na posicao
    # inicial e no goal
    labirinto[inicio.y][inicio.x] = 0
    labirinto[goal.y][goal.x] = 0

    return labirinto


class Celula:
    def __init__(self, y, x, anterior):
        self.y = y
        self.x = x
        self.anterior = anterior


def distancia(celula_1, celula_2):
    dx = celula_1.x - celula_2.x
    dy = celula_1.y - celula_2.y
    return sqrt(dx ** 2 + dy ** 2)


def esta_contido(lista, celula):
    for elemento in lista:
        if (elemento.y == celula.y) and (elemento.x == celula.x):
            return True
    return False


def custo_caminho(caminho):
    if len(caminho) == 0:
        return inf

    custo_total = 0
    for i in range(1, len(caminho)):
        custo_total += distancia(caminho[i].anterior, caminho[i])

    return custo_total


def obtem_caminho(goal):
    caminho = []

    celula_atual = goal
    while celula_atual is not None:
        caminho.append(celula_atual)
        celula_atual = celula_atual.anterior

    # o caminho foi gerado do final para o
    # comeco, entao precisamos inverter.
    caminho.reverse()

    return caminho


def print_resultado(titulo, caminho, custo_total, expandidos, gerados, tempo):
    print(
        f"{titulo}:"
        f"\tTempo de execução: {tempo}.\n"
        f"\tTamanho do caminho: {len(caminho)-1}.\n"
        f"\tCusto total do caminho: {custo_total}.\n"
        f"\tNumero total de nos expandidos: {len(expandidos)}.\n"
        f"\tNumero total de gerados: {len(gerados)}.\n\n"
    )


def celulas_vizinhas_livres(celula_atual, labirinto):
    # generate neighbors of the current state
    vizinhos = [
        Celula(y=celula_atual.y-1, x=celula_atual.x-1, anterior=celula_atual),
        Celula(y=celula_atual.y+0, x=celula_atual.x-1, anterior=celula_atual),
        Celula(y=celula_atual.y+1, x=celula_atual.x-1, anterior=celula_atual),
        Celula(y=celula_atual.y-1, x=celula_atual.x+0, anterior=celula_atual),
        Celula(y=celula_atual.y+1, x=celula_atual.x+0, anterior=celula_atual),
        Celula(y=celula_atual.y+1, x=celula_atual.x+1, anterior=celula_atual),
        Celula(y=celula_atual.y+0, x=celula_atual.x+1, anterior=celula_atual),
        Celula(y=celula_atual.y-1, x=celula_atual.x+1, anterior=celula_atual),
    ]

    # seleciona as celulas livres
    vizinhos_livres = []
    for v in vizinhos:
        # verifica se a celula esta dentro dos limites do labirinto
        if (v.y < 0) or (v.x < 0) or (v.y >= len(labirinto)) or (v.x >= len(labirinto[0])):
            continue
        # verifica se a celula esta livre de obstaculos.
        if labirinto[v.y][v.x] == 0:
            vizinhos_livres.append(v)

    return vizinhos_livres


def breadth_first_search(labirinto, inicio, goal, viewer):
    # nos gerados e que podem ser expandidos (vermelhos)
    fronteira = deque()
    # nos ja expandidos (amarelos)
    expandidos = set()
    # nos gerados no total
    gerados = []

    # adiciona o no inicial na fronteira
    fronteira.append(inicio)

    # variavel para armazenar o goal quando ele for encontrado.
    goal_encontrado = None

    # Repete enquanto nos nao encontramos o goal e ainda
    # existem para serem expandidos na fronteira. Se
    # acabarem os nos da fronteira antes do goal ser encontrado,
    # entao ele nao eh alcancavel.
    while (len(fronteira) > 0) and (goal_encontrado is None):

        # seleciona o no mais antigo para ser expandido
        no_atual = fronteira.popleft()

        # busca os vizinhos do no
        vizinhos = celulas_vizinhas_livres(no_atual, labirinto)

        # para cada vizinho verifica se eh o goal e adiciona na
        # fronteira se ainda nao foi expandido e nao esta na fronteira
        for v in vizinhos:
            if v.y == goal.y and v.x == goal.x:
                goal_encontrado = v
                # encerra o loop interno
                break
            else:
                if (not esta_contido(expandidos, v)) and (not esta_contido(fronteira, v)):
                    fronteira.append(v)
                    gerados.append(v)

        expandidos.add(no_atual)

        viewer.update(generated=fronteira,
                      expanded=expandidos)
        # viewer.pause()

    caminho = obtem_caminho(goal_encontrado)
    custo = custo_caminho(caminho)

    return caminho, custo, expandidos, gerados

def depth_first_search(labirinto, inicio, goal, viewer):
    # nos gerados e que podem ser expandidos (vermelhos)
    pilha = deque()
    # nos ja expandidos (amarelos)
    expandidos = set()
    # nos gerados no total
    gerados = []

    # adiciona o no inicial na pilha
    pilha.append(inicio)

    # variavel para armazenar o goal quando ele for encontrado.
    goal_encontrado = None

    # Repete enquanto nos nao encontramos o goal e ainda
    # existem para serem expandidos na pilha. Se
    # acabarem os nos da pilha antes do goal ser encontrado,
    # entao ele nao eh alcancavel.
    while (len(pilha) > 0) and (goal_encontrado is None):

        # seleciona o no mais novo para ser expandido
        no_atual = pilha.pop()

        # busca os vizinhos do no
        vizinhos = celulas_vizinhas_livres(no_atual, labirinto)

        # para cada vizinho verifica se eh o goal e adiciona na
        # pilha se ainda nao foi expandido e nao esta na pilha
        for v in vizinhos:
            if v.y == goal.y and v.x == goal.x:
                goal_encontrado = v
                # encerra o loop interno
                break
            else:
                if (not esta_contido(expandidos, v)) and (not esta_contido(pilha, v)):
                    pilha.append(v)
                    gerados.append(v)

        expandidos.add(no_atual)

        viewer.update(generated=pilha,
                      expanded=expandidos)
        # viewer.pause()

    caminho = obtem_caminho(goal_encontrado)
    custo = custo_caminho(caminho)

    return caminho, custo, expandidos, gerados

def uniform_cost_search(labirinto, inicio, goal, viewer):
    # nos gerados e que podem ser expandidos (vermelhos)
    fronteira = []
    # nos ja expandidos (amarelos)
    expandidos = set()
    # nos gerados no total
    gerados = []

    # adiciona o no inicial na fronteira
    fronteira.append(inicio)

    # variavel para armazenar o goal quando ele for encontrado.
    goal_encontrado = None

    # Repete enquanto nos nao encontramos o goal e ainda
    # existem para serem expandidos na fronteira. Se
    # acabarem os nos da fronteira antes do goal ser encontrado,
    # entao ele nao eh alcancavel.
    while (len(fronteira) > 0) and (goal_encontrado is None):

        # seleciona o no de menor custo para ser expandido
        no_atual = fronteira.pop(0)

        # busca os vizinhos do no
        vizinhos = celulas_vizinhas_livres(no_atual, labirinto)

        # para cada vizinho verifica se eh o goal e adiciona na
        # fronteira se ainda nao foi expandido e nao esta na fronteira
        for v in vizinhos:
            if v.y == goal.y and v.x == goal.x:
                goal_encontrado = v
                # encerra o loop interno
                break
            else:
                if (not esta_contido(expandidos, v)) and (not esta_contido(fronteira, v)):
                    fronteira.append(v)
                    gerados.append(v)

        expandidos.add(no_atual)

        def obtemCustoProximoNo(prox_no: Celula):
            return custo_caminho(obtem_caminho(prox_no))

        fronteira.sort(key = obtemCustoProximoNo)

        viewer.update(generated=fronteira,
                      expanded=expandidos)
        # viewer.pause()

    caminho = obtem_caminho(goal_encontrado)
    custo = custo_caminho(caminho)

    return caminho, custo, expandidos, gerados

def a_star_search(labirinto, inicio, goal, viewer):
    # nos gerados e que podem ser expandidos (vermelhos)
    fronteira = []
    # nos ja expandidos (amarelos)
    expandidos = set()
    # nos gerados no total
    gerados = []

    # adiciona o no inicial na fronteira
    fronteira.append(inicio)

    # variavel para armazenar o goal quando ele for encontrado.
    goal_encontrado = None

    # Repete enquanto nos nao encontramos o goal e ainda
    # existem para serem expandidos na fronteira. Se
    # acabarem os nos da fronteira antes do goal ser encontrado,
    # entao ele nao eh alcancavel.
    while (len(fronteira) > 0) and (goal_encontrado is None):

        # seleciona o no de menor custo para ser expandido
        no_atual = fronteira.pop(0)

        # busca os vizinhos do no
        vizinhos = celulas_vizinhas_livres(no_atual, labirinto)

        # para cada vizinho verifica se eh o goal e adiciona na
        # fronteira se ainda nao foi expandido e nao esta na fronteira
        for v in vizinhos:
            if v.y == goal.y and v.x == goal.x:
                goal_encontrado = v
                # encerra o loop interno
                break
            else:
                if (not esta_contido(expandidos, v)) and (not esta_contido(fronteira, v)):
                    fronteira.append(v)
                    gerados.append(v)

        expandidos.add(no_atual)

        def obtemCustoEHeuristica(prox_no: Celula):
            return custo_caminho(obtem_caminho(prox_no)) + distancia(prox_no, goal)

        fronteira.sort(key = obtemCustoEHeuristica)

        viewer.update(generated=fronteira,
                      expanded=expandidos)
        # viewer.pause()

    caminho = obtem_caminho(goal_encontrado)
    custo = custo_caminho(caminho)

    return caminho, custo, expandidos, gerados


# -------------------------------


def main():
    SEED = None  # coloque None para deixar aleatorio OU 42 para fixo
    random.seed(SEED)
    N_LINHAS = 20
    N_COLUNAS = 20
    STEP_TIME_MILISECONDS = 20
    ZOOM = 10
    INICIO = Celula(y=0, x=0, anterior=None)
    GOAL = Celula(y=N_LINHAS-1, x=N_COLUNAS-1, anterior=None)

    """
    O labirinto sera representado por uma matriz (lista de listas)
    em que uma posicao tem 0 se ela eh livre e 1 se ela esta ocupada.
    """
    labirinto = gera_labirinto(N_LINHAS, N_COLUNAS, INICIO, GOAL)

    # ----------------------------------------
    # BFS Search
    # ----------------------------------------
    viewerBFS = MazeViewer(labirinto, INICIO, GOAL, titulo_janela="BFS",
                            step_time_miliseconds = STEP_TIME_MILISECONDS, zoom = ZOOM)
    
    # Iniciando Contator
    inicio = time.time()

    caminho, custo_total, expandidos, gerados = \
        breadth_first_search(labirinto, INICIO, GOAL, viewerBFS)
    
    # Terminando contador
    fim = time.time()
    tempo = round(fim - inicio, 2)

    if len(caminho) == 0:
        print("Goal é inalcançavel neste labirinto.")
        return

    # PRINT DOS RESULTADOS DO BFS
    print_resultado("BFS", caminho, custo_total, expandidos, gerados, tempo)

    viewerBFS.update(path=caminho)

    # ----------------------------------------
    # DFS Search
    # ----------------------------------------
    viewerDFS = MazeViewer(labirinto, INICIO, GOAL, titulo_janela="DFS",
                            step_time_miliseconds = STEP_TIME_MILISECONDS, zoom = ZOOM)
    
    # Iniciando Contator
    inicio = time.time()

    caminho, custo_total, expandidos, gerados = \
        depth_first_search(labirinto, INICIO, GOAL, viewerDFS)
    
    # Terminando contador
    fim = time.time()
    tempo = round(fim - inicio, 2)

    if len(caminho) == 0:
        print("Goal é inalcançavel neste labirinto.")
        return

    # PRINT DOS RESULTADOS DO DFS
    print_resultado("DFS", caminho, custo_total, expandidos, gerados, tempo)

    viewerDFS.update(path=caminho)

    # ----------------------------------------
    # Uniform Cost Search
    # ----------------------------------------
    viewerUCS = MazeViewer(labirinto, INICIO, GOAL, titulo_janela="UCS",
                                step_time_miliseconds = STEP_TIME_MILISECONDS, zoom = ZOOM)

    # Iniciando Contator
    inicio = time.time()
    
    caminho, custo_total, expandidos, gerados = \
        uniform_cost_search(labirinto, INICIO, GOAL, viewerUCS)

    # Terminando contador
    fim = time.time()
    tempo = round(fim - inicio, 2)
    
    if len(caminho) == 0:
        print("Goal é inalcançavel neste labirinto.")
        return

    # PRINT DOS RESULTADOS DO UCS
    print_resultado("UCS", caminho, custo_total, expandidos, gerados, tempo)

    viewerUCS.update(path=caminho)

    # ----------------------------------------
    # A-Star Search
    # ----------------------------------------
    viewerAStar = MazeViewer(labirinto, INICIO, GOAL, titulo_janela="A*",
                                step_time_miliseconds = STEP_TIME_MILISECONDS, zoom = ZOOM)
    
    
    # Iniciando Contator
    inicio = time.time()

    caminho, custo_total, expandidos, gerados = \
        a_star_search(labirinto, INICIO, GOAL, viewerAStar)
    
    # Terminando contador
    fim = time.time()
    tempo = round(fim - inicio, 2)

    if len(caminho) == 0:
        print("Goal é inalcançavel neste labirinto.")
        return

    # PRINT DOS RESULTADOS DO A*
    print_resultado("A*", caminho, custo_total, expandidos, gerados, tempo)

    viewerAStar.update(path=caminho)

    print("OK! Pressione alguma tecla pra finalizar...")
    input()


if __name__ == "__main__":
    main()
