from __future__ import annotations

import logging
from threading import Semaphore, Thread
from typing import ContextManager, Iterable, TypeVar

from codenames.classic.color import ClassicTeam
from codenames.classic.runner import ClassicGamePlayers, ClassicGameRunner
from codenames.generic.move import Clue, Guess
from codenames.generic.player import Operative, Player, PlayerRole, Spymaster
from codenames.online.codenames_game.adapter import (
    CodenamesGamePlayerAdapter,
    GameConfigs,
    IllegalOperation,
)
from codenames.online.codenames_game.agent import Agent, OperativeAgent, SpymasterAgent

log = logging.getLogger(__name__)

T = TypeVar("T", bound=Player)


def player_or_agent(player: T | None, role: PlayerRole, team: ClassicTeam) -> T:
    if player is not None:
        return player
    player_class = SpymasterAgent if role == PlayerRole.SPYMASTER else OperativeAgent
    name = f"{team} {role} Agent"
    return player_class(name=name, team=team)  # type: ignore


class CodenamesGameRunner(ContextManager):
    def __init__(
        self,
        blue_spymaster: Spymaster | None = None,
        red_spymaster: Spymaster | None = None,
        blue_operative: Operative | None = None,
        red_operative: Operative | None = None,
        show_host: bool = True,
        game_configs: GameConfigs | None = None,
    ):
        self._host: CodenamesGamePlayerAdapter | None = None
        self.guests: list[CodenamesGamePlayerAdapter] = []
        blue_spymaster = player_or_agent(blue_spymaster, PlayerRole.SPYMASTER, ClassicTeam.BLUE)
        red_spymaster = player_or_agent(red_spymaster, PlayerRole.SPYMASTER, ClassicTeam.RED)
        blue_operative = player_or_agent(blue_operative, PlayerRole.OPERATIVE, ClassicTeam.BLUE)
        red_operative = player_or_agent(red_operative, PlayerRole.OPERATIVE, ClassicTeam.RED)
        self.players = ClassicGamePlayers.from_collection(blue_spymaster, red_spymaster, blue_operative, red_operative)
        self._show_host = show_host
        self.game_configs = game_configs or GameConfigs()
        self._running_game_url: str | None = None
        self._auto_start_semaphore = Semaphore()

    @property
    def host_connected(self) -> bool:
        return self._host is not None

    @property
    def host(self) -> CodenamesGamePlayerAdapter:
        if not self.host_connected:
            raise IllegalOperation("Game host not initialized.")
        return self._host  # type: ignore

    @property
    def adapters(self) -> Iterable[CodenamesGamePlayerAdapter]:
        yield self.host  # type: ignore
        yield from self.guests

    @property
    def agents(self) -> tuple[Agent, ...]:
        return tuple(player for player in self.players if isinstance(player, Agent))

    def __exit__(self, __exc_type, __exc_value, __traceback):
        self.close()

    def auto_start(self) -> ClassicGameRunner:
        number_of_guests = 3
        self._auto_start_semaphore = Semaphore(value=number_of_guests)
        for player in self.players:
            if not self.host_connected and isinstance(player, Spymaster):
                self.host_game(host_player=player, game_configs=self.game_configs)
            else:
                self._auto_start_semaphore.acquire()  # pylint: disable=consider-using-with
                log.debug("Semaphore acquired.")
                self.add_to_game(guest_player=player, multithreaded=True)
        if not self._running_game_url:
            raise ValueError("Game not running after auto start.")
        for i in range(number_of_guests):
            self._auto_start_semaphore.acquire()  # pylint: disable=consider-using-with
            log.debug(f"Thread {i} done.")
        log.info(f"All {number_of_guests} joined, starting.")
        return self.run_game()

    def all_players_screenshots(self, tag: str):
        for adapter in self.adapters:
            try:
                adapter.screenshot(tag=tag)
            except Exception as e:  # pylint: disable=broad-except
                log.error(f"Error taking screenshot: {e}")

    def run_game(self) -> ClassicGameRunner:
        self._start_game()
        board = self.host.parse_board(language=self.game_configs.language.value)
        game_runner = ClassicGameRunner(players=self.players, board=board)
        game_runner.clue_given_subscribers.append(self._handle_clue_given)
        game_runner.guess_given_subscribers.append(self._handle_guess_given)
        try:
            game_runner.run_game()
        except Exception as e:  # pylint: disable=broad-except
            self.all_players_screenshots(tag="game error")
            raise e
        self.host.screenshot("game over")
        return game_runner

    def host_game(
        self,
        host_player: Spymaster | None = None,
        game_configs: GameConfigs | None = None,
    ) -> CodenamesGameRunner:
        if self.host_connected:
            raise IllegalOperation("A game is already running.")
        if host_player is None:
            host_player = self.players.blue_team.spymaster
        if not isinstance(host_player, Spymaster):
            raise IllegalOperation("Host player must be a Spymaster.")
        game_configs = game_configs or GameConfigs()
        self._host = CodenamesGamePlayerAdapter(player=host_player, headless=not self._show_host)
        self.host.open().host_game()
        self.host.configure_language(language=game_configs.language)
        self.host.choose_role()
        self._running_game_url = self.host.get_game_url()
        log.info(f"Game URL: {self._running_game_url}")
        return self

    def add_to_game(self, guest_player: Player, multithreaded: bool = False) -> CodenamesGameRunner:
        if not self._running_game_url:
            raise IllegalOperation("Can't join game before hosting initiated. Call host_game() first.")
        if self.has_joined_game(guest_player):
            log.warning(f"Player {guest_player} already joined.")
            return self
        if isinstance(guest_player, Agent):
            log.debug("Not adding agent guest to online game.")
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

    def close(self):
        log.info("Closing online manager...")
        for guest in self.guests:
            guest.close()
        if self.host_connected:
            self.host.close()

    def has_joined_game(self, player: Player) -> bool:
        return any(adapter.player == player for adapter in self.adapters)

    def _get_adapter_for_player(self, player: Player) -> CodenamesGamePlayerAdapter:
        for adapter in self.adapters:
            if adapter.player == player:
                return adapter
        raise ValueError(f"Player {player} not found in this game manager.")

    def _start_game(self) -> CodenamesGameRunner:
        if not self.host_connected:
            raise IllegalOperation("Can't start game before hosting initiated. Call host_game() first.")
        for agent in self.agents:
            agent.set_host_adapter(adapter=self.host)
        self.host.screenshot("game start")
        self.host.start_game()
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
