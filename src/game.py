import pygame
from static import *

import sys

DEBUG = False
if len(sys.argv) > 1:
    if sys.argv[1] in ("-debug", "-d", "debug", "d"):
        DEBUG = True

pygame.init()
pygame.joystick.init()
screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), FRAMERATE,
)
clock = pygame.time.Clock()

arena = Arena([
    Platform(-12, 7, 24),
])

connected = 0
for joystick_id in range(pygame.joystick.get_count()):
    if connected == 0:
        arena.playerA.controller = Controller(pygame.joystick.Joystick(joystick_id))
        arena.playerA.controller.player = arena.playerA
        connected = 1
    elif connected == 1:
        arena.playerB.controller = Controller(pygame.joystick.Joystick(joystick_id))
        arena.playerB.controller.player = arena.playerB
        connected = 2

running = True
while running:

    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN:

            if e.key == pygame.K_ESCAPE:
                running = False
                pygame.quit()
                break

        if e.type == pygame.JOYBUTTONDOWN:
            if e.joy == 0:
                arena.playerA.controller.buttonDown(e.button)
            if e.joy == 1:
                arena.playerB.controller.buttonDown(e.button)

        elif e.type == pygame.JOYBUTTONUP:
            if e.joy == 0:
                arena.playerA.controller.buttonUp(e.button)
            if e.joy == 1:
                arena.playerB.controller.buttonUp(e.button)

        elif e.type == pygame.JOYAXISMOTION:
            if e.joy == 0:
                arena.playerA.controller.joystickAxis(e.axis, round(e.value, 2))
            if e.joy == 1:
                arena.playerB.controller.joystickAxis(e.axis, round(e.value, 2))

    if not running: break

    arena.playerA.tick()
    arena.playerB.tick()
    arena.tick()

    for ray in arena.rays:
        ray.tick()
        if ray.destroy:
            arena.rays.remove(ray)
            del ray

    screen.fill("#030303")

    pygame.draw.rect(screen, "#FF0000", (
        arena.playerA.x * arena.scale + WIDTH // 2,
        arena.playerA.y * arena.scale + HEIGHT // 2,
        2 * arena.scale, 2 * arena.scale,
    ))

    pygame.draw.rect(screen, "#0000FF", (
        arena.playerB.x * arena.scale + WIDTH // 2,
        arena.playerB.y * arena.scale + HEIGHT // 2,
        2 * arena.scale, 2 * arena.scale,
    ))

    for hitbox in arena.hitboxes:
        if isinstance(hitbox, Platform):
            pygame.draw.line(
                screen, "#FFFFFF",
                (hitbox.x * arena.scale + WIDTH // 2, hitbox.y * arena.scale + HEIGHT // 2),
                ((hitbox.x + hitbox.w) * arena.scale + WIDTH // 2, hitbox.y * arena.scale + HEIGHT // 2),
                5,
            )

    idx = 0
    for sound_data in arena.sounds:
        if sound_data[1] == 0:
            sound = pygame.mixer.Sound(f"src/make/sfx/{sound_data[0]}.mp3")
            sound.set_volume(1.25)
            sound.play()
            arena.sounds.remove(sound_data)
        else:
            arena.sounds[idx][1] -= 1
        idx += 1

    for particle in arena.particles:
        particle.tick()
        if not particle.visible:
            arena.particles.remove(particle)

    for particle in arena.particles:
        # print(particle.x, particle.y)
        img = pygame.image.load(f"src/make/particle/{particle.icon}.png")
        screen.blit(
            img, (
                particle.x * arena.scale + WIDTH // 2,
                particle.y * arena.scale + HEIGHT // 2,
            )
        )

    # if DEBUG:
    #     for ray in arena.rays:
    #         pygame.draw.rect(
    #             screen, "#FFFFFF",
    #             (
    #                 ray.x * arena.scale + WIDTH // 2 - 5,
    #                 ray.y * arena.scale + HEIGHT // 2 - 5,
    #                 10, 10,
    #             ), 2,
    #         )

    #     rayA = arena.getRay("rayblastA1")
    #     rayB = arena.getRay("rayblastA2")
    #     if rayA and rayB:
    #         pygame.draw.line(
    #             screen, "#FFFFFF",
    #             (
    #                 rayA.x * arena.scale + WIDTH // 2,
    #                 rayA.y * arena.scale + HEIGHT // 2,
    #             ),
    #             (
    #                 rayB.x * arena.scale + WIDTH // 2,
    #                 rayB.y * arena.scale + HEIGHT // 2,
    #             )
    #         )

    pygame.display.update()
    clock.tick(FRAMERATE)