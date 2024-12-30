import pygame

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

    def Connect(self, obj):
        self.handles.append(obj)

    def Trigger(self, *args):
        for handle in self.handles:
            handle(*args)

class Text:
    def __init__(self, size, pos, color, text):
        self.size = size
        self.pos = pos
        self.color = color
        self.text = text
        self.font = pygame.font.SysFont("Arial", size)
        self.text_surface = self.render()
        self.rect = self.text_surface.get_rect(topleft=self.pos)

    def render(self):
        return self.font.render(self.text, True, self.color)

    def draw(self, surface):
        self.text_surface = self.render()
        self.rect = self.text_surface.get_rect(topleft=self.pos)
        surface.blit(self.text_surface, self.pos)

    def click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)   

class Object:
    def __init__(self, id ,size, pos, sprite):
        self.id = id
        self.size = size
        self.pos = pos
        self.sprite = pygame.image.load(sprite)
        self.sprite = pygame.transform.scale(self.sprite, size)

        self.visible = True

        self.Interacted = TriggerEvent()

    def Interact(self, *args):
        self.Interacted.Trigger(self, *args)
        return self

    def Clicked(self, mouse):
        x, y = mouse
        obj_x, obj_y = self.pos
        obj_width, obj_height = self.size

        if obj_x <= x <= obj_x + obj_width and obj_y <= y <= obj_y + obj_height:
            self.Interact()
            return True
        return False

    def draw(self, screen):
        screen.blit(self.sprite, self.pos)

class Location:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.objects = []

    def Connect(self, obj):
        self.objects.append(obj)

pygame.init()

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

        self.PlayerAdded = GameEvent()
        self.PlayerRemoved = GameEvent()

        info = pygame.display.Info()
        size = int(15 / 100 * info.current_h)

        self.left = Text(size, (20, info.current_h - size * 1.2), (0, 0, 0), '<')
        self.right = Text(size, (info.current_w - size, info.current_h - size * 1.2), (0, 0, 0), '>')

        self.clock = pygame.time.Clock()
        self.fps = conf.get('fps', 60)

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
            else:
                print('Cannot go Right!')
        else:
            print('Cannot Go Left!')

    def execute(self):
        self.PlayerAdded.Trigger()

        while self.running:          
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

                    if self.left.click(mouse_pos):
                        self.Move_Location('left')
                    elif self.right.click(mouse_pos):
                        self.Move_Location('right')

                elif event.type == pygame.MOUSEBUTTONUP:
                    pygame.mouse.set_pos(0, 0)

            self.screen.fill(self.location.color)

            list_obj = []
            for obj in self.location.objects:
                list_obj.append(obj.id)

            for obj in self.objects:
                if obj.id in list_obj:
                    if obj.visible:
                        obj.draw(self.screen)

            info = pygame.display.Info()
            ui_height = (20 / 100) * info.current_h

            self.screen.fill((196, 196, 196), (0, info.current_h - ui_height, info.current_w, ui_height))                
            self.left.draw(self.screen)
            self.right.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(self.fps)

        self.PlayerRemoved.Trigger()

        pygame.quit()