from __future__ import annotations

import logging
from threading import Semaphore, Thread
from typing import Iterable, TypeVar, tuple

from selenium.common.exceptions import WebDriverException

from codenames.game.board import Board
from codenames.game.move import Clue, Guess
from codenames.game.player import Operative, Player, PlayerRole, Spymaster
from codenames.game.runner import GameRunner
from codenames.game.winner import Winner
from codenames.online.namecoding.adapter import (
    IllegalOperation,
    NamecodingLanguage,
    NamecodingPlayerAdapter,
)
from codenames.online.namecoding.players import Agent, OperativeAgent, SpymasterAgent

log = logging.getLogger(__name__)

T = TypeVar("T")


def player_or_agent(player: T, role: PlayerRole) -> T:
    if player is not None:
        return player
    player_class = SpymasterAgent if role == PlayerRole.SPYMASTER else OperativeAgent
    return player_class("Agent")


class NamecodingGameRunner:
    def __init__(
        self,
        blue_spymaster: Spymaster | None = None,
        red_spymaster: Spymaster | None = None,
        blue_operative: Operative | None = None,
        red_operative: Operative | None = None,
        show_host: bool = True,
    ):
        self.host: NamecodingPlayerAdapter | None = None
        self.guests: list[NamecodingPlayerAdapter] = []
        blue_spymaster = player_or_agent(blue_spymaster, PlayerRole.SPYMASTER)
        red_spymaster = player_or_agent(red_spymaster, PlayerRole.SPYMASTER)
        blue_operative = player_or_agent(blue_operative, PlayerRole.OPERATIVE)
        red_operative = player_or_agent(red_operative, PlayerRole.OPERATIVE)
        self.game_runner = GameRunner(
            blue_spymaster=blue_spymaster,  # type: ignore
            red_spymaster=red_spymaster,  # type: ignore
            blue_operative=blue_operative,  # type: ignore
            red_operative=red_operative,  # type: ignore
        )
        self._show_host = show_host
        self._running_game_id: str | None = None
        self._auto_start_semaphore = Semaphore()
        self._language: NamecodingLanguage = NamecodingLanguage.HEBREW
        self.game_runner.clue_given_subscribers.append(self._handle_clue_given)
        self.game_runner.guess_given_subscribers.append(self._handle_guess_given)

    @property
    def adapters(self) -> Iterable[NamecodingPlayerAdapter]:
        yield self.host  # type: ignore
        yield from self.guests

    @property
    def winner(self) -> Winner | None:
        return self.game_runner.winner

    @property
    def board(self) -> Board:
        return self.game_runner.state.board

    @property
    def players(self) -> tuple[Player, ...]:
        return self.game_runner.players

    @property
    def agents(self) -> tuple[Agent, ...]:
        return tuple(player for player in self.players if isinstance(player, Agent))

    def _get_adapter_for_player(self, player: Player) -> NamecodingPlayerAdapter:
        for adapter in self.adapters:
            if adapter.player == player:
                return adapter
        raise ValueError(f"Player {player} not found in this game manager.")

    def has_joined_game(self, player: Player) -> bool:
        return any(adapter.player == player for adapter in self.adapters)

    def auto_start(
        self, language: NamecodingLanguage = NamecodingLanguage.ENGLISH, clock: bool = True
    ) -> NamecodingGameRunner:
        number_of_guests = 3
        self._auto_start_semaphore = Semaphore(value=number_of_guests)
        for player in self.players:
            if not self.host:
                self.host_game(host_player=player)  # type: ignore
                self.configure_game(language=language, clock=clock)
            else:
                self._auto_start_semaphore.acquire()  # pylint: disable=consider-using-with
                log.debug("Semaphore acquired.")
                self.add_to_game(guest_player=player, multithreaded=True)
        if not self._running_game_id:
            log.warning("Game not running after auto start.")
            return self
        for i in range(number_of_guests):
            self._auto_start_semaphore.acquire()  # pylint: disable=consider-using-with
            log.debug(f"Thread {i} done.")
        log.info(f"All {number_of_guests} joined, starting.")
        self.run_game()
        return self

    def host_game(self, host_player: Spymaster | None = None) -> NamecodingGameRunner:
        if self.host:
            raise IllegalOperation("A game is already running.")
        if host_player is None:
            host_player = self.game_runner.blue_spymaster
        if not isinstance(host_player, Spymaster):
            raise IllegalOperation("Host player must be a Spymaster.")
        host = NamecodingPlayerAdapter(player=host_player, headless=not self._show_host)
        host.open().host_game().choose_role().ready()
        self._running_game_id = host.get_game_id()
        print(f"Running game id: {self._running_game_id}")
        self.host = host
        return self

    def add_to_game(self, guest_player: Player, multithreaded: bool = False) -> NamecodingGameRunner:
        if not self._running_game_id:
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
        guest = NamecodingPlayerAdapter(player=guest_player)
        guest.open().join_game(game_id=self._running_game_id).choose_role()
        self.guests.append(guest)
        guest.ready()
        self._auto_start_semaphore.release()
        log.debug("Semaphore release")
        return self

    def configure_game(
        self, language: NamecodingLanguage = NamecodingLanguage.ENGLISH, clock: bool = True
    ) -> NamecodingGameRunner:
        if not self.host:
            raise IllegalOperation("Can't configure game before hosting initiated. Call host_game() first.")
        self._language = language
        self.host.set_language(language=language)
        self.host.set_clock(clock=clock)
        return self

    def run_game(self):
        self._start_game()
        board = self.host.parse_board(language=self._language.value)
        try:
            self.game_runner.run_game(board=board)
        except WebDriverException:
            log.exception("Online adapter failed")
            self.close()

    def _start_game(self) -> NamecodingGameRunner:
        if not self.host:
            raise IllegalOperation("Can't start game before hosting initiated. Call host_game() first.")
        for adapter in self.adapters:
            adapter.ready()
        for agent in self.agents:
            agent.set_host_adapter(adapter=self.host)
        self.host.click_start_game()
        return self

    def _handle_clue_given(self, spymaster: Spymaster, clue: Clue):
        if isinstance(spymaster, Agent):
            log.debug("Skipped clue given by agent.")
            return
        adapter = self._get_adapter_for_player(player=spymaster)
        adapter.transmit_clue(clue=clue)

    def _handle_guess_given(self, operative: Operative, guess: Guess):
        if isinstance(operative, Agent):
            log.debug("Skipped guess given by agent.")
            return
        adapter = self._get_adapter_for_player(player=operative)
        adapter.transmit_guess(guess=guess)

    def close(self):
        log.info("Closing online manager...")
        for guest in self.guests:
            guest.close()
        if self.host:
            self.host.close()
