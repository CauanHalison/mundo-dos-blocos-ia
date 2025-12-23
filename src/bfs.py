import processing as pr
from collections import deque


def bfs(actions, initial_state, goal_state, mapping):

    actions_int = pr.encode_actions(actions, mapping)
    initial_state_int = pr.encode_states(initial_state, mapping)
    goal_state_int = pr.encode_states(goal_state, mapping)

    frozen_initial_state = frozenset(initial_state_int)

    queue = deque([frozen_initial_state])
    visited_states = {frozen_initial_state}

    parents = {frozen_initial_state: (None, None)} #Guandando dentro de um dicionario o  nó que originou esse estado e também a ação que originou ele

    while queue:
        current_node = queue.popleft()

        if pr.goal_test(current_node, goal_state_int):
            return pr.reconstruct_path(current_node, parents), len(visited_states)

        for action in actions_int:
            if action['preconditions'].issubset(current_node):
                new_state = set(current_node)

                for p in action['posconditions']:
                    if p > 0:
                        new_state.add(p)
                    else:
                        new_state.discard(-p)

                frozen_new_state = frozenset(new_state)

                if frozen_new_state not in visited_states:
                    visited_states.add(frozen_new_state)
                    parents[frozen_new_state] = (current_node, action['name'])
                    queue.append(frozen_new_state)

    return None

pr.executar_com_metricas('BFS', bfs, pr.actions, pr.initial_state, pr.goal_state, pr.actions_mapping_int)