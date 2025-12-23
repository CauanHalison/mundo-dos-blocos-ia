import processing as pr
import heapq

def a_star(actions, initial_state, goal_state, mapping):
    actions_int = pr.encode_actions(actions, mapping)
    initial_state_int = pr.encode_states(initial_state, mapping)
    goal_state_int = pr.encode_states(goal_state, mapping)

    frozen_initial_state = frozenset(initial_state_int)

    start_g = 0
    start_h = pr.check_heuristic(frozen_initial_state, goal_state_int)
    start_f = start_g + start_h

    parents = {frozen_initial_state: (None, None)}

    open_set = []
    heapq.heappush(open_set, (start_f, start_h, frozen_initial_state))

    closed_set = set()  # conjunto de estados já explorados

    while open_set:
        f, h, current_state = heapq.heappop(open_set)

        g = f - h

        # se já visitado, pula
        if current_state in closed_set:
            continue

        closed_set.add(current_state)

        if pr.goal_test(current_state, goal_state_int):
            return pr.reconstruct_path(current_state, parents), len(closed_set)

        for action in actions_int:
            if action['preconditions'].issubset(current_state):
                new_state = set(current_state)

                for p in action['posconditions']:
                    if p > 0:
                        new_state.add(p)
                    else:
                        new_state.discard(-p)

                frozen_new_state = frozenset(new_state)

                if frozen_new_state not in closed_set:
                    parents[frozen_new_state] = (current_state, action['name'])

                    new_g = g + 1
                    new_h = pr.check_heuristic(frozen_new_state, goal_state_int)

                    new_f = new_g + new_h

                    heapq.heappush(open_set, (new_f, new_h, frozen_new_state))

    return None

pr.executar_com_metricas("A*", a_star, pr.actions, pr.initial_state, pr.goal_state, pr.actions_mapping_int)

