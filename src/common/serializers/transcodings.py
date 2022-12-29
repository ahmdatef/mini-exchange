from eventsourcing.persistence import Transcoding

from common.models.basic import BuyOrder, SellOrder


class SellOrderTranscoding(Transcoding):
    type = SellOrder
    name = 'SellOrder'

    def encode(self, obj: SellOrder) -> dict:
        return obj.dict()

    def decode(self, data: dict) -> SellOrder:
        return SellOrder(**data)


class BuyOrderTranscoding(Transcoding):
    type = BuyOrder
    name = 'BuyOrder'

    def encode(self, obj: BuyOrder) -> dict:
        return obj.dict()

    def decode(self, data: dict) -> BuyOrder:
        return BuyOrder(**data)
