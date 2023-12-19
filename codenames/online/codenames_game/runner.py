from __future__ import annotations

import logging
from threading import Semaphore, Thread
from typing import Iterable, List, Optional, Tuple, TypeVar

from selenium.common.exceptions import WebDriverException

from codenames.game.board import Board
from codenames.game.move import Guess, Hint
from codenames.game.player import Guesser, Hinter, Player, PlayerRole
from codenames.game.runner import GameRunner
from codenames.game.winner import Winner
from codenames.online.codenames_game.adapter import (
    CodenamesGameLanguage,
    CodenamesGamePlayerAdapter,
    GameConfigs,
    IllegalOperation,
)
from codenames.online.codenames_game.agent import Agent, GuesserAgent, HinterAgent

log = logging.getLogger(__name__)

T = TypeVar("T")


def player_or_agent(player: T, role: PlayerRole) -> T:
    if player is not None:
        return player
    player_class = HinterAgent if role == PlayerRole.HINTER else GuesserAgent
    return player_class("Agent")


class CodenamesGameRunner:
    def __init__(
        self,
        blue_hinter: Optional[Hinter] = None,
        red_hinter: Optional[Hinter] = None,
        blue_guesser: Optional[Guesser] = None,
        red_guesser: Optional[Guesser] = None,
        show_host: bool = True,
        language: CodenamesGameLanguage = CodenamesGameLanguage.ENGLISH,
    ):
        self.host: Optional[CodenamesGamePlayerAdapter] = None
        self.guests: List[CodenamesGamePlayerAdapter] = []
        blue_hinter = player_or_agent(blue_hinter, PlayerRole.HINTER)
        red_hinter = player_or_agent(red_hinter, PlayerRole.HINTER)
        blue_guesser = player_or_agent(blue_guesser, PlayerRole.GUESSER)
        red_guesser = player_or_agent(red_guesser, PlayerRole.GUESSER)
        self.game_runner = GameRunner(
            blue_hinter=blue_hinter,  # type: ignore
            red_hinter=red_hinter,  # type: ignore
            blue_guesser=blue_guesser,  # type: ignore
            red_guesser=red_guesser,  # type: ignore
        )
        self._show_host = show_host
        self._language = language
        self._running_game_url: Optional[str] = None
        self._auto_start_semaphore = Semaphore()
        self.game_runner.hint_given_subscribers.append(self._handle_hint_given)
        self.game_runner.guess_given_subscribers.append(self._handle_guess_given)

    @property
    def adapters(self) -> Iterable[CodenamesGamePlayerAdapter]:
        yield self.host  # type: ignore
        yield from self.guests

    @property
    def winner(self) -> Optional[Winner]:
        return self.game_runner.winner

    @property
    def board(self) -> Board:
        return self.game_runner.state.board

    @property
    def players(self) -> Tuple[Player, ...]:
        return self.game_runner.players

    @property
    def agents(self) -> Tuple[Agent, ...]:
        return tuple(player for player in self.players if isinstance(player, Agent))

    def _get_adapter_for_player(self, player: Player) -> CodenamesGamePlayerAdapter:
        for adapter in self.adapters:
            if adapter.player == player:
                return adapter
        raise ValueError(f"Player {player} not found in this game manager.")

    def has_joined_game(self, player: Player) -> bool:
        return any(adapter.player == player for adapter in self.adapters)

    def auto_start(self, game_configs: Optional[GameConfigs] = None) -> "CodenamesGameRunner":
        number_of_guests = 3
        self._auto_start_semaphore = Semaphore(value=number_of_guests)
        for player in self.players:
            if not self.host:
                self.host_game(host_player=player, game_configs=game_configs)  # type: ignore
            else:
                self._auto_start_semaphore.acquire()  # pylint: disable=consider-using-with
                log.debug("Semaphore acquired.")
                self.add_to_game(guest_player=player, multithreaded=True)
        if not self._running_game_url:
            log.warning("Game not running after auto start.")
            return self
        for i in range(number_of_guests):
            self._auto_start_semaphore.acquire()  # pylint: disable=consider-using-with
            log.debug(f"Thread {i} done.")
        log.info(f"All {number_of_guests} joined, starting.")
        self.run_game()
        return self

    def host_game(
        self,
        host_player: Optional[Hinter] = None,
        game_configs: Optional[GameConfigs] = None,
    ) -> "CodenamesGameRunner":
        if self.host:
            raise IllegalOperation("A game is already running.")
        if host_player is None:
            host_player = self.game_runner.blue_hinter
        if not isinstance(host_player, Hinter):
            raise IllegalOperation("Host player must be a Hinter.")
        host = CodenamesGamePlayerAdapter(player=host_player, headless=not self._show_host)
        host.open().host_game(game_configs=game_configs)
        self._running_game_url = host.get_game_url()
        log.info(f"Game URL: {self._running_game_url}")
        self.host = host
        host.choose_role()
        return self

    def add_to_game(self, guest_player: Player, multithreaded: bool = False) -> CodenamesGameRunner:
        if not self._running_game_url:
            raise IllegalOperation("Can't join game before hosting initiated. Call host_game() first.")
        if self.has_joined_game(guest_player):
            log.warning(f"Player {guest_player} already joined.")
            return self
        if isinstance(guest_player, Agent):
            log.debug("Not adding agent to online game.")
            self._auto_start_semaphore.release()
            return self
        if multithreaded:
            thread = Thread(target=self.add_to_game, args=[guest_player, False], daemon=True)
            thread.start()
            return self
        guest = CodenamesGamePlayerAdapter(player=guest_player, game_url=self._running_game_url)
        guest.open().login().choose_role()
        self.guests.append(guest)
        self._auto_start_semaphore.release()
        log.debug("Semaphore release")
        return self

    def run_game(self):
        self._start_game()
        board = self.host.parse_board()
        try:
            self.game_runner.run_game(language=self._language.value, board=board)
        except WebDriverException:
            log.exception("Online adapter failed")
            self.close()

    def _start_game(self) -> CodenamesGameRunner:
        if not self.host:
            raise IllegalOperation("Can't start game before hosting initiated. Call host_game() first.")
        for agent in self.agents:
            agent.set_host_adapter(adapter=self.host)
        self.host.start_game()
        return self

    def _handle_hint_given(self, hinter: Hinter, hint: Hint):
        if isinstance(hinter, Agent):
            log.debug("Skipped hint given by agent.")
            return
        adapter = self._get_adapter_for_player(player=hinter)
        adapter.transmit_hint(hint=hint)

    def _handle_guess_given(self, guesser: Guesser, guess: Guess):
        if isinstance(guesser, Agent):
            log.debug("Skipped guess given by agent.")
            return
        adapter = self._get_adapter_for_player(player=guesser)
        adapter.transmit_guess(guess=guess)

    def close(self):
        log.info("Closing online manager...")
        for guest in self.guests:
            guest.close()
        if self.host:
            self.host.close()
