import pygame

pygame.init()
pygame.joystick.init()

# List all detected controllers
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    print(f"Joystick {i}: {joystick.get_name()}")

clk = pygame.time.Clock()

while True:

    for e in pygame.event.get():
        if e.type == pygame.JOYBUTTONDOWN:
            print(e.joy, e.button)
        if e.type == pygame.JOYAXISMOTION:
            print(e.joy, e.axis, e.value)

    clk.tick(60)