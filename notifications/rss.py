from datetime import datetime
from rfeed import Item, Feed
from models import FoodBank


class RSSManager:
    """Uses the rfeed library to create a stock alerts RSS feed"""

    def __init__(self):
        self.feed = Feed(title="Feeding Newcastle Alerts Feed",
                         link="placeholderurl.com",
                         description="Alert feed for food bank stock notifications.")

    def generate_item(self, food_bank_id, generated_message):
        food_bank = FoodBank.query.filter_by(id=food_bank_id).first()
        new_item = Item(title=food_bank.name,
                        link=f"url/food-bank-information/{food_bank_id})",
                        description=generated_message,
                        pubDate=datetime.now())
        self.feed.items.append(new_item)

    def write_feed(self):
        for line in self.feed.rss():
            print(line)
        with open("rss.xml", "w") as rss_file:
            rss_file.writelines(self.feed.rss())
