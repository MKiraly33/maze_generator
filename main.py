import pygame
import random
import math
from queue import PriorityQueue


class Node:
    def __init__(self, index_x, index_y, pos=(5.0, 5.0), _side_length=50, _color="white"):
        self.pos = pos  # Top left corner
        self.side_length = _side_length  # square side length
        self.color = _color
        self.upper_left = pos
        self.upper_right = (self.pos[0] + self.side_length, self.pos[1])
        self.lower_left = (self.pos[0], self.pos[1] + self.side_length)
        self.lower_right = (self.pos[0] + self.side_length, self.pos[1] + self.side_length)
        self.render_left = True
        self.render_top = True
        self.render_right = True
        self.render_bottom = True
        self.is_visited = False
        self.index_x = index_x
        self.index_y = index_y
        self.is_current = False
        # A star props
        self.is_in_path = False
        self.parent = None
        self.g_score = 9999999999
        self.f_score = 9999999999

    def __eq__(self, other):
        if isinstance(other, Node) and self.index_x == other.index_x and self.index_y == other.index_y:
            return True
        return False

    def __lt__(self, other):
        return self.f_score < other.f_score

    def draw(self, _screen=None, is_debug=False):
        # Upper left to upper right
        if self.render_top:
            pygame.draw.line(_screen, self.color, self.upper_left, self.upper_right)
        # Upper right to lower right
        if self.render_right:
            pygame.draw.line(_screen, self.color, self.upper_right, self.lower_right)
        # Lower right to lower left
        if self.render_bottom:
            pygame.draw.line(_screen, self.color, self.lower_right, self.lower_left)
        # Lower left to upper right
        if self.render_left:
            pygame.draw.line(_screen, self.color, self.lower_left, self.upper_left)
        if is_debug:
            pygame.draw.rect(_screen, "red", pygame.Rect(self.pos[0], self.pos[1], self.side_length, self.side_length))
        if self.is_current:
            pygame.draw.rect(_screen, "green", pygame.Rect(self.pos[0], self.pos[1],
                                                           self.side_length, self.side_length))
        if self.is_in_path:
            pygame.draw.rect(_screen, "blue", pygame.Rect(self.pos[0] + self.side_length / 4, self.pos[1] +
                                                          self.side_length / 4,
                                                          self.side_length / 2, self.side_length / 2))


class Graph:
    def __init__(self, start_x, start_y, side_length, line_color):
        current_x = start_x
        current_y = start_y
        self.graph = []
        for _x in range(graph_size):
            current_y = start_y
            current_x = start_x + _x * side_length
            self.graph.append([])
            for _y in range(graph_size):
                self.graph[_x].append(Node(_x, _y, (current_x, current_y), side_length, line_color))
                current_y += side_length
        self.is_generating = False

    def get_unvisited_neighbours(self, _x, _y):
        to_return = []

        if _x + 1 < len(self.graph) and not self.graph[_x + 1][_y].is_visited:
            to_return.append(self.graph[_x + 1][_y])
        if _x - 1 >= 0 and not self.graph[_x - 1][_y].is_visited:
            to_return.append(self.graph[_x - 1][_y])
        if _y + 1 < len(self.graph[0]) and not self.graph[_x][_y + 1].is_visited:
            to_return.append(self.graph[_x][_y + 1])
        if _y - 1 >= 0 and not self.graph[_x][_y - 1].is_visited:
            to_return.append(self.graph[_x][_y - 1])

        return to_return

    def generate_maze(self):
        self.is_generating = True
        self.graph[0][0].is_visited = True
        stack = [self.graph[0][0]]
        while len(stack) > 0:
            current_cell = stack.pop()
            current_cell.is_current = True
            neighbours = self.get_unvisited_neighbours(current_cell.index_x, current_cell.index_y)
            if len(neighbours) > 0:
                stack.append(current_cell)
                chosen_cell = random.choice(neighbours)
                if current_cell.index_x - chosen_cell.index_x == 0:  # Same X coord
                    if current_cell.index_y - chosen_cell.index_y < 0:  # Chosen cell has greater y, so it is below
                        chosen_cell.render_top = False
                        current_cell.render_bottom = False
                    else:
                        chosen_cell.render_bottom = False
                        current_cell.render_top = False
                else:  # Same Y coord
                    if current_cell.index_x - chosen_cell.index_x < 0:  # Chosen cell has greater x so it's to the right
                        chosen_cell.render_left = False
                        current_cell.render_right = False
                    else:
                        chosen_cell.render_right = False
                        current_cell.render_left = False
                chosen_cell.is_visited = True
                stack.append(chosen_cell)
            yield
            current_cell.is_current = False
        self.is_generating = False

    def a_star_get_neighbours(self, node):
        neighbours = []
        if not node.render_top:
            neighbours.append(self.graph[node.index_x][node.index_y - 1])
        if not node.render_bottom:
            neighbours.append(self.graph[node.index_x][node.index_y + 1])
        if not node.render_left:
            neighbours.append(self.graph[node.index_x - 1][node.index_y])
        if not node.render_right:
            neighbours.append(self.graph[node.index_x + 1][node.index_y])
        return neighbours

    def get_path(self, last_node_in_path):
        last_node_in_path.is_in_path = True
        current = last_node_in_path.parent
        while current is not None:
            current.is_in_path = True
            current = current.parent

    def a_star(self):
        open_set = PriorityQueue()
        start = self.graph[0][0]
        start.g_score = 0
        start.f_score = math.sqrt(((self.graph[graph_size - 1][graph_size - 1].index_x - start.index_x) ** 2) +
                                  ((self.graph[graph_size - 1][graph_size - 1].index_y - start.index_y) ** 2))
        open_set.put((start.f_score, start))

        while not open_set.empty():
            current = open_set.get_nowait()[1]
            if current == self.graph[graph_size - 1][graph_size - 1]:
                self.get_path(current)
            for n in self.a_star_get_neighbours(current):
                # Instead of +1 we can use a function, this way "speed" can be implemented
                tentative_g_score = current.g_score + 1
                if tentative_g_score < n.g_score:
                    # This path to the neighbour is better
                    n.parent = current
                    n.g_score = tentative_g_score
                    n.f_score = tentative_g_score + \
                                math.sqrt(((self.graph[graph_size - 1][graph_size - 1].index_x - n.index_x) ** 2) +
                                          ((self.graph[graph_size - 1][graph_size - 1].index_y - n.index_y) ** 2))
                    if n not in open_set.queue:
                        open_set.put((n.f_score, n))

    def reset(self):
        for x in range(graph_size):
            for y in range(graph_size):
                self.graph[x][y].g_score = 9999999999
                self.graph[x][y].f_score = 9999999999
                self.graph[x][y].parent = None
                self.graph[x][y].is_in_path = False


# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 1100))
clock = pygame.time.Clock()
running = True
graph_size = 20
graph = Graph(5.0, 5.0, 50, random.choice(["white", "red", "green", "blue", "cyan", "yellow"]))

update_timer = 501
generator = graph.generate_maze()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    dt = clock.tick(60)  # limits FPS to 60
    update_timer += dt

    screen.fill("black")  # fill the screen with a color to wipe away anything from last frame

    if generator and update_timer > 1:
        try:
            next(generator)
        except StopIteration:
            generator = None
        update_timer = 0

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        graph = Graph(5.0, 5.0, 50, random.choice(["white", "red", "green", "blue", "cyan", "yellow"]))
        generator = graph.generate_maze()
        update_timer = 501
    if keys[pygame.K_a]:
        if not graph.is_generating:
            graph.reset()
            graph.a_star()
    # RENDER YOUR GAME HERE
    for x in range(graph_size):
        for y in range(graph_size):
            graph.graph[x][y].draw(screen)

    pygame.display.flip()  # flip() the display to put your work on screen

pygame.quit()
