from pydantic import BaseModel
from typing import Optional, List, Dict

# Rasa classes


class IntentsOut(BaseModel):
    intents: List[str]


class ExamplesOut(BaseModel):
    intent: str # not working right now
    examples: List[str]


class ResponsesOut(BaseModel):
    response: str
    examples: List[str]


class Buttons(BaseModel):
    payload: str #TODO: is payload always a string?
    title: str


class MessageIn(BaseModel):
    query: str
    identifier: str
    bot_name: Optional[str]


class MessageOut(BaseModel):
    text: Optional[str]
    buttons: Optional[List[Buttons]]
    recipient_id: str


