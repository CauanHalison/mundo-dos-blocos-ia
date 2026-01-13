import processing as pr
import heapq
from collections import deque

def bidirectional_search(actions, initial_state, goal_state):
    parents_foward = {initial_state: (None, None)}
    parents_backward = {goal_state: (None, None)}

    visited_states_foward = {initial_state: True}
    visited_states_backward = {goal_state: True}

    queue_foward = deque([initial_state])
    queue_backward = deque([goal_state])

    while queue_foward and queue_backward:
        current_state_foward = queue_foward.popleft()

        match_state = pr.check_intersection(current_state_foward, visited_states_backward)

        if match_state is not None:
            path_foward = pr.reconstruct_path(current_state_foward, parents_foward)
            path_backward = pr.reconstruct_path(match_state, parents_backward)
            return path_foward + path_backward[::-1], (len(visited_states_foward) + len(visited_states_backward))

        else:
            for action in actions:
                new_state_foward = pr.expand(action, current_state_foward, 'foward', visited_states_foward)

                if new_state_foward != None:
                    queue_foward.append(new_state_foward)
                    visited_states_foward[new_state_foward] = True
                    parents_foward[new_state_foward] = (current_state_foward, action['name'])


        current_state_backward = queue_backward.popleft()

        match_state = pr.check_intersection(current_state_backward, visited_states_foward)

        if match_state is not None:
            print('Encontro Backward -> Forward!')
            path_foward = pr.reconstruct_path(match_state, parents_foward)
            path_backward = pr.reconstruct_path(current_state_backward, parents_backward)
            return path_foward + path_backward[::-1], (len(visited_states_foward) + len(visited_states_backward))

        else:
            possible_states = {}

            for action in actions:
                new_state_backward = pr.expand(action, current_state_backward, 'backward', visited_states_backward)

                if new_state_backward != None:
                    possible_states[new_state_backward] = action

            inconsistent_states = set()

            for s in possible_states:
                for c in possible_states:
                    if s != c:
                        if possible_states[s]['preconditions'].intersection(possible_states[c]['posconditions']):
                            inconsistent_states.add(c)

            for s in possible_states:
                if s not in inconsistent_states:
                    queue_backward.append(s)
                    visited_states_backward[s] = True
                    parents_backward[s] = (current_state_backward, possible_states[s]['name'])

    return None

def bidirectional_search_heuristic(actions, initial_state, goal_state):
    parents_foward = {initial_state: (None, None)}
    parents_backward = {goal_state: (None, None)}

    visited_states_foward = {initial_state: True}
    visited_states_backward = {goal_state: True}
    
    open_set_foward = []
    
    g_foward = 0
    h_foward = pr.check_heuristic_bidirectional(initial_state, goal_state, initial_state, 'foward')
    f_foward = g_foward + h_foward
    heapq.heappush(open_set_foward,(f_foward, h_foward, frozenset(initial_state)))
    
    open_set_backward = []
    
    g_backward = 0
    h_backward = pr.check_heuristic_bidirectional(goal_state, goal_state, initial_state, 'backward')
    f_backward = g_backward + h_backward
    heapq.heappush(open_set_backward,(f_backward, h_backward, frozenset(goal_state)))
    
    while open_set_foward and open_set_backward:
        current_f_foward, current_h_foward,  current_state_foward = heapq.heappop(open_set_foward)
        current_g_foward = current_f_foward - current_h_foward

        match_state = pr.check_intersection(current_state_foward, visited_states_backward)

        if match_state is not None:
            print('Encontro Forward! -> Backward')
            path_foward = pr.reconstruct_path(current_state_foward, parents_foward)
            path_backward = pr.reconstruct_path(match_state, parents_backward)
            return path_foward + path_backward[::-1], (len(visited_states_foward) + len(visited_states_backward))

        else:
            for action in actions:
                new_state_foward = pr.expand(action, current_state_foward, 'foward', visited_states_foward)

                if new_state_foward != None:
                    new_g_foward = current_g_foward + 1
                    new_h_foward = pr.check_heuristic_bidirectional(new_state_foward, goal_state, initial_state, 'foward')
                    new_f_foward = new_g_foward + new_h_foward
                    
                    heapq.heappush(open_set_foward, (new_f_foward, new_h_foward, frozenset(new_state_foward)))                    
                    
                    visited_states_foward[new_state_foward] = True
                    parents_foward[new_state_foward] = (current_state_foward, action['name'])


        current_f_backward, current_h_backward, current_state_backward = heapq.heappop(open_set_backward)
        current_g_backward = current_f_backward - current_h_backward

        match_state = pr.check_intersection(current_state_backward, visited_states_foward)

        if match_state is not None:
            print('Encontro Backward -> Forward!')
            path_foward = pr.reconstruct_path(match_state, parents_foward)
            path_backward = pr.reconstruct_path(current_state_backward, parents_backward)
            return path_foward + path_backward[::-1], (len(visited_states_foward) + len(visited_states_backward))

        else:
            possible_states = {}

            for action in actions:
                new_state_backward = pr.expand(action, current_state_backward, 'backward', visited_states_backward)

                if new_state_backward != None:
                    possible_states[new_state_backward] = action

            for s in possible_states:
                new_g_backward = current_g_backward + 1
                new_h_backward = pr.check_heuristic_bidirectional(s, goal_state, initial_state, 'backward')
                new_f_backward = new_g_backward + new_h_backward
                
                heapq.heappush(open_set_backward, (new_f_backward, new_h_backward, frozenset(s))) 
                
                visited_states_backward[s] = True
                parents_backward[s] = (current_state_backward, possible_states[s]['name'])

    return None

pr.executar_com_metricas("Bidirecional", bidirectional_search, pr.actions_int, pr.initial_state_int, pr.goal_state_int)

pr.executar_com_metricas("Bidirecional Heurística", bidirectional_search_heuristic, pr.actions_int, pr.initial_state_int, pr.goal_state_int)