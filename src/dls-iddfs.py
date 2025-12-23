import processing as pr

def dls(actions_int, current_state_int, goal_state_int, limit, path, visited):
    if pr.goal_test(current_state_int, goal_state_int):
        return path, len(visited)
    if limit <= 0:
        return None

    for action in actions_int:
        if action['preconditions'].issubset(current_state_int):
            new_state = set(current_state_int)

            for p in action['posconditions']:
                if p > 0:
                    new_state.add(p)
                else:
                    new_state.discard(-p)

            frozen_new_state = frozenset(new_state)

            if frozen_new_state not in visited:
                visited.add(frozen_new_state)
                path.append(action['name'])

                result = dls(actions_int, frozen_new_state, goal_state_int, limit - 1, path, visited)

                if result is not None:
                    return result

                visited.remove(frozen_new_state)
                path.pop()

    return None

#implementação do busca em profundidade Iterativa
def iddfs(actions, current_state, goal_state, limit):
    for l in range(limit):
        result = dls(actions, current_state, goal_state, l, path = [], visited=set())

        if result is not None:
            return result, l

    return None, None

pr.executar_com_metricas("DLS", dls, pr.actions_int, pr.initial_state_int, pr.goal_state_int, 30, [], set())

pr.executar_com_metricas("IDDFS", iddfs, pr.actions_int, pr.initial_state_int, pr.goal_state_int, 300)