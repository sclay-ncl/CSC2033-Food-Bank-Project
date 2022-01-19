from datetime import datetime

from flask import url_for
from rfeed import Item, Feed


class RSSManager:
    """
    @author: Sol Clay
    Uses the rfeed library to create a stock alerts RSS feed
    """

    def __init__(self):
        self.feed = Feed(title="Feeding Newcastle Alerts Feed",
                         link="PlaceholderURL",
                         description="Alert feed for food bank stock notifications.")

    def generate_item(self, food_bank_id, generated_message):
        """
        @author: Sol Clay
        Generates a rfeed Item with food bank stock information

        @param: food_bank_id - id of the food bank the notification is for
        @param: generated_message - string message to be posted on the item
        """
        from models import FoodBank  # imported here to avoid circular imports
        food_bank = FoodBank.query.filter_by(id=food_bank_id).first()
        new_item = Item(title=food_bank.name,
                        link=f"url/food-bank-information/{food_bank_id})",
                        description=generated_message,
                        pubDate=datetime.now())
        self.feed.items.append(new_item)

    def write_feed(self):
        """
        @author: Sol Clay
        Writes the rss feed to the rss xml file
        """
        with open("rss.xml", "w") as rss_file:
            rss_file.writelines(self.feed.rss())
