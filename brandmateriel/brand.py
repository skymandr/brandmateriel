#! /usr/bin/env python
import sys
import pygame
import pygame.locals as l
import src.menu as m
import src.game as g


KEYBOARD = {l.K_UP: 'up', l.K_k: 'up', l.K_w: 'up',
            l.K_DOWN: 'down', l.K_j: 'down', l.K_s: 'down',
            l.K_LEFT: 'left', l.K_h: 'left', l.K_a: 'left',
            l.K_RIGHT: 'right', l.K_l: 'right', l.K_d: 'right',
            l.K_RETURN: 'start', l.K_SPACE: 'start',
            l.K_ESCAPE: 'quit', l.K_F1: 'help'}

if not pygame.font:
    print "Warning: no fonts detected; fonts disabled."

if not pygame.mixer:
    print "Warning: no sound detected; sound disabled."


def main():
    pygame.init()
    fps_clock = pygame.time.Clock()
    fps = 23.8
    window = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF)

    mode = "menu"
    menu = m.Menu('config/menu.conf', 'config/user.conf',
                  'config/default.conf')

    while(mode):

        while(mode == "menu"):

            if menu.resolution != window.get_size():

                window = pygame.display.set_mode(menu.resolution,
                                                 pygame.DOUBLEBUF)

            m.draw_menu(menu, window)
            pygame.display.flip()
            fps_clock.tick(fps)

            mode = menu.menu_navigation()

        if mode == "game":
            try:
                print "loading map: {0}".format(menu.config["map"])
                game = g.Game(menu.config, 'assets/maps/{0}.npy'.format(
                    menu.config["map"]), menu.setup["font"],
                    menu.setup["fontsize"], fps)
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
                pygame.mouse.get_rel()
            except IOError:
                print "no such map: {0}; using Legacy".format(
                    menu.config["map"])
                game = g.Game(menu.config, 'assets/maps/legacy.npy',
                              menu.setup["font"], menu.setup["fontsize"], fps)
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
                pygame.mouse.get_rel()

        while(mode == "game"):
            mode = game.do_step(window)
            pygame.display.flip()
            fps_clock.tick(fps)

        while(mode == "hiscore"):
            print "high-score list is not implemented. returning to menu ..."
            mode = "menu"

        while(mode == "gallery"):
            print "gallery is not implemented. returning to menu ..."
            mode = "menu"

        while(mode == "credits"):
            print "game is not implemented. returning to menu ..."
            mode = "menu"

        while(mode == "quit"):
            print "quitting game ..."
            pygame.quit()
            mode = False

if __name__ == "__main__":
    sys.exit(main())
