# This file is where game logic lives. No input
# or output happens here. The logic in this file
# should be unit-testable.

from numpy import random
import pandas

class DB():
    def __init__(self, CSV_file):
        self.CSV_file = CSV_file
        try:
            self.games = pandas.read_csv(CSV_file)
        except FileNotFoundError:
            self.games = pandas.DataFrame(columns = [
                "game ID",
                "player 1",
                "player 2",
                "winner",
            ])

    def record(self, O_player, X_player, winner):
        self.games.loc[len(self.games)] = {
            "game ID": len(self.games),
            "player 1": O_player.get_name(),
            "player 2": X_player.get_name(),
            "winner": winner.get_name(),
        }

        self.games.to_csv(self.CSV_file)

    def show_statistics(self, O_player, X_player):
        O_player_games = self.games.loc[
            (self.games['player 1'] == O_player.get_name()) | (self.games['player 2'] == O_player.get_name())]
        O_player_games_wins = len(O_player_games.loc[(O_player_games['winner'] == O_player.get_name())])
        O_player_games_draws = len(O_player_games.loc[(O_player_games['winner'] == "drawer")])
        O_player_games_loses = len(O_player_games) - O_player_games_wins - O_player_games_draws
        X_player_games = self.games.loc[(self.games['player 1'] == X_player.get_name()) | (self.games['player 2'] == X_player.get_name())]
        X_player_games_wins = len(X_player_games.loc[(X_player_games['winner'] == X_player.get_name())])
        X_player_games_draws = len(X_player_games.loc[(X_player_games['winner'] == "drawer")])
        X_player_games_loses = len(X_player_games) - X_player_games_wins - X_player_games_draws

        print(O_player.get_name() + " played: " + str(len(O_player_games)) + ", won: " + str(O_player_games_wins) + ", drew: " + str(O_player_games_draws) + ", lost: " + str(O_player_games_loses))
        print(X_player.get_name() + " played: " + str(len(X_player_games)) + ", won: " + str(X_player_games_wins) + ", drew: " + str(X_player_games_draws) + ", lost: " + str(X_player_games_loses))

# Base class
class Player():
    def __init__(self, name):
        self.name = name

    def move(self, board):
        pass

    def is_bot(self):
        pass

    def get_name(self):
        return self.name

# Extended class for human player
class HumanPlayer(Player):
    def move(self, board):
        # Specifies the row and column index of the cell to move in
        row = int(input()) - 1;
        col = int(input()) - 1;
        # Check if it's a valid move
        while 0 > row or 2 < row or 0 > col or 2 < col or None != board[row][col]:
            print ("Invalid move!")
            row = int(input()) - 1;
            col = int(input()) - 1;

        # Update the game board
        board[row][col] = self

    def is_bot(self):
        return False

# Extended class for bot player
class BotPlayer(Player):
    # Bot is a dummy player, it never try to win, but just follow the basic rule
    def move(self, board):
        while True:
            # Find a random cell to move in
            rnd = random.randint(8)
            row = int(rnd / 3)
            col = int(rnd % 3)
            # Check validity
            if None == board[row][col]:
                break

        board[row][col] = self

    def is_bot(self):
        return True

class Game:
    def __init__(self, O_player, X_player):
        self.db = DB('db.csv')

        self.board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]

        """Member "drawer" just used to indicate the situation that the game draws. In such case, "get_winner()" method will return "drawer" """
        self.drawer = Player("drawer")
        self.O_player = O_player
        self.X_player = X_player
        self.current_player = O_player

    def show_board(self):
        for row in self.board:
            for player in row:
                if self.O_player == player:
                    print('O', end = '')
                elif self.X_player == player:
                    print('X', end = '')
                else:
                    # It's an empty cell
                    print('_', end = '')
            print()

    def check_line(self, first, second, third):
        if None == first:
            if None == second or None == third or second == third:
                return None
            return self.drawer

        if first == second and first == third:
            return first

        if first != second and None != second or first != third and None != third:
            return self.drawer
        return None

    def get_winner(self):
        result = self.drawer

        # Check 3 "horizonal" lines
        for row in self.board:
            line_result = self.check_line(row[0], row[1], row[2])
            # if a winner found
            if self.O_player == line_result or self.X_player == line_result:
                return line_result
            # if no winner till now but the game will go on
            if None == line_result:
                result = None

        # Check 3 "vertical" lines
        col = 0
        while col < 3:
            line_result = self.check_line(self.board[0][col], self.board[1][col], self.board[2][col])
            if self.O_player == line_result or self.X_player == line_result:
                return line_result
            if None == line_result:
                result = None
            col += 1

        # Check 2 "diagonal" lines
        line_result = self.check_line(self.board[0][0], self.board[1][1], self.board[2][2])
        if self.O_player == line_result or self.X_player == line_result:
            return line_result
        if None == line_result:
            result = None

        line_result = self.check_line(self.board[0][2], self.board[1][1], self.board[2][0])
        if self.O_player == line_result or self.X_player == line_result:
            return line_result
        if None == line_result:
            result = None

        return result

    def run(self):
        winner = None
        while winner == None:
            # If it's a human player, the show the game board and a prompt
            if not self.current_player.is_bot():
                self.show_board()
                print(self.current_player.get_name() + " to move:")
            self.current_player.move(self.board)
            # Switch turn
            if self.current_player == self.O_player:
                self.current_player = self.X_player
            else:
                self.current_player = self.O_player
            # Get winner
            winner = self.get_winner()

        # Game over. Show the final game board and the winner or 'draw'
        self.show_board()
        if self.drawer == winner:
            print("It draws.")
        else:
            print(winner.get_name() + " won!")

        self.db.record(self.O_player, self.X_player, winner)
        self.db.show_statistics(self.O_player, self.X_player)

if __name__ == '__main__':
    print("Your name?")
    name = input()
    print("Play with a bot?")
    answer = input()
    if 'y' == answer or 'Y' == answer:
        # Play with bot
        print("Play first?")
        answer = input()
        if 'y' == answer or 'Y' == answer:
            # U play first
            game = Game(HumanPlayer(name), BotPlayer('Bot'))
        else:
            # Bot plays first
            game = Game(BotPlayer('Bot'), HumanPlayer(name))
    else:
        # It's a human x human game
        print("Another player's name?")
        another = input()
        game = Game(HumanPlayer(name), HumanPlayer(another))

    # Game starts!
    game.run()
