import pygame
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 700
BACKGROUND_COLOR = (20, 20, 30)
CUBE_COLORS = {
    'F': (0, 255, 100),    # Front - Green
    'B': (0, 150, 255),    # Back - Blue
    'U': (255, 255, 255),  # Up - White
    'D': (255, 255, 0),    # Down - Yellow
    'L': (255, 150, 0),    # Left - Orange
    'R': (255, 50, 50)     # Right - Red
}
FACE_NAMES = ['F', 'B', 'U', 'D', 'L', 'R']

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Rubik's Cube Simulator")
clock = pygame.time.Clock()

# Matrix multiplication helper functions
def matrix_multiply(matrix, vector):
    result = [0, 0, 0]
    for i in range(3):
        for j in range(3):
            result[i] += matrix[i][j] * vector[j]
    return result

def create_rotation_x(angle):
    return [
        [1, 0, 0],
        [0, math.cos(angle), -math.sin(angle)],
        [0, math.sin(angle), math.cos(angle)]
    ]

def create_rotation_y(angle):
    return [
        [math.cos(angle), 0, math.sin(angle)],
        [0, 1, 0],
        [-math.sin(angle), 0, math.cos(angle)]
    ]

# Cube class
class RubiksCube:
    def __init__(self):
        self.reset()
        self.angle_x = 0.5
        self.angle_y = 0.7
        self.zoom = 12
        self.rotating = False
        self.rotation_axis = None
        self.rotation_angle = 0
        self.target_angle = 0
        self.rotation_speed = 0.1
        self.rotation_layer = None
        self.rotation_direction = 1
        self.rotation_progress = 0
        
    def reset(self):
        # Initialize the cube state
        self.state = {}
        for face in FACE_NAMES:
            self.state[face] = [[face for _ in range(3)] for _ in range(3)]
    
    def rotate_face(self, face, direction):
        # Rotate a face clockwise or counter-clockwise
        if direction == 1:  # Clockwise
            # Rotate the face itself
            self.state[face] = [list(row) for row in zip(*self.state[face][::-1])]
            
            # Rotate the adjacent stickers
            if face == 'F':
                temp = [self.state['U'][2][i] for i in range(3)]
                for i in range(3):
                    self.state['U'][2][i] = self.state['L'][2-i][2]
                    self.state['L'][2-i][2] = self.state['D'][0][2-i]
                    self.state['D'][0][2-i] = self.state['R'][i][0]
                    self.state['R'][i][0] = temp[i]
                    
            elif face == 'B':
                temp = [self.state['U'][0][i] for i in range(3)]
                for i in range(3):
                    self.state['U'][0][i] = self.state['R'][i][2]
                    self.state['R'][i][2] = self.state['D'][2][2-i]
                    self.state['D'][2][2-i] = self.state['L'][2-i][0]
                    self.state['L'][2-i][0] = temp[i]
                    
            elif face == 'U':
                temp = self.state['F'][0][:]
                for i in range(3):
                    self.state['F'][0][i] = self.state['R'][0][i]
                    self.state['R'][0][i] = self.state['B'][0][i]
                    self.state['B'][0][i] = self.state['L'][0][i]
                    self.state['L'][0][i] = temp[i]
                    
            elif face == 'D':
                temp = self.state['F'][2][:]
                for i in range(3):
                    self.state['F'][2][i] = self.state['L'][2][i]
                    self.state['L'][2][i] = self.state['B'][2][i]
                    self.state['B'][2][i] = self.state['R'][2][i]
                    self.state['R'][2][i] = temp[i]
                    
            elif face == 'L':
                temp = [self.state['U'][i][0] for i in range(3)]
                for i in range(3):
                    self.state['U'][i][0] = self.state['B'][2-i][2]
                    self.state['B'][2-i][2] = self.state['D'][i][0]
                    self.state['D'][i][0] = self.state['F'][i][0]
                    self.state['F'][i][0] = temp[i]
                    
            elif face == 'R':
                temp = [self.state['U'][i][2] for i in range(3)]
                for i in range(3):
                    self.state['U'][i][2] = self.state['F'][i][2]
                    self.state['F'][i][2] = self.state['D'][i][2]
                    self.state['D'][i][2] = self.state['B'][2-i][0]
                    self.state['B'][2-i][0] = temp[i]
        
        else:  # Counter-clockwise
            # For counter-clockwise, rotate clockwise three times
            for _ in range(3):
                self.rotate_face(face, 1)
    
    def start_rotation(self, face, direction):
        self.rotating = True
        self.rotation_layer = face
        self.rotation_direction = direction
        self.target_angle = direction * (math.pi / 2)
        self.rotation_progress = 0
        
    def update_rotation(self):
        if self.rotating:
            self.rotation_progress += self.rotation_speed
            if self.rotation_progress >= 1:
                self.rotating = False
                self.rotate_face(self.rotation_layer, self.rotation_direction)
    
    def get_rotation_angle(self):
        if self.rotating:
            return self.rotation_direction * (math.pi / 2) * self.rotation_progress
        return 0
    
    def draw(self, screen):
        # Project 3D point to 2D
        def project_point(x, y, z):
            # Create rotation matrices
            rot_x = create_rotation_x(self.angle_x)
            rot_y = create_rotation_y(self.angle_y)
            
            # Apply rotations
            point = [x, y, z]
            point = matrix_multiply(rot_x, point)
            point = matrix_multiply(rot_y, point)
            
            # Perspective projection
            z = 1.5 + point[2]  # Adjust z for perspective
            scale = self.zoom / z
            x_proj = point[0] * scale + WIDTH / 2
            y_proj = point[1] * scale + HEIGHT / 2
            
            return x_proj, y_proj
        
        # Draw cube
        size = 0.5
        rotation_angle = self.get_rotation_angle()
        
        # Draw the cube faces
        for face_idx, face in enumerate(FACE_NAMES):
            for i in range(3):
                for j in range(3):
                    x, y, z = 0, 0, 0
                    rotation_axis = None
                    
                    if face == 'F':
                        x, y, z = j - 1, 1 - i, 1.5
                        rotation_axis = 'z'
                    elif face == 'B':
                        x, y, z = 1 - j, 1 - i, -1.5
                        rotation_axis = 'z'
                    elif face == 'U':
                        x, y, z = j - 1, -1.5, 1 - i
                        rotation_axis = 'y'
                    elif face == 'D':
                        x, y, z = j - 1, 1.5, i - 1
                        rotation_axis = 'y'
                    elif face == 'L':
                        x, y, z = -1.5, 1 - i, j - 1
                        rotation_axis = 'x'
                    elif face == 'R':
                        x, y, z = 1.5, 1 - i, 1 - j
                        rotation_axis = 'x'
                    
                    # Apply rotation if this is the rotating layer
                    if self.rotating and face == self.rotation_layer:
                        if rotation_axis == 'x':
                            y, z = self.rotate_point(y, z, rotation_angle)
                        elif rotation_axis == 'y':
                            x, z = self.rotate_point(x, z, rotation_angle)
                        elif rotation_axis == 'z':
                            x, y = self.rotate_point(x, y, rotation_angle)
                    
                    # Project to 2D
                    points = []
                    for dx, dy in [(-size, -size), (size, -size), (size, size), (-size, size)]:
                        px, py = x, y
                        if face in ['F', 'B']:
                            px += dx
                            py += dy
                        elif face in ['U', 'D']:
                            px += dx
                            pz = z + dy
                        elif face in ['L', 'R']:
                            py += dx
                            pz = z + dy
                        
                        if face == 'F' or face == 'B':
                            p2d = project_point(px, py, z)
                        elif face == 'U' or face == 'D':
                            p2d = project_point(px, y, pz)
                        elif face == 'L' or face == 'R':
                            p2d = project_point(x, py, pz)
                        
                        points.append(p2d)
                    
                    # Draw the face
                    color = CUBE_COLORS[self.state[face][i][j]]
                    pygame.draw.polygon(screen, color, points)
                    pygame.draw.polygon(screen, (30, 30, 40), points, 1)
    
    def rotate_point(self, x, y, angle):
        # Rotate a point around the origin
        new_x = x * math.cos(angle) - y * math.sin(angle)
        new_y = x * math.sin(angle) + y * math.cos(angle)
        return new_x, new_y

# Create cube
cube = RubiksCube()

# UI Elements
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 150), self.rect, 3, border_radius=10)
        
        text_surf = self.font.render(self.text, True, (240, 240, 240))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Create buttons
buttons = []
face_btns = []
for i, face in enumerate(['F', 'B', 'U', 'D', 'L', 'R']):
    btn = Button(50 + i*150, 600, 120, 50, f"{face} (Clockwise)", (80, 80, 120), (120, 120, 170))
    face_btns.append((face, 1, btn))
    buttons.append(btn)

for i, face in enumerate(['F', 'B', 'U', 'D', 'L', 'R']):
    btn = Button(50 + i*150, 660, 120, 50, f"{face} (Counter)", (80, 80, 120), (120, 120, 170))
    face_btns.append((face, -1, btn))
    buttons.append(btn)

# Reset button
reset_btn = Button(800, 600, 150, 50, "Reset Cube", (180, 70, 70), (220, 100, 100))
buttons.append(reset_btn)

# Instructions
font = pygame.font.SysFont('Arial', 18)
title_font = pygame.font.SysFont('Arial', 40, bold=True)

# Main loop
running = True
dragging = False
last_mouse_pos = None

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        # Handle button clicks
        for face, direction, btn in face_btns:
            if btn.is_clicked(mouse_pos, event) and not cube.rotating:
                cube.start_rotation(face, direction)
        
        if reset_btn.is_clicked(mouse_pos, event) and not cube.rotating:
            cube.reset()
        
        # Handle mouse dragging for cube rotation
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for btn in buttons:
                    if btn.rect.collidepoint(mouse_pos):
                        break
                else:
                    dragging = True
                    last_mouse_pos = mouse_pos
        
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
        
        elif event.type == MOUSEMOTION and dragging and not cube.rotating:
            dx = mouse_pos[0] - last_mouse_pos[0]
            dy = mouse_pos[1] - last_mouse_pos[1]
            cube.angle_y += dx * 0.01
            cube.angle_x += dy * 0.01
            last_mouse_pos = mouse_pos
    
    # Update button hover states
    for btn in buttons:
        btn.check_hover(mouse_pos)
    
    # Update cube rotation
    cube.update_rotation()
    
    # Draw everything
    screen.fill(BACKGROUND_COLOR)
    
    # Draw title
    title = title_font.render("3D RUBIK'S CUBE SIMULATOR", True, (220, 220, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
    
    # Draw instructions
    instructions = [
        "CONTROLS:",
        "- Click the buttons below to rotate faces",
        "- Drag the cube to rotate it in 3D space",
        "- Reset button returns cube to solved state"
    ]
    
    for i, text in enumerate(instructions):
        text_surf = font.render(text, True, (180, 180, 220))
        screen.blit(text_surf, (50, 80 + i*30))
    
    # Draw the cube
    cube.draw(screen)
    
    # Draw buttons
    for btn in buttons:
        btn.draw(screen)
    
    # Draw current rotation status
    if cube.rotating:
        status = font.render(f"Rotating {cube.rotation_layer} face...", True, (255, 255, 150))
        screen.blit(status, (WIDTH//2 - status.get_width()//2, HEIGHT - 40))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()