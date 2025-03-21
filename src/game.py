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

    cameraX, cameraY = arena.getCamera()

    for ray in arena.rays:
        ray.tick()
        if ray.destroy:
            arena.rays.remove(ray)
            del ray

    screen.fill("#030303")
    # print(cameraX, cameraY)

    if arena.playerA.move == "RAYBLAST":
        if arena.playerA.moveTimer <= FRAMERATE:
            d = arena.playerA.moveTimer / 60
            pygame.draw.rect(
                screen, "#FF3333",
                (
                    0, (arena.playerA.y - 1.5 * d) * arena.scale + HEIGHT // 2,
                    WIDTH, d * arena.scale * 3,
                )
            )
            pygame.draw.rect(
                screen, "#FF4444",
                (
                    0, (arena.playerA.y - 1.5 * d * 0.8) * arena.scale + HEIGHT // 2,
                    WIDTH, d * arena.scale * 3 * 0.8,
                )
            )
            pygame.draw.rect(
                screen, "#FF5555",
                (
                    0, (arena.playerA.y - 1.5 * d * 0.7) * arena.scale + HEIGHT // 2,
                    WIDTH, d * arena.scale * 3 * 0.7,
                )
            )

    pygame.draw.rect(screen, "#FF0000", (
        (arena.playerA.x - 1) * arena.scale + WIDTH // 2 - cameraX,
        (arena.playerA.y - 1) * arena.scale + HEIGHT // 2 - cameraY,
        2 * arena.scale, 2 * arena.scale,
    ))

    face = "normal"
    if arena.playerA.move:
        face = "charging"
    if arena.playerA.launchTimer > 0:
        face = "impact"
    if arena.playerA.stun > 0 and arena.playerA.stunNegative:
        face = "stunned"
    img = pygame.image.load(f"src/make/face/{face}.png")
    img = pygame.transform.scale(img, (arena.scale * 2, arena.scale * 2))
    screen.blit(img, (
        (arena.playerA.x - 1) * arena.scale + WIDTH // 2 - cameraX,
        (arena.playerA.y - 1) * arena.scale + HEIGHT // 2 - cameraY,
    ))

    pygame.draw.rect(screen, "#0000FF", (
        (arena.playerB.x - 1) * arena.scale + WIDTH // 2 - cameraX,
        (arena.playerB.y - 1) * arena.scale + HEIGHT // 2 - cameraY,
        2 * arena.scale, 2 * arena.scale,
    ))

    face = "normal"
    if arena.playerB.move:
        face = "charging"
    if arena.playerB.launchTimer > 0:
        face = "impact"
    if arena.playerB.stun > 0 and arena.playerB.stunNegative:
        face = "stunned"
    img = pygame.image.load(f"src/make/face/{face}.png")
    img = pygame.transform.scale(img, (arena.scale * 2, arena.scale * 2))
    screen.blit(img, (
        (arena.playerB.x - 1) * arena.scale + WIDTH // 2 - cameraX,
        (arena.playerB.y - 1) * arena.scale + HEIGHT // 2 - cameraY,
    ))

    for hitbox in arena.hitboxes:
        if isinstance(hitbox, Platform):
            pygame.draw.line(
                screen, "#FFFFFF",
                (hitbox.x * arena.scale + WIDTH // 2 - cameraX, hitbox.y * arena.scale + HEIGHT // 2 - cameraY),
                ((hitbox.x + hitbox.w) * arena.scale + WIDTH // 2 - cameraX, hitbox.y * arena.scale + HEIGHT // 2 - cameraY),
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
                particle.x * arena.scale + WIDTH // 2 - cameraX,
                particle.y * arena.scale + HEIGHT // 2 - cameraY,
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

    pygame.draw.circle(
        screen, "#FFFFFF",
        (arena.playerA.x * arena.scale + WIDTH // 2, arena.playerA.y * arena.scale + HEIGHT // 2), 5
    )

    pygame.display.update()
    clock.tick(FRAMERATE)