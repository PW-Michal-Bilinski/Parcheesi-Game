"""
Module for Board class
"""
from typing import Any

from src.entities.field import Field
from src.entities.pawn import Pawn
from src.entities.player import Player
CELL_NUM = 40


class NoAvailablePlayerMoveException(Exception):
    """
    Exception class for end of the game
    """


class Board:
    """Main Class representing Parcheesi board"""

    def __init__(self, players):
        """
        :param players: Dict containing {player: starting_point}
        """
        self.player_number = len(players)
        self.fields = [Field() for _ in range(CELL_NUM)]
        self.players = players

    def make_move_on_board(self, position, new_position, pawn, active_player) -> None:
        """
        Moves pawn on board
        :param position: Starting pawn position
        :param new_position: Position where pawn will be moved
        :param pawn: Pawn to move
        :param active_player: player which round it is
        """
        other_pawns = self.fields[new_position].move_pawn(pawn)
        active_player.move_pawn_loc(position, new_position)
        self.fix_pawns_in_hand(other_pawns, new_position)

    def update(self, dice_result: int, round_num: int) -> None:
        """
        Make one player move
        :param dice_result: Number thrown by the dice
        :param round_num: Number of the round
        """
        if (active_player := self.player_round(round_num)) is None:
            raise NoAvailablePlayerMoveException("Game finished")
        self.move_pawn(active_player, dice_result)

    # TODO: Refactor this to new class
    def move_pawn(self, active_player: Player, to_move: int, following_pawn: int = 1) -> int:
        """
        Moves pawn in the Field
        :param following_pawn: number of further pawn to take
        :param active_player: player which is the move
        :param to_move: number of points from dice
        """
        position = active_player.get_selected_furthest_pawn(following_pawn)
        if position == -2:
            return -2
        if position == -1:
            if to_move in [1, 6] and active_player.pick_pawn_from_hand():
                self.add_pawn_to_board(active_player)
            return -1

        if not active_player.try_move_in_house(to_move):
            pawn = self.fields[position].take_pawn(active_player.color)
            new_position = (position + to_move) % 40
            if (position < active_player.starting_point <= new_position
                    or position > new_position >= active_player.starting_point):
                in_house_position = new_position - active_player.starting_point
                next_pawn = following_pawn + 1
                if in_house_position < 4 and active_player.house[in_house_position] == 0:
                    active_player.move_to_house(in_house_position, position)
                elif active_player.get_selected_furthest_pawn(next_pawn):
                    self.fields[position].move_pawn(pawn)
                    if self.move_pawn(active_player, to_move, next_pawn) == -2:
                        active_player.pawns_position.append(position)
            else:
                self.make_move_on_board(position, new_position, pawn, active_player)
        return None

    def fix_pawns_in_hand(self, pawns: list, position: int) -> None:
        """
        Adds beaten pawns to players hand:
        :param pawns: list of beaten pawns
        :param position: nr o field fixing
        """
        for pawn in pawns:
            for player in self.players:
                if player.color == pawn.color:
                    player.return_pawn(position)

    def __repr__(self) -> str:
        """
        :return: fields of board representation
        """
        result_str = ""
        for i, j in enumerate(self.fields):
            result_str += f"Field nr. {i}: {j}\n"
        for player in self.players:
            result_str += repr(player)
        return result_str

    def player_round(self, round_num: int) -> Any | None:
        """
        Return player which round is it
        :param round_num: player round number
        :return: player
        """
        for i in range(len(self.players)):
            player_round = (round_num + i) % 4
            if self.players[player_round].pawns_position:
                return self.players[player_round]
        return None

    def add_pawn_to_board(self, player: Player) -> None:
        """
        Adds player pawn to board
        :param player:
        """
        pawn = Pawn(color=player.color)
        other_pawns = self.fields[player.starting_point].move_pawn(pawn)
        self.fix_pawns_in_hand(other_pawns, player.starting_point)
