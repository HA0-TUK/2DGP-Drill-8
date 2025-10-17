from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a  

from state_machine import StateMachine


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE
def time_out(e):
    return e[0] == 'TIME_OUT'

def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


class Idle:

    def __init__(self, boy):
        self.boy = boy
        self.start_time = 0

    def enter(self, e):
        self.boy.dir = 0
        self.start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        
        # 5초 후 TIME_OUT 이벤트 발생
        elapsed_time = get_time() - self.start_time
        if elapsed_time >= 5.0:
            self.boy.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_draw(self.boy.frame * 100, 300, 100, 100, self.boy.x, self.boy.y)
        else: # face_dir == -1: # left
            self.boy.image.clip_draw(self.boy.frame * 100, 200, 100, 100, self.boy.x, self.boy.y)

class Run:
    def __init__(self, boy):
        self.boy = boy
    def enter(self, e):
        if right_down(e) or left_up(e):
            self.boy.dir = self.boy.face_dir = 1
        elif left_down(e) or right_up(e):
            self.boy.dir = self.boy.face_dir = -1
    def exit(self, e):
        pass
    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        self.boy.x += self.boy.dir * 5
    def draw(self):
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_draw(self.boy.frame * 100, 100, 100, 100, self.boy.x, self.boy.y)
        else: # face_dir == -1: # left
            self.boy.image.clip_draw(self.boy.frame * 100, 0, 100, 100, self.boy.x, self.boy.y)
            
class Sleep:
    def __init__(self, boy):
        self.boy = boy
    def enter(self, e):
        self.boy.dir = 0
    def exit(self, e):
        pass
    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        pass
    def draw(self):
        if self.boy.face_dir == 1:
            self.boy.image.clip_composite_draw(self.boy.frame * 100, 300, 100, 100, 3.141592/2, '', self.boy.x - 25, self.boy.y - 25, 100, 100)
        else:
            self.boy.image.clip_composite_draw(self.boy.frame * 100, 200, 100, 100, -3.141592/2, '', self.boy.x + 25, self.boy.y - 25, 100, 100)
# 5초 진행 후 idle
# 진입 키 입력

class AUTORUN:
    def __init__(self, boy):
        self.boy = boy

        self.start_time = 0
        self.speed = 3

        self.scale = 1.0

    def enter(self, e):
        # a 키입력으로 진입
        self.start_time = get_time()
        self.boy.dir = self.boy.face_dir  # 현재 방향 유지


    def exit(self,e):
        self.scale = 1.0  # 원래 크기로 복원
        self.speed = 3

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        
        # 시간에 따른 속도와 크기 증가
        elapsed_time = get_time() - self.start_time
        self.speed = 3 + (elapsed_time * 4)
        self.scale = 1.0 + (elapsed_time * 0.2)
        
        # 키 조작 없이도 좌우로 계속 이동
        self.boy.x += self.boy.dir * self.speed
        
        # 화면 좌우 끝에서 방향전환
        if self.boy.x <= 50:
            self.boy.x = 50
            self.boy.dir = self.boy.face_dir = 1
        elif self.boy.x >= 750:
            self.boy.x = 750
            self.boy.dir = self.boy.face_dir = -1
            
        # 5초 후 타임아웃 이벤트 발생
        if elapsed_time >= 5.0:
            self.boy.state_machine.handle_state_event(('AUTORUN_TIME_OUT', None))

    def draw(self):
        size = int(100 * self.scale)
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_draw(self.boy.frame * 100, 100, 100, 100, self.boy.x, self.boy.y, size, size)
        else: # face_dir == -1: # left
            self.boy.image.clip_draw(self.boy.frame * 100, 0, 100, 100, self.boy.x, self.boy.y, size, size)



class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.image = load_image('animation_sheet.png')

        self.IDLE = Idle(self)
        self.SLEEP = Sleep(self)
        self.RUN = Run(self)
        self.AUTORUN = AUTORUN(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.SLEEP : {space_down: self.IDLE, right_down: self.RUN, left_down: self.RUN, right_up: self.RUN, left_up: self.RUN},
                self.IDLE : {time_out: self.SLEEP, right_down: self.RUN, left_down: self.RUN, right_up: self.RUN, left_up: self.RUN, a_down: self.AUTORUN},
                self.RUN : {right_up: self.IDLE, left_up: self.IDLE, right_down: self.IDLE, left_down: self.IDLE},
                self.AUTORUN : {time_out: self.IDLE, right_down: self.RUN, left_down: self.RUN}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
                                              
    def draw(self):
        self.state_machine.draw()
