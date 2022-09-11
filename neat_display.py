import pygame

class Neat_display():
    def __init__(self, width=240, height=160, offset=(0, 0)):
        self.display_surface = pygame.display.get_surface()
        self.width = width
        self.height = height
        self.x_offset = offset[0]
        self.y_offset = offset[1]
        self.scaler = self.height / 160
        self.node_size = int(5 * self.scaler)
        self.font = pygame.font.SysFont('arial', 15, bold=True)

    def update(self, neural_network, caption=''):
        node_positions = {}
        node_index = 0
        self.node_layers = neural_network.node_layers
        self.nodes = neural_network.nodes
        self.connects = neural_network.connects

        # background
        draw_rect_alpha(self.display_surface, (255, 255, 255, 50), (self.x_offset, self.y_offset, self.width, self.height))

        # create dictionary of node positions
        for n in range(len(self.node_layers)):
            x = (self.width // (len(self.node_layers) + 1)) * (n + 1) + self.x_offset
            for i in range(self.node_layers[n]):
                y = (self.height // (self.node_layers[n] + 1)) * (i + 1) + self.y_offset
                node_positions[self.nodes[node_index].id] = (x, y)
                node_index += 1
        # draw connections
        for connect in self.connects:
            if connect.enabled:
                start = node_positions[connect.input_node]
                end = node_positions[connect.output_node]
                width = int(1 + 3 * self.scaler * abs(connect.weight))
                if connect.weight > 0:
                    colour = 'green'
                else:
                    colour = 'red'
                pygame.draw.line(self.display_surface, colour, start, end, width)
        # draw nodes
        for node in self.nodes:
            pygame.draw.circle(self.display_surface, 'blue', node_positions[node.id], self.node_size)
        # draw caption
        text = self.font.render(str(caption), True, 'black')
        self.display_surface.blit(text, (self.x_offset + 5, self.y_offset + 5))

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

