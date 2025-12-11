import random

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Player
from app.schema import PlayerOut, RandomPlayersResponse, VerifyRequest, VerifyResponse


class GameService:
    @staticmethod
    async def get_two_random_players(session: AsyncSession) -> RandomPlayersResponse:
        query = select(Player).order_by(func.random()).limit(2)
        result = await session.execute(query)
        players = result.scalars().all()

        if len(players) < 2:
            raise ValueError("Not enough players in the database")

        return RandomPlayersResponse(
            players=[GameService._to_player_out(p) for p in players]
        )

    @staticmethod
    async def verify_guess(session: AsyncSession, payload: VerifyRequest) -> VerifyResponse:
        ids = [payload.player_left_id, payload.player_right_id]
        result = await session.execute(select(Player).where(Player.id.in_(ids)))
        players = {p.id: p for p in result.scalars().all()}

        left = players.get(payload.player_left_id)
        right = players.get(payload.player_right_id)

        if left is None or right is None:
            raise ValueError("Players not found")

        left_val = int(left.stat_value)
        right_val = int(right.stat_value)

        if payload.guess == "left":
            correct = left_val >= right_val
        else:
            correct = right_val >= left_val

        return VerifyResponse(
            correct=correct,
            left_value=left_val,
            right_value=right_val,
        )

    @staticmethod
    def _to_player_out(player: Player) -> PlayerOut:
        return PlayerOut(
            id=player.id,
            name=player.name,
            image_url=player.image_url,
            stat_value=player.stat_value,
        )
