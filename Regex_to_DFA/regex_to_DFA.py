import re
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx

class NFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

def regex_to_nfa(regex):
    states = set()
    alphabet = set()
    transitions = defaultdict(list)
    start_state = 0
    accept_states = set()

    current_state = 0
    for i, char in enumerate(regex):
        if char == '*':
            if i > 0:
                prev_char = regex[i-1]
                transitions[(current_state-1, prev_char)].append(current_state-1)
                transitions[(current_state-1, '')].append(current_state)
        elif char not in {'(', ')', '|'}:  # Basic character
            states.add(current_state)
            states.add(current_state + 1)
            alphabet.add(char)
            transitions[(current_state, char)].append(current_state + 1)
            if i < len(regex) - 1 and regex[i+1] == '*':
                transitions[(current_state, '')].append(current_state + 1)
            current_state += 1

    accept_states.add(current_state)
    states.add(current_state)

    return NFA(states, alphabet, transitions, start_state, accept_states)

def epsilon_closure(nfa, states):
    closure = set(states)
    stack = list(states)
    while stack:
        state = stack.pop()
        for next_state in nfa.transitions.get((state, ''), []):
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return frozenset(closure)

def nfa_to_dfa(nfa):
    dfa_states = set()
    dfa_alphabet = nfa.alphabet
    dfa_transitions = {}
    dfa_start_state = epsilon_closure(nfa, {nfa.start_state})
    dfa_accept_states = set()

    worklist = [dfa_start_state]
    state_mapping = {dfa_start_state: 0}
    current_dfa_state = 1

    while worklist:
        current_states = worklist.pop(0)
        dfa_states.add(state_mapping[current_states])

        if any(state in nfa.accept_states for state in current_states):
            dfa_accept_states.add(state_mapping[current_states])

        for char in dfa_alphabet:
            next_states = set()
            for state in current_states:
                next_states.update(nfa.transitions.get((state, char), []))
            next_states = epsilon_closure(nfa, next_states)

            if next_states:
                if next_states not in state_mapping:
                    state_mapping[next_states] = current_dfa_state
                    current_dfa_state += 1
                    worklist.append(next_states)

                dfa_transitions[(state_mapping[current_states], char)] = state_mapping[next_states]

    return DFA(set(range(len(state_mapping))), dfa_alphabet, dfa_transitions, 0, dfa_accept_states)

def visualize_dfa(dfa, filename):
    G = nx.DiGraph()
    
    # Add nodes
    for state in dfa.states:
        if state in dfa.accept_states:
            G.add_node(state, accepting=True)
        else:
            G.add_node(state, accepting=False)
    
    # Add edges
    for (from_state, char), to_state in dfa.transitions.items():
        G.add_edge(from_state, to_state, label=char)
    
    # Set up the plot
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700)
    nx.draw_networkx_nodes(G, pos, nodelist=dfa.accept_states, node_color='lightgreen', node_size=700)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)
    
    # Add labels
    nx.draw_networkx_labels(G, pos)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # Highlight start state
    plt.scatter(pos[dfa.start_state][0], pos[dfa.start_state][1], s=800, color='none', edgecolor='r', linewidth=2)
    
    plt.title("DFA Visualization")
    plt.axis('off')
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(f"{filename}.png")
    print(f"DFA image saved as {filename}.png")
    
    # Close the plot to free up memory
    plt.close()

def main():
    regex = input("Enter a regular expression: ")
    nfa = regex_to_nfa(regex)
    dfa = nfa_to_dfa(nfa)
    visualize_dfa(dfa, "dfa_output")

if __name__ == "__main__":
    main()