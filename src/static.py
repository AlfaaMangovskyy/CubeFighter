import math, random
import json as j

WIDTH = 1920
HEIGHT = 1080
FRAMERATE = 60

with open("src/characters.json") as source:
    CHARACTERS : dict[str, dict[str, str | int]] = j.load(source)
    source.close()

def sign(n : int | float) -> int:
    if n == 0: return 0
    return n // abs(n)
def nullf():
    print("No function defined here.")

def ned(a : int | float, b : int | float):
    if b != 0:
        return a / b
    return a

"""
float uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1));
float uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1));
"""
def lineIntersection(
    A1 : tuple[float, float],
    A2 : tuple[float, float],
    B1 : tuple[float, float],
    B2 : tuple[float, float],
):
    uA1 = ((B2[0] - B1[0]) * (A1[1] - B1[1]) - (B2[1] - B1[1]) * (A1[0] - B1[0]))
    uA2 = ((B2[1] - B1[1]) * (A2[0] - A1[0]) - (B2[0] - B1[0]) * (A2[1] - A1[1]))
    uB1 = ((A2[0] - A1[0]) * (A1[1] - B1[1]) - (A2[1] - A1[1]) * (A1[0] - B1[0]))
    uB2 = ((B2[1] - B1[1]) * (A2[0] - A1[0]) - (B2[0] - B1[0]) * (A2[1] - A1[1]))

    if uA2 != 0:
        uA = uA1 / uA2
    else:
        uA = uA1
    if uB2 != 0:
        uB = uB1 / uB2
    else:
        uB = uB1

    return 0 <= uA <= 1 and 0 <= uB <= 1

class Platform:
    def __init__(self, x : int, y : int, w : int):
        self.x, self.y = x, y
        self.w = w

class Arena:
    def __init__(self, hitboxes : list[Platform], controllers : list = []):
        self.hitboxes = hitboxes
        self.playerA = Player("A", self, -9, 0)
        self.playerB = Player("B", self, 7, 0)
        self.playerA.opponent = self.playerB
        self.playerB.opponent = self.playerA

        self.controllers : list[Controller] = controllers

        self.scale = 50

        self.sounds : list[str] = []
        # self.rays : list[Ray] = []
        self.entities : list[Entity] = []

        self.particles : list[Particle] = []
        self.shake = 0
        self.shakeForce = 0
        self.shakeDuration = 0

        self.sounds : list[str] = []

    def reset(self):
        self.playerA.reset()
        self.playerB.reset()
        self.playerA.hp = 5
        self.playerB.hp = 5
        self.playerA.reward = 0
        self.playerB.reward = 0

        self.scale = 50

        self.sounds : list[str] = []
        # self.rays : list[Ray] = []
        self.entities : list[Entity] = []

        self.particles : list[Particle] = []
        self.shake = 0
        self.shakeForce = 0
        self.shakeDuration = 0

    def particle(self, icon : str, x : float, y : float, vx : float, vy : float, d : int):
        self.particles.append(Particle(icon, x, y, vx, vy, d))

    def playSound(self, sound : str, delay : int = 0):
        self.sounds.append([sound, delay])

    def ray(self, id : str, x : float, y : float, vx : float, vy : float, d : int):
        self.rays.append(Ray(id, x, y, vx, vy, d))

    def cameraShake(self, f : int, d : int):
        self.shake = d
        self.shakeForce = f
        self.shakeDuration = d

    def getCamera(self) -> tuple[float, float]:
        shakeX = random.randint(5, 25) / 10 * random.choice([self.shake % 2, self.shake % 2 + 1]) * self.shakeForce * random.choice([1, -1])
        shakeY = random.randint(5, 25) / 10 * random.choice([self.shake % 2, self.shake % 2 + 1]) * self.shakeForce * random.choice([1, -1])
        # delta = min(ned(WIDTH, abs(self.playerB.x - self.playerA.x)), ned(HEIGHT, abs(self.playerB.y - self.playerA.y))) * 0.75
        # deltaX = delta * self.scale + WIDTH // 2
        # deltaY = delta * self.scale + HEIGHT // 2
        return (
            shakeX, # + deltaX
            shakeY, # + deltaY
        )

    def tick(self):
        if self.shake > 0:
            self.shake -= 1
            if self.shake == 0:
                self.shakeForce = 0
                self.shakeDuration = 0

        for entity in self.entities:
            entity.tick()
            if entity.destroy:
                self.entities.remove(entity)
                del entity

    def getRay(self, id : str):
        ret : Ray | None = None
        for ray in self.rays:
            if ray.id == id:
                ret = ray
                break
        return ret

    def existsRay(self, id : str):
        ret : bool = False
        for ray in self.rays:
            if ray.id == id:
                ret = True
                break
        return ret

class Particle:
    def __init__(self, icon : str, x : float, y : float, vx : float, vy : float, d : int):
        self.icon = icon
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.d = d

        self.timer = 0
        self.visible = True

    def tick(self):
        self.timer += 1
        self.x += self.vx
        self.y += self.vy
        if self.timer >= self.d:
            self.visible = False

class Ray:
    def __init__(self, id : str, x : float, y : float, vx : float, vy : float, d : int):
        self.id = id
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.d = d
        self.timer = 0
        self.destroy = False

    def tick(self):
        self.timer += 1
        self.x += self.vx
        self.y += self.vy
        if self.timer >= self.d:
            self.destroy = True

class Controller:
    def __init__(self, joystick):
        self.joystick = joystick
        self.player : Player | None = None

        self.axisX = 0.0
        self.axisY = 0.0

        self.axisD = 0

        self.sensitivity = 0.25

    def buttonDown(self, id : int):
        if self.player:
            if id == 1:
                self.player.jump()
            elif id == 0:
                # func = getattr(self.player, self.player.chardata.get("moveset", {}).get("normal", "punch"), nullf)
                # func()
                self.player.moveNormal()
            elif id == 3:
                # func = getattr(self.player, self.player.chardata.get("moveset", {}).get("special", "rayblast"), nullf)
                # func()
                self.player.moveSpecial()
            elif id == 2:
                # func = getattr(self.player, self.player.chardata.get("moveset", {}).get("ultimate", "earthpound"), nullf)
                # func()
                self.player.moveUltimate()
            else:
                print(id)

    def buttonUp(self, id : int):
        if self.player:
            if id == 1:
                pass
            else:
                print(id)

    def joystickAxis(self, axis : int, value : float):
        if axis == 0:
            self.axisX = value
        if axis == 1:
            self.axisY = value
        if self.player:
            if axis == 0:
                if self.axisX >= self.sensitivity:
                    self.axisD = 1
                elif self.axisX <= -self.sensitivity:
                    self.axisD = -1
                else:
                    self.axisD = 0

class Player:
    def __init__(self, playerID : str, arena, x : float = 0, y : float = 0):
        self.playerID = playerID
        self.rootX, self.rootY = x, y
        self.arena : Arena = arena
        self.x, self.y = x, y
        self.speed = 0.35
        self.gravity = 0.25

        self.opponent : Player | None = None

        self.grounded = False
        self.jumpTimer = 0
        self.speed = 0.125
        self.canDoubleJump = False
        self.doubleJump = False

        self.potentialv = 0
        self.potentialh = 0

        self.stun = 0
        self.stunNegative = True
        self.launchV = 0
        self.launchA = 0
        self.launchTimer = 0
        self.launchMaxTime = 0
        self.launchPoint = (0,0)

        self.damage = 0
        self.damageCounter = 0
        self.gravStun = 0
        self.shield = 0

        self.specialCounter = 0
        self.specialCommunicate = 0

        self.move : str | None = None
        self.moveTimer : int = 0
        # self.moveStartup = 0
        # self.moveActive = 0
        # self.moveStopout = 0

        self.character = "FIGHTER"
        self.chardata = CHARACTERS.get(self.character, {})

        self.controller : Controller | None = None

        self.hp = 0
        self.reward = 0

    def moveNormal(self):
        getattr(self, CHARACTERS.get(self.character, {}).get("moveset", {}).get("normal", "punch"))()

    def moveSpecial(self):
        if self.specialCounter == 0:
            getattr(self, CHARACTERS.get(self.character, {}).get("moveset", {}).get("special", "rayblast"))()
            self.specialCounter = FRAMERATE * 20
            self.specialCommunicate = 0

    def moveUltimate(self):
        if self.reward == 300:
            getattr(self, CHARACTERS.get(self.character, {}).get("moveset", {}).get("ultimate", "earthpound"))()
            self.reward = 0

    def tick(self):
        if self.gravStun == 0:
            if self.jumpTimer > 0:
                self.jumpTimer -= 1
                self.movementY(-self.gravity * 0.8 * (3 if self.doubleJump else 1))
                self.potentialv = 0
            elif self.launchTimer == 0:
                self.movementY(self.gravity * self.potentialv)
                self.tilt = 0

        if self.moveTimer > 0:
            self.moveTimer -= 1
        if self.moveTimer == 0:
            self.move = None

        if self.specialCounter > 0:
            self.specialCounter -= 1
            if self.specialCounter == 0:
                self.specialCommunicate = FRAMERATE * 2

        if self.specialCommunicate > 0:
            self.specialCommunicate -= 1

        if self.stun > 0:
            self.stun -= 1
        if self.stun == 0:
            self.stunNegative = False

        if self.gravStun > 0:
            self.gravStun -= 1

        if self.shield > 0:
            self.shield -= 1

        if self.controller:
            self.movementX(self.speed * self.controller.axisD)

        if not (-22 <= self.x <= 22):
            self.eliminate()
        elif not (-15 <= self.y <= 15):
            self.eliminate()

        # """
        # boolean left =   lineLine(x1,y1,x2,y2, rx,ry,rx, ry+rh);
        # boolean right =  lineLine(x1,y1,x2,y2, rx+rw,ry, rx+rw,ry+rh);
        # boolean top =    lineLine(x1,y1,x2,y2, rx,ry, rx+rw,ry);
        # boolean bottom = lineLine(x1,y1,x2,y2, rx,ry+rh, rx+rw,ry+rh);
        # """

        # if self.arena.existsRay(f"rayblast{self.playerID}1") and self.arena.existsRay(f"rayblast{self.playerID}2"):
        #     R1 = (self.arena.getRay(f"rayblast{self.playerID}1").x, self.arena.getRay(f"rayblast{self.playerID}1").y)
        #     R2 = (self.arena.getRay(f"rayblast{self.playerID}2").x, self.arena.getRay(f"rayblast{self.playerID}2").y)
        #     l = lineIntersection(R1, R2, (self.x, self.y), (self.x, self.y + 2))
        #     r = lineIntersection(R1, R2, (self.x + 2, self.y), (self.x + 2, self.y + 2))
        #     t = lineIntersection(R1, R2, (self.x, self.y), (self.x + 2, self.y))
        #     b = lineIntersection(R1, R2, (self.x, self.y + 2), (self.x + 2, self.y + 2))
        #     hit = l or r or t or b
        #     if hit:
        #         self.opponent.hitDamage(25)
        #         self.opponent.launch(12, 45 / 180 * math.pi)
        #         self.arena.playSound("hit")

        if self.move == "RAYBLAST":
            if self.moveTimer == FRAMERATE:
                self.arena.playSound(f"ultimate{random.randint(1, 3)}")
                self.arena.cameraShake(7, FRAMERATE // 4)
                if self.x - 1.5 <= self.opponent.x + 1 and self.opponent.x - 1 <= self.x + 1.5:
                    self.opponent.hitDamage(30)
                    self.opponent.launch(0.1 * self.opponent.damage, 60 / 180 * math.pi * sign(self.x - self.opponent.x))
                    self.arena.playSound("hit")
                    self.arena.cameraShake(15, FRAMERATE // 4)

                    direction = sign(self.opponent.y - self.y)
                    if direction == 0:
                        direction = -1
                    for e in range(25):
                        theta = random.randint(45, 135) / 180 * math.pi
                        rf = random.randint(25, 75) / 100
                        self.arena.particle(
                            "rayblast_red" if self.playerID == "A" else "rayblast_blue",
                            self.opponent.x, self.opponent.y + direction * 1,
                            direction * rf * math.cos(theta),
                            direction * rf * math.sin(theta),
                            FRAMERATE // 2,
                        )
                elif self.y - 1.5 <= self.opponent.y + 1 and self.opponent.y - 1 <= self.y + 1.5:
                    self.opponent.hitDamage(30)
                    self.opponent.launch(0.1 * self.opponent.damage, 30 / 180 * math.pi * sign(self.x - self.opponent.x))
                    self.arena.playSound("hit")
                    self.arena.cameraShake(15, FRAMERATE // 4)

                    direction = sign(self.opponent.x - self.x)
                    for e in range(25):
                        theta = random.randint(-45, 45) / 180 * math.pi
                        rf = random.randint(25, 75) / 100
                        self.arena.particle(
                            "rayblast_red" if self.playerID == "A" else "rayblast_blue",
                            self.opponent.x + direction * 3, self.opponent.y,
                            direction * rf * math.cos(theta),
                            direction * rf * math.sin(theta),
                            FRAMERATE // 2,
                        )

        if self.move == "EARTHPOUND":
            # self.arena.particle("smoke", self.x, self.y, 0, 0, 1)
            if self.moveTimer == round(FRAMERATE * 1.5):
                self.arena.cameraShake(20, round(FRAMERATE * 1.5))
            if self.moveTimer <= round(FRAMERATE * 1.5):
                if self.moveTimer % (FRAMERATE // 3) == 1:
                    if self.opponent.grounded and self.opponent.launchTimer == 0:
                        self.opponent.hitDamage(7)
                        self.opponent.hitStun(FRAMERATE)
                        self.opponent.launch(2.5, 85 * sign(self.opponent.x - self.x) / 180 * math.pi)
                        self.arena.playSound("hit")

        if self.move == "TAKEOFF":
            self.y += -self.speed * 2
            self.potentialv = 0
            self.arena.particle(
                "potential",
                self.x, self.y, 0, 0.25, FRAMERATE * 1
            )
            # if self.launchTimer == 0:
            #     self.moveTimer = 0
            #     self.move = None

        if self.launchTimer > 0:
            tn = self.launchMaxTime / 15 * (15 - self.launchTimer)
            tp = self.launchMaxTime / 15 * (16 - self.launchTimer)

            xn = self.launchV * tn * math.cos(self.launchA)
            xp = self.launchV * tp * math.cos(self.launchA)
            xd = xn - xp

            yn = self.launchV * tn * math.sin(self.launchA) - 5 * tn ** 2
            yp = self.launchV * tp * math.sin(self.launchA) - 5 * tp ** 2
            yd = yn - yp

            self.x += xd
            self.y += yd
            self.launchTimer -= 1

            self.tilt += round(self.launchV * 4)

    def eliminate(self):
        self.arena.particles.clear()
        for e in range(25):
            v = random.randint(75, 150) / 100
            theta = math.atan2(self.y, self.x) + random.randint(-45, 45) / 180 * math.pi
            # print(theta)
            self.arena.particle(
                "smoke_red" if self.playerID == "A" else "smoke_blue",
                self.x, self.y, v * -math.cos(theta), v * -math.sin(theta), FRAMERATE * 2,
            )
        self.arena.playSound("hit", 0)
        self.arena.playSound("hit", FRAMERATE // 12)
        self.arena.playSound("hit", FRAMERATE // 6)
        self.arena.cameraShake(15, FRAMERATE // 4)
        self.reset()

    def movementX(self, delta : float):
        if self.stun == 0:
            if sign(delta) != sign(self.potentialh) and self.potentialh != 0:
                self.potentialh = 0
            self.potentialh += 0.05 * sign(delta)
            self.x += delta * (1 + abs(self.potentialh))

    def movementY(self, delta : float):
        self.y += delta
        self.potentialv += 0.05
        for hitbox in self.arena.hitboxes:
            if isinstance(hitbox, Platform):
                if hitbox.x <= self.x - 1 <= hitbox.x + hitbox.w or hitbox.x <= self.x + 1 <= hitbox.x + hitbox.w:
                    if self.y - 1 <= hitbox.y <= self.y + 1:
                        diff = hitbox.y - self.y
                        if diff >= 0:
                            self.y = hitbox.y - 1
                            if not self.grounded: self.land()
                            self.potentialv = 0
                            self.grounded = True
                            self.canDoubleJump = True
                            self.doubleJump = False
                            self.canDash = False
                            self.tilt = 0
                        else:
                            self.y = hitbox.y

    def launch(self, v : float, a : float):
        if self.shield > 0: return
        self.launchV = v
        self.launchA = a
        self.launchTimer = 15
        self.launchMaxTime = (0.2 * self.launchV * math.sin(self.launchA))# * 1.2
        self.launchPoint = (self.x,self.y)

    def hitStun(self, duration : int, negative : bool = True):
        if self.shield > 0: return
        self.stun += duration
        self.stunNegative = negative

    def hitGravStun(self, duration : int):
        if self.shield > 0: return
        self.gravStun += duration

    def jump(self):
        if self.stun == 0:
            if self.grounded:
                self.grounded = False
                self.jumpTimer = 15
                self.canDash = True
            else:
                if self.canDoubleJump:
                    self.canDoubleJump = False
                    self.doubleJump = True
                    self.jumpTimer += 15

    def land(self):
        # pass
        self.arena.playSound("land")
        if self.potentialv >= 1.5:
            d = math.sqrt((self.x - self.opponent.x) ** 2 + (self.y - self.opponent.y) ** 2)
            if d <= 4.5:
                self.opponent.hitDamage(12)

                self.opponent.launch(
                    self.potentialv * (self.opponent.damage + 10) / 30,
                    45 * sign(self.x - self.opponent.x),
                )

                self.arena.cameraShake(round(self.potentialv * 2), FRAMERATE * 0.2)
                self.arena.playSound("hit")

    def reset(self):
        self.x = self.rootX
        self.y = self.rootY
        self.potentialv = 0
        self.potentialh = 0
        self.launchV = 0
        self.launchA = 0
        self.launchTimer = 0
        self.launchMaxTime = 0
        self.launchPoint = (0,0)
        self.damage = 0
        self.combo = 0
        self.comboTimer = 0
        self.reward = 0

    def hitDamage(self, amount : int):
        if self.shield > 0: return
        self.damage += amount
        if self.damage > 200:
            self.damage = 200
        self.opponent.reward += amount
        if self.opponent.reward > 300:
            self.opponent.reward = 300

    ################################################

    def punch(self):
        distance = math.sqrt((self.x - self.opponent.x) ** 2 + (self.y - self.opponent.y) ** 2)
        if distance <= 2.5:
            self.opponent.hitDamage(3)
            self.potentialh *= 0.75

            self.opponent.launch(
                self.opponent.damage * 0.1, sign(self.x - self.opponent.x) * 15 / 180 * math.pi
            )

            self.arena.playSound("hit")
            for e in range(10):
                theta = random.randint(-25, 25) / 180 * math.pi
                directorial = sign(self.opponent.x - self.x)
                v = random.randint(25, 50) * self.opponent.damage / 10000
                self.arena.particle(
                    "smoke_red" if self.playerID == "A" else "smoke_blue",
                    self.opponent.x + directorial, self.opponent.y,
                    v * math.cos(theta) * directorial,
                    v * math.sin(theta) * directorial,
                    round(FRAMERATE * 0.25),
                )

    def rayblast(self):

        if not self.move:
            self.move = "RAYBLAST"
            self.moveTimer = round(FRAMERATE * 1.5)
            self.hitStun(round(FRAMERATE * 1.5), False)
            self.hitGravStun(round(FRAMERATE * 1.5))
            self.doubleJump = False
            self.canDoubleJump = True
            for e in range(25):
                theta = random.randint(0, 360) / 180 * math.pi
                distance = random.randint(225, 475) / 100
                self.arena.particle(
                    "smoke_red" if self.playerID == "A" else "smoke_blue",
                    self.x + distance * math.cos(theta),
                    self.y + distance * math.sin(theta),
                    distance * -math.cos(theta) * (1 / (FRAMERATE // 2)),
                    distance * -math.sin(theta) * (1 / (FRAMERATE // 2)),
                    FRAMERATE // 2,
                )

    def earthpound(self):

        if not self.move:
            self.move = "EARTHPOUND"
            self.moveTimer = round(FRAMERATE * 3)
            self.hitStun(round(FRAMERATE * 3), False)
            self.hitGravStun(round(FRAMERATE * 3))
            self.doubleJump = False
            self.canDoubleJump = True
            for e in range(25):
                theta = random.randint(0, 360) / 180 * math.pi
                distance = random.randint(450, 850) / 100
                self.arena.particle(
                    "smoke",
                    self.x + distance * math.cos(theta),
                    self.y + distance * math.sin(theta),
                    distance * -math.cos(theta) * (1 / round(FRAMERATE * 1.5)),
                    distance * -math.sin(theta) * (1 / round(FRAMERATE * 1.5)),
                    round(FRAMERATE * 1.5),
                )

    def takeoff(self):

        if not self.move:
            self.move = "TAKEOFF"
            self.moveTimer = round(FRAMERATE * 0.75)
            self.arena.playSound(f"ultimate{random.randint(1, 3)}")
            # self.hitStun(round(FRAMERATE * 1), False)
            self.doubleJump = False
            self.canDoubleJump = True

            d = math.sqrt((self.x - self.opponent.x) ** 2 + (self.y - self.opponent.y) ** 2)
            director = 45 * -sign(self.opponent.x - self.x) / 180 * math.pi
            if sign(self.opponent.x - self.x) == 0:
                director = 85 / 180 * math.pi
            if d <= 3.5:
                self.arena.playSound("hit")
                self.opponent.launch(
                    7.5, director
                )
                self.opponent.hitDamage(12)
                self.opponent.hitStun(round(FRAMERATE * 0.75))

            self.potentialv = 0

            for e in range(25):
                theta = random.randint(225, 315) / 180 * math.pi
                v = random.randint(25, 125) / 100
                self.arena.particle(
                    "smoke",
                    self.x, self.y - 1,
                    v * math.cos(theta), -v * math.sin(theta),
                    round(FRAMERATE * 0.75),
                )

class Entity:
    def __init__(self, image : str, x : float, y : float, w : int, h : int, vx : float, vy : float, d : int = -1):
        self.image = image
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.vx, self.vy = vx, vy
        self.d = d

        self.timer = 0
        self.destroy = False

    def tick(self):
        self.timer += 1
        self.x += self.vx
        self.y += self.vy
        if self.d >= 0:
            if self.timer >= self.d:
                self.destroy = True

    def collides(self, player : Player) -> bool:
        collidesX = self.x + self.w >= player.x and self.x <= player.x + 2
        collidesY = self.y + self.h >= player.y and self.y <= player.y + 2
        return collidesX and collidesY