import os
os.environ["SDL_JOYSTICK_HIDAPI_JOYCON"] = "1"
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

def getFont(size : int) -> pygame.font.Font:
    return pygame.font.Font(f"src/make/fontJ.otf", size)
def getDigitFont(size : int) -> pygame.font.Font:
    return pygame.font.Font(f"src/make/fontD.ttf", size)

print(pygame.joystick.get_count())
print(list(pygame.joystick.Joystick(n) for n in range(pygame.joystick.get_count())))

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

            if e.key == pygame.K_s:
                arena.playerB.jump()
            if e.key == pygame.K_w:
                func = getattr(arena.playerB, arena.playerB.chardata.get("moveset", {}).get("normal", "punch"), nullf)
                func()
            if e.key == pygame.K_q:
                func = getattr(arena.playerB, arena.playerB.chardata.get("moveset", {}).get("special", "rayblast"), nullf)
                func()
            if e.key == pygame.K_e:
                func = getattr(arena.playerB, arena.playerB.chardata.get("moveset", {}).get("ultimate", "earthpound"), nullf)
                func()

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

    keymap = pygame.key.get_pressed()
    if keymap[pygame.K_a]:
        arena.playerB.movementX(-arena.playerB.speed)
    if keymap[pygame.K_d]:
        arena.playerB.movementX(arena.playerB.speed)

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
                screen, "#FF3333",
                (
                    (arena.playerA.x - 1.5 * d) * arena.scale + WIDTH // 2, 0,
                    d * arena.scale * 3, HEIGHT,
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
                screen, "#FF4444",
                (
                    (arena.playerA.x - 1.5 * d * 0.8) * arena.scale + WIDTH // 2, 0,
                    d * arena.scale * 3 * 0.8, HEIGHT,
                )
            )
            pygame.draw.rect(
                screen, "#FF5555",
                (
                    0, (arena.playerA.y - 1.5 * d * 0.7) * arena.scale + HEIGHT // 2,
                    WIDTH, d * arena.scale * 3 * 0.7,
                )
            )
            pygame.draw.rect(
                screen, "#FF5555",
                (
                    (arena.playerA.x - 1.5 * d * 0.7) * arena.scale + WIDTH // 2, 0,
                    d * arena.scale * 3 * 0.7, HEIGHT,
                )
            )

    if arena.playerB.move == "RAYBLAST":
        if arena.playerB.moveTimer <= FRAMERATE:
            d = arena.playerB.moveTimer / 60
            pygame.draw.rect(
                screen, "#3333FF",
                (
                    0, (arena.playerB.y - 1.5 * d) * arena.scale + HEIGHT // 2,
                    WIDTH, d * arena.scale * 3,
                )
            )
            pygame.draw.rect(
                screen, "#3333FF",
                (
                    (arena.playerB.x - 1.5 * d) * arena.scale + WIDTH // 2, 0,
                    d * arena.scale * 3, HEIGHT,
                )
            )
            pygame.draw.rect(
                screen, "#4444FF",
                (
                    0, (arena.playerB.y - 1.5 * d * 0.8) * arena.scale + HEIGHT // 2,
                    WIDTH, d * arena.scale * 3 * 0.8,
                )
            )
            pygame.draw.rect(
                screen, "#4444FF",
                (
                    (arena.playerB.x - 1.5 * d * 0.8) * arena.scale + WIDTH // 2, 0,
                    d * arena.scale * 3 * 0.8, HEIGHT,
                )
            )
            pygame.draw.rect(
                screen, "#5555FF",
                (
                    0, (arena.playerB.y - 1.5 * d * 0.7) * arena.scale + HEIGHT // 2,
                    WIDTH, d * arena.scale * 3 * 0.7,
                )
            )
            pygame.draw.rect(
                screen, "#5555FF",
                (
                    (arena.playerB.x - 1.5 * d * 0.7) * arena.scale + WIDTH // 2, 0,
                    d * arena.scale * 3 * 0.7, HEIGHT,
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
    imgA = pygame.image.load(f"src/make/face/{face}.png")
    imgA = pygame.transform.scale(imgA, (arena.scale * 2, arena.scale * 2))
    screen.blit(imgA, (
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
    imgB = pygame.image.load(f"src/make/face/{face}.png")
    imgB = pygame.transform.scale(imgB, (arena.scale * 2, arena.scale * 2))
    screen.blit(imgB, (
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
                particle.x * arena.scale + WIDTH // 2 - cameraX - img.get_width() // 2,
                particle.y * arena.scale + HEIGHT // 2 - cameraY - img.get_height() // 2,
            )
        )

    damageAcolor = "#FFFFFF"
    if arena.playerA.damage >= 125:
        damageAcolor = "#FFFF00"
    if arena.playerA.damage >= 175:
        damageAcolor = "#FF0000"
    damageA = getDigitFont(75).render(
        f"{arena.playerA.damage}%", 0, damageAcolor
    )
    screen.blit(
        damageA, (150, 25)
    )

    damageBcolor = "#FFFFFF"
    if arena.playerB.damage >= 125:
        damageBcolor = "#FFFF00"
    if arena.playerB.damage >= 175:
        damageBcolor = "#FF0000"
    damageB = getDigitFont(75).render(
        f"{arena.playerB.damage}%", 0, damageBcolor
    )
    screen.blit(
        damageB, (WIDTH - 150 - damageB.get_width(), 25)
    )

    pygame.draw.rect(
        screen, "#FF0000",
        (25, 25, 100, 100)
    )
    screen.blit(
        imgA, (25, 25)
    )

    pygame.draw.rect(
        screen, "#0000FF",
        (WIDTH - 125, 25, 100, 100)
    )
    screen.blit(
        imgB, (WIDTH - 125, 25)
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

    # pygame.draw.circle(
    #     screen, "#FFFFFF",
    #     (arena.playerA.x * arena.scale + WIDTH // 2, arena.playerA.y * arena.scale + HEIGHT // 2), 5
    # )

    pygame.display.update()
    clock.tick(FRAMERATE)