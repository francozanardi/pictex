from pictex import *

AVATAR_PATH = "mersenne.jpg"
DISPLAY_NAME = "Marin Mersenne"
USERNAME = "@marin.mersenne"
TWEET_TEXT = "Spent all week calculating 2⁶⁷-1 by hand only to find it's composite.\nMy quill is broken and I'm out of ink."
REPLIES = "31"
REPOSTS = "127"
LIKES = "1.9K"

avatar = Image(AVATAR_PATH).size(50, 50).border_radius('50%')
user_info = Column(
    Text(DISPLAY_NAME).font_size(16).font_weight(700),
    Text(USERNAME).font_size(15).color("#536471")
).gap(2)

tweet_header = Row(avatar, user_info).vertical_align("center").gap(12)
tweet_body = Text(TWEET_TEXT).font_size(18).line_height(1.4)

def create_stat(icon: str, count: str) -> Row:
    """Helper to create a stat with an 'icon' and a count."""
    return Row(
        Text(icon).font_size(16),
        Text(count).font_size(15).color("#536471")
    ).vertical_align('center').gap(2)

tweet_footer = Row(
    create_stat("💬", REPLIES),
    create_stat("🔁", REPOSTS),
    create_stat("❤", LIKES),
).size(width=550).horizontal_distribution('space-between')

tweet_card = (
    Column(
        tweet_header,
        tweet_body,
        tweet_footer
    )
    .size(width=600)
    .background_color("white")
    .padding(25)
    .gap(15)
    .border_radius(16)
    .border(1, "#CFD9DE")
)

canvas = (
    Canvas()
    .font_family("Arial")
    .background_color("#E9ECEF")
    .padding(50)
)

canvas.render(tweet_card).save("tweet.png")
