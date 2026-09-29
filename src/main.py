import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move
from menu import Menu
from ai import find_best_move, game_status

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('AI Chess')
        self.game = Game()
        self.menu = Menu()
        self.banner_font = pygame.font.SysFont('arial', 32, bold=True)
        self.small_font = pygame.font.SysFont('arial', 20)

        self.state = 'menu'       # 'menu' or 'playing'
        self.mode = 'pvai'        # 'pvp', 'pvai', or 'aivai'
        self.ai_color = 'black'
        self.depth = 2
        self.game_over = False
        self.status = ''

    # helpers

    def start_game(self):
        self.mode = self.menu.mode
        self.ai_color = self.menu.ai_color
        self.depth = self.menu.depth
        self.game.reset()
        self.game_over = False
        self.status = ''
        self.state = 'playing'
        self.update_caption()

    def update_caption(self):
        if self.mode == 'pvp':
            text = 'AI Chess | Player vs Player'
        elif self.mode == 'aivai':
            text = f'AI Chess | AI vs AI | depth {self.depth}'
        else:
            you = 'white' if self.ai_color == 'black' else 'black'
            text = f'AI Chess | You play {you} | depth {self.depth}'
        pygame.display.set_caption(text)

    def is_ai_turn(self):
        if self.mode == 'aivai':
            return True
        if self.mode == 'pvai':
            return self.game.next_player == self.ai_color
        return False

    def draw(self):
        self.game.show_bg(self.screen)
        self.game.show_last_move(self.screen)
        self.game.show_moves(self.screen)
        self.game.show_pieces(self.screen)
        self.game.show_hover(self.screen)
        if self.game_over:
            self.draw_banner()

    def draw_banner(self):
        overlay = pygame.Surface((WIDTH, 130), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, HEIGHT // 2 - 65))

        text = self.banner_font.render(self.status, True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 18)))

        hint = self.small_font.render('R = play again    Esc = menu', True, (200, 200, 200))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 28)))

    def check_game_over(self):
        status = game_status(self.game.board, self.game.next_player)
        if status == 'checkmate':
            winner = 'White' if self.game.next_player == 'black' else 'Black'
            self.game_over = True
            self.status = f'Checkmate - {winner} wins'
        elif status == 'stalemate':
            self.game_over = True
            self.status = 'Stalemate - Draw'

    def ai_move(self):
        game = self.game
        board = game.board

        piece, move = find_best_move(board, game.next_player, self.depth)

        # recalculate this piece's real moves (sets up the rook for castling)
        row, col = move.initial.row, move.initial.col
        piece.clear_moves()
        board.calc_moves(piece, row, col, bool=True)

        # same steps a human move runs
        captured = board.squares[move.final.row][move.final.col].has_piece()
        board.move(piece, move)
        board.set_true_en_passant(piece)
        game.play_sound(captured)
        game.next_turn()
        self.check_game_over()

    # main loop

    def mainloop(self):
        screen = self.screen

        while True:
            game = self.game
            board = self.game.board
            dragger = self.game.dragger

            # menu screen 
            if self.state == 'menu':
                self.menu.draw(screen, pygame.mouse.get_pos())

                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.menu.handle_click(event.pos):
                            self.start_game()
                    elif event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                pygame.display.update()
                continue

            # ----- game screen -----
            self.draw()

            if dragger.dragging:
                dragger.update_blit(screen)

            # AI turn
            if self.is_ai_turn() and not self.game_over and not dragger.dragging:
                pygame.display.update()   # show the last move before the AI thinks
                self.ai_move()
                self.draw()

            for event in pygame.event.get():

                # click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over or self.is_ai_turn():
                        continue

                    dragger.update_mouse(event.pos)

                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE

                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        if piece.color == game.next_player:
                            piece.clear_moves()   # avoid stale moves piling up
                            board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)
                            self.draw()

                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE

                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        self.draw()
                        dragger.update_blit(screen)

                # click release
                elif event.type == pygame.MOUSEBUTTONUP:

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        if board.valid_move(dragger.piece, move):
                            captured = board.squares[released_row][released_col].has_piece()
                            board.move(dragger.piece, move)
                            board.set_true_en_passant(dragger.piece)
                            game.play_sound(captured)
                            self.draw()
                            game.next_turn()
                            self.check_game_over()

                    dragger.undrag_piece()

                # key press
                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_t:
                        game.change_theme()

                    if event.key == pygame.K_r:
                        self.start_game()   # same settings, fresh board

                    if event.key == pygame.K_ESCAPE:
                        dragger.undrag_piece()
                        self.state = 'menu'
                        pygame.display.set_caption('AI Chess')

                # quit
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()


if __name__ == '__main__':
    main = Main()
    main.mainloop()