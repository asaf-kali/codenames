from codenames.duet.state import DuetGameState, DuetPlayerState, DuetSide
from tests.utils.moves import ClueMove, Move, get_moves


def get_duet_moves(state: DuetGameState) -> list[Move]:
    moves_a = get_side_moves(state=state.side_a)
    moves_b = get_side_moves(state=state.side_b)
    moves = []
    current_side = DuetSide.SIDE_A
    while moves_a and moves_b:
        current_moves = moves_a if current_side == DuetSide.SIDE_A else moves_b
        turn_moves = _extract_turn_moves(moves=current_moves)
        moves.extend(turn_moves)
        current_side = current_side.other
    assert not moves_a or not moves_b
    if moves_a:
        moves.extend(moves_a)
    if moves_b:
        moves.extend(moves_b)
    return moves


def _extract_turn_moves(moves: list[Move]) -> list[Move]:
    if not moves:
        return moves
    first_move = moves.pop(0)
    assert isinstance(first_move, ClueMove)
    turn_moves: list[Move] = [first_move]
    while moves:
        if isinstance(moves[0], ClueMove):
            return turn_moves
        guess_move = moves.pop(0)
        turn_moves.append(guess_move)
    return turn_moves


def get_side_moves(state: DuetPlayerState) -> list[Move]:
    return get_moves(
        given_clues=state.given_clues,
        given_guesses=state.given_guesses,
        current_turn=state.current_player_role,
    )
