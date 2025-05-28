import pygame
import sys
import time
import random
from collections import deque
import heapq

# Konstanta dan konfigurasi
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_WIDTH = 35
GRID_HEIGHT = 25
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
TURQUOISE = (64, 224, 208)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)
DARK_RED = (139, 0, 0)
PINK = (255, 192, 203)
LIGHT_GREEN = (144, 238, 144)

# Inisialisasi pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Race: Player vs Super Smart AI (A* + BFS)")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 16)

class SuperSmartAI:
    def __init__(self, maze_solver):
        self.maze_solver = maze_solver
        self.position = None
        self.start_position = None
        self.last_move_time = 0
        self.move_delay = 500  # AI bergerak setiap 500ms
        self.reached_goal = False
        self.step_count = 0
        self.visited_cells = set()
        self.path_history = []
        
        # AI yang BENAR-BENAR cerdas - dengan 2 metode pathfinding
        self.current_path = []  # Path yang sedang diikuti
        self.path_index = 0     # Index langkah dalam path
        self.algorithm = "A*"   # Default menggunakan A*, bisa diubah ke "BFS"
        
    def reset(self):
        self.position = None
        self.start_position = None
        self.last_move_time = 0
        self.reached_goal = False
        self.step_count = 0
        self.visited_cells = set()
        self.path_history = []
        self.current_path = []
        self.path_index = 0
        
    def set_start_position(self, position):
        """Set posisi start untuk AI"""
        self.start_position = position
        self.position = position
        self.visited_cells.add(position)
        self.path_history.append(position)
        
        # Langsung hitung path optimal saat start
        self.calculate_optimal_path()
        
    def set_algorithm(self, algorithm):
        """Set algoritma pathfinding: 'A*' atau 'BFS'"""
        if algorithm in ["A*", "BFS"]:
            self.algorithm = algorithm
            # Hitung ulang path dengan algoritma baru
            if self.position:
                self.calculate_optimal_path()
        
    def calculate_optimal_path_astar(self):
        """Hitung path optimal menggunakan A* - dijamin optimal dengan heuristic"""
        if not self.position or not self.maze_solver.goal:
            self.current_path = []
            return
            
        start = self.position
        goal = self.maze_solver.goal
        
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and 
                    self.maze_solver.grid[ny][nx] == 0):
                    neighbors.append((nx, ny))
            return neighbors
        
        # A* algorithm - implementasi yang sempurna
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                # Rekonstruksi path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                self.current_path = path
                self.path_index = 0
                return
            
            for neighbor in get_neighbors(current):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # Jika tidak ada path, kosongkan
        self.current_path = []
    
    def calculate_optimal_path_bfs(self):
        """Hitung path optimal menggunakan BFS - dijamin jalur terpendek"""
        if not self.position or not self.maze_solver.goal:
            self.current_path = []
            return
            
        start = self.position
        goal = self.maze_solver.goal
        
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and 
                    self.maze_solver.grid[ny][nx] == 0):
                    neighbors.append((nx, ny))
            return neighbors
        
        # BFS algorithm - implementasi klasik untuk jalur terpendek
        queue = deque([start])
        came_from = {start: None}
        visited = {start}
        
        while queue:
            current = queue.popleft()
            
            if current == goal:
                # Rekonstruksi path
                path = []
                while current != start:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                self.current_path = path
                self.path_index = 0
                return
            
            for neighbor in get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)
        
        # Jika tidak ada path, kosongkan
        self.current_path = []
    
    def calculate_optimal_path(self):
        """Hitung path optimal menggunakan algoritma yang dipilih"""
        if self.algorithm == "A*":
            self.calculate_optimal_path_astar()
        elif self.algorithm == "BFS":
            self.calculate_optimal_path_bfs()
    
    def move(self):
        """AI bergerak mengikuti path optimal - NO RANDOMNESS"""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_move_time < self.move_delay:
            return
            
        if not self.position or self.reached_goal:
            return
        
        # Jika belum ada path atau path kosong, hitung ulang
        if not self.current_path:
            self.calculate_optimal_path()
            
        # Jika masih belum ada path, berarti tidak ada solusi
        if not self.current_path:
            return
            
        # Ikuti path yang sudah dihitung
        if self.path_index < len(self.current_path):
            next_position = self.current_path[self.path_index]
            
            # Validasi gerakan (pastikan masih valid)
            x, y = self.position
            nx, ny = next_position
            
            # Cek apakah gerakan valid (adjacent dan tidak ada wall)
            if (abs(nx - x) + abs(ny - y) == 1 and 
                0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and 
                self.maze_solver.grid[ny][nx] == 0):
                
                # Lakukan gerakan
                self.position = next_position
                self.visited_cells.add(next_position)
                self.path_history.append(next_position)
                self.step_count += 1
                self.path_index += 1
                self.last_move_time = current_time
                
                # Cek apakah mencapai goal
                if self.position == self.maze_solver.goal:
                    self.reached_goal = True
                    self.maze_solver.declare_winner("AI")
            else:
                # Jika path tidak valid (maze berubah), hitung ulang
                self.calculate_optimal_path()

class MazeSolver:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.player_start = None
        self.ai_start = None
        self.goal = None
        self.wall_positions = set()
        self.player_position = None
        self.visited_cells = set()
        self.path_history = []
        self.running = True
        self.game_completed = False
        self.game_over = False
        self.step_count = 0
        self.winner = None
        self.race_started = False
        self.message = "Tekan 'G' untuk Generate Maze dan race melawan Super Smart AI!"
        self.super_ai = SuperSmartAI(self)
        
    def reset(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.player_start = None
        self.ai_start = None
        self.goal = None
        self.player_position = None
        self.wall_positions = set()
        self.visited_cells = set()
        self.path_history = []
        self.game_completed = False
        self.game_over = False
        self.step_count = 0
        self.winner = None
        self.race_started = False
        self.message = "Tekan 'G' untuk Generate Maze dan race melawan Super Smart AI!"
        self.super_ai.reset()
        
    def generate_random_maze(self):
        self.reset()
        # Buat grid dengan semua sel sebagai tembok
        self.grid = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.wall_positions = {(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)}
        
        # Algoritma DFS untuk membuat maze
        stack = []
        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = 0
        self.wall_positions.remove((start_x, start_y))
        stack.append((start_x, start_y))
        
        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy in [(0, -2), (2, 0), (0, 2), (-2, 0)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < GRID_WIDTH-1 and 0 < ny < GRID_HEIGHT-1 and self.grid[ny][nx] == 1:
                    neighbors.append((nx, ny, dx//2, dy//2))
            
            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                self.grid[y + dy][x + dx] = 0
                self.wall_positions.remove((x + dx, y + dy))
                self.grid[ny][nx] = 0
                self.wall_positions.remove((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        
        self.set_race_positions()
        self.start_race()
    
    def set_race_positions(self):
        """Set posisi start yang BENAR-BENAR adil"""
        empty_cells = [(x, y) for x in range(1, GRID_WIDTH-1) 
                       for y in range(1, GRID_HEIGHT-1) if self.grid[y][x] == 0]
        
        if len(empty_cells) < 3:
            return
        
        # Pilih goal di corner yang tersedia
        corners = [(1, 1), (GRID_WIDTH-2, 1), (1, GRID_HEIGHT-2), (GRID_WIDTH-2, GRID_HEIGHT-2)]
        goal_candidates = [corner for corner in corners if corner in empty_cells]
        
        if not goal_candidates:
            # Jika tidak ada corner, pilih dari area pinggiran
            edge_cells = [pos for pos in empty_cells 
                         if pos[0] <= 3 or pos[0] >= GRID_WIDTH-4 or pos[1] <= 3 or pos[1] >= GRID_HEIGHT-4]
            goal_candidates = edge_cells if edge_cells else empty_cells[-5:]
        
        self.goal = random.choice(goal_candidates)
        
        # Cari posisi start dengan jarak PERSIS SAMA ke goal
        remaining_cells = [pos for pos in empty_cells if pos != self.goal]
        
        # Hitung jarak Manhattan untuk semua posisi
        distances = {}
        for pos in remaining_cells:
            distances[pos] = abs(pos[0] - self.goal[0]) + abs(pos[1] - self.goal[1])
        
        # Kelompokkan berdasarkan jarak yang sama
        distance_groups = {}
        for pos, dist in distances.items():
            if dist not in distance_groups:
                distance_groups[dist] = []
            distance_groups[dist].append(pos)
        
        # Cari jarak yang punya minimal 2 posisi dan cukup jauh
        valid_distances = [dist for dist, positions in distance_groups.items() 
                          if len(positions) >= 2 and dist >= max(distances.values()) * 0.8]
        
        if valid_distances:
            # Pilih jarak terpanjang yang valid
            chosen_distance = max(valid_distances)
            candidates = distance_groups[chosen_distance]
            selected = random.sample(candidates, 2)
            self.player_start = selected[0]
            self.ai_start = selected[1]
        else:
            # Fallback: pilih 2 posisi terjauh
            sorted_positions = sorted(remaining_cells, key=lambda pos: distances[pos], reverse=True)
            self.player_start = sorted_positions[0]
            self.ai_start = sorted_positions[1] if len(sorted_positions) > 1 else sorted_positions[0]
    
    def start_race(self):
        """Mulai race dengan kondisi yang adil"""
        if self.player_start and self.ai_start and self.goal:
            self.player_position = self.player_start
            self.visited_cells = {self.player_start}
            self.path_history = [self.player_start]
            self.step_count = 0
            
            self.super_ai.set_start_position(self.ai_start)
            
            self.game_completed = False
            self.game_over = False
            self.winner = None
            self.race_started = True
            
            player_dist = abs(self.player_start[0] - self.goal[0]) + abs(self.player_start[1] - self.goal[1])
            ai_dist = abs(self.ai_start[0] - self.goal[0]) + abs(self.ai_start[1] - self.goal[1])
            
            self.message = f"🏁 RACE DIMULAI! Player (biru) vs Super Smart AI (ungu) [{self.super_ai.algorithm}] → Goal (merah)\nJarak start: Player={player_dist}, AI={ai_dist} - Cari jalan sendiri!"
        else:
            self.message = "Generate maze dulu dengan 'G'!"
    
    def declare_winner(self, winner):
        """Deklarasi pemenang"""
        self.winner = winner
        self.game_completed = True
        self.race_started = False
        
        if winner == "Player":
            self.message = f"🎉 LUAR BIASA! PLAYER MENANG! 🎉\n👤 Anda: {self.step_count} langkah\n🤖 Super Smart AI [{self.super_ai.algorithm}]: {self.super_ai.step_count} langkah\nAnda mengalahkan AI pintar! Tekan 'R' untuk race lagi!"
        else:
            self.message = f"🤖 SUPER SMART AI [{self.super_ai.algorithm}] MENANG! 🤖\n🤖 Super Smart AI: {self.super_ai.step_count} langkah\n👤 Anda: {self.step_count} langkah\nAI menemukan jalur optimal! Tekan 'R' untuk tantangan baru!"
    
    def move_player(self, direction):
        if (not self.player_position or not self.goal or self.game_completed or 
            self.game_over or not self.race_started):
            return
        
        x, y = self.player_position
        dx, dy = 0, 0
        
        if direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        elif direction == "left":
            dx = -1
        elif direction == "right":
            dx = 1
        
        new_x, new_y = x + dx, y + dy
        
        if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and 
            self.grid[new_y][new_x] == 0):
            
            self.player_position = (new_x, new_y)
            self.visited_cells.add((new_x, new_y))
            self.path_history.append((new_x, new_y))
            self.step_count += 1
            
            if (new_x, new_y) == self.goal:
                if not self.super_ai.reached_goal:
                    self.declare_winner("Player")
                else:
                    # Jika keduanya mencapai goal, yang langkah lebih sedikit menang
                    if self.step_count <= self.super_ai.step_count:
                        self.declare_winner("Player")
                    else:
                        self.declare_winner("AI")
            else:
                # Update status race real-time
                player_dist = abs(new_x - self.goal[0]) + abs(new_y - self.goal[1])
                ai_dist = (abs(self.super_ai.position[0] - self.goal[0]) + 
                          abs(self.super_ai.position[1] - self.goal[1])) if self.super_ai.position else 999
                
                if player_dist < ai_dist:
                    status = "👤 Player MEMIMPIN!"
                elif player_dist > ai_dist:
                    status = f"🤖 AI [{self.super_ai.algorithm}] MEMIMPIN!"
                else:
                    status = "🤝 SERI!"
                
                self.message = f"{status} | 👤 Player: {self.step_count} langkah (jarak: {player_dist}) | 🤖 AI: {self.super_ai.step_count} langkah (jarak: {ai_dist})"
    
    def draw_grid(self):
        # Gambar maze
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.grid[y][x] == 1:
                    pygame.draw.rect(screen, BLACK, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, GRAY, rect, 1)
        
        # Gambar jejak player (tanpa menunjukkan jalur AI)
        for x, y in self.visited_cells:
            if (x, y) not in [self.player_start, self.goal, self.player_position, self.ai_start, self.super_ai.position]:
                rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                pygame.draw.rect(screen, TURQUOISE, rect)
        
        # Gambar jejak AI (yang sudah dilalui) - tanpa menunjukkan rencana
        for x, y in self.super_ai.visited_cells:
            if (x, y) not in [self.ai_start, self.goal, self.super_ai.position, self.player_start, self.player_position]:
                rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                pygame.draw.rect(screen, PINK, rect)
        
        # Gambar start positions
        if self.player_start:
            start_rect = pygame.Rect(self.player_start[0] * CELL_SIZE + 1, self.player_start[1] * CELL_SIZE + 1, 
                                     CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(screen, LIGHT_GREEN, start_rect)
            # Label
            text = pygame.font.SysFont('Arial', 10).render('P', True, BLACK)
            screen.blit(text, (self.player_start[0] * CELL_SIZE + 7, self.player_start[1] * CELL_SIZE + 5))
        
        if self.ai_start:
            ai_start_rect = pygame.Rect(self.ai_start[0] * CELL_SIZE + 1, self.ai_start[1] * CELL_SIZE + 1, 
                                       CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(screen, ORANGE, ai_start_rect)
            # Label
            text = pygame.font.SysFont('Arial', 10).render('AI', True, BLACK)
            screen.blit(text, (self.ai_start[0] * CELL_SIZE + 5, self.ai_start[1] * CELL_SIZE + 5))
        
        # Gambar goal dengan efek animasi
        if self.goal:
            goal_rect = pygame.Rect(self.goal[0] * CELL_SIZE + 1, self.goal[1] * CELL_SIZE + 1, 
                                   CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(screen, RED, goal_rect)
            
            if self.race_started and not self.game_completed:
                current_time = pygame.time.get_ticks()
                if (current_time // 250) % 2 == 0:
                    pygame.draw.rect(screen, YELLOW, goal_rect, 4)
            
            # Label goal
            text = pygame.font.SysFont('Arial', 8).render('GOAL', True, WHITE)
            screen.blit(text, (self.goal[0] * CELL_SIZE + 2, self.goal[1] * CELL_SIZE + 6))
        
        # Gambar player
        if self.player_position:
            player_rect = pygame.Rect(self.player_position[0] * CELL_SIZE + 1, 
                                     self.player_position[1] * CELL_SIZE + 1, 
                                     CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(screen, BLUE, player_rect)
            
            if self.winner == "Player":
                # Crown untuk pemenang
                crown_rect = pygame.Rect(self.player_position[0] * CELL_SIZE + 6, 
                                       self.player_position[1] * CELL_SIZE - 5, 8, 8)
                pygame.draw.rect(screen, YELLOW, crown_rect)
        
        # Gambar Super Smart AI
        if self.super_ai.position:
            ai_rect = pygame.Rect(self.super_ai.position[0] * CELL_SIZE + 1, 
                                 self.super_ai.position[1] * CELL_SIZE + 1, 
                                 CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(screen, PURPLE, ai_rect)
            
            if self.winner == "AI":
                # Crown untuk pemenang
                crown_rect = pygame.Rect(self.super_ai.position[0] * CELL_SIZE + 6, 
                                       self.super_ai.position[1] * CELL_SIZE - 5, 8, 8)
                pygame.draw.rect(screen, YELLOW, crown_rect)
    
    def draw_message(self):
        lines = self.message.split('\n')
        y_offset = HEIGHT - 100
        for i, line in enumerate(lines):
            color = BLACK
            if i == 0 and ('MENANG' in line or 'RACE' in line):
                color = (0, 100, 0) if 'PLAYER MENANG' in line else (100, 0, 100) if 'AI MENANG' in line else (0, 0, 100)
            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (10, y_offset))
            y_offset += 18
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:  # Generate maze
                        self.generate_random_maze()
                    elif event.key == pygame.K_r and self.game_completed:  # Restart
                        self.generate_random_maze()
                    elif event.key == pygame.K_1:  # Switch to A*
                        self.super_ai.set_algorithm("A*")
                        if self.race_started:
                            self.message = self.message.replace("[BFS]", "[A*]")
                    elif event.key == pygame.K_2:  # Switch to BFS
                        self.super_ai.set_algorithm("BFS")
                        if self.race_started:
                            self.message = self.message.replace("[A*]", "[BFS]")
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.move_player("up")
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.move_player("down")
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.move_player("left")
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.move_player("right")
            
            # Update AI - selalu bergerak optimal
            if self.race_started and not self.game_completed:
                self.super_ai.move()
            
            # Render
            screen.fill(WHITE)
            self.draw_grid()
            self.draw_message()
            
            # Instructions
            instructions = [
                "🎮 CONTROLS: Arrow Keys/WASD = Gerak | G = New Maze | R = Restart | 1 = A* | 2 = BFS",
                f"🧠 Super Smart AI [{self.super_ai.algorithm}] vs Player - Tidak ada petunjuk jalan!",
                "🏆 CHALLENGE: Bisakah Anda mengalahkan AI tanpa bantuan visual?"
            ]
            for i, instruction in enumerate(instructions):
                color = (60, 60, 60) if i < 2 else (0, 100, 0)
                text = pygame.font.SysFont('Arial', 11).render(instruction, True, color)
                screen.blit(text, (10, 10 + i * 14))
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Jalankan game
if __name__ == "__main__":
    game = MazeSolver()
    game.run()