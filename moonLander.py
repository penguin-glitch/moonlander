import pygame, math, random, time, os

import pymunk
from pymunk import Vec2d

from explosion import Explosion
from spritesheet import SpriteSheet

pygame.init()
pygame.font.init()

file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)

font = pygame.font.Font("a.ttf", 25)

screen = pygame.display.set_mode((1000,1000))
pygame.display.set_caption("Moon Lander")

points = 0

clock = pygame.time.Clock()

#pymunk


#collisions
collision_types = {
        "player": 1,
        "landing": 2,
        "mountain": 3,
        }

def flipy(y):
	return -y+1000

def generateTerrain():
        global staticLines

        staticLines = []
	
        #generate landing spots
        hx = random.randint(50, 300)
        hy = random.randint(500, 600)
        high = pymunk.Segment(space.static_body, (hx, hy), (hx + 20, hy), 0.0)
        high.collision_type = collision_types["landing"]
        
        mx = random.randint(700, 1000)
        my = random.randint(300, 450)
        med = pymunk.Segment(space.static_body, (mx, my), (mx + 20, my), 0.0)
        med.collision_type = collision_types["landing"]
        
        lx = random.randint(400, 600)
        ly = random.randint(100, 150)
        low = pymunk.Segment(space.static_body, (lx, ly), (lx + 20, ly), 0.0)
        low.collision_type = collision_types["landing"]

        staticLines = [high, med, low]

        #mountain sides
        try: #first in between point
                px = random.randint(hx + 100, lx - 100)
                py = random.randint(ly + 50, hy - 100)
        except ValueError as e:
                print(e)
                px = hx + 100
                py = ly + 100

        #line from first point to end
        seg = pymunk.Segment(space.static_body, (px,py), (lx,ly), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)

        try: #second point
                px2 = random.randint(hx + 50, px - 50)
                py2 = random.randint(py + 50, hy - 50)
        except ValueError as e:
                print(e)
                px2 = hx + 50
                py2 = py - 50

        #line from point 1 to point 2
        seg = pymunk.Segment(space.static_body, (px, py), (px2,py2), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)

        #line from source to point 2
        seg = pymunk.Segment(space.static_body, (hx + 20, hy), (px2,py2), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)

        try: #repeat
                px = random.randint(lx + 100, mx - 100)
                py = random.randint(ly + 50, my - 100)
        except ValueError as e:
                print(str(e) + " at high to low")
                px = lx + 100
                py = ly + 100

        seg = pymunk.Segment(space.static_body, (px,py), (mx,my), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)
        
        try:
                px2 = random.randint(lx + 50, px - 25)
                py2 = random.randint(py + 50, ly + 50)
        except ValueError as e:
                print(str(e) + " at low to med")
                px2 = lx + 50
                py2 = py - 50

        seg = pymunk.Segment(space.static_body, (px, py), (px2,py2), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)     
        
        seg = pymunk.Segment(space.static_body, (lx + 20, ly), (px2,py2), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)

        #border sides
        try:
                px = random.randint(50, hx - 40)
        except ValueError as e:
                px = hx - 40
        py = random.randint(400, hy - 40)
        
        seg = pymunk.Segment(space.static_body, (0, random.randint(200, 300)), (px,py), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)
        seg = pymunk.Segment(space.static_body, (px,py), (hx,hy), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)

        try:
                px = random.randint(mx + 90, 900)
        except:
                px = mx + 90
        py = random.randint(my + 50, 500)
        seg = pymunk.Segment(space.static_body, (1000, random.randint(500, 700)), (px,py), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)
        seg = pymunk.Segment(space.static_body, (mx + 20, my), (px,py), 0.0)
        seg.collision_type = collision_types["mountain"]
        staticLines.append(seg)
        
        for line in staticLines:
                space.add(line)

old_points = 0

def initialise():
        global player, player_img, done, won, fuel, angle, space, exp, throttle, frames, marker, asteroids

        space = pymunk.Space()
        space.gravity = Vec2d(0.0, -10.0)

        throttle = 0

        exp = None

        asteroids = []
        
        #spawning the player with physics
        x = random.randint(100, 900)
        y = 950
        angle = 180
        vs = [(-6,18), (6,18), (0,-18)]
        mass = 10
        moment = pymunk.moment_for_poly(mass, vs)
        body = pymunk.Body(mass, moment)
        shape = pymunk.Poly(body, vs)
        shape.friction = 0.5
        body.position = x, y
        body.angle = angle
        space.add(body, shape)
        player = shape
        player.collision_type = collision_types["player"]

        marker = pygame.image.load('images/marker.png')

        player_ss = SpriteSheet("images/player_ss.png")

        frameRects = []
        for i in range(11):
                if i <= 6:
                        x = 12*i
                else:
                        x = 12*i - 72
                frameRects.append((x,int(i / 6) * 36, 12, 36))

        print(frameRects[6])

        frames = []     
        for i in frameRects:
                frames.append(player_ss.image_at(i))

        player_img = frames[0]

        done = False
        won = False

        fuel = 200
        
        generateTerrain()

        def destroy_player(arbiter, space, data):
                global points, old_points
                if not won and not invuln: #and points == old_points:
                        global exp
                        points -= 10
                        old_points = points
                        exp = Explosion(player.body.position)
                return True

        def win(arbiter, space, data):
                if int(speed) < 10:
                        global won, points, old_points, invuln
                        print("Victory!")
                        won = True
                        old_points = points #helps stop the player from dying and winning at the same time
                        if player.body.position[1] > 500:
                                points += 10
                        elif player.body.position[1] < 500 and player.body.position[1] > 300:
                                points += 5
                        elif player.body.position[1] < 300:
                                points += 20
                        time.sleep(1)
                        initialise()
                        invuln = True
                else:
                        destroy_player('a', space, 'c')
                return True
        

        death = space.add_collision_handler(
                collision_types["player"],
                collision_types["mountain"])
        death.begin = destroy_player

        land = space.add_collision_handler(
                collision_types["player"],
                collision_types["landing"],
                )
        land.begin = win

initialise()

def calc_speed(pos, oldPos):
        difX = pos[0] - oldPos[0]
        difY = pos[1] - oldPos[1]

        return int(math.sqrt(difX**2 + difY**2) * 10)

def draw():
        screen.fill((0,0,0))

        if exp == None:
                player.body.angle = math.radians(angle)
                
                p = player.body.position
                p = Vec2d(p.x, flipy(p.y) + 12.5)

                angle_degrees = math.degrees(player.body.angle) + 180
                rotated_player_img = pygame.transform.rotate(player_img, angle_degrees)

                offset = Vec2d(rotated_player_img.get_size()[0], rotated_player_img.get_size()[1]) / 2
                p = p - offset

                screen.blit(rotated_player_img, p)

                if player.body.position[1] > 1030:
                        screen.blit(marker, (player.body.position[0], 15))
        else:
                exp.draw(screen)
                if exp.step >= 15:
                        time.sleep(0.5)
                        initialise()
        
        for line in staticLines:
                body = line.body
                
                pv1 = body.position + line.a.rotated(body.angle)
                pv2 = body.position + line.b.rotated(body.angle)
                p1 = pv1.x, flipy(pv1.y)
                p2 = pv2.x, flipy(pv2.y)
                pygame.draw.lines(screen, (255,255,255), False, [p1,p2], 2)

        pygame.draw.rect(screen, (255,255,255), (950, 250 + (200 - fuel), 25, fuel), width=5)
        screen.blit(speedLabel,(500,900))

        pointsLabel = font.render(str(points), False, (255,255,255))
        screen.blit(pointsLabel, (50,50))

while not done: #update
        oldPos = player.body.position
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    done = True
                elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                                angle += 45
                        elif event.key == pygame.K_d:
                                angle -= 45
                        #elif event.key == pygame.K_w:
                         #       angle = 180

        if not won:
                dt = 1.0/60.0
                for x in range(1):
                        space.step(dt)
                        #for i in asteroids:
                         #       i.update()

                keys = pygame.key.get_pressed()
                #if keys[pygame.K_a] and fuel > 0:
                #        player.body.apply_impulse_at_local_point(Vec2d((5,-10)))
                #        fuel -= 1
                #if keys[pygame.K_d] and fuel > 0:
                #        player.body.apply_impulse_at_local_point(Vec2d((5,-10)))
                #        fuel -= 1
                #if keys[pygame.K_w] and angle == 180 and fuel > 0:
                #        player.body.apply_impulse_at_local_point(Vec2d((1, -30)))
                #        fuel -= 2

                if keys[pygame.K_SPACE] and throttle < 10 and fuel > 0:
                        throttle += 0.5
                elif throttle > 0:
                        throttle -= 1

                if fuel <= 0:
                        throttle = 0

                if int(throttle) != 6:
                        player_img = frames[int(throttle)]
                else:
                        player_img = frames[5]

                if angle < 0:
                        angle = 315
                elif angle > 360:
                        angle = 45

                if throttle > 0 and fuel > 0: #ok this bits a mystery to me i just changed the numbers until it worked
                        if angle < 90 or angle > 270 and angle != 0:
                                player.body.apply_impulse_at_local_point(Vec2d(3.5, -3 * throttle))
                        elif angle > 90 and angle < 270 and angle != 180:
                                player.body.apply_impulse_at_local_point(Vec2d(-3.5, -5 * throttle))
                        elif angle == 270 or angle == 90:
                                player.body.apply_impulse_at_local_point(Vec2d(1, -3 * throttle))
                        elif angle == 0:
                                player.body.apply_impulse_at_local_point(Vec2d(0, -2 * throttle))
                        elif angle == 180:
                                player.body.apply_impulse_at_local_point(Vec2d(0, -2 * throttle))
                        fuel -= 0.1 * throttle
        
        speed = str(calc_speed(player.body.position, oldPos))
        if calc_speed(player.body.position, oldPos) < 10:
                speedLabel = font.render(speed, False, (255,255,255))
        else:
                speedLabel = font.render(speed, False, (255,0,0))
        draw()
        
        if player.body.position[0] > 1000 or player.body.position[0] < 0:
                points -= 10
                initialise()

        pygame.display.flip()
        clock.tick(60)
        invuln = False

        
while True:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        pygame.quit()
                        break
#pygame.quit()
