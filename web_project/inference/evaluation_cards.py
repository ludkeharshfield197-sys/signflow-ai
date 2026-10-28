import json
from functools import lru_cache
from pathlib import Path

CARDS_PATH = Path(__file__).with_name("evaluation_cards.json")


@lru_cache(maxsize=1)
def load_evaluation_cards():
    payload = json.loads(CARDS_PATH.read_text(encoding="utf-8"))
    return {str(filename).lower(): card for filename, card in payload.get("models", {}).items()}


def evaluation_card_for(file_path):
    filename = Path(str(file_path or "")).name.lower()
    card = load_evaluation_cards().get(filename)
    return dict(card) if card else {}
