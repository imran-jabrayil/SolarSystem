import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import math

def draw_sphere(radius, slices, stacks, tilt_angle=0):
    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)

    glMatrixMode(GL_TEXTURE)
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)

    glRotatef(tilt_angle, 1, 0, 0)

    gluSphere(quadric, radius, slices, stacks)

    glMatrixMode(GL_TEXTURE)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    gluDeleteQuadric(quadric)


def draw_ring(texture, inner_radius, outer_radius, num_segments=64):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUAD_STRIP)

    for i in range(num_segments + 1):
        theta = 2.0 * 3.1415926 * i / num_segments
        x = math.cos(theta)
        y = math.sin(theta)

        glTexCoord2f(1, i % 2)
        glVertex3f(x * outer_radius, 0, y * outer_radius)

        glTexCoord2f(0, i % 2)
        glVertex3f(x * inner_radius, 0, y * inner_radius)

    glEnd()
    glDisable(GL_TEXTURE_2D)


def load_texture(image_path):
    if not os.path.exists(image_path):
        print(f"Error: Texture file '{image_path}' not found.")
        return None

    texture = glGenTextures(1)
    texture_surface = pygame.image.load(image_path)
    if not texture_surface:
        print(f"Error: Failed to load texture from '{image_path}'.")
        return None

    texture_data = pygame.image.tostring(texture_surface, "RGB", True)
    width, height = texture_surface.get_size()
    
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    print(f"Texture '{image_path}' loaded successfully.")
    return texture

def init_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    light_position = [0.0, 0.0, 0.0, 1.0]
    light_color = [1.0, 1.0, 0.8, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_color)

def draw_planet(texture, radius, distance, angle, tilt_angle=0):
    glPushMatrix()
    glRotatef(angle, 0, 1, 0)
    glTranslatef(distance, 0, 0)
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
    draw_sphere(radius, 32, 32, tilt_angle)
    glDisable(GL_TEXTURE_2D)
    
    glPopMatrix()

def draw_stars_background(texture):
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTranslatef(0, 0, 0)

    glColor4f(1, 1, 1, 1)
    draw_sphere(1000, 64, 64, tilt_angle=90)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glPopMatrix()


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 5000.0)
    glTranslatef(0.0, 0.0, -100)
    glEnable(GL_DEPTH_TEST)

    textures = {
        "stars": load_texture("textures/8k_stars_milky_way.jpg"),
        "sun": load_texture("textures/8k_sun.jpg"),
        "mercury": load_texture("textures/8k_mercury.jpg"),
        "venus": load_texture("textures/4k_venus_atmosphere.jpg"),
        "earth": load_texture("textures/8k_earth_daymap.jpg"),
        "moon": load_texture("textures/8k_moon.jpg"),
        "mars": load_texture("textures/8k_mars.jpg"),
        "jupiter": load_texture("textures/8k_jupiter.jpg"),
        "saturn": load_texture("textures/8k_saturn.jpg"),
        "saturn_ring": load_texture("textures/8k_saturn_ring_alpha.png"),
        "uranus": load_texture("textures/2k_uranus.jpg"),
        "neptune": load_texture("textures/2k_neptune.jpg"),
    }

    if any(v is None for v in textures.values()):
        print("Error: One or more textures failed to load.")
        pygame.quit()
        return

    planets = [
        ("mercury", 0.3, 40, 0.415, -90),
        ("venus", 0.7, 70, 0.162, 87.4),
        ("earth", 1.0, 100, 0.1, -66.6),
        ("mars", 0.5, 150, 0.053, -64.8),
        ("jupiter", 3.0, 300, 0.0084, -86.9),
        ("saturn", 2.5, 500, 0.0034, -63.3),
        ("uranus", 2.0, 700, 0.0011, 7.8),
        ("neptune", 1.8, 900, 0.0006, -61.7),
    ]

    orbital_angles = {planet[0]: 0 for planet in planets}
    moon_angle = 0

    mouse_down = False
    rotation_x, rotation_y = 0, 0
    zoom = -100

    paused = False

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                elif event.button == 4:
                    zoom += 2
                elif event.button == 5:
                    zoom -= 2
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    dx, dy = event.rel
                    rotation_x += dy * 0.2
                    rotation_y += dx * 0.2
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            for planet in planets:
                orbital_angles[planet[0]] += planet[3]
            moon_angle += 2.0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        init_lighting()

        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 5000.0)
        glTranslatef(0.0, 0.0, zoom)
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)

        draw_stars_background(textures["stars"])

        glPushMatrix()
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures["sun"])
        draw_sphere(20, 32, 32)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPopMatrix()

        for planet, radius, distance, speed, tilt_angle in planets:
            draw_planet(textures[planet], radius, distance, orbital_angles[planet], tilt_angle)

            if planet == "saturn":
                glPushMatrix()
                glRotatef(orbital_angles["saturn"], 0, 1, 0)
                glTranslatef(distance, 0, 0)
                draw_ring(textures["saturn_ring"], 3.0, 5.0)
                glPopMatrix()

            if planet == "earth":
                glPushMatrix()
                glRotatef(orbital_angles["earth"], 0, 1, 0)
                glTranslatef(distance, 0, 0)
                draw_planet(textures["moon"], 0.3, 1.5, moon_angle, 0)
                glPopMatrix()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
