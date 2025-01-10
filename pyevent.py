import pygame
import time
import math

pygame.init()
pygame.font.init()

K_a = 97
K_b = 98
K_c = 99
K_d = 100
K_e = 101
K_f = 102
K_g = 103
K_h = 104
K_i = 105
K_j = 106
K_k = 107
K_l = 108
K_m = 109
K_n = 110
K_o = 111
K_p = 112
K_q = 113
K_r = 114
K_s = 115
K_t = 116
K_u = 117
K_v = 118
K_w = 119
K_x = 120
K_y = 121
K_z = 122
K_0 = 48
K_1 = 49
K_2 = 50
K_3 = 51
K_4 = 52
K_5 = 53
K_6 = 54
K_7 = 55
K_8 = 56
K_9 = 57
K_F1 = 1073741882
K_F2 = 1073741883
K_F3 = 1073741884
K_F4 = 1073741885
K_F5 = 1073741886
K_F6 = 1073741887
K_F7 = 1073741888
K_F8 = 1073741889
K_F9 = 1073741890
K_F10 = 1073741891
K_F11 = 1073741892
K_F12 = 1073741893

class ConfigError:
    def __init__(self, lack):
        raise Exception(f'Lack of Configuration: {lack}')

class TriggerEvent:
    def __init__(self):
        self.handles = []
        
    def Connect(self, obj):
        self.handles.append(obj)
    
    def Trigger(self, object, *args):
        for handle in self.handles:
            handle(object, *args)

class GameEvent:
    def __init__(self):
        self.handles = []
        
    def Connect(self, func):
        self.handles.append(func)
    
    def Trigger(self, *args):
        for handle in self.handles:
            handle(*args)

class RepeatedEvent:
    def __init__(self, function, interval_seconds):
        self.function = function
        self.interval = interval_seconds
        self.last_called = time.time()

    def update(self):
        if time.time() - self.last_called >= self.interval:
            self.function()
            self.last_called = time.time()

class KeyEvent:
    def __init__(self):
        self.handles = {}
    
    def Connect(self, key, func):
        self.handles.update({key:func})
    
    def Trigger(self, event):
        for key in self.handles.items():
            if key == event.key:
                self.handles[key]()
        
class NotifyEvent:
    def __init__(self, bg_color, text_color):
        self.bgc = bg_color
        self.textc = text_color
        self.Title = None
        self.Subtitles = []
        self.request = False
        self.duration = 0
        self.last_saved = 0

    def Save(self, info, screen, title, subtitle, duration):
        self.request = True
        self.duration = duration
        self.last_saved = time.time()
        
        width, height = info.current_w, info.current_h - int(20 / 100 * info.current_h)
        self.box_w, self.box_h = width // 1.5, height // 1.5
        self.box_x, self.box_y = (width - self.box_w) // 2, (height - self.box_h) // 2

        margin = int(3 / 100 * self.box_w)
        title_size = int(self.box_w // 14)
        subtitle_size = int(self.box_w // 18)

        if not self.Title or self.Title.text != title:
            self.Title = Text(title_size, (self.box_x + margin, self.box_y + margin), self.textc, title)

        self.Subtitles = []
        subtitle_lines = subtitle.split('\n')
        for i, line in enumerate(subtitle_lines):
            y_offset = self.box_y + margin + title_size + (i * (subtitle_size + margin))
            self.Subtitles.append(Text(subtitle_size, (self.box_x + margin, y_offset), self.textc, line))
            
    def Notify(self, screen):    
        if time.time() - self.last_saved > self.duration:
            self.request = False
         
        pygame.draw.rect(screen, self.bgc, (self.box_x, self.box_y, self.box_w, self.box_h))
                  
        self.Title.Draw(screen)
        for subtitle_obj in self.Subtitles:
            subtitle_obj.Draw(screen)
                     
class Text:
    def __init__(self, size, pos, color, text):
        self.size = size
        self.pos = pos
        self.color = color
        self.text = text
        self.font = pygame.font.SysFont('Roboto', size)
        self.text_surface = self.Render()
        self.rect = self.text_surface.get_rect(topleft=self.pos)

        self.visible = True
        
    def Render(self):
        return self.font.render(self.text, True, self.color)

    def Draw(self, surface):
        self.text_surface = self.Render()
        self.rect = self.text_surface.get_rect(topleft=self.pos)
        surface.blit(self.text_surface, self.pos)

    def Click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)   

import math

class Object:
    def __init__(self, id, size, pos, sprite):
        self.id = id
        self.size = size
        self.x, self.y = pos
        self.sprite = pygame.image.load(sprite)
        self.sprite = pygame.transform.scale(self.sprite, size)
        
        self.transparency = 0
        self.locked = True
        
        self.xvel = 0
        self.yvel = 0        
        
        self.Interacted = TriggerEvent()
        
    def Interact(self, *args):
        self.Interacted.Trigger(self, *args)
        return self
        
    def Clicked(self, mouse):
        x, y = mouse
        obj_x, obj_y = self.x, self.y
        obj_width, obj_height = self.size
        if obj_x <= x <= obj_x + obj_width and obj_y <= y <= obj_y + obj_height:
            self.Interact()
            return True
        return False
    
    def Update(self, info, gravity, args):
        if not self.locked:
            width = info.current_w
            height = info.current_h
            H = height - int(20 / 100 * height)
            
            self.x += self.xvel
            
            if self.x > 0:
                self.x -= 1
            elif self.x < 0:
                self.x += 1
            
            if self.y < 0:
                self.y += 2
                
            self.y += self.yvel
            
            for obj in args:
                if self != obj:
                    if (self.x < obj.x + obj.size[0] and self.x + self.size[0] > obj.x and
                        self.y < obj.y + obj.size[1] and self.y + self.size[1] > obj.y):
                        self.reflect(obj)

            self.check_wall_collision(info, H)

    def reflect(self, other):
        normal_x = self.x - other.x
        normal_y = self.y - other.y
        normal_length = math.sqrt(normal_x**2 + normal_y**2)
        
        if normal_length == 0:
            return
        
        normal_x /= normal_length
        normal_y /= normal_length
        
        v1x, v1y = self.xvel, self.yvel
        v2x, v2y = other.xvel, other.yvel
        
        v_rel = (v1x - v2x) * normal_x + (v1y - v2y) * normal_y
        
        if v_rel < 0:
            impulse = 2 * v_rel / 2
            self.xvel -= impulse * normal_x
            self.yvel -= impulse * normal_y
            other.xvel += impulse * normal_x
            other.yvel += impulse * normal_y

    def check_wall_collision(self, info, H):
        screen_width, screen_height = info.current_w, H
        
        if self.x <= 0:
            self.xvel = abs(self.xvel)
        elif self.x + self.size[0] >= screen_width:
            self.xvel = -abs(self.xvel)
        
        if self.y <= 0:
            self.yvel = abs(self.yvel)
        elif self.y + self.size[1] >= screen_height:
            self.yvel = 0

    def Draw(self, screen):
        alpha_value = int((1 - self.transparency) * 255)
        sprite_copy = self.sprite.copy()
        sprite_copy.set_alpha(alpha_value)
        screen.blit(sprite_copy, (self.x, self.y))
        
class Location:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.objects = []
    
    def Connect(self, obj):
        self.objects.append(obj)

class Bar:
    def __init__(self, progress, max, pos, color, size, outline=2, outlinec=(0, 0, 0)):
        self.progress = progress
        self.max = max
        self.pos = pos
        self.color = color
        self.size = size
        self.outline = outline
        self.outlinec = outlinec
        
    def Draw(self, screen):
        bar_width = int((self.progress / self.max) * self.size[0])
        outline_color = self.outlinec
        outline_thickness = self.outline 

        pygame.draw.rect(screen, (200, 200, 200), (*self.pos, *self.size))        
        pygame.draw.rect(screen, self.color, (*self.pos, bar_width, self.size[1]))
        pygame.draw.rect(screen, outline_color, (*self.pos, *self.size), outline_thickness)
        
class Leaderstats:
    def __init__(self):
        self.variable = {}
        
    def Add(self, name, value):
        self.variable.update({name:value})    
    
    def Edit(self, name, value):
        self.variable[name] = value
    
    def Delete(self, name):
        self.variable.pop(name)

class Health:
    def __init__(self):
        self.health = 100
    
    def Heal(self, value):
        self.health += value
    
    def Set(self, value):
        self.health = value
    
    def Damage(self, value):
        self.health -= value
    
    def OnDeath(self):
        if self.health <= 0:
            self.health = 100
            return True
            
        return False
        
class Character:
    def __init__(self):
        self.Leaderstats = Leaderstats()
        self.Health = Health()
    
class Game:
    def __init__(self, conf):
        self.running = True
        self.dependency = ['resolution', 'place']
        
        all_config = True
        for key in self.dependency:
            if key not in conf:
                all_config = False
                config = key
                break
        
        if all_config:
            print('Game Setup Successful')
        else:
            raise ConfigError(config)                
              
        self.config = conf
        self.screen = pygame.display.set_mode(conf['resolution'], conf.get('flags', pygame.RESIZABLE))
        pygame.display.set_caption(conf.get('title', 'PyEvent'))
        self.objects = []
        
        Default = conf['place']
        self.locations = [Default]
        self.locindex = 1
        self.location = Default
        
        self.Notification = NotifyEvent(conf.get('notify_background', (255, 255, 255)), conf.get('notify_text', (0, 0, 0)))
        self.KeyPressed = KeyEvent()
        self.PlayerAdded = GameEvent()
        self.PlayerRemoved = GameEvent()
        self.PlayerDeath = GameEvent()
        self.PlayerMoved = GameEvent()
        
        info = pygame.display.Info()
        size = int(20 / 100 * info.current_h)
        
        self.left = Text(size, (0, info.current_h - size), (0, 0, 0), '<')
        self.right = Text(size, (info.current_w - size / 2, info.current_h - size), (0, 0, 0), '>')
        self.stop = Text(size, (size, info.current_h - size * 1.1), (0, 0, 0), 'x')
        self.indicator = Text(int(size // 2), (size * 2, info.current_h - size // 1.5), (0, 0, 0), 'Not Found')
        
        screen_width = info.current_w
        screen_height = info.current_h
        margin = int(0.02 * screen_width)
        bar_width = int(0.2 * screen_width)
        bar_height = int(0.1 * screen_height)
        bar_x = screen_width - bar_width - margin
        bar_y = margin

        self.health_bar = Bar(progress=100, max=100, pos=(bar_x, bar_y), color=(255, 0, 0), size=(bar_width, bar_height), outline=margin//4)
        
        self.clock = pygame.time.Clock()
        self.fps = conf.get('fps', 60)
        
        self.functions = []
        
        self.Player = Character()
        
        self.gravity = conf.get('gravity', 0)
        
    def Add_Object(self, obj):
        self.objects.append(obj)
         
    def Add_Location(self, location):
        self.locations.append(location)
        
    def Move_Location(self, direction):
        if direction == 'left':
            move_to = self.locindex - 1
        elif direction == 'right':
            move_to = self.locindex + 1
   
        if move_to > 0:
            if move_to <= len(self.locations):
                self.locindex = move_to
                self.location = self.locations[move_to-1]
                self.PlayerMoved.Trigger()
      
    def Notify(self, title, subtitle='', duration=3):
        info = pygame.display.Info()
        self.Notification.Save(info, self.screen, title, subtitle, duration)     
    
    def Repeat(self, func, interval):
        self.functions.append(RepeatedFuction(func, interval))
          
    def Execute(self):
        self.PlayerAdded.Trigger()
        calc = []
        start = time.time()
        
        while self.running:
            Loops = time.time()
            
            for function in self.functions:
                function.update()
                
            self.health_bar.progress = self.Player.Health.health
            self.indicator.text = self.location.name
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    list_obj = []
                    for obj in self.location.objects:
                        list_obj.append(obj.id)
                        
                    for obj in self.objects:
                        if obj.id in list_obj:
                            obj.Clicked(mouse_pos)
                    
                    if self.left.Click(mouse_pos):
                        self.Move_Location('left')
                    elif self.right.Click(mouse_pos):
                        self.Move_Location('right')
                    elif self.stop.Click(mouse_pos):
                        self.running = False
                                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    pygame.mouse.set_pos(0, 0)
                
                if event.type == pygame.KEYDOWN:
                    self.KeyPressed.Trigger(event)
                    
            if self.Player.Health.OnDeath():
                self.PlayerDeath.Trigger()
                
            self.screen.fill(self.location.color)
            
            list_obj_id = []
            list_obj = []
            
            for obj in self.location.objects:
                list_obj_id.append(obj.id)
            
            for obj in self.objects:
                if obj.id in list_obj_id:
                    list_obj.append(obj)
                    
            info = pygame.display.Info()
            
            for obj in self.objects:
                if obj.id in list_obj_id:
                    obj.Update(info, self.gravity, list_obj)
                    obj.Draw(self.screen)
                        
            ui_height = (20 / 100) * info.current_h
            self.screen.fill((196, 196, 196), (0, info.current_h - ui_height, info.current_w, ui_height))    
                        
            self.left.Draw(self.screen)
            self.right.Draw(self.screen)
            self.stop.Draw(self.screen)
            self.indicator.Draw(self.screen)
            self.health_bar.Draw(self.screen)
            
            if self.Notification.request:
                self.Notification.Notify(self.screen)
                
            pygame.display.flip()
                      
            self.clock.tick(self.fps)
            
            calc.append(time.time() - Loops)
        
        Average = round(sum(calc) / len(calc), 3)
        
        print('--- Performance Data ---')
        print(f'Loops: {len(calc)}')
        print(f'Runtime: {round(time.time() - start)}s')
        print(f'Average Loop Time: {Average}')
        
        self.PlayerRemoved.Trigger()
        
        pygame.quit() 