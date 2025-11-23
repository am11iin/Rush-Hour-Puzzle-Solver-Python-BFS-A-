import csv
from collections import deque
import os
import pygame
import heapq
from itertools import count


# ---------------- CLASSES DU JEU ----------------

class Vehicle:
    def __init__(self, vid, x, y, orientation, length):
        self.id = vid
        self.x = x
        self.y = y
        self.orientation = orientation
        self.length = length

    def positions(self):
        if self.orientation == 'H':
            return [(self.x + i, self.y) for i in range(self.length)]
        else:
            return [(self.x, self.y + i) for i in range(self.length)]


class RushHourPuzzle:
    def __init__(self):
        self.board_height = 0
        self.board_width = 0
        self.vehicles = []
        self.board = []

    def setVehicles(self, csv_path):
        with open(csv_path, newline='') as csvfile:
            content = csvfile.read().strip()
            delimiter = ';' if ';' in content else ','
            csvfile.seek(0)
            reader = csv.reader(csvfile, delimiter=delimiter)
            rows = [r for r in reader if r]

        cleaned_rows = []
        for r in rows:
            r = [x.strip() for x in r if x.strip() != '']
            if len(r) > 0:
                cleaned_rows.append(r)

        if not cleaned_rows:
            raise ValueError("⚠️ Fichier vide ou invalide.")

        first = cleaned_rows[0]
        self.board_height = int(first[0])
        self.board_width = int(first[1])

        for r in cleaned_rows[1:]:
            if r[0].startswith('#'):
                continue
            if len(r) < 5:
                continue
            vid, x, y, orientation, length = [x.strip() for x in r[:5]]
            self.vehicles.append(Vehicle(vid, int(x), int(y), orientation.upper(), int(length)))

        self.setBoard()

    def setBoard(self):
        self.board = [[' ' for _ in range(self.board_width)] for _ in range(self.board_height)]
        for v in self.vehicles:
            for (x, y) in v.positions():
                if not (0 <= x < self.board_width and 0 <= y < self.board_height):
                    raise ValueError(f"⚠️ Le véhicule {v.id} dépasse du plateau ({x},{y}).")
                if self.board[y][x] != ' ':
                    raise ValueError(f"⚠️ Conflit entre véhicules en ({x},{y}).")
                self.board[y][x] = v.id

    def printBoard(self):
        for row in self.board:
            print(" ".join(row))
        print("-" * (2 * self.board_width - 1))

    def isGoal(self):
        for v in self.vehicles:
            if v.id == 'X':
                return v.x + v.length == self.board_width
        return False

    def successorFunction(self):
        successors = []
        for v in self.vehicles:
            if v.orientation == 'H':
                # gauche
                if v.x > 0 and self.board[v.y][v.x - 1] == ' ':
                    successors.append(((v.id, 'L'), self.move_vehicle(v.id, -1, 0)))
                # droite
                if v.x + v.length < self.board_width and self.board[v.y][v.x + v.length] == ' ':
                    successors.append(((v.id, 'R'), self.move_vehicle(v.id, 1, 0)))
            else:
                # haut
                if v.y > 0 and self.board[v.y - 1][v.x] == ' ':
                    successors.append(((v.id, 'U'), self.move_vehicle(v.id, 0, -1)))
                # bas
                if v.y + v.length < self.board_height and self.board[v.y + v.length][v.x] == ' ':
                    successors.append(((v.id, 'D'), self.move_vehicle(v.id, 0, 1)))
        return successors

    def move_vehicle(self, vid, dx, dy):
        new_vehicles = [Vehicle(v.id, v.x, v.y, v.orientation, v.length) for v in self.vehicles]
        for nv in new_vehicles:
            if nv.id == vid:
                nv.x += dx
                nv.y += dy
        new_state = RushHourPuzzle()
        new_state.board_height = self.board_height
        new_state.board_width = self.board_width
        new_state.vehicles = new_vehicles
        new_state.setBoard()
        return new_state


class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action

    def getSolution(self):
        node, actions = self, []
        while node and node.action:
            actions.append(node.action)
            node = node.parent
        return list(reversed(actions))


# ---------------- BFS ----------------

def bfs(start_state):
    start_node = Node(start_state)
    frontier = deque([start_node])
    explored = set()
    nb_explored = 0

    while frontier:
        node = frontier.popleft()
        nb_explored += 1

        if node.state.isGoal():
            print(f"\n Solution trouvée après {nb_explored} états explorés.")
            return node.getSolution()

        state_repr = str(sorted([(v.id, v.x, v.y) for v in node.state.vehicles]))
        if state_repr in explored:
            continue
        explored.add(state_repr)

        for action, succ in node.state.successorFunction():
            frontier.append(Node(succ, node, action))

    print(f"\n Aucune solution trouvée après {nb_explored} états explorés.")
    return None


# ---------------- A* ----------------

def heuristic(puzzle):

    for v in puzzle.vehicles:
        if v.id == 'X':
            dist = puzzle.board_width - (v.x + v.length)
            # compter les obstacles devant X
            blockers = 0
            for x in range(v.x + v.length, puzzle.board_width):
                if puzzle.board[v.y][x] != ' ':
                    blockers += 1
            return dist + blockers
    return 0


import time
from itertools import count
import heapq

def a_star(start_state, time_limit=30, max_expansions=200000):
   
    def state_repr(state):
        return tuple(sorted((v.id, v.x, v.y) for v in state.vehicles))

    def reconstruct_solution(rep):
        actions = []
        cur = rep
        while cur in parent_map and parent_map[cur] is not None:
            parent_rep, action = parent_map[cur]
            actions.append(action)
            cur = parent_rep
        actions.reverse()
        return actions

    start_time = time.time()
    uid = count()
    open_heap = []
    g_score = {}
    parent_map = {}
    state_map = {}

    start_rep = state_repr(start_state)
    g_score[start_rep] = 0
    parent_map[start_rep] = None
    state_map[start_rep] = start_state
    f_start = heuristic(start_state)

    heapq.heappush(open_heap, (f_start, next(uid), start_rep))
    expansions = 0

    while open_heap:
        if time.time() - start_time > time_limit:
            print(f"[A*]  Timeout après {time_limit}s, expansions={expansions}.")
            return None
        if expansions >= max_expansions:
            print(f"[A*]  Max expansions atteint ({max_expansions}).")
            return None

        f, _, cur_rep = heapq.heappop(open_heap)
        cur_state = state_map[cur_rep]

        if cur_state.isGoal():
            print(f"[A*] Solution trouvée en {time.time()-start_time:.2f}s après {expansions} expansions.")
            return reconstruct_solution(cur_rep)

        expansions += 1
        if expansions % 500 == 0:
            print(f"[A*] expansions={expansions}, open={len(open_heap)}, best f={f:.1f}")

        for action, succ in cur_state.successorFunction():
            succ_rep = state_repr(succ)
            tentative_g = g_score[cur_rep] + 1
            if tentative_g < g_score.get(succ_rep, float('inf')):
                g_score[succ_rep] = tentative_g
                parent_map[succ_rep] = (cur_rep, action)
                state_map[succ_rep] = succ
                f_succ = tentative_g + heuristic(succ)
                heapq.heappush(open_heap, (f_succ, next(uid), succ_rep))

    print("[A*]  Aucun chemin trouvé.")
    return None




# ---------------- INTERFACE PYGAME ----------------

def run_animation(puzzle, solution):
    pygame.init()
    cell_size = 80
    width = puzzle.board_width * cell_size
    height = puzzle.board_height * cell_size
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("🚗 Rush Hour Solver")
    font = pygame.font.Font(None, 30)

    colors = {
        'X': (255, 100, 100),
        'default': (100, 200, 255)
    }

    clock = pygame.time.Clock()

    def draw_board(state):
        screen.fill((30, 30, 30))
        for v in state.vehicles:
            color = colors.get(v.id, colors['default'])
            rect = pygame.Rect(v.x * cell_size, v.y * cell_size,
                               (v.length if v.orientation == 'H' else 1) * cell_size,
                               (1 if v.orientation == 'H' else v.length) * cell_size)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            text = font.render(v.id, True, (0, 0, 0))
            screen.blit(text, (v.x * cell_size + 10, v.y * cell_size + 10))
        pygame.display.flip()

    # --- Animation des mouvements ---
    current_state = puzzle
    draw_board(current_state)
    pygame.time.wait(1000)

    for move in solution:
        # Gérer les événements pour éviter que la fenêtre freeze
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        vid, direction = move
        dx, dy = 0, 0
        if direction == 'L': dx = -1
        elif direction == 'R': dx = 1
        elif direction == 'U': dy = -1
        elif direction == 'D': dy = 1

        current_state = current_state.move_vehicle(vid, dx, dy)
        draw_board(current_state)

        # Petite pause entre chaque mouvement
        pygame.time.wait(600)

    # Affiche le texte de fin
    text = font.render(f"Solved in {len(solution)} moves!", True, (255, 255, 255))
    screen.blit(text, (10, height - 40))
    pygame.display.flip()

    # --- Boucle d'attente pour garder la fenêtre ouverte ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(30)

    pygame.quit()
    pygame.init()
    cell_size = 80
    width = puzzle.board_width * cell_size
    height = puzzle.board_height * cell_size
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(" Rush Hour Solver")
    font = pygame.font.Font(None, 30)

    colors = {
        'X': (255, 100, 100),
        'default': (100, 200, 255)
    }

    clock = pygame.time.Clock()

    def draw_board(state):
        screen.fill((30, 30, 30))
        for v in state.vehicles:
            color = colors.get(v.id, colors['default'])
            rect = pygame.Rect(v.x * cell_size, v.y * cell_size,
                               (v.length if v.orientation == 'H' else 1) * cell_size,
                               (1 if v.orientation == 'H' else v.length) * cell_size)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            text = font.render(v.id, True, (0, 0, 0))
            screen.blit(text, (v.x * cell_size + 10, v.y * cell_size + 10))
        pygame.display.flip()

    # --- Animation des mouvements ---
    current_state = puzzle
    draw_board(current_state)
    pygame.time.wait(1000)

    for move in solution:
        vid, direction = move
        dx, dy = 0, 0
        if direction == 'L': dx = -1
        elif direction == 'R': dx = 1
        elif direction == 'U': dy = -1
        elif direction == 'D': dy = 1
        current_state = current_state.move_vehicle(vid, dx, dy)
        draw_board(current_state)
        pygame.time.wait(400)

    # Affiche le texte de fin
    text = font.render(f"Solved in {len(solution)} moves!", True, (255, 255, 255))
    screen.blit(text, (10, height - 40))
    pygame.display.flip()

    # --- Boucle d'attente pour garder la fenêtre ouverte ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(30)

    pygame.quit()


# ---------------- MAIN ----------------

if __name__ == "__main__":
    folder = "examples"
    print("Fichiers disponibles :")
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")

    choice = input("\nEntrez le numéro du fichier à utiliser : ")
    try:
        choice = int(choice)
        filename = files[choice - 1]
    except (ValueError, IndexError):
        print("Choix invalide.")
        exit()

    path = os.path.join(folder, filename)
    puzzle = RushHourPuzzle()

    try:
        puzzle.setVehicles(path)
    except Exception as e:
        print("\nErreur lors du chargement du fichier :")
        print(e)
        exit()

    print(f"\nPlateau initial ({filename}) :")
    puzzle.printBoard()

    algo = input("\nChoisir l’algorithme (bfs / a*) : ").lower()
    if algo == "bfs":
        solution = bfs(puzzle)
    else:
        solution = a_star(puzzle)

    if solution:
        print("\nSolution trouvée en", len(solution), "mouvements :")
        for move in solution:
            print("  ", move)
        run_animation(puzzle, solution)
    else:
        print("Aucune solution trouvée.")