# map_system.py
import pygame
import random
import math
import heapq
from config import WIDTH, HEIGHT

class Tile:
    """Represents a single tile in the game map"""
    def __init__(self, x, y, size, walkable=True):
        self.x = x
        self.y = y
        self.size = size
        self.grid_x = int(x / size)
        self.grid_y = int(y / size)
        self.walkable = walkable
        self.center_x = x + size / 2
        self.center_y = y + size / 2
        self.f_score = 0  # For pathfinding
        self.g_score = 0  # For pathfinding
        self.parent = None  # For pathfinding
    
    def get_center(self):
        """Get the center position of the tile"""
        return (self.center_x, self.center_y)
    
    def get_rect(self):
        """Get the pygame Rect for this tile"""
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def draw(self, surface, color=None):
        """Draw the tile"""
        if color is None:
            color = (200, 200, 200) if self.walkable else (100, 100, 100)
        
        pygame.draw.rect(surface, color, self.get_rect())
        pygame.draw.rect(surface, (50, 50, 50), self.get_rect(), 1)


class Obstacle:
    """Represents an obstacle in the game map"""
    def __init__(self, x, y, width, height, color=(100, 100, 100)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def get_rect(self):
        """Get the pygame Rect for this obstacle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface):
        """Draw the obstacle"""
        pygame.draw.rect(surface, self.color, self.get_rect())
        pygame.draw.rect(surface, (50, 50, 50), self.get_rect(), 2)


class SpawnPoint:
    """Represents a point where enemies can spawn"""
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius
    
    def get_position(self):
        """Get the position of the spawn point"""
        return (self.x, self.y)
    
    def get_random_position(self, variance=50):
        """Get a random position near the spawn point"""
        return (
            self.x + random.randint(-variance, variance),
            self.y + random.randint(-variance, variance)
        )
    
    def draw(self, surface):
        """Draw the spawn point (for debugging)"""
        pygame.draw.circle(
            surface, (200, 50, 50), (int(self.x), int(self.y)), self.radius, 2)


class Map:
    """Represents the game map"""
    def __init__(self, width, height, tile_size=32):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        
        # Calculate grid dimensions
        self.grid_width = int(width / tile_size)
        self.grid_height = int(height / tile_size)
        
        # Create tiles
        self.tiles = [[None for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                self.tiles[x][y] = Tile(
                    x * tile_size, y * tile_size, tile_size, walkable=True)
        
        # Lists for map elements
        self.obstacles = []
        self.spawn_points = []
    
    def add_obstacle(self, x, y, width, height):
        """Add an obstacle to the map"""
        obstacle = Obstacle(x, y, width, height)
        self.obstacles.append(obstacle)
        
        # Mark tiles under the obstacle as non-walkable
        start_x = max(0, int(x / self.tile_size))
        start_y = max(0, int(y / self.tile_size))
        end_x = min(self.grid_width, int((x + width) / self.tile_size) + 1)
        end_y = min(self.grid_height, int((y + height) / self.tile_size) + 1)
        
        for grid_x in range(start_x, end_x):
            for grid_y in range(start_y, end_y):
                self.tiles[grid_x][grid_y].walkable = False
        
        return obstacle
    
    def add_spawn_point(self, x, y):
        """Add a spawn point to the map"""
        spawn_point = SpawnPoint(x, y)
        self.spawn_points.append(spawn_point)
        return spawn_point
    
    def is_position_walkable(self, x, y):
        """Check if a position is walkable"""
        grid_x = int(x / self.tile_size)
        grid_y = int(y / self.tile_size)
        
        # Check bounds
        if (grid_x < 0 or grid_x >= self.grid_width or
            grid_y < 0 or grid_y >= self.grid_height):
            return False
        
        return self.tiles[grid_x][grid_y].walkable
    
    def get_tile_at_position(self, x, y):
        """Get the tile at a position"""
        grid_x = int(x / self.tile_size)
        grid_y = int(y / self.tile_size)
        
        # Check bounds
        if (grid_x < 0 or grid_x >= self.grid_width or
            grid_y < 0 or grid_y >= self.grid_height):
            return None
        
        return self.tiles[grid_x][grid_y]
    
    def get_neighbors(self, tile):
        """Get walkable neighboring tiles for pathfinding"""
        neighbors = []
        directions = [
            (0, -1),  # Up
            (1, 0),   # Right
            (0, 1),   # Down
            (-1, 0),  # Left
            (1, -1),  # Up-Right
            (1, 1),   # Down-Right
            (-1, 1),  # Down-Left
            (-1, -1)  # Up-Left
        ]
        
        for dx, dy in directions:
            nx, ny = tile.grid_x + dx, tile.grid_y + dy
            
            # Check bounds
            if nx < 0 or nx >= self.grid_width or ny < 0 or ny >= self.grid_height:
                continue
            
            neighbor = self.tiles[nx][ny]
            if neighbor.walkable:
                neighbors.append(neighbor)
        
        return neighbors
    
    def draw(self, surface, debug=False):
        """Draw the map and all elements"""
        if debug:
            # Draw all tiles with walkability colors
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    self.tiles[x][y].draw(surface)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(surface)
        
        # Draw spawn points in debug mode
        if debug:
            for spawn in self.spawn_points:
                spawn.draw(surface)


class Pathfinder:
    """A* pathfinding for enemy navigation"""
    def __init__(self, game_map):
        self.map = game_map
    
    def find_path(self, start_x, start_y, goal_x, goal_y):
        """Find a path from start to goal positions using A*"""
        start_tile = self.map.get_tile_at_position(start_x, start_y)
        goal_tile = self.map.get_tile_at_position(goal_x, goal_y)
        
        if not start_tile or not goal_tile:
            return []
        
        if not start_tile.walkable or not goal_tile.walkable:
            return []
        
        # Reset pathfinding properties
        for x in range(self.map.grid_width):
            for y in range(self.map.grid_height):
                tile = self.map.tiles[x][y]
                tile.f_score = float('inf')
                tile.g_score = float('inf')
                tile.parent = None
        
        # Priority queue for open set
        open_set = []
        start_tile.g_score = 0
        start_tile.f_score = self._heuristic(start_tile, goal_tile)
        heapq.heappush(open_set, (start_tile.f_score, id(start_tile), start_tile))
        
        while open_set:
            # Get tile with lowest f_score
            _, _, current = heapq.heappop(open_set)
            
            # Check if reached goal
            if current == goal_tile:
                return self._reconstruct_path(current)
            
            # Check each neighbor
            for neighbor in self.map.get_neighbors(current):
                # Distance from start to neighbor through current
                tentative_g = current.g_score + self._distance(current, neighbor)
                
                if tentative_g < neighbor.g_score:
                    # This path is better
                    neighbor.parent = current
                    neighbor.g_score = tentative_g
                    neighbor.f_score = tentative_g + self._heuristic(neighbor, goal_tile)
                    
                    # Add to open set if not already there
                    # Note: This is inefficient - ideally we'd update in place
                    heapq.heappush(open_set, (neighbor.f_score, id(neighbor), neighbor))
        
        # No path found
        return []
    
    def _heuristic(self, a, b):
        """Heuristic function (straight-line distance)"""
        return math.sqrt((a.center_x - b.center_x) ** 2 + (a.center_y - b.center_y) ** 2)
    
    def _distance(self, a, b):
        """Distance between two tiles"""
        return math.sqrt((a.center_x - b.center_x) ** 2 + (a.center_y - b.center_y) ** 2)
    
    def _reconstruct_path(self, current):
        """Reconstruct path from goal to start"""
        path = []
        while current:
            path.append((current.center_x, current.center_y))
            current = current.parent
        return list(reversed(path))


class MapManager:
    """Manages the game map and provides interfaces for other systems"""
    def __init__(self, width, height, debug=False):
        self.width = width
        self.height = height
        self.debug = debug
        self.game_map = None
        self.pathfinder = None
        
        # Create a default empty map
        self.create_empty_map()
    
    def create_empty_map(self):
        """Create an empty map with just boundaries"""
        self.game_map = Map(self.width, self.height)
        self.pathfinder = Pathfinder(self.game_map)
        
        # Add spawn points around the edges
        spawn_margin = 100
        self.game_map.add_spawn_point(spawn_margin, spawn_margin)  # Top-left
        self.game_map.add_spawn_point(self.width - spawn_margin, spawn_margin)  # Top-right
        self.game_map.add_spawn_point(spawn_margin, self.height - spawn_margin)  # Bottom-left
        self.game_map.add_spawn_point(self.width - spawn_margin, self.height - spawn_margin)  # Bottom-right
    
    def create_random_map(self):
        """Create a map with random obstacles"""
        self.game_map = Map(self.width, self.height)
        self.pathfinder = Pathfinder(self.game_map)
        
        # Add spawn points around the edges
        spawn_margin = 100
        self.game_map.add_spawn_point(spawn_margin, spawn_margin)  # Top-left
        self.game_map.add_spawn_point(self.width - spawn_margin, spawn_margin)  # Top-right
        self.game_map.add_spawn_point(spawn_margin, self.height - spawn_margin)  # Bottom-left
        self.game_map.add_spawn_point(self.width - spawn_margin, self.height - spawn_margin)  # Bottom-right
        
        # Add some random obstacles
        obstacles_count = random.randint(5, 10)
        center_clear_radius = 150  # Keep the center clear for player
        
        for _ in range(obstacles_count):
            # Random size
            width = random.randint(50, 150)
            height = random.randint(50, 150)
            
            # Random position (avoid center)
            while True:
                x = random.randint(0, self.width - width)
                y = random.randint(0, self.height - height)
                
                # Check if obstacle is too close to center
                center_x, center_y = self.width / 2, self.height / 2
                obstacle_center_x, obstacle_center_y = x + width / 2, y + height / 2
                distance_to_center = math.sqrt(
                    (center_x - obstacle_center_x) ** 2 + 
                    (center_y - obstacle_center_y) ** 2)
                
                if distance_to_center > center_clear_radius:
                    break
            
            self.game_map.add_obstacle(x, y, width, height)
    
    def get_random_spawn_position(self):
        """Get a random position from a spawn point"""
        if not self.game_map.spawn_points:
            return (random.randint(0, self.width), random.randint(0, self.height))
        
        spawn_point = random.choice(self.game_map.spawn_points)
        return spawn_point.get_random_position()
    
    def find_path(self, start_x, start_y, goal_x, goal_y):
        """Find a path from start to goal"""
        return self.pathfinder.find_path(start_x, start_y, goal_x, goal_y)
    
    def is_position_walkable(self, x, y):
        """Check if a position is walkable"""
        return self.game_map.is_position_walkable(x, y)
    
    def draw(self, surface):
        """Draw the map"""
        self.game_map.draw(surface, self.debug)