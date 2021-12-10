from regularexp import RegularExp

class Automata:
    def __init__(self, n, start_state, end_state_list, transition_list):
                
        # Create Adjacency Matrix
        self.adjacency_matrix = [[None for i in range(n+2)] for j in range(n+2)]
        # TRANSITION TUPLE
        # => str:regex, bool:RequiresParenthesis

        # Initalize normalized state
        # Normalized Start: n
        # Normalized End: n+1
        normalized_start_index = n
        normalized_end_index = n+1

        self.adjacency_matrix[normalized_start_index][start_state] = RegularExp("e") # Epsilon
        for state in end_state_list:
            self.adjacency_matrix[state][normalized_end_index] = RegularExp("e") # Epsilon transition


        # Inicializar transiciones
        for (state, transition, next) in transition_list:
            self.add_transition(state, transition, next)
        
    def add_transition(self, state, transition, next): # Método para añadir un estado al automata
        if self.adjacency_matrix[state][next] is None: 
            # New Transition
            self.adjacency_matrix[state][next] = RegularExp(str(transition), False)
        else:
            # NORMALIZACION de doble transicion
            self.adjacency_matrix[state][next] = RegularExp(str(transition), False)+self.adjacency_matrix[state][next]

    def display(self):
        print(end="\t")
        for j in range( len(self.adjacency_matrix[0]) ):
            print( j, end="\t")
        print()

        for i in range( len(self.adjacency_matrix) ):
            print(i, end = "\t")
            for j in range( len(self.adjacency_matrix[0]) ):
                print( self.adjacency_matrix[i][j], end="\t")
            print()
    
    # PREGUNTA 1:
    def get_regular_expression_AEE(self):
        n = len(self.adjacency_matrix)

        for s in range( n -2):
            # s = estado a remover

            # Declarando elemento de loop (*)
            if self.adjacency_matrix[s][s] is None:
                loop = RegularExp("", False)
            else:
                loop = self.adjacency_matrix[s][s].star()

            # Lista de todas las entras y salidas validas
            in_transitions = [i for i in range(s+1,n) if self.adjacency_matrix[i][s] is not None]
            out_transitions = [o for o in range(s+1,n) if self.adjacency_matrix[s][o] is not None]

            # Combinacion de todas las entradas validas con todas las salidas valdias
            for i in in_transitions:
                for o in out_transitions:
                    if self.adjacency_matrix[i][o] is None:
                        self.adjacency_matrix[i][o] = self.adjacency_matrix[i][s] ^ loop ^  self.adjacency_matrix[s][o] 
                    else:
                        self.adjacency_matrix[i][o] = self.adjacency_matrix[i][o] +  (self.adjacency_matrix[i][s] ^ loop ^ self.adjacency_matrix[s][o])
            
        return self.adjacency_matrix[n-2][n-1]

    # PREGUNTA 2:
    def get_regular_expression_HDM(self):
        # List of active states and iterable states
        n = len(self.adjacency_matrix)
        active_states = [i for i in range(n-2)]
        iterbale_states = [i for i in range(n)]

        for s in range( n - 2):
            ## TEST LOOP COUNTING:
            #print(self.count_cycles(active_states))
            #print("\n\n\n\n\n")


            # Get state of minimum weight
            minimum_weight_state = None
            minimum_weight_value = None
            for s in active_states:
                l = 0
                m = 0
                in_sum = 0
                out_sum = 0
                loop_len = 0

                for j in iterbale_states:
                    if (j == s):
                        # Loop
                        if (self.adjacency_matrix[s][s] is not None):
                            loop_len += len(self.adjacency_matrix[s][s])
                    else:
                        # In
                        if (self.adjacency_matrix[j][s] is not None):
                            m += 1
                            in_sum += len(self.adjacency_matrix[j][s])
                        # Out
                        if (self.adjacency_matrix[s][j] is not None):
                            l += 1
                            out_sum += len(self.adjacency_matrix[s][j])
                state_w = ((l-1) * in_sum) + ((m-1)*out_sum) + ((m*l - 1) * loop_len)
                if minimum_weight_state is None:
                    minimum_weight_state = s
                    minimum_weight_value = state_w
                elif minimum_weight_value > state_w:
                    minimum_weight_state = s
                    minimum_weight_value = state_w
            
            ## Delete state of minimum weight
            s = minimum_weight_state
            # Declarando elemento de loop (*)
            if self.adjacency_matrix[s][s] is None:
                loop = RegularExp("", False)
            else:
                loop = self.adjacency_matrix[s][s].star()
            # Delete currently deleting from iterables
            iterbale_states.remove(s)

            # Lista de todas las entras y salidas validas
            in_transitions = [i for i in iterbale_states if self.adjacency_matrix[i][s] is not None]
            out_transitions = [o for o in iterbale_states if self.adjacency_matrix[s][o] is not None]

            # Combinacion de todas las entradas validas con todas las salidas valdias
            for i in in_transitions:
                for o in out_transitions:
                    if self.adjacency_matrix[i][o] is None:
                        self.adjacency_matrix[i][o] = self.adjacency_matrix[i][s] ^ loop ^  self.adjacency_matrix[s][o] 
                    else:
                        self.adjacency_matrix[i][o] = self.adjacency_matrix[i][o] +  (self.adjacency_matrix[i][s] ^ loop ^ self.adjacency_matrix[s][o])

            # Delete from lists
            active_states.remove(s)

        return self.adjacency_matrix[n-2][n-1]

    # PREGUNTA 3:
    def count_cycles(self, iterbale_states):
        # O(n^2): Adycacency list
        ady_list = {a:[] for a in iterbale_states}
        for i in iterbale_states:
            for o in iterbale_states:
                if (self.adjacency_matrix[i][o] is not None):
                    ady_list[i].append(o)

        # O(n)*O(n) = O(n^2): Counting por estado
        count_dict = {}       
        for node in iterbale_states:
            # O(v+e) = O(v+2v) = O(v) = O(n): DFS counting cycles
            loops = {i:None for i in ady_list}
            loops[node] = True
            count = self.count_cycle_dfs(ady_list, loops, node, node, 0)
            # Save
            count_dict[node] = count
        return count_dict

    def count_cycle_dfs(self, ady_list, loops, node, objective, count):
        # Temporarily set current node as dead end (Unless it is origin)
        if (objective != node):
            loops[node] = False
            current_loops = False
        # Loop
        for s in ady_list[node]:
            if loops[s] is None: 
                # Needs to be explored
                count = self.count_cycle_dfs(ady_list, loops, s, objective, count)
            elif loops[s] is True: 
                # Next node loops
                count += 1
                current_loops = True
            else: #loops[s] is False: 
                # Next node is dead end
                pass
        # Set current node to appropiate loop status
        if (objective != node):
            loops[node] = current_loops
        # Return count
        return count