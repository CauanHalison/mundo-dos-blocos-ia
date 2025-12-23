from collections import deque
import heapq
import time           
import psutil
import os

def process_strips(file_name):
    #ler arquivo
    with open(file_name, 'r') as file:
        content = file.read()
        lines = content.splitlines()

    #processar arquivo
    actions = []

    for i in range(0, len(lines), 3):
        if lines[i] == '':
            initial_state = lines[i + 1].split(';')
            goal_state = lines[i + 2].split(';')
            break

        #Criando estrutura de ação, com o nome, precondições e póscondições
        action = {
            'name': lines[i],
            'preconditions': lines[i + 1].split(';'),
            'posconditions': lines[i + 2].split(';')
        }

        actions.append(action)

    #pre-processando goal_state
    handempty = True
    stacked_blocks = [] #guardo apenas os blocos empilhados

    for s in goal_state:
        if 'holding' in s:
            handempty = False #caso no estado final o braço esteja segurando algum bloco mão vazia falsa
        if 'on' in s:
            stacked_blocks.append(s)

    if handempty:
        goal_state.append('handempty')

    clear_blocks = {} #guardando um booleano para cada bloco, True = clear, False = tem outro bloco acima


    #Lógica para adicionar os estados faltantes no objetivo
    for b in stacked_blocks:
        block = b.split('_')[1]
        clear_blocks[block] = True

        for cb in stacked_blocks:
            if cb != b:
                compared_block = cb.split('_')[2]

                if compared_block == block:
                    clear_blocks[block] = False

    for b in clear_blocks:
        if clear_blocks[b]:
            goal_state.append('clear_'+b)

    base_blocks = []
    top_blocks = set()
    bot_blocks = set()

    for b in stacked_blocks:
        block1 = b.split('_')[1]
        block2 = b.split('_')[2]

        top_blocks.add(block1)
        bot_blocks.add(block2)

    base_blocks = bot_blocks - top_blocks.intersection(bot_blocks)

    for b in base_blocks:
        goal_state.append('ontable_'+b)


    return actions, initial_state, goal_state

def mapping(actions, initial_state, goal_state):
    #Coletando lista de todas as ações
    states = []

    for state in initial_state:
        if state not in states:
            states.append(state)

    for state in goal_state:
        if state not in states:
            states.append(state)




    for action in actions:
        if action not in states:
            for p in action['preconditions']:
                if p not in states:
                    states.append(p)
            for p in action['posconditions']:
                if p not in states:
                    states.append(p)

    #Eliminando negações da lista de estados

    clean_states = []
    for state in states:
        if state.startswith('~'):
            new_state = state[1:]
            if new_state not in clean_states:
                clean_states.append(new_state)
        else:
            if state not in clean_states:
                clean_states.append(state)

    #encodando estados
    encoded_states_int = {}
    encoded_int_states = {}
    for i, state in enumerate(clean_states, start=1):
        encoded_states_int[state] = i
        encoded_int_states[i] = state

    return encoded_states_int, encoded_int_states

def encode_actions(actions, mapping): #Fazendo o mapeamento de ação(String) para inteiros
    actions_int = []

    for action in actions:
        precond = set()
        poscond = set()

        for p in action['preconditions']:
            precond.add(mapping[p])

        for p in action['posconditions']:
            if p.startswith('~'):
                base = p[1:]
                poscond.add(-mapping[base])
            else:
                poscond.add(mapping[p])

        actions_int.append({
            'name': action['name'],
            'preconditions': precond,
            'posconditions': poscond
        })

    return (actions_int)

def encode_states(state, mapping): #atribui valores inteiros à cada estado 
    encoded_state = []

    for s in state:
        encoded_state.append(mapping[s])

    return frozenset(encoded_state)

def expand(action, state, direction, visited): #expansão utilizada nos algoritmos de busca direcional
    if direction == 'foward':
        if action['preconditions'].issubset(state):
            new_state = set(state)

            for p in action['posconditions']:
                if p > 0:
                    new_state.add(p)
                else:
                    new_state.discard(-p)

            frozen_new_state = frozenset(new_state)

            if not visited.get(frozen_new_state, False):
                return frozen_new_state
            return None

        return None

    else:
        poscond_add = set()
        poscond_del = set()

        for p in action['posconditions']:
            if p > 0:
                poscond_add.add(p)
            else:
                poscond_del.add(-p)

        if not poscond_add.issubset(state):
            return None

        if poscond_del.intersection(state):
            return None

        new_state = set(state)

        for p in action['preconditions']:
            new_state.add(p)

        intersec = poscond_add.intersection(state)

        for elem in intersec:
            new_state.discard(elem)

        frozen_new_state = frozenset(new_state)

        if not visited.get(frozen_new_state, False) and check_state(new_state):
            return frozen_new_state

        return None

def check_state(state): #Verificação de restições para o estado
    holding = []
    ontable = set()
    clear = set()
    handempty = False
    
    parents = {}
    children = {}
        
    for s in state:
        str_s = int_mapping_actions[s]
        
        parts = str_s.split('_')
        
        tipo = parts[0]
        
        if tipo =='handempty':
            handempty = True

        elif tipo == 'holding':        
            block = parts[1]
            holding.append(block)
            
        elif tipo == 'ontable':
            block = parts[1]
            ontable.add(block)
            
        elif tipo == 'clear':
            block = parts[1]
            clear.add(block)
            
        elif tipo == 'on':
            block_top = parts[1]
            block_bot = parts[2]
            
            if block_top in parents:
                return False
            
            parents[block_top] = block_bot
            
            if block_bot in children:
                return False
            
            elif block_bot in children.keys():
                return False
            
            children[block_bot] = block_top
            
    if len(holding) > 1:
        return False
    
    if handempty and len(holding) > 0:
        return False
    
    if not handempty and len(holding) == 0:
        return False
        
    for base in children.keys():
        if base in clear:
            return False
    
    for b in holding:
        if b in ontable or b in parents or b in children:
            return False
    
    return True

def check_intersection(state, oposition_queue):
    if state in oposition_queue:
        return state

    return None

def goal_test(node, goal_state):
    return all(goal in node for goal in goal_state)

def reconstruct_path(node, parents):
    path = []

    while node in parents:
        parent_state, action = parents[node]
        if action is None:
            break
        node = parent_state
        path.append(action)

    return path[::-1]

def check_heuristic(current_state, goal_state):
    heuristic_value = 0

    inter = current_state.intersection(goal_state)

    wrong_blocks = current_state - inter
    heuristic_value += len(wrong_blocks)

    false_correct_blocks = check_base(current_state, goal_state)

    heuristic_value += false_correct_blocks

    return heuristic_value

def check_heuristic_bidirectional(current_state, goal_state, initial_state, direction):
    heuristic_value = 0
    
    if direction == 'foward':
        objective = goal_state
    else:
        objective = initial_state    

    inter = current_state.intersection(objective)

    wrong_blocks = current_state - inter
    heuristic_value += len(wrong_blocks)

    false_correct_blocks = check_base(current_state, objective)

    heuristic_value += false_correct_blocks

    return heuristic_value

def check_base(state, goal_state): #lógica para verificar e determinar blocos que são falsos positivos dentro do meu estado atual, o estado em si está no objetivo mas não da forma que está no estado atual
    if state == goal_state:
        return 0

    bases = []
    correct_bases = 0

    for s in goal_state:
        if int_mapping_actions[s].startswith("ontable"):
            bases.append(s)

    for b in bases:
        base_block = int_mapping_actions[b].split('_')[1]

        while base_block != None:
            original_base = base_block
            for s in goal_state:
                str_state = int_mapping_actions[s]

                if str_state.startswith('on_') and str_state.split('_')[2] == base_block:
                    new_state = frozenset({actions_mapping_int[str_state]})
                    if new_state.issubset(state):
                        base_block = str_state.split('_')[1]
                        correct_bases += 1
                    else:
                        base_block = None
                        break
            if original_base == base_block:
                break

    stacked_blocks = 0
    for s in state:
        if int_mapping_actions[s].startswith('on_'):
            stacked_blocks += 1

    result = stacked_blocks - correct_bases

    return result*2

def executar_com_metricas(nome_algoritmo, funcao_busca, *args):
    print(f"\n{'='*10} Executando: {nome_algoritmo} {'='*10}")
    
    # 1. Inicia o monitoramento de memória e tempo
    process = psutil.Process(os.getpid())
    inicio_tempo = time.time()
    
    # 2. Executa o algoritmo
    resultado, visited_states = funcao_busca(*args)
    
    # 3. Para o monitoramento
    fim_tempo = time.time()
    
    # 4. Cálculos e Relatório
    tempo_total = fim_tempo - inicio_tempo
    pico_memoria = process.memory_info().peak_wset
    
    print(f"Tempo Final: {tempo_total:.6f} segundos")
    print(f"Uso de memória: {pico_memoria / 1024 / 1024:.2f} MB")
    print(f"Estados visitados: {visited_states}")
    print("-" * 40)
    
    if resultado:
        path = []
        # Tratamento especial para o IDDFS que retorna uma tupla (caminho, nivel)
        if isinstance(resultado, tuple):
            path = resultado[0]
            # print(f"Nível IDDFS atingido: {resultado[1]}") # opcional
        else:
            path = resultado

        print(f"\nSolução encontrada com {len(path)} passos:")
        for i, s in enumerate(path):
            print(f'{i}: {s}')
    else:
        print("\nNenhuma solução encontrada.")

# --- Bloco Principal ---

actions, initial_state, goal_state = process_strips('src/instancias.txt')
actions_mapping_int, int_mapping_actions = mapping(actions, initial_state, goal_state)

actions_int = encode_actions(actions, actions_mapping_int)
initial_state_int = encode_states(initial_state, actions_mapping_int)
goal_state_int = encode_states(goal_state, actions_mapping_int)