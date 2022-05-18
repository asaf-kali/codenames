from typing import List


class ModelFormatAdapter:
    def to_model_format(self, word: str) -> str:
        raise NotImplementedError()

    def to_model_formats(self, word: str) -> List[str]:
        return [self.to_model_format(word)]

    def to_board_format(self, word: str) -> str:
        raise NotImplementedError()

    def to_board_formats(self, word: str) -> List[str]:
        return [self.to_board_format(word)]


class DefaultFormatAdapter(ModelFormatAdapter):
    def to_model_format(self, word: str) -> str:
        return word

    def to_board_format(self, word: str) -> str:
        return word


DEFAULT_MODEL_ADAPTER = DefaultFormatAdapter()
