from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    user_id: int
    is_vip: bool = False
    total_ads: int = 0
    total_tickets: int = 0
    stars: float = 0
    joined_at: str = str(datetime.now())


@dataclass
class Ad:
    user_id: int
    channel: str
    text: str
    banner: str
    days: int
    price: int
    status: str = "pending"
    created_at: str = str(datetime.now())


@dataclass
class Ticket:
    ticket_id: int
    user_id: int
    text: str
    status: str = "open"
    created_at: str = str(datetime.now())


@dataclass
class SupportChat:
    user_id: int
    admin_id: int
    started_at: str = str(datetime.now())


@dataclass
class Rating:
    user_id: int
    admin_id: int
    stars: int
    created_at: str = str(datetime.now())