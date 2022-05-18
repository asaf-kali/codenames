import logging
from threading import Semaphore, Thread
from typing import Iterable, List, Optional, Tuple, TypeVar

from selenium.common.exceptions import WebDriverException

from codenames.game import (
    Board,
    Guess,
    Guesser,
    Hint,
    Hinter,
    Player,
    PlayerRole,
    Winner,
)
from codenames.game.runner import GameRunner
from codenames.online import (
    IllegalOperation,
    NamecodingLanguage,
    NamecodingPlayerAdapter,
)
from codenames.online.online_players import Agent, GuesserAgent, HinterAgent

log = logging.getLogger(__name__)

T = TypeVar("T")


def player_or_agent(player: T, role: PlayerRole) -> T:
    if player is not None:
        return player
    player_class = HinterAgent if role == PlayerRole.HINTER else GuesserAgent
    return player_class("Agent")


class NamecodingGameRunner:
    def __init__(
        self,
        blue_hinter: Hinter = None,
        red_hinter: Hinter = None,
        blue_guesser: Guesser = None,
        red_guesser: Guesser = None,
        show_host: bool = True,
    ):
        self.host: Optional[NamecodingPlayerAdapter] = None
        self.guests: List[NamecodingPlayerAdapter] = []
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
        self._running_game_id: Optional[str] = None
        self._auto_start_semaphore = Semaphore()
        self._language: NamecodingLanguage = NamecodingLanguage.HEBREW
        self.game_runner.hint_given_subscribers.append(self._handle_hint_given)
        self.game_runner.guess_given_subscribers.append(self._handle_guess_given)

    @property
    def adapters(self) -> Iterable[NamecodingPlayerAdapter]:
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

    def _get_adapter_for_player(self, player: Player) -> NamecodingPlayerAdapter:
        for adapter in self.adapters:
            if adapter.player == player:
                return adapter
        raise ValueError(f"Player {player} not found in this game manager.")

    def has_joined_game(self, player: Player) -> bool:
        return any(adapter.player == player for adapter in self.adapters)

    def auto_start(
        self, language: NamecodingLanguage = NamecodingLanguage.ENGLISH, clock: bool = True
    ) -> "NamecodingGameRunner":
        number_of_guests = 3
        self._auto_start_semaphore = Semaphore(value=number_of_guests)
        for player in self.players:
            if not self.host:
                self.host_game(host_player=player)  # type: ignore
                self.configure_game(language=language, clock=clock)
            else:
                self._auto_start_semaphore.acquire()
                log.debug("Semaphore acquired.")
                self.add_to_game(guest_player=player, multithreaded=True)
        if not self._running_game_id:
            log.warning("Game not running after auto start.")
            return self
        for i in range(number_of_guests):
            self._auto_start_semaphore.acquire()
            log.debug(f"Thread {i} done.")
        log.info(f"All {number_of_guests} joined, starting.")
        self.run_game()
        return self

    def host_game(self, host_player: Optional[Hinter] = None) -> "NamecodingGameRunner":
        if self.host:
            raise IllegalOperation("A game is already running.")
        if host_player is None:
            host_player = self.game_runner.blue_hinter
        if not isinstance(host_player, Hinter):
            raise IllegalOperation("Host player must be a Hinter.")
        host = NamecodingPlayerAdapter(player=host_player, headless=not self._show_host)
        host.open().host_game().choose_role().ready()
        self._running_game_id = host.get_game_id()
        print(f"Running game id: {self._running_game_id}")
        self.host = host
        return self

    def add_to_game(self, guest_player: Player, multithreaded: bool = False) -> "NamecodingGameRunner":
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
            t = Thread(target=self.add_to_game, args=[guest_player, False], daemon=True)
            t.start()
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
    ) -> "NamecodingGameRunner":
        if not self.host:
            raise IllegalOperation("Can't configure game before hosting initiated. Call host_game() first.")
        self._language = language
        self.host.set_language(language=language)
        self.host.set_clock(clock=clock)
        return self

    def run_game(self):
        self._start_game()
        board = self.host.parse_board()
        try:
            self.game_runner.run_game(language=self._language.value, board=board)
        except WebDriverException:
            log.exception("Online adapter failed")
            self.close()

    def _start_game(self) -> "NamecodingGameRunner":
        if not self.host:
            raise IllegalOperation("Can't start game before hosting initiated. Call host_game() first.")
        for adapter in self.adapters:
            adapter.ready()
        for agent in self.agents:
            agent.set_host_adapter(adapter=self.host)
        self.host.click_start_game()
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
