from turtle import back
import pygame as pg
from pygame.locals import *
import sys
import time

import colors
from constants import *

from scipy.misc import central_diff_weights

board = [[None]*3 for _ in range(3)]
current_player = 1 # player 1 takes first turn, player 2 takes second turn
turn_number = 0

pg.init()
fps = 30
cl = pg.time.Clock()
screen = pg.display.set_mode((game_window_width, game_window_length), 0, 32)
pg.display.set_caption("Board Game Master")

x_img = pg.image.load('X.png')
o_img = pg.image.load('O.png')

x_img = pg.transform.scale(x_img, (100,100))
o_img = pg.transform.scale(o_img, (100,100))

scene = "menu"

def draw_menu():
    global start_button_rect
    screen.fill((255,255,255)) # white
    font = pg.font.Font(None, 80)
    font.set_italic(True)
    font.set_bold(True)
    text = font.render("Board Game Master", 1, colors.DARK_PURPLE)
    # put the title at the center of the screen
    text_rect = text.get_rect(center=(game_window_width/2, 200))
    screen.blit(text, text_rect)

    # draw start button
    font = pg.font.Font(None, 56)
    start_button = font.render("Start Game", 1, colors.BLACK)
    start_button_rect = start_button.get_rect(center=(game_window_width / 2, 400))
    screen.blit(start_button, start_button_rect)
    pg.display.update()

def draw_game():
    global board_rect, pause_button_rect, restart_button_rect, back_button_rect
    # clear the screen by filling it with white
    screen.fill(colors.WHITE)
    # fill the board with a background colour
    screen.fill((222,184,135), (0, 0, 600, 600))

    # draw the lines using two for loops
    # horizontal
    for i in range(4):
        pg.draw.line(screen, colors.BLACK, (0, 200 * i), (board_size, 200 * i), board_line_width)
    
    # vertical
    for i in range(4):
        pg.draw.line(screen, colors.BLACK, (200 * i, 0), (200 * i, board_size), board_line_width)

    # draw the background of the board
    # pg.Rect(left, top, width, height)
    board_rect = pg.Rect(0, 0, board_size, board_size)

    # write the instructions text
    instructions_font = pg.font.Font(None, 32)
    instructions = instructions_font.render('Player ' + str(current_player) + '\'s turn', 1, (0, 0, 0))
    instructions_rect = instructions.get_rect(center=(game_scene_button_center_x, 50))
    screen.blit(instructions, instructions_rect)

    button_font = pg.font.Font(None, 56)
    # write the menu buttons
    ## can i use constants to make this more legible?
    ## can i use a loop to make this better?
    ## how can i adjust the buttons so that they do not cover the board?
    pause_text = button_font.render('PAUSE', 1, (0, 0, 0))
    back_text = button_font.render('BACK', 1, (0, 0, 0))
    restart_text = button_font.render('RESTART', 1, (0, 0, 0))
    ## get the center position for the menu text
    pause_rect = pause_text.get_rect(center=(game_scene_button_center_x, 150))
    back_rect = back_text.get_rect(center=(game_scene_button_center_x, 250))
    restart_rect = restart_text.get_rect(center=(game_scene_button_center_x, 350))
    ## create the button rectangles at the specified position
    pause_button_rect = pg.Rect(board_size + 4, 100, 300, 100)
    back_button_rect = pg.Rect(board_size + 4, 200, 300, 100)
    restart_button_rect = pg.Rect(board_size + 4, 300, 300, 100)
    ## draw the rectangles on the 
    pg.draw.rect(screen, (250, 0, 0), pause_button_rect)
    pg.draw.rect(screen, (122, 122, 122), back_button_rect)
    pg.draw.rect(screen, (160, 184, 135), restart_button_rect)
    screen.blit(pause_text, pause_rect)
    screen.blit(back_text, back_rect)
    screen.blit(restart_text, restart_rect)

    pg.display.update()

def draw_pause():
    global pause_message_dialog
    message_width = 500
    message_height = 150
    pause_message_dialog = pg.Rect((game_window_width - message_width) / 2, (game_window_length - message_height) / 2, message_width, message_height)
    pg.draw.rect(screen, colors.BLUE, pause_message_dialog)

    pause_font = pg.font.Font(None, 50)
    pause_message = pause_font.render("Game Paused", 1, colors.WHITE)
    pause_message_rect = pause_message.get_rect(center=(game_window_width / 2, game_window_length / 2))
    screen.blit(pause_message, pause_message_rect)

    pg.display.update()

def draw_result(result):
    global result_dialog, scene
    scene = 'result'
    message_width = 500
    message_height = 150
    result_dialog = pg.Rect((game_window_width - message_width) / 2, (game_window_length - message_height) / 2, message_width, message_height)
    pg.draw.rect(screen, colors.CYAN, result_dialog)

    font = pg.font.Font(None, 50)
    result_message = font.render(result, 1, colors.BLACK)
    result_message_rect = result_message.get_rect(center=(game_window_width / 2, game_window_length / 2))
    screen.blit(result_message, result_message_rect)

    pg.display.update()

def draw_step(mouse_pos):
    global current_player, board, turn_number
    mouse_x, mouse_y = mouse_pos
    if mouse_x < board_square_size:
        column = 0
    elif mouse_x < 2 * board_square_size:
        column = 1
    else:
        column = 2
    
    if mouse_y < board_square_size:
        row = 0
    elif mouse_y < 2 * board_square_size:
        row = 1
    else:
        row = 2
    # the above if statements can be replaced by the 2 following lines:
    # index_x = mouse_x // board_square_size
    # index_y = mouse_y // board_square_size

    # check if we have drawn already at this square
    if board[row][column] is not None:
        # there is a value => do not update
        return
    
    # update the state of the game
    board[row][column] = current_player
    print(board)

    # offset by 50 px so that the center of the image is placed in the center of the square
    draw_x = column * board_square_size + board_square_size / 4
    draw_y = row * board_square_size + board_square_size / 4
    # print('index', (index_x, index_y), '; drawing at', (draw_x + board_square_size / 4, draw_y + board_square_size / 4))
    if current_player == 1:
        screen.blit(x_img, (draw_x, draw_y))
    else:
        screen.blit(o_img, (draw_x, draw_y))
    
    win_text = check_win()
    print('win text', win_text)
    if win_text:
        draw_result(win_text)
    else:
        update_instruction()
        # turn_number += 1
        # if turn_number >= 9:
        #     draw_result('It\'s a draw')
        # else:
        #     update_instruction()

def draw_previous_steps():
    for row in range(3):
        # row = 0, 1, or 2
        for col in range(3):
            # y-index
            # drawing indices for top left corner of image
            draw_x = col * board_square_size + board_square_size / 4
            draw_y = row * board_square_size + board_square_size / 4
            if board[row][col] == 1:
                # draw X
                screen.blit(x_img, (draw_x, draw_y))
            elif board[row][col] == 2:
                # draw O
                screen.blit(o_img, (draw_x, draw_y))


def reset():
    global board, current_player, turn_number
    current_player = 1
    board = [[None]*3 for _ in range(3)]
    turn_number = 0

# returns an empty string if no one has won
def check_win():
    has_empty_square = False
    # horizontal wins
    for row in board:
        print('checking row', row)
        if row[0] is None:
            has_empty_square = True
            continue
        if row[0] == row[1] == row[2]:
            return 'Player ' + str(row[0]) + ' wins!'
        elif row[1] is None or row[2] is None:
            has_empty_square = True

    # vertical wins
    for col in range(3):
        if board[0][col] is None:
            continue
        if board[0][col] == board[1][col] == board[2][col]:
            return 'Player ' + str(board[0][col]) + ' wins!'

    # diagonal wins
    if board[1][1] is not None and board[0][0] == board[1][1] == board[2][2]:
        return 'Player ' + str(board[1][1]) + ' wins!'
    if board[1][1] is not None and board[0][2] == board[1][1] == board[2][0]:
        return 'Player ' + str(board[1][1]) + ' wins!'
    
    if has_empty_square:
        return ''
    else:
        return 'It\'s a draw!'

def update_instruction():
    global current_player
    if current_player == 1:
        current_player = 2
    else:
        current_player = 1

    # update the instructions text
    # issue: we need to clear the previous instructions first! -- use screen.fill((r, g, b), (x, y, width, length))
    screen.fill(colors.WHITE, (board_size + board_line_width, 0, 300, 100))
    instructions_font = pg.font.Font(None, 32)
    instructions = instructions_font.render('Player ' + str(current_player) + '\'s turn', 1, colors.BLACK)
    instructions_rect = instructions.get_rect(center=(game_scene_button_center_x, 50))
    screen.blit(instructions, instructions_rect)


draw_menu()
pg.event.clear()
# run the game loop forever
while True:
    if scene == "menu":
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                print('mouse button clicked', event)
                print('mouse is at', pg.mouse.get_pos())
                if start_button_rect.collidepoint(event.pos):
                    print('start clicked')
                    scene = 'game'
                    draw_game()
    if scene == 'game':
        for event in pg.event.get():
            if event.type == QUIT:
                print('quitting from game')
                pg.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                print('mouse clicked on game screen', event, event.pos)
                if board_rect.collidepoint(event.pos):
                    draw_step(event.pos)
                elif pause_button_rect.collidepoint(event.pos):
                    scene = 'pause'
                    draw_pause()
                elif restart_button_rect.collidepoint(event.pos):
                    reset()
                    draw_game()
                elif back_button_rect.collidepoint(event.pos):
                    print('back button clicked')
                    scene = 'menu'
                    draw_menu()
    if scene == 'pause':
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            # if mouse collides with game pause message, unpause
            if event.type == MOUSEBUTTONDOWN:
                if pause_message_dialog.collidepoint(event.pos):
                    print('unpaused')
                    # unpause
                    scene = 'game'
                    draw_game()
                    # redraw previous moves
                    draw_previous_steps()
    if scene == 'result':
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            # if mouse collides with game result message, reset
            if event.type == MOUSEBUTTONDOWN:
                if result_dialog.collidepoint(event.pos):
                    print('new game')
                    scene = 'game'
                    reset()
                    draw_game()
                    
            
    pg.display.update()
    cl.tick(fps)
