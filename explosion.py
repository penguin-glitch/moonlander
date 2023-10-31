from spritesheet import SpriteSheet

class Explosion:
    def __init__(self, pos):
        self.x = pos[0]
        self.y = -pos[1]+1000
        self.frames = []

        self.load_frames()

        self.step = 0

    def load_frames(self):
        ss = SpriteSheet('images/explosion.png') #load spritesheet

        frame_rect = (0, 0, 15, 15)
        frame = ss.image_at(frame_rect)

        self.frames.append(frame)

        frame_rect = (15,0,15,15)
        frame = ss.image_at(frame_rect)

        self.frames.append(frame)

        frame_rect = (0,15,15,15)
        frame = ss.image_at(frame_rect)

        self.frames.append(frame)

    def draw(self, screen):
        screen.blit(self.frames[int(self.step / 5)], (self.x,self.y))
        self.step += 1
        
