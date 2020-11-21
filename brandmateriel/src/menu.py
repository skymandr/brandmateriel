import json
import pygame
import pygame.locals as l


KEYBOARD = {l.K_UP: 'up', l.K_k: 'up', l.K_w: 'up',
            l.K_DOWN: 'down', l.K_j: 'down', l.K_s: 'down',
            l.K_LEFT: 'left', l.K_h: 'left', l.K_a: 'left',
            l.K_RIGHT: 'right', l.K_l: 'right', l.K_d: 'right',
            l.K_RETURN: 'start', l.K_SPACE: 'start',
            l.K_ESCAPE: 'quit', l.K_F1: 'help', l.K_TAB: 'pause'}


class Menu(object):
    """
    A simple menu class, configured using JSON.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, _structure='menu.conf', options='user.conf',
                 default='default.conf', mixer=None):
        self._item = 0
        self.menu = "main menu"

        with open(_structure, 'r') as f:
            self._structure = json.load(f)

        self._default = default
        self._config = options

        self._load_options(options)

        if mixer is not None:
            try:
                self._menu_sound = mixer.Sound(self.setup.get("sound"))
            except (pygame.error, IOError):
                self._menu_sound = None
        else:
            self._menu_sound = None

        pygame.mouse.set_visible(False)

    @property
    def setup(self):
        return self._structure["setup"]

    @property
    def config(self):
        return self.options

    @property
    def items(self):
        return self._structure[self.menu]['items']

    @property
    def text(self):
        return self._structure[self.menu]['text']

    @property
    def _items(self):
        return len(self.items)

    @property
    def item(self):
        return self._structure[self.menu]["items"][self._item]

    @property
    def resolution(self):
        return tuple(self.options["resolution"])

    def _load_options(self, filename):
        try:
            with open(filename, 'r') as f:
                self.options = json.load(f)
        except IOError:
            print "Loading default settings..."
            with open(self._default, 'r') as f:
                self.options = json.load(f)

        self._set_options()

    def _set_options(self):

        for o in self.options.keys():

            for n, item in enumerate(self._structure["options"]["items"]):

                if item[0] == o:

                    break

            if self._structure["options"]["items"][n][1][0] in ("toggle",
                                                                "lander"):

                self._structure["options"]["items"][n][1][1] = int(
                    self.options[o])

            elif self._structure["options"]["items"][n][1][0] == "list":

                for m, l in enumerate(self._structure["options"
                                                      ]["items"][n][1][2]):
                    if l == self.options[o]:

                        self._structure["options"]["items"][n][1][1] = m

    def _save_settings(self):

        for o in self.options.keys():

            for n, item in enumerate(self._structure["options"]["items"]):

                if item[0] == o:

                    break

            if self._structure["options"]["items"][n][1][0] in ("toggle",
                                                                "lander"):

                self.options[o] = (1 == self._structure["options"
                                                        ]["items"][n][1][1])

            elif self._structure["options"]["items"][n][1][0] == "list":

                self.options[o] = self._structure["options"]["items"][n][1][2][
                    self._structure["options"]["items"][n][1][1]]

            else:
                print o

        with open(self._config, 'w') as f:
            json.dump(self.options, f)

    def close(self):
        """ Close menu. """

        self._save_settings()

        return "quit"

    def menu_navigation(self):
        """ Handles inputs from user. """
        flag = "menu"

        for event in pygame.event.get():

            if event.type == l.QUIT:

                flag = self.close()

            elif event.type == l.KEYDOWN and event.key in KEYBOARD.keys():

                if KEYBOARD[event.key] == 'quit':

                    self.menu = "main menu"
                    self._item = 0

                elif KEYBOARD[event.key] == 'up':

                    self._item = (self._item - 1) % self._items

                elif KEYBOARD[event.key] == 'down':

                    self._item = (self._item + 1) % self._items

                elif KEYBOARD[event.key] == 'help':

                    flag = "help"
                    self._item = 0

                elif KEYBOARD[event.key] == 'pause':

                    pygame.mouse.set_visible(True)

                else:
                    self.play_sound()
                    flag = self._relay_input(event.key)

            elif event.type == l.MOUSEBUTTONDOWN:

                pygame.mouse.set_visible(False)

        return flag

    def _relay_input(self, event_key):

        if KEYBOARD[event_key] == 'start':

            if self.item[1][0] == 'start':

                return "game"

            elif self.item[1][0] == 'quit':

                return "quit"

            elif self.item[1][0] == 'hiscore':

                return "hiscore"

            elif self.item[1][0] == 'gallery':

                return "gallery"

            elif self.item[1][0] == 'credits':

                return "credits"

            elif self.item[1][0] == 'menu':

                self.menu = self.item[1][1]
                self._item = 0

            elif self.item[1][0] == "toggle":

                self.item[1][1] = (self.item[1][1] + 1) % 2

            elif self.item[1][0] == "list":

                self.item[1][1] = ((self.item[1][1] + 1) %
                                   len(self.item[1][2]))

            elif self.item[1][0] == "default":

                self._load_options(self._default)

        elif KEYBOARD[event_key] == 'left':

            if self.item[1][0] in ("toggle", "lander"):

                self.item[1][1] = (self.item[1][1] - 1) % 2

            elif self.item[1][0] == "list":

                self.item[1][1] = ((self.item[1][1] - 1) %
                                   len(self.item[1][2]))

        elif KEYBOARD[event_key] == 'right':

            if self.item[1][0] == "toggle":

                self.item[1][1] = (self.item[1][1] + 1) % 2

            elif self.item[1][0] == "list":

                self.item[1][1] = ((self.item[1][1] + 1) %
                                   len(self.item[1][2]))

        self._save_settings()

        return "menu"

    def play_sound(self):
        if self._menu_sound:
            self._menu_sound.play()

def draw_menu(menu, surface):
    centre = menu.setup["centre"]
    resolution = menu.options["resolution"]
    fontsize = menu.setup["fontsize"] * resolution[0] / 320
    font = pygame.font.Font(menu.setup["font"], fontsize)

    surface.fill((0, 0, 0))

    for n, i in enumerate(menu.text):

        colour = menu.setup["colour"]

        text = font.render("  {0}  ".format(i[0]), True, colour)

        if centre:

            textpos = text.get_rect(center=(resolution[0] / 2,
                                            (2 + n) * (fontsize + 1)))

        else:

            textpos = text.get_rect(centery=(2 + n) * (fontsize + 1))

        surface.blit(text, textpos)

    for n, i in enumerate(menu.items):

        if i == menu.item:

            colour = menu.setup["selected"]

        else:

            colour = menu.setup["colour"]

        if i[1][0] == "toggle":

            text = font.render("  {0}: {1}  ".format(i[0], i[1][2][i[1][1]]),
                               True, colour)

        if i[1][0] == "list":

            text = font.render("  {0}: {1}  ".format(i[0], i[1][3][i[1][1]]),
                               True, colour)

        else:

            text = font.render("  {0}  ".format(i[0]), True, colour)

        if centre:

            textpos = text.get_rect(center=(resolution[0] / 2, resolution[1] -
                                            (1 + fontsize) *
                                            (len(menu.items) - n + 1)))

        else:

            textpos = text.get_rect(centery=resolution[1] -
                                    (1 + fontsize) * (len(menu.items) - n + 1))

        surface.blit(text, textpos)
