import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import math

def draw_sphere(radius, slices, stacks, tile_factor=1):
    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)

    # Enable texture tiling
    glMatrixMode(GL_TEXTURE)
    glPushMatrix()
    glScalef(tile_factor, tile_factor, 1.0)  # Repeat the texture
    glMatrixMode(GL_MODELVIEW)

    gluSphere(quadric, radius, slices, stacks)

    # Reset texture matrix
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

        # Outer edge of the ring
        glTexCoord2f(1, i % 2)  # Alternate texture coordinate to stretch texture
        glVertex3f(x * outer_radius, 0, y * outer_radius)

        # Inner edge of the ring
        glTexCoord2f(0, i % 2)  # Alternate texture coordinate to stretch texture
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
    
    light_position = [0.0, 0.0, 0.0, 1.0]  # Sun's position
    light_color = [1.0, 1.0, 0.8, 1.0]    # Warm light for the Sun
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_color)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_color)

def draw_planet(texture, radius, distance, angle):
    glPushMatrix()
    glRotatef(angle, 0, 1, 0)  # Orbit rotation
    glTranslatef(distance, 0, 0)  # Distance from the Sun
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
    draw_sphere(radius, 32, 32)
    glDisable(GL_TEXTURE_2D)
    
    glPopMatrix()

def draw_stars_background(texture):
    glPushMatrix()
    glDisable(GL_LIGHTING)  # Disable lighting for the background
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Move the background sphere further away
    glTranslatef(0, 0, 0)  # Distance from the Sun

    # Render a large sphere for the background
    glColor4f(1, 1, 1, 1)  # Ensure the texture renders at full brightness
    draw_sphere(1000, 64, 64, tile_factor=100)  # Large radius for the background
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)  # Re-enable lighting
    glPopMatrix()


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 5000.0)
    glTranslatef(0.0, 0.0, -100)
    glEnable(GL_DEPTH_TEST)

    # Load textures
    textures = {
        "stars": load_texture("textures/8k_stars.jpg"),
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

    # Planet data: (texture_key, radius, distance_from_sun, orbital_speed)
    planets = [
        ("mercury", 0.3, 40, 0.415),
        ("venus", 0.7, 70, 0.162),
        ("earth", 1.0, 100, 0.1),
        ("mars", 0.5, 150, 0.053),
        ("jupiter", 3.0, 300, 0.0084),
        ("saturn", 2.5, 500, 0.0034),
        ("uranus", 2.0, 700, 0.0011),
        ("neptune", 1.8, 900, 0.0006),
    ]

    # Orbital angles for planets and moon
    orbital_angles = {planet[0]: 0 for planet in planets}
    moon_angle = 0  # Moon's orbital angle around Earth

    # Mouse and zoom controls
    mouse_down = False
    rotation_x, rotation_y = 0, 0
    zoom = -100

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_down = True
                elif event.button == 4:  # Mouse wheel up
                    zoom += 2  # Zoom in
                elif event.button == 5:  # Mouse wheel down
                    zoom -= 2  # Zoom out
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_down = False
            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    dx, dy = event.rel
                    rotation_x += dy * 0.2  # Adjust sensitivity
                    rotation_y += dx * 0.2

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        init_lighting()

        # Reset and apply camera transformations
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 5000.0)
        glTranslatef(0.0, 0.0, zoom)
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)

        # Draw stars background
        draw_stars_background(textures["stars"])

        # Draw Sun
        glPushMatrix()
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures["sun"])
        draw_sphere(2.0, 32, 32)  # Sun's size
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPopMatrix()

        # Draw planets
        for planet, radius, distance, speed in planets:
            orbital_angles[planet] += speed  # Update orbital angle
            draw_planet(textures[planet], radius, distance, orbital_angles[planet])

            # Add rings to Saturn
            if planet == "saturn":
                glPushMatrix()
                glRotatef(orbital_angles["saturn"], 0, 1, 0)  # Saturn's orbit
                glTranslatef(distance, 0, 0)  # Saturn's position
                draw_ring(textures["saturn_ring"], 3.0, 5.0)  # Inner and outer radius
                glPopMatrix()

            # Add Moon orbiting Earth
            if planet == "earth":
                moon_angle += 2.0  # Moon's orbital speed around Earth
                glPushMatrix()
                glRotatef(orbital_angles["earth"], 0, 1, 0)  # Earth's orbit
                glTranslatef(distance, 0, 0)  # Earth's position
                draw_planet(textures["moon"], 0.3, 1.5, moon_angle)  # Moon size and distance from Earth
                glPopMatrix()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
