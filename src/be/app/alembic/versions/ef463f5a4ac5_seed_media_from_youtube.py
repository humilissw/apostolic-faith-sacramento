"""seed media table from AFC Sacramento YouTube channel

Revision ID: ef463f5a4ac5
Revises: p1q2r3s4t5u6
Create Date: 2026-08-24 03:43:00.160137

Data migration: one row per video on the channel (extracted via
scripts/extract_youtube_services.py). Rows are idempotent — ids are UUID5 of the
YouTube video id and inserts use ON DUPLICATE KEY UPDATE, so re-running after a
fresh extraction only updates changed titles/descriptions.
"""

from typing import Sequence, Union


from alembic import op

revision: str = "ef463f5a4ac5"
down_revision: Union[str, Sequence[str], None] = "p1q2r3s4t5u6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (id, name, description, owner_id, uploaded_on) — one tuple per YouTube video.
MEDIA_ROWS = [
    (
        "5147a444-eb67-5e9f-ba74-2bb9181fd873",
        "Two Worldviews Of Freedom — Bro. Noah Mocan • Romans 8:1-2",
        "8/16/2026 — 5:00 pm Sunday evening service - Two Worldviews Of Freedom — Bro. Noah Mocan • Romans 8:1-2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-08-18 00:00:00",
    ),  # youtube:2bb9181fd873
    (
        "13f7674b-b503-5ca7-9525-474588cc3a01",
        "Walk In Humility — Brother Sorin Filimon • Ephesians 4:1-16",
        "8/16/2026 — 11:00 am Sunday morning service - Walk In Humility — Brother Sorin Filimon • Ephesians 4:1-16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-08-16 00:00:00",
    ),  # youtube:474588cc3a01
    (
        "0b0353c3-1c23-52cd-9b41-e7b89b52ec79",
        "The Standard For Spiritual Success — Bro. Noah Mocan • Joshua 1:7-9",
        "8/9/2026 — 5:00 pm Sunday evening youth service - The Standard For Spiritual Success — Bro. Noah Mocan • Joshua 1:7-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-08-10 00:00:00",
    ),  # youtube:e7b89b52ec79
    (
        "a8a812eb-c503-56ec-9957-8826fa299b3c",
        "As The Dear — Jack, James, Lance",
        "8/9/2026 — 11:00 am Sunday morning service - As The Dear — Jack, James, Lance\n Trinity Apostolic Faith Church, Sacramento County, California For more information, please visit us at www.afcsacramento.org, email: pete@sferle.com CCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-08-09 00:00:00",
    ),  # youtube:8826fa299b3c
    (
        "62ad7c88-00d3-5ad6-a85e-1c645965d934",
        "What Would Ye That I Should Do For You? — Rev. Mark Worthington • Mark 10:35-45",
        "8/9/2026 — 11:00 am Sunday morning service - What Would Ye That I Should Do For You? — Rev. Mark Worthington • Mark 10:35-45\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-08-09 00:00:00",
    ),  # youtube:1c645965d934
    (
        "b342cf67-767b-51df-8222-d2c74372e9cd",
        "God Is My Salvation — Brother Sorin Filimon • Isaiah 12:1-6",
        "8/2/2026 — 5:00 pm Sunday evening service - God Is My Salvation — Brother Sorin Filimon • Isaiah 12:1-6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-08-03 00:00:00",
    ),  # youtube:d2c74372e9cd
    (
        "c8703250-867b-550e-a7af-c53b4d6fc5fd",
        "Living In The Light Of That Day — Rev. Pete Sferle • 2 Peter 3:10-14",
        "8/2/2026 — 11:00 am Sunday morning service - Living In The Light Of That Day — Rev. Pete Sferle • 2 Peter 3:10-14 Trinity Apostolic Faith Church, Sacramento County, California For more information, please visit us at www.afcsacramento.org, email: pete@sferle.com CCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-08-02 00:00:00",
    ),  # youtube:c53b4d6fc5fd
    (
        "42baaada-924c-5cbf-a592-ac9ce005e4e6",
        "Confidence In God — Bro. Sorin Filimon • 1 Samuel 17:32-36",
        "7/26/2026 — 5:00 pm Sunday evening service - Confidence In God — Bro. Sorin Filimon • 1 Samuel 17:32-36\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-07-27 00:00:00",
    ),  # youtube:ac9ce005e4e6
    (
        "47975d83-eef7-5bc5-a778-dd13e181594f",
        "Do Not Conform - But Be Transformed — Rev. Pete Sferle • Romans 12-2",
        "7/26/2026 — 11:00 am Sunday morning service - Do Not Conform - But Be Transformed — Rev. Pete Sferle • Romans 12-2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-07-26 00:00:00",
    ),  # youtube:dd13e181594f
    (
        "a4a5a17a-ac3c-5c38-a552-dbe553f4b1a8",
        "Dead and Alive — Rev. Pete Sferle • Romans 12:1",
        "7/19/2026 — 11:00 am Sunday morning service - Dead and Alive — Rev. Pete Sferle • Romans 12:1\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-07-22 00:00:00",
    ),  # youtube:dbe553f4b1a8
    (
        "cac9d85a-667f-5f9c-b27c-51de56fc22f3",
        "A Nameless Father That Had Great Influence Upon His Child — Rev. Pete Sferle • Daniel 1:17-21",
        "6/21/2026 — 11:00 am Sunday morning service - A Nameless Father That Had Great Influence Upon His Child — Rev. Pete Sferle • Daniel 1:17-21\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-07-17 00:00:00",
    ),  # youtube:51de56fc22f3
    (
        "76b048f1-193c-5e45-b392-f142849a8550",
        "God''s Means and Methods — Bro. Noah Mocan • Isiah 55:8-11",
        "6/14/2026 —  2:00 pm Sunday youth service  - God''s Means and Methods — Bro. Noah Mocan • Isiah 55:8-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com  ♪♫\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-07-05 00:00:00",
    ),  # youtube:f142849a8550
    (
        "74c8c03f-5688-56e5-bc6a-9b2f8aa00afc",
        "God''s Answer To The Scoffers — Rev. Pete Sferle • 2 Peter 3:1-9",
        "6/14/2026 — 11:00 am Sunday morning service - God''s Answer To The Scoffers — Rev. Pete Sferle • 2 Peter 3:1-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-06-24 00:00:00",
    ),  # youtube:9b2f8aa00afc
    (
        "b11d52d5-b771-578e-886c-3c5ef993b63d",
        "The Call — Rev. John Musgrave • 2 Kings 2:9-15 › Scripture 1 Kings 19:13-19",
        "6/7/2026 — 11:00 am Sunday morning service - The Call — Rev. John Musgrave • 2 Kings 2:9-15 › Scripture 1 Kings 19:13-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-06-08 00:00:00",
    ),  # youtube:3c5ef993b63d
    (
        "7df88cf7-364e-5187-a1b3-5fe59c3270af",
        "Bartimaeus Healed — Bro. Sorin Filimon •  Mark 10:46-53",
        "5/31/2026 —  5:00 pm Sunday evening service  -  Bartimaeus Healed — Bro. Sorin Filimon •  Mark 10:46-53\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-06-01 00:00:00",
    ),  # youtube:5fe59c3270af
    (
        "6c2b8ba3-b77e-56dc-ad59-77609137cf09",
        "Walking On Water — Rev. Mark Worthington • Matthew 14:25-32",
        "5/31/2026 — 11:00 am Sunday morning service - Walking On Water — Rev. Mark Worthington • Matthew 14:25-32\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-05-31 00:00:00",
    ),  # youtube:77609137cf09
    (
        "35b42b71-8c9a-554a-b2cd-c4182feb541d",
        "Memorials - Bro. Noah Mocan • Psalm 77:1-12",
        "5/24/2026 — 11:00 am Sunday morning service - Memorials - Bro. Noah Mocan • Psalm 77:1-12 Trinity Apostolic Faith Church, Sacramento County, California For more information, please visit us at www.afcsacramento.org, email: pete@sferle.com CCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-05-24 00:00:00",
    ),  # youtube:c4182feb541d
    (
        "29d068e5-7427-5e92-8769-c61cc153a562",
        "Enduring — Rev. Mark Worthington • Haggai 2:1-9",
        "5/17/2026 — 11:00 am Sunday morning service - Enduring — Rev. Mark Worthington • Haggai 2:1-9 Trinity Apostolic Faith Church, Sacramento County, California \nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com \nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-05-22 00:00:00",
    ),  # youtube:c61cc153a562
    (
        "058e0f23-5109-55d3-bc31-1b682ef62a2e",
        "Mother''s Day › A Mother''s Influence — Rev. Pete  Sferle • 2 Timothy  1:5; 3:14-17",
        "5/10/2026 — 11:00 am Sunday morning service - Mother''s Day › A Mother''s Influence — Rev. Pete  Sferle • 2 Timothy  1:5; 3:14-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-05-21 00:00:00",
    ),  # youtube:1b682ef62a2e
    (
        "2f4805f0-a895-5a3f-b268-ba1b68b46a29",
        "An Encounter with Jesus — Rev. Pete Sferle • Luke  19:1-10",
        "5/3/2026 —  5:00 pm Sunday evening Youth/Children''s service  - An Encounter with Jesus — Rev. Pete Sferle • Luke  19:1-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com  ♪♫\nCCLI Streaming Plus License #20833650",
        "00000000-0000-0000-0000-000000000000",
        "2026-05-21 00:00:00",
    ),  # youtube:ba1b68b46a29
    (
        "4bc58eeb-d826-5827-b7c8-f98e8cd331e0",
        "What A Friend",
        "What A Friend  By: Joseph Medlicott Scriven\nLillenas Publishing Company, Public Domain\nCopyrights: © Words: Public Domain; Music: 2005 Lillenas Publishing Company\nAdministrators: Music Services, Inc., Public Domain\n\nTrinity Apostolic Faith Church, Sacramento County, California. For more information, please visit us at www.afcsacramento.org, email: pete@sferle.com. CCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-05-08 00:00:00",
    ),  # youtube:f98e8cd331e0
    (
        "72290648-32ce-5569-bf63-f4994fe99ac6",
        "Beauty For Ashes — Bro. Sorin Filimon • Luke 4:14-22",
        "5/3/2026 —  11:00 am Sunday morning service -  Beauty For Ashes — Bro. Sorin Filimon • Luke 4:14-22\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-05-04 00:00:00",
    ),  # youtube:f4994fe99ac6
    (
        "fddeec44-5747-571d-9835-8af000068649",
        "O Lord Revive Us Again — Rev. Pete Sferle • Psalm 85:6",
        "4/26/2026 — 11:00 am Sunday morning service - O Lord Revive Us Again — Rev. Pete Sferle • Psalm 85:6 › Scripture Jonah 3:1-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-04-30 00:00:00",
    ),  # youtube:8af000068649
    (
        "1eb198a4-1a3b-51d0-9b97-08a9c6fc7019",
        "Abide in the Vine — Bro. Sorin Filimon • John 15:1-8",
        "4/19/2026 —  5:00 pm Sunday evening service  -  Abide in the Vine — Bro. Sorin Filimon • John 15:1-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-04-21 00:00:00",
    ),  # youtube:08a9c6fc7019
    (
        "adcd5d18-dc2d-501e-9b98-a98c28d8ded0",
        "The Rise of the Antichrist — Rev. Pete Sferle • Revelation 2 Thessalonians 2:1-12",
        "4/19/2026 —  11:00 am Sunday morning service - The Rise of the Antichrist — Rev. Pete Sferle • Revelation 2 Thessalonians 2:1-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-04-19 00:00:00",
    ),  # youtube:a98c28d8ded0
    (
        "b6d7b026-043d-5a8d-b579-445e70e16433",
        "Only Jesus — Bro. Noah Mocan • Acts 4:12",
        "4/12/2026 —  5:00 pm Sunday evening youth service  -  Only Jesus — Bro. Noah Mocan • Acts 4:12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-04-14 00:00:00",
    ),  # youtube:445e70e16433
    (
        "e70e50e0-c36b-5573-b25f-2c8d1b2d9d2a",
        "Evangelism — Rev. Mark Worthington • John 9:24-34",
        "4/12/2026 —  11:00 am Sunday morning service - Evangelism — Rev. Mark Worthington • John 9:24-34\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-04-12 00:00:00",
    ),  # youtube:2c8d1b2d9d2a
    (
        "dc132874-90bc-5ae9-b946-4f34d4cff2a0",
        "Night Of Music April 5, 202",
        "4/5/2026 —  5:00 pm Sunday evening Night Of Music\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-04-11 00:00:00",
    ),  # youtube:4f34d4cff2a0
    (
        "baa3357c-9eb6-53c0-9eed-147add163496",
        "Jesus, The Only One Who Conquered Death — Rev. Pete Sferle • 2 Timothy 2:8",
        "4/5/2026 —  11:00 am Easter Sunday morning service - Jesus, The Only One Who Conquered Death — Rev. Pete Sferle • 2 Timothy 2:8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-04-06 00:00:00",
    ),  # youtube:147add163496
    (
        "21033936-6015-5f4f-8de5-1c8f99c15845",
        "Jesus The Lamb Of God — Rev. Pete Sferle • Revelation 5:6",
        "4/3/2026 — 7:00 pm Good Friday evening service - Jesus The Lamb Of God — Rev. Pete Sferle • Revelation 5:6 Trinity Apostolic Faith Church, Sacramento County, California For more information, please visit us at www.afcsacramento.org, email: pete@sferle.com CCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-04-05 00:00:00",
    ),  # youtube:1c8f99c15845
    (
        "cc910286-2cb8-5611-93c0-794912dad4ca",
        "Parable  Of The Sower — Bro. Sorin Filimon • Mark 4:1-20",
        "3/29/2026 —  5:00 pm Sunday evening service  -  Parable  Of The Sower — Bro. Sorin Filimon • Mark 4:1-20\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-03-31 00:00:00",
    ),  # youtube:794912dad4ca
    (
        "7bb221b7-350d-5db1-b6b3-19545a164ad3",
        "Palm Sunday - Seeing The Glory Of Jesus — Rev. Mark Worthington • Luke 19:28-38",
        "3/29/2026 — 11:00 am Sunday morning service - Palm Sunday - Seeing The Glory Of Jesus — Rev. Mark Worthington • Luke 19:28-38\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-03-29 00:00:00",
    ),  # youtube:19545a164ad3
    (
        "585005a8-5234-5d0b-b437-acbbcfd0e91e",
        "Let Your Gentleness Be Known To All Men — Rev. Pete Sferle • Philippians 4:5",
        "3/22/2026 —  11:00 am Sunday morning service - Let Your Gentleness Be Known To All Men — Rev. Pete Sferle • Philippians 4:5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-03-25 00:00:00",
    ),  # youtube:acbbcfd0e91e
    (
        "6323525e-a6a4-53b4-ace8-0d20f995c124",
        "Be a Berean — 1 Thessalonians 5:21 • Bro. Noah Mocan",
        "3/15/2026 —  2:15 pm Sunday youth afternoon service  -  Be a Berean — 1 Thessalonians 5:21 • Bro. Noah Mocan\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-03-22 00:00:00",
    ),  # youtube:0d20f995c124
    (
        "fa8cbe95-8042-53b8-b0dc-1453ad1b26be",
        "God''s Certain Judgement — Rev. Pete Sferle • 2 Peter 2:4-9",
        "3/15/2026 — 11:00 am Sunday morning service - God''s Certain Judgement — Rev. Pete Sferle • 2 Peter 2:4-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-03-17 00:00:00",
    ),  # youtube:1453ad1b26be
    (
        "b1f773e1-ddb2-5dbc-b90c-e01d53c658b3",
        "When You Can''t, God Can — Bro Sorin Filimon •  Isaiah 40:27:31",
        "3/8/2026 —  11:00 am Sunday morning service - When You Can''t, God Can — Bro Sorin Filimon •  Isaiah 40:27:31\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-03-12 00:00:00",
    ),  # youtube:e01d53c658b3
    (
        "9ac31ef2-fea7-550e-93f4-bdea78bbc304",
        "Are You Ready? — Rev. Mark Worthington • Matthew 25:1-13",
        "3/1/2026 —  5:00 pm Sunday morning service  -  Are You Ready? — Rev. Mark Worthington • Matthew 25:1-13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-03-02 00:00:00",
    ),  # youtube:bdea78bbc304
    (
        "cb471ff2-806f-5b37-a43d-26aaad0c3cf1",
        "Be on Alert of False Teachers - 2 Peter 2:1-3",
        "3/1/2026 —  5:00 pm Sunday morning service - No Man Can Serve Two Masters — Be on Alert of False Teachers - 2 Peter 2:1-3\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-03-02 00:00:00",
    ),  # youtube:26aaad0c3cf1
    (
        "9aa99f65-53cf-5ceb-9df0-bed44f5a4e6a",
        "No Man Can Serve Two Masters — Bro. Sorin Filimon • Matthew  6:24",
        "2/22/2026 —  5:00 pm Sunday evening  service - No Man Can Serve Two Masters — Bro. Sorin Filimon • Matthew  6:24\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-02-23 00:00:00",
    ),  # youtube:bed44f5a4e6a
    (
        "38bc3242-3103-5073-acec-7e5227bb1351",
        "Why Not To Worry — Rev. Pete Sferle • St Matthew 6:25-34",
        "2/22/2026 — 11:00 am Sunday morning service - Why Not To Worry — Rev. Pete Sferle • St Matthew 6:25-34\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-02-23 00:00:00",
    ),  # youtube:7e5227bb1351
    (
        "1c4bbd66-2ef2-508c-a6a7-04aa2097fcbe",
        "Where Is Wisdom Found? — Bro. Noah Mocan • Job 28",
        "2/8/2026 —  5:00 pm Sunday evening youth service - Where Is Wisdom Found? — Bro. Noah Mocan • Job 28 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A ♪♫",
        "00000000-0000-0000-0000-000000000000",
        "2026-02-15 00:00:00",
    ),  # youtube:04aa2097fcbe
    (
        "8af5c80d-ab44-54ef-b477-3f58f53a9e34",
        "How Is Your Memory? The Importance Of Reminders — Rev. Pete Sferle • 2 Peter 1:12-15;  Joshua 4:...",
        "2/1/26 —  11:00 am Sunday morning service - How Is Your Memory? The Importance Of Reminders — Rev. Pete Sferle • 2 Peter 1:12-15; Reading:  Joshua 4:19-24\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-02-02 00:00:00",
    ),  # youtube:3f58f53a9e34
    (
        "896ac2cc-527b-55fd-a961-b5d1ed9e4270",
        "Africa Presentation — Rev. Pete Sferle",
        "1/25/26 —  5:00 pm Africa Presentation\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-02-02 00:00:00",
    ),  # youtube:b5d1ed9e4270
    (
        "366d1b23-6998-5433-b0de-1d62d5099b34",
        "Dare To Be A Daniel  — Rev. Mark Worthington • Daniel 1:8-17",
        "1/25/26 — 11:00 am Sunday morning service -  Dare To Be A Daniel  — Rev. Mark Worthington • Daniel 1:8-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-01-25 00:00:00",
    ),  # youtube:1d62d5099b34
    (
        "ba506406-58ae-5adc-8fc7-13797681ea7e",
        "Continue To Grow — Rev. Pete Sferle • 2 Peter 1: 5-11",
        "1/18/26 — 11:00 am Sunday morning service - Continue To Grow — Rev. Pete Sferle • 2 Peter 1: 5-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-01-19 00:00:00",
    ),  # youtube:13797681ea7e
    (
        "040a6d75-8bfb-5618-a7fe-6eaa8aa0d680",
        "The Greatest Of These — Bro. Noah Mocan • 1 Corinthians 13:13",
        "1/11/26 —  5:00 pm Sunday evening youth service - The Greatest Of These — Bro. Noah Mocan • 1 Corinthians 13:13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-01-12 00:00:00",
    ),  # youtube:6eaa8aa0d680
    (
        "9db19091-aa8e-5f5a-99f6-5aeb54270f19",
        "God Gives Us Everything To Live A Godly Life — Rev. Pete Sferle • 2 Peter 1:3-4",
        "1/11/26 —  11:00 am Sunday morning service - God Gives Us Everything To Live A Godly Life — Rev. Pete Sferle • 2 Peter 1:3-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-01-12 00:00:00",
    ),  # youtube:5aeb54270f19
    (
        "4b0e6635-0eb5-58e1-bb52-14edfdcf8f3b",
        "Hear My Song Lord • Justin Noah",
        "1/11/26 —  11:00 am Sunday morning service - God Gives Us Everything To Live A Godly Life — Rev. Pete Sferle • 2 Peter 1:3-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-01-12 00:00:00",
    ),  # youtube:14edfdcf8f3b
    (
        "c4ce6334-0ab7-5824-a523-cbd4e8fb396e",
        "Grace and Peace be Multiplied to You! — Rev. Pete Sferle • 2 Peter 1:1-2",
        "1/4/26 — 11:00 am Sunday morning service - Grace and Peace be Multiplied to You! — Rev. Pete Sferle • 2 Peter 1:1-2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-01-10 00:00:00",
    ),  # youtube:cbd4e8fb396e
    (
        "2b2aa07e-58b9-5aac-ab77-0c549f25a639",
        "James Budean 12/28/2025",
        "Trinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nhttps://youtu.be/f0FPPR0LAWs\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-01-03 00:00:00",
    ),  # youtube:0c549f25a639
    (
        "847f9f23-2758-57dc-bf5b-6804b3120ed6",
        "Make Room by Mark Hall and Matt Maher",
        "Trinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A\n\nhttps://youtu.be/f0FPPR0LAWs The Wise Men — Bro Sorin Filimon • Matthew 2:1-12",
        "00000000-0000-0000-0000-000000000000",
        "2026-01-03 00:00:00",
    ),  # youtube:6804b3120ed6
    (
        "964ebb54-b6f4-5a4c-ad60-f760a0406562",
        "The Wise Men — Bro. Sorin Filimon • Matthew 2:1-12",
        "12/28/25 — 11:00 am Sunday morning service - The Wise Men — Bro. Sorin Filimon • Matthew 2:1-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2026-01-03 00:00:00",
    ),  # youtube:f760a0406562
    (
        "a65bb901-7af9-5ace-aa48-a04d420275ad",
        "Anticipating Our Lord''s Soon Return — Rev. Jeffery Downey • Acts 1:9-11",
        "Sunday Morning 11:00 am December 21, 2025 • Anticipating Our Lord''s Soon Return — Rev. Jeffery Downey • Acts 1:9-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\n\nCCLI Streaming license #20833650 A+",
        "00000000-0000-0000-0000-000000000000",
        "2025-12-22 00:00:00",
    ),  # youtube:a04d420275ad
    (
        "bd52c4c9-821f-555b-9ef1-1e9076de46a7",
        "Christmas Candle Light program 2025",
        "Christmas / Candle Light program 12/14/2025\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\n\nCCLI Streaming license #20833650 A+",
        "00000000-0000-0000-0000-000000000000",
        "2025-12-16 00:00:00",
    ),  # youtube:1e9076de46a7
    (
        "5e101b94-99a8-56de-9a48-ce3d2afdd632",
        "Joseph - An Example Of Obedience — Bro. Sorin Filimon • Matthew 1:24; 2:12, Luke 1:38; 2:15",
        "Chanukah begins • 12/14/25 —  11:00 am Sunday morning service - Joseph - An Example Of Obedience — Bro. Sorin Filimon • Matthew 1:24; 2:12, Luke 1:38; 2:15 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-12-15 00:00:00",
    ),  # youtube:ce3d2afdd632
    (
        "976ca1e3-791b-5cc6-91c9-622139f7c5e8",
        "The Lord Is My Shepherd— Bro. Noah Mocan • Psalm 23",
        "12/7/25 —  5:00 pm Sunday evening service - The Lord Is My Shepherd — Bro. Noah Mocan • Psalm 23\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-12-10 00:00:00",
    ),  # youtube:622139f7c5e8
    (
        "ccf40be1-b1a7-5553-bcc3-5ebdd6701dcb",
        "Godliness with Contentment is Great Gain — Rev. John Baros • 1 Timothy 6:1-12",
        "11/30/25 —  11:00 am Sunday morning service - Godliness with Contentment is Great Gain — Rev. John Baros (Medford, OR)• 1 Timothy 6:1-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-12-03 00:00:00",
    ),  # youtube:5ebdd6701dcb
    (
        "1ce93c74-7b6f-5681-b181-2b390a314266",
        "Thanksgiving — Bro Sorin Filimon • Colossians 3:15-17",
        "11/23/25 —  11:00 am Sunday morning service - Thanksgiving — Bro Sorin Filimon • Colossians 3:15-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-11-27 00:00:00",
    ),  # youtube:2b390a314266
    (
        "8b62f7f7-5a6b-5a51-b937-b88a208e0a58",
        "Bro. Harvey Knight Memorial  Service",
        "11/22/25 —  1:00 pm Saturday  — Bro. Harvey Knight Memorial  Service\nTrinity Apostolic Faith Church, 7842 Elmont Ave. Elverta, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-11-26 00:00:00",
    ),  # youtube:b88a208e0a58
    (
        "96d48277-0ae2-5347-992b-eb034b3ad86f",
        "Who Is God — Bro. Noah Mocan • Exodus 3:13-14",
        "11/16/25 —  5:00 pm Sunday evening youth service - Who Is God — Bro. Noah Mocan • Exodus 3:13-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-11-23 00:00:00",
    ),  # youtube:eb034b3ad86f
    (
        "6d82f437-640f-5085-93eb-50b7f26c2e64",
        "Daniel - Conceal Until The End - When Travel And Knowledge Shall Be Increased — Rev. Pete Sferle...",
        "11/16/25 —  11:00 am Sunday morning service - Daniel - Conceal Until The End - When Travel And Knowledge Shall Be Increased — Rev. Pete Sferle • Daniel 12:4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-11-17 00:00:00",
    ),  # youtube:50b7f26c2e64
    (
        "2226354c-c8bb-5df3-91d3-fc1edafc85cf",
        "A Double-Minded Man is Unstable in All His Ways — Bro. Sorin Filimon • James -1:6-8",
        "11/9/25 —  5:00 pm Sunday evening service  - A Double-Minded Man is Unstable in All His Ways — Bro. Sorin Filimon • James -1:6-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or  email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-11-12 00:00:00",
    ),  # youtube:fc1edafc85cf
    (
        "34ac0e08-c60c-5e26-8b9e-50afab95e61b",
        "Three More Signs That Point To Jesus'' Soon Return: Deceivers, Scoffers, And Lawlessness — Rev . ...",
        "11/9/25 —  11:00 am Sunday morning service - Three More Signs That Point To Jesus'' Soon Return: Deceivers, Scoffers, And Lawlessness — Rev . Pete Sferle • Matthew 24: 4-5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-11-10 00:00:00",
    ),  # youtube:50afab95e61b
    (
        "7918779e-516e-5a7d-8578-6308a5389bc5",
        "The First Rain And The Latter Rain — Rev. Pete Sferle • Deuteronomy 11:10-14",
        "11/2/25 —  5:00 pm Sunday evening service -The First Rain And The Latter Rain — Rev. Pete Sferle • Deuteronomy 11:10-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-11-08 00:00:00",
    ),  # youtube:6308a5389bc5
    (
        "63086f51-be20-54d5-b582-e0487371886e",
        "Spiritual Warfare — Rev. Mark Worthington •  Ephesians 6:10-19",
        "11/2/25 —  11:00 am Sunday morning service - Spiritual Warfare — Rev. Mark Worthington •  Ephesians 6:10-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-11-08 00:00:00",
    ),  # youtube:e0487371886e
    (
        "3f1e075e-c7f1-5097-985f-4219ba211e5b",
        "Baby Dedication › Mark 10:13-16 • Except the Lord Build a House — Rev. Pete Sferle • Psalm 127: 1-5",
        "10/26/25 —  11:00 am Sunday morning service - Baby Dedication › Mark 10:13-16 • Except the Lord Build a House — Rev. Pete Sferle • Psalm 127: 1-5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-26 00:00:00",
    ),  # youtube:4219ba211e5b
    (
        "6a931e7b-7e4a-51ae-84a6-74a63e697c8e",
        "Called & Enabled — Bro. Noah Mocan — Isaiah 6:5-8",
        "10/19/25 —  5:00 pm Sunday evening Youth Service • Called & Enabled — Bro. Noah Mocan — Isaiah 6:5-8 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org  email: pete@sferle.com \nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-20 00:00:00",
    ),  # youtube:74a63e697c8e
    (
        "380146f9-d00a-5fdf-bcae-3ef4171f10e5",
        "\"Israel\" The Sign Of Jesus''s Soon Return — Rev. Pete Sferle • Matthew 24:1-2",
        "10/19/25 —  11:00 am Sunday morning service - \"Israel\" The Sign Of Jesus''s Soon Return — Rev. Pete Sferle • Matthew 24:1-2 » Scripture Reading – Matthew 24:33-39 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-19 00:00:00",
    ),  # youtube:3ef4171f10e5
    (
        "75a0eecb-a574-5252-a0d5-24e1ce7deeed",
        "The Armor Of God — Bro. Noah Mocan • Ephesians 6:10-20",
        "10/12/25 —  5:00 pm Sunday evening service  The Armor Of God — Bro. Noah Mocan • Ephesians 6:10-20\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-18 00:00:00",
    ),  # youtube:24e1ce7deeed
    (
        "0165369d-d609-5e57-b6c9-3fb6f5c7c355",
        "Understanding The Real Battle — Rev. Mark Worthington • 1 Samuel 17:1-50",
        "10/12/25 —  11:00 am Sunday morning service - Understanding The Real Battle — Rev. Mark Worthington • 1 Samuel 17:1-50\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-13 00:00:00",
    ),  # youtube:3fb6f5c7c355
    (
        "1b131820-22bb-5bf3-a944-523bbd6fca3b",
        "Marvelous are thy works — Bro. Sorin Filimon  • Rev 15:1-4",
        "10/5/25 —  5:00 pm Sunday evening service - Marvelous are thy works — Bro. Sorin Filimon  • Rev 15:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-12 00:00:00",
    ),  # youtube:523bbd6fca3b
    (
        "c7e70775-cd20-556a-a6c1-6d2b979b552b",
        "God''s Grace Is More Than Enough — Rev. Pete Sferle • 2 Corinthians 12:9-11",
        "10/5/25 —  11:00 am Sunday morning service - God''s Grace Is More Than Enough — Rev. Pete Sferle • 2 Corinthians 12:9-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-11 00:00:00",
    ),  # youtube:6d2b979b552b
    (
        "ed4640a1-bb37-5b70-b9ca-1bf529ea1ffe",
        "Sis. Brenda Bishop Memorial Service 1955—2025",
        "10/4/25 —  11:00 am Saturday  Sis. Brenda Bishop Memorial Service\nTrinity Apostolic Faith Church, Richmond, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-09 00:00:00",
    ),  # youtube:1bf529ea1ffe
    (
        "8b711cc9-95b2-515d-b575-13579700632a",
        "Rooted And Grounded In Love — Rev. Nick Segres Jr. • Ephesians 3:14-21",
        "9/28/25 —  5:00 pm Sunday evening service -  Rooted And Grounded In Love — Rev. Nick Segres Jr. • Ephesians 3:14-21 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-05 00:00:00",
    ),  # youtube:13579700632a
    (
        "5276b50c-3506-51cc-8c61-b7f4327ded1d",
        "Rooted And Grounded In Love — Rev. Nick Segres Jr. • Ephesians 3:14-21",
        "9/28/25 —  11:00 am Sunday morning service -  Rooted And Grounded In Love — Rev. Nick Segres Jr. • Ephesians 3:14-21 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-10-05 00:00:00",
    ),  # youtube:b7f4327ded1d
    (
        "79f03b5b-4aed-53cc-ae12-f9797fbaa431",
        "Youth service -   Bro. Sola Akindele  — Rooted And Grounded In Love",
        "9/27/25 —  6:00 pm Saturday youth service -   Bro. Sola Akindele  — Rooted And Grounded In Love — \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-09-28 00:00:00",
    ),  # youtube:f9797fbaa431
    (
        "d45209a8-9607-5571-9fb4-80791a9ee7b5",
        "Bro. Sola Akindele • Rooted And Grounded In Love",
        "9/27/2025 10:30 am Saturday morning devotional — Bro. Sola Akindele • Rooted And Grounded In Love\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-09-28 00:00:00",
    ),  # youtube:80791a9ee7b5
    (
        "29908f03-67cd-52b3-80a7-94709a09a522",
        "Rooted And Grounded In Love — Rev. Nick Segres Jr. • Ephesians 3:14-21",
        "9/26/2025 —  8:00 pm Friday evening service - Rooted And Grounded In Love — Rev. Nick Segres Jr. • Ephesians 3:14-21 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-09-27 00:00:00",
    ),  # youtube:94709a09a522
    (
        "05e91e0d-90c2-5c1e-9b44-1587b322dea2",
        "Christ''s Supremacy And Sufficiency — Bro. Noah Mocan • Colossians 1:14-16, 2:9-10, 3:17",
        "9/21/25 —  11:00 am Sunday morning youth service - Christ''s Supremacy And Sufficiency — Bro. Noah Mocan • Colossians 1:14-16, 2:9-10, 3:17 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-09-26 00:00:00",
    ),  # youtube:1587b322dea2
    (
        "d32f48fb-f43f-5c31-8b94-fae595855899",
        "Fight the Good Fight of Faith — Bro.  Sorin Filimon •  1 Timothy 6:11-12",
        "9/14/2025 5:00 pm Sunday  evening - Fight the Good Fight of Faith — Bro.  Sorin Filimon •  1 Timothy 6:11-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-09-16 00:00:00",
    ),  # youtube:fae595855899
    (
        "6504983a-1156-5ddf-8988-a8177db3b420",
        "A Sermon To Die For — Rev. Mark Worthington • Acts 20:6-12",
        "9/14/25 —  11:00 am Sunday morning service -  A Sermon To Die For — Rev. Mark Worthington • Acts 20:6-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-09-14 00:00:00",
    ),  # youtube:a8177db3b420
    (
        "9c88da49-b554-5aea-a69e-43307a411857",
        "A Tree Planted By The River — Bro. Sorin Filimon • Psalm 1:3",
        "9/7/2025 5:00 pm Sunday  evening A Tree Planted By The River — Bro. Sorin Filimon • Psalm 1:3\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-09-08 00:00:00",
    ),  # youtube:43307a411857
    (
        "34b4f310-09e3-5698-aa89-375c619e62d0",
        "The Pretribulation Rapture — Rev. Pete Sferle • 2 Thessalonians 2:1-17",
        "9/7/25 —  11:00 am Sunday morning service -  The Pretribulation Rapture — Rev. Pete Sferle • 2 Thessalonians 2:1-17 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-09-07 00:00:00",
    ),  # youtube:375c619e62d0
    (
        "2a7f3b7f-9140-5eca-8051-98959a25fbf0",
        "Bringing Our Children To Jesus — Rev. Pete Sferle • Mark 10:13-16",
        "8/31/25 —  11:00 am Sunday morning service - Bringing Our Children To Jesus — Rev. Pete Sferle • Mark 10:13-16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-09-03 00:00:00",
    ),  # youtube:98959a25fbf0
    (
        "2f2425a8-1e35-55eb-ac82-4e7c5a0c6b23",
        "What Have You Come to See? — Bro. Sorin Filimon • Matthew 11:7",
        "8/24/25 —  5:00 pm Sunday evening service - What Have You Come to See? — Bro. Sorin Filimon • Matthew 11:7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-08-29 00:00:00",
    ),  # youtube:4e7c5a0c6b23
    (
        "0bdfb492-fcb9-5b26-bd22-31d7348e0a54",
        "A Courageous Heart — Rev.  Mark Worthington • Joshua 1:1-9",
        "8/24/25 —  11:00 am Sunday morning service - A Courageous Heart — Rev.  Mark Worthington • Joshua 1:1-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-08-24 00:00:00",
    ),  # youtube:31d7348e0a54
    (
        "599132eb-6be8-58a0-a90d-e65bf19a8e2a",
        "Be Ye Ready — Rev. Pete Sferle • 1 Thessalonians 4:13-18",
        "8/17/25 11:00 am Sunday morning service Be Ye Ready — Rev. Pete Sferle • 1 Thessalonians 4:13-18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-08-18 00:00:00",
    ),  # youtube:e65bf19a8e2a
    (
        "29ea2900-aa5f-5b5a-aec7-7a46519ed02a",
        "Follow The Instructions — Bro. Noah Mocan • 2 Timothy 3:14-17",
        "8/17/2025 2:00 pm Sunday afternoon youth service Follow The Instructions — Bro. Noah Mocan • 2 Timothy 3:14-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-08-18 00:00:00",
    ),  # youtube:7a46519ed02a
    (
        "41ba2edc-644b-5e37-8958-313e183d8bcb",
        "Where Are The Spiritual Potholes? Know Your Enemy - Rev. Mark Worthington • Luke 10:20",
        "8/10/25 —  5:00 pm Sunday evening service - Where Are The Spiritual Potholes? Know Your Enemy\xa0- Rev. Mark Worthington • Luke 10:20\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-08-15 00:00:00",
    ),  # youtube:313e183d8bcb
    (
        "5a45a2ab-572c-5855-950f-da81fe1fa875",
        "You Are Fearfully and Wonderfully Made — Rev. Pete Sferle • Psalms 139:14-18",
        "8/10/25 —  11:00 am Sunday morning service - You Are Fearfully and Wonderfully Made — Rev. Pete Sferle • Psalms 139:14-18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-08-10 00:00:00",
    ),  # youtube:da81fe1fa875
    (
        "7cb4dfe8-e95d-5959-9226-85a7238fc16d",
        "Biblical Prayer — Bro. Noah Mocan • Matthew 6:5-13",
        "8/03/2025 5:00 pm Sunday evening  —  Biblical Prayer — Bro. Noah Mocan • Matthew 6:5-13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-08-07 00:00:00",
    ),  # youtube:85a7238fc16d
    (
        "067e8738-30fd-5d23-a81c-2547471d6a4a",
        "How Do We seek God — Bro. Sorin Filimon • Deuteronomy 4:29-30",
        "8/3/25 —  11:00 am Sunday morning service - How Do We seek God — Bro. Sorin Filimon • Deuteronomy 4:29-30\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-08-03 00:00:00",
    ),  # youtube:2547471d6a4a
    (
        "9a4a1a11-2ca7-5d72-be1d-f4517074b6b9",
        "Palm Branches & Willow Branches — Rev. Mark Worthington • Leviticus 23:40",
        "7/27/2025 11:00 am Sunday morning  —  Palm Branches & Willow Branches — Rev. Mark Worthington • Leviticus 23:40\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-08-02 00:00:00",
    ),  # youtube:f4517074b6b9
    (
        "43be8242-1a2b-539e-a3e5-9cab740babbf",
        "Seeking The Lord Is Like Seeking For the Monalisa —  Bro. Sorin Filimon • Matthew 7:7-11",
        "7/20/2025 11:00 am Sunday morning — Seeking The Lord Is Like Seeking For the Monalisa —  Bro. Sorin Filimon • Matthew 7:7-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-07-23 00:00:00",
    ),  # youtube:9cab740babbf
    (
        "f38ec1a2-56a7-522d-946b-c60226993941",
        "Seek The Lord In Righteousness — Rev. Mark Worthington • 2 Chronicles 7:1-3",
        "6/22/2025 11:00 am Sunday morning  —  Seek The Lord In Righteousness — Rev. Mark Worthington • 2 Chronicles 7:1-3\n\nTrinity Apostolic Faith Church, Sacramento County, California\n\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-06-27 00:00:00",
    ),  # youtube:c60226993941
    (
        "d114d4d2-a1eb-564e-8613-4f8579dc2491",
        "What Is Truth — Bro. Sola Omolayo • Daniel 2: 47",
        "6/15/2025 —  11:00 am Sunday morning service - What Is Truth — Bro. Sola Omolayo • Daniel 2: 47\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-06-15 00:00:00",
    ),  # youtube:4f8579dc2491
    (
        "c4391bff-ba0c-5644-8a95-e34b61a93a9c",
        "Stand In God''s Grace — Rev. Pete Sferle • 1 Peter 5:12-14",
        "6/8/2025 11:00 am Sunday morning — Stand In God''s Grace — Rev. Pete Sferle • 1 Peter 5:12-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-06-09 00:00:00",
    ),  # youtube:e34b61a93a9c
    (
        "5696b4a2-ceba-5ad1-aef3-453593163b38",
        "From Good To Better  — Bro. Noah Mocan • 2 Corinthians 3:6-9",
        "6/1/25 —  5:00 pm Sunday evening service - From Good To Better  — Bro. Noah Mocan • 2 Corinthians 3:6-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-06-04 00:00:00",
    ),  # youtube:453593163b38
    (
        "653aed0f-406c-5f2b-8d72-424524e1dcfe",
        "Resisting The Devil! Successfully Like Jesus Did —  Bro. Pete Sferle • 1 Peter 5:8-11",
        "6/1/2025 11:00 am Sunday morning Resisting The Devil! Successfully Like Jesus Did —  Bro. Pete Sferle • 1 Peter 5:8-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-06-01 00:00:00",
    ),  # youtube:424524e1dcfe
    (
        "0e601663-7192-5a5a-91d8-3dc2c9a3b04d",
        "A Caring God To Cast Your Cares Upon — Rev. Pete Sferle • 1 Peter 5:7",
        "5/25/2025 11:00 am Sunday morning — A Caring God To Cast Your Cares Upon — Rev. Pete Sferle • 1 Peter 5:7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-05-25 00:00:00",
    ),  # youtube:3dc2c9a3b04d
    (
        "dd539277-0b01-569e-a72d-b8e39986ac49",
        "Who Can Find A Virtues Woman? — Rev. Pete Sferle • Proverbs 31:10-31",
        "5/11/2025 11:00 am Sunday morning —  Who Can Find A Virtues Woman? — Rev. Pete Sferle • Proverbs 31:10-31\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-05-11 00:00:00",
    ),  # youtube:b8e39986ac49
    (
        "3862c21b-8b7e-5f58-a46a-5e1dcb1133de",
        "Divine Direction — Rev. Mark Worthington • Proverbs 3:3-5",
        "5/4/2025 —  5:00 pm Sunday evening service - Divine Direction — Rev. Mark Worthington • Proverbs 3:3-5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-05-10 00:00:00",
    ),  # youtube:5e1dcb1133de
    (
        "0d781c6f-d575-5cbb-b3b4-1f2e2910c8f0",
        "Be Clothed with Humility — Rev. Pete Sferle • 2 Peter 5:5-6",
        "5/4/2025 11:00 am Sunday morning service - Be Clothed with Humility — Rev. Pete Sferle • 2 Peter 5:5-6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-05-06 00:00:00",
    ),  # youtube:1f2e2910c8f0
    (
        "c6a45986-4583-5aed-9642-beaf07782d55",
        "Making Decisions Gods Way — Rev. Mark Worthington • Mark 16:15",
        "04/27/2025 — 5:00 pm Sunday evening service - Making Decisions Gods Way — Rev. Mark Worthington • Mark 16:15\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-05-02 00:00:00",
    ),  # youtube:beaf07782d55
    (
        "e461ec89-2407-5ffa-a1f1-9cd0fb30317d",
        "Exhortation and Encouragement from 1 Peter 5:1-4 — Rev. Pete Sferle",
        "4/27/2025 11:00 am Sunday morning — Exhortation and Encouragement from 1 Peter 5:1-4 — Rev. Pete Sferle \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-04-27 00:00:00",
    ),  # youtube:9cd0fb30317d
    (
        "6e5da48c-92bb-5fa2-b7de-34c22608a541",
        "Remember The Truth: God Cares  — Bro. Noah Mocan • Psalm 22",
        "04/20/2025 — Sunday evening service - Remember The Truth: God Cares  — Bro. Noah Mocan • Psalm 22\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-04-27 00:00:00",
    ),  # youtube:34c22608a541
    (
        "5fcdf5e3-b504-539e-98ff-536a4d646dd1",
        "Easter Sunday — Rev. Pete Sferle • Luke 24:1-12",
        "4/20/2025 11:00 am morning service - Easter Sunday — Rev. Pete Sferle • Luke 24:1-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-04-20 00:00:00",
    ),  # youtube:536a4d646dd1
    (
        "d07e57a5-0494-5692-8668-88e8ecbcbd55",
        "Good Friday — Rev. Mark Worthington • Hebrews 12:2",
        "04/18/2025 7:00 pm\xa0— Good Friday — Rev. Mark Worthington • Hebrews 12:2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-04-19 00:00:00",
    ),  # youtube:88e8ecbcbd55
    (
        "f4552ac8-cb86-5206-bb54-154cf83c2d97",
        "God Deeply Cares — Bro. Noah Mocan • John 3:16",
        "04/13/2025 — Sunday evening youth service -  God Deeply Cares — Bro. Noah Mocan • John 3:16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-04-14 00:00:00",
    ),  # youtube:154cf83c2d97
    (
        "0894e970-a5c8-5d5e-aa12-fe17579856ef",
        "Palm Sunday — Rev. Pete Sferle • Luke 19:28-40",
        "4/13/2025 11:00 am Palm Sunday morning — Rev. Pete Sferle • Luke 19:28-40 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-04-13 00:00:00",
    ),  # youtube:fe17579856ef
    (
        "2fc20ec0-35d5-51dd-b902-20522c2a8f78",
        "Meekness — Rev. Mark Worthington • Galatians 5:16-25",
        "4/6/2025 11:00 am Sunday morning service • Meekness — Rev. Mark Worthington • Galatians 5:16-25\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-04-07 00:00:00",
    ),  # youtube:20522c2a8f78
    (
        "835e7aee-3e19-52bb-8e71-049b52eaa4e6",
        "Think It Not Strange — Rev. Pete Sferle • 1 Peter 4:12-19",
        "3/30/2025 11:00 am Sunday morning service - Think It Not Strange — Rev. Pete Sferle • 1 Peter 4:12-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-03-31 00:00:00",
    ),  # youtube:049b52eaa4e6
    (
        "f470c249-7307-5af0-8a7a-e9f5d856181d",
        "The End Of All Things Is At Hand So Serve God And Others With The Gift He Has Given You — Rev Pe...",
        "3/23/2025 11:00 am Sunday morning service • The End Of All Things Is At Hand So Serve God And Others With The Gift He Has Given You — Rev Pete Sferle - 1 Peter 4:7-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-03-29 00:00:00",
    ),  # youtube:e9f5d856181d
    (
        "1649fc5b-61f2-5501-b2dd-09ecf49e1ef3",
        "The Testimony of Creation — Rev. Mark Worthington",
        "03/23/2025 — Sunday evening service - The Testimony of Creation — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-03-25 00:00:00",
    ),  # youtube:09ecf49e1ef3
    (
        "f263632e-a870-5892-82a9-d2e6d1f596ca",
        "Bringing Our Questions Before God — Bro. Noah Mocan • Matthew 7:7-11",
        "Bringing Our Questions Before God — Bro. Noah Mocan • Matthew 7:7-11\n 03/16/2025 — Sunday evening Youth service \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-03-22 00:00:00",
    ),  # youtube:d2e6d1f596ca
    (
        "61091ade-c201-5899-8986-181ae0f24b46",
        "The End Is At Hand, So Fervently Love One Another — Rev. Pete Sferle • 1 Peter 4:7-8",
        "3/16/2025 11:00 am Sunday morning service - The End Is At Hand, So Fervently Love One Another — Rev. Pete Sferle • 1 Peter 4:7-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-03-17 00:00:00",
    ),  # youtube:181ae0f24b46
    (
        "9705e94b-d061-5b49-b5a4-072be889366c",
        "Reading The Signs Of The Times — Rev. Mark Worthington • Matthew 16: 1-4",
        "3/9/2025 11:00 am Sunday morning service Reading The Signs Of The Times — Rev. Mark Worthington • Matthew 16: 1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-03-10 00:00:00",
    ),  # youtube:072be889366c
    (
        "72a0e5e0-d79a-503e-8ef2-47be1fa4e47b",
        "The End is Near, Be Ready, Watching and Praying — Rev. Pete Sferle • 1 Peter 4:7",
        "3/2/2025 11:00 am Sunday morning — The End is Near, Be Ready, Watching and Praying — Rev. Pete Sferle • 1 Peter 4:7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-03-03 00:00:00",
    ),  # youtube:47be1fa4e47b
    (
        "12fae71f-5c75-5911-9e1d-c6649925a2c3",
        "Are we a Thermometer or Thermostat? — Bro. Mark Worthington — Revelation 3:14-22",
        "Are we a Thermometer or Thermostat? • Bro. Mark Worthington — Revelation 3:14-22\n2/23/2025 11:00 am Sunday morning service\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-02-23 00:00:00",
    ),  # youtube:c6649925a2c3
    (
        "a1d1bb18-b47f-5f5a-b31c-1dbca3425bdb",
        "Victory In Jesus — Bro. Noah Mocan • 1 Corinthians 15:50 - 57",
        "Victory In Jesus — Bro. Noah Mocan • 1 Corinthians 15:50 - 57 — Youth Service\n 02/09/2025 — Sunday afternoon Youth service • • • after the potluck\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-02-17 00:00:00",
    ),  # youtube:1dbca3425bdb
    (
        "e9c249e6-c0d8-5d9b-a5e0-4d04058ac977",
        "Deny Yourself and Follow Jesus — Bro. Sorin Filimon • Matthew 16:24-28",
        "11:00 am Sunday 2/9/2025 • Deny Yourself and Follow Jesus — Bro. Sorin Filimon • Matthew 16:24-28\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-02-16 00:00:00",
    ),  # youtube:4d04058ac977
    (
        "99435559-e1e9-5872-ab19-28ae77a69713",
        "Ordinance Service Rev. Mark Worthington, Bro. Sorin Filimon",
        "2/2/2025 Sunday evening service 5:00 pm - Ordinance\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-02-16 00:00:00",
    ),  # youtube:28ae77a69713
    (
        "ada6f2e2-5a69-53a7-be07-c59f8f60389b",
        "The Good Shepherd — Bro. Sorin Filimon • John 10:22-29",
        "11:00 am Sunday 2/2/2025 - The Good Sheep — Bro. Sorin Filimon • John 10:22-29\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-02-03 00:00:00",
    ),  # youtube:c59f8f60389b
    (
        "e5afa805-e004-5bed-a385-c0f123198dcc",
        "From Glory To Glory • Bro. Sorin Filimon — 2 Corinthians 3:18",
        "11:00 am Sunday 1/26/2025 • From Glory To Glory • Bro. Sorin Filimon — 2 Corinthians 3:18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-01-31 00:00:00",
    ),  # youtube:c0f123198dcc
    (
        "74247510-2f58-591c-aaa9-2a923ea6c7f7",
        "The Object Of Our Faith — Bro. Noah Mocan • Hebrews 11:1, 6-8",
        "1/26/2025 Sunday evening youth service 5:00 pm - The Object Of Our Faith — Bro. Noah Mocan • Hebrews 11:1, 6-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-01-28 00:00:00",
    ),  # youtube:2a923ea6c7f7
    (
        "d3990322-c1b0-5403-b7cb-f37f88570db8",
        "They Think It Strange That Ye Run Not With Them — Rev. Pete Sferle • 1 Peter 4:1-6",
        "11:00 am Sunday 1/19/2025 • They Think It Strange That Ye Run Not With Them — Rev. Pete Sferle • 1 Peter 4:1-6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-01-20 00:00:00",
    ),  # youtube:f37f88570db8
    (
        "b2f1effa-5db8-5394-8598-f7bc638a7d58",
        "An Old Challenge For A New Year • Rev. Mark Worthington — Colossians 3:1-4",
        "1/12/2025 Sunday evening service 5:00 pm - An Old Challenge For A New Year • Rev. Mark Worthington — Colossians 3:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-01-13 00:00:00",
    ),  # youtube:f7bc638a7d58
    (
        "a29c1996-af31-5452-a453-6b864695fe52",
        "When You Suffer  For Christ''s Sake • Rev. Pete Sferle — 1 Peter 3:13-17",
        "Sunday Morning 11:00 am January 12, 2025  -  • Rev. Pete Sferle — 1 Peter 3:13-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-01-12 00:00:00",
    ),  # youtube:6b864695fe52
    (
        "61b9aa35-b7d9-5c61-acdb-692f1022a2f7",
        "Quench Not The Spirit — Bro. Sorin Filimon • I Thessalonians 5:19",
        "1/5/2025 Sunday evening service 5:00 pm - Quench Not The Spirit — Bro. Sorin Filimon • I Thessalonians 5:19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-01-11 00:00:00",
    ),  # youtube:692f1022a2f7
    (
        "cc0670b3-45bc-5ec5-8ecf-b3f9911950eb",
        "Be Connected To The Vine This Coming Year — Bro. Toinda Gono • John 15:1-8",
        "11:00 am Sunday 1/5/2025 • Be Connected To The Vine This Coming Year — Bro. Toinda Gono • John 15:1-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2025-01-06 00:00:00",
    ),  # youtube:b3f9911950eb
    (
        "9cf4c71e-b9a8-5705-98fd-1612d16bbf52",
        "Living Our Lives With Trust in God and Honoring Him in Humility and Obedience.   •  Rev. Pete Sf...",
        "Sunday Morning 11:00 am December 29, 2024  - Living Our Lives With Trust in God and Honoring Him in Humility and Obedience.  •  Rev. Pete Sferle — Proverbs 3:1-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-12-30 00:00:00",
    ),  # youtube:1612d16bbf52
    (
        "e392c367-3667-5d56-a15f-a50ebb3459b6",
        "Candlelight service",
        "12/22/2024 Sunday evening service 5:00 pm - Candlelight service\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-12-23 00:00:00",
    ),  # youtube:a50ebb3459b6
    (
        "f963cfb6-0a1f-5a12-a3bc-5aac11fcc3c2",
        "Spiritual Wish List — Bro. Florin Baros • Like 1:26-38",
        "11:00 am Sunday 12/22/2024 • Spiritual Wish List — Bro. Florin Baros • Like 1:26-38\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-12-23 00:00:00",
    ),  # youtube:5aac11fcc3c2
    (
        "adacf544-121e-59f4-9de6-2963c9b8bebf",
        "Christmas Concert",
        "Sunday evening 12/15/2024 5:00 pm - Christmas Concert\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-12-16 00:00:00",
    ),  # youtube:2963c9b8bebf
    (
        "18521ab1-cc6b-5c24-bdd8-bfd0ab91fe86",
        "Sunday Morning 11:00 am December 15, 2024 • Gabriel''s Conversation With Mary — Rev. Pete Sferle •...",
        "Sunday Morning 11:00 am December 15, 2024 • Gabriel''s Conversation With Mary — Rev. Pete Sferle • Luke 1: 26:38\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-12-16 00:00:00",
    ),  # youtube:bfd0ab91fe86
    (
        "7e90791e-f7db-546e-9456-6755c85210be",
        "Christmas Is For Thanks-Giving — Rev. Mark Worthington • Philippians 4:6-7",
        "Sunday evening service 5:00 pm - Christmas Is For Thanks-Giving — Rev. Mark Worthington • Philippians 4:6-7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-12-14 00:00:00",
    ),  # youtube:6755c85210be
    (
        "9af0ac0c-901c-5a7b-a662-749e9229825b",
        "Treatment of Our Christian Brother and Sisters — Rev. Pete Sferle • 1 Peter 3:8-13",
        "11:00 am Sunday 12/8/2024 • Treatment of Our Christian Brother and Sisters — Rev. Pete Sferle • 1 Peter 3:8-13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-12-09 00:00:00",
    ),  # youtube:749e9229825b
    (
        "f35440d8-4de0-5719-a3db-cddc750f5045",
        "Unto Us a Son Is Given — Bro. Sorin Filimon • Isaiah 9:1-7",
        "Sunday Morning 11:00 am December 17, 2024 • Unto Us a Son Is Given — Bro. Sorin Filimon • Isaiah 9:1-7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-12-01 00:00:00",
    ),  # youtube:cddc750f5045
    (
        "a8a65f20-e88f-57f3-a44a-11c04cba5e22",
        "Thanksgiving • Rev. Pete Sferle — Psalms 34:1-3",
        "11:00 am Sunday 11/24/2024 • Thanksgiving • Rev. Pete Sferle — Psalms 34:1-3\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-11-25 00:00:00",
    ),  # youtube:11c04cba5e22
    (
        "c11653ad-ec42-5c88-a847-2130598d734c",
        "Husbands - Rev.Pete Sferle — Ephesians 5:22-33",
        "Sunday Morning 11:00 am November 17, 2024 • Husbands - Rev.Pete Sferle — Ephesians 5:22-33\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-11-18 00:00:00",
    ),  # youtube:2130598d734c
    (
        "8f76ae30-79ba-50d1-8817-7e6f222f4bfb",
        "Lord, if thou wilt, thou canst make me clean. - Rev. Pete Sferle — Luke 5:12-14",
        "Sunday Morning 11:00 am November 10, 2024 •  Lord, if thou wilt, thou canst make me clean. - Rev. Pete Sferle — Luke 5:12-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-11-10 00:00:00",
    ),  # youtube:7e6f222f4bfb
    (
        "04388d24-80d7-54cf-92d1-4c3793efb18c",
        "This World Is Not My Home - Bro. Sorin Filimon — Hebrews 13:14",
        "Sunday evening 11/3/2024 5:00 pm - This World Is Not My Home - Bro. Sorin Filimon — Hebrews 13:14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-11-08 00:00:00",
    ),  # youtube:4c3793efb18c
    (
        "a3bfed05-de17-5307-944a-e64c758e243a",
        "Fear Not - Rev. Mark Worthington— Isaiah 41:10-13",
        "11:00 am Sunday 11/3/2024 • Fear Not - Rev. Mark Worthington— Isaiah 41:10-13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-11-04 00:00:00",
    ),  # youtube:e64c758e243a
    (
        "84969447-c615-5860-be09-91bc792bfb40",
        "Nothing Is Too Hard For The Lord - Bro. Sorin Filimon — Jeremiah 32:16-19",
        "Youth Service 5:00 pm Sunday evening 10/20/2024 • Nothing Is Too Hard For The Lord - Bro. Sorin Filimon — Jeremiah 32:16-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-10-28 00:00:00",
    ),  # youtube:91bc792bfb40
    (
        "56465e5e-b1e6-5219-89e7-26e5443f4cd0",
        "Be Not Ashamed - Rev. Mark Worthington— 2 Timothy 1:8-17",
        "Sunday Morning 11:00 am October 20, 2024 • Be Not Ashamed - Rev. Mark Worthington— 2 Timothy 1:8-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-10-21 00:00:00",
    ),  # youtube:26e5443f4cd0
    (
        "df470d85-7ec1-5abf-a07f-9e73a3dd7911",
        "Salvation is by Faith, Not by Works — Bro. Sorin Filimon - Galatians 2:15-21",
        "Sunday evening 10/13/2024 5:00 pm - Salvation is by Faith, Not by Works — Bro. Sorin Filimon - Galatians 2:15-21\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-10-16 00:00:00",
    ),  # youtube:9e73a3dd7911
    (
        "46219058-6cc7-5838-b805-a5de0e2a3bfe",
        "Instructions For Wives - Rev. Pete Sferle — 1 Peter 3:1-6",
        "11:00 am Sunday 10/13/2024 • Instructions For Wives - Rev. Pete Sferle — 1 Peter 3:1-6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-10-13 00:00:00",
    ),  # youtube:a5de0e2a3bfe
    (
        "5677aaa9-4c66-551c-9157-a4892130d096",
        "Pray Without Ceasing  — Rev. Mark Worthington - 1 Thessalonians 5:17",
        "Sunday evening 10/6/2024 5:00 pm -  Pray Without Ceasing  — Rev. Mark Worthington - 1 Thessalonians 5:17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-10-10 00:00:00",
    ),  # youtube:a4892130d096
    (
        "7d4fb33c-2d15-58eb-a032-e97eac619bf5",
        "The Goodness Of God — Bro. Sorin Filimon - Romans 2:1-4",
        "Sunday Morning 11:00 am  The Goodness Of God — Bro. Sorin Filimon - Romans 2:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-10-10 00:00:00",
    ),  # youtube:e97eac619bf5
    (
        "968560cd-b39e-5392-aba4-c557eaef71e0",
        "Facing The Giants In Your Life — Rev. John Baros - 1 Samuel 17:37",
        "September 2024 Special Meetings: Sunday Evening 5:00 pm\nFacing The Giants In Your Life — Rev. John Baros - 1 Samuel 17:37\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-10-06 00:00:00",
    ),  # youtube:c557eaef71e0
    (
        "1ecd303a-0c6b-5fda-99ed-e9635a16f3de",
        "Facing The Giants In Your Life — Rev. John Baros - 1 Samuel 17:37",
        "September 2024 Special Meetings: Sunday Morning 11:00 am\nFacing The Giants In Your Life — Rev. John Baros - 1 Samuel 17:37\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-10-02 00:00:00",
    ),  # youtube:e9635a16f3de
    (
        "107b3f97-882e-54c1-9402-e31afa723a2a",
        "2024 Special Meetings: Saturday Evening 6:00 pm Youth Service Facing The Giants In Your Life — B...",
        "September 2024 Special Meetings: Saturday Evening 6:00 pm Youth Service\nFacing The Giants In Your Life — Brother Sola • 1 Timothy 4:12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-09-29 00:00:00",
    ),  # youtube:e31afa723a2a
    (
        "9134f942-821f-5e14-a375-ccdbd9f8ba87",
        "Facing The Giants In Your Life — Rev. Pierre Hancock",
        "September 2024 Special Meetings: Saturday morning devotional 10:30 am\nFacing The Giants In Your Life — Rev. Pierre Hancock\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-09-28 00:00:00",
    ),  # youtube:ccdbd9f8ba87
    (
        "b4943f7f-36f9-5239-9d0d-f02d6513893b",
        "Facing The Giants In Your Life — Rev. John Baros - 1 Samuel 17:37",
        "September 2024 Special Meetings Friday Evening 8:00 pm\nFacing The Giants In Your Life — Rev. John Baros - 1 Samuel 17:37\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-09-28 00:00:00",
    ),  # youtube:f02d6513893b
    (
        "574c219b-073d-56c0-9cca-cd24cb4495f1",
        "Be The Best Influencer For God In Your Workplace — Rev. Pete Sferle • 1 Peter 2:18-25",
        "11:00 am Sunday 9/22/2024 •  Be The Best Influencer For God In Your Workplace — Rev. Pete Sferle • 1 Peter 2:18-25\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-09-22 00:00:00",
    ),  # youtube:cd24cb4495f1
    (
        "90902186-4db8-5954-9dfb-a63db3c3fc3a",
        "The Lord God is a Sun and Shield  — Bro. Sorin Filimon • Psalm 84:11",
        "Sunday evening 9/15/2024 5:00 pm - The Lord God is a Sun and Shield  — Bro. Sorin Filimon • Psalm 84:11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-09-22 00:00:00",
    ),  # youtube:a63db3c3fc3a
    (
        "ab652e26-d8d3-5865-82ab-49b84216dbff",
        "Called To Be  Model Citizens  — Rev. Pete Sferle • 1 Peter 2:13-17",
        "11:00 am Sunday 9/15/2024 • Called To Be  Model Citizens  — Rev. Pete Sferle • 1 Peter 2:13-17 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-09-21 00:00:00",
    ),  # youtube:49b84216dbff
    (
        "51e81765-b734-582d-a82a-2d4d15d52047",
        "Forgiveness Sets You Free — Bro. Sorin Filimon • Genesis 50:15-21, Ephesians 4:31-32",
        "11:00 am Sunday 9/8/2024 •  Forgiveness Sets You Free — Bro. Sorin Filimon • Genesis 50:15-21, Ephesians 4:31-32\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-09-09 00:00:00",
    ),  # youtube:2d4d15d52047
    (
        "1a51b62d-875f-511a-96e7-93805cc6a3b9",
        "Our Labor For The Lord — Rev. Pete Sferle • 1 Corinthians 5:58",
        "11:00 am Sunday 9/1/2024 • Our Labor For The Lord — Rev. Pete Sferle • 1 Corinthians 5:58\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-09-06 00:00:00",
    ),  # youtube:93805cc6a3b9
    (
        "371e2c3b-66d1-557f-ad57-1f4d85889eaa",
        "Touch The Lord; But, Not Just Any Way • Bro. Sorin Filimon — Mark 5:21-34",
        "5:00 pm Sunday evening 8/25/2024 •   Touch The Lord; But, Not Just Any Way • Bro. Sorin Filimon — Mark 5:21-34\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-09-05 00:00:00",
    ),  # youtube:1f4d85889eaa
    (
        "6e858033-215c-56e3-a98d-309a834fddb7",
        "God''s Blessing To A Privileged People — Rev. Pete Sferle • 1 Peter 2:9-10",
        "11:00 am Sunday 8/25/2024 • God''s Blessing To A Privileged People — Rev. Pete Sferle • 1 Peter 2:9-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-08-25 00:00:00",
    ),  # youtube:309a834fddb7
    (
        "dbe00208-395a-5037-bbac-a5c120c0f8a5",
        "08/18/2024 Night of Music",
        "5:00 pm Sunday evening 8/18/2024 •  Night of Music\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-08-25 00:00:00",
    ),  # youtube:a5c120c0f8a5
    (
        "5feb5bda-0675-535e-8f57-641d72de47b0",
        "Jesus Our Cornerstone — Rev. Pete Sferle • 1 Peter 2 1-10",
        "11:00 am Sunday 8/18/2024 •  Jesus Our Cornerstone — Rev. Pete Sferle • 1 Peter 2 1-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-08-18 00:00:00",
    ),  # youtube:641d72de47b0
    (
        "d3a55b0b-4ad0-59f2-8f10-663662088cc9",
        "The Word of God •  Bro. Sorin Filimon — Jeremiah 15:16",
        "5:00 pm Sunday evening 8/11/2024 •   Youth Service  — The Word of God •  Bro. Sorin Filimon — Jeremiah 15:16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-08-15 00:00:00",
    ),  # youtube:663662088cc9
    (
        "466394e0-145e-504a-911c-21e8d91dde34",
        "Walking on Eggs — Josh and Annika",
        "5:00 pm Sunday evening 8/11/2024 •   Youth Service  — Walking on Eggs — Josh and Annika •  \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-08-12 00:00:00",
    ),  # youtube:21e8d91dde34
    (
        "09b5dbb9-9902-52a5-b6ba-a9a71cb0bb08",
        "Attitude of Thanksgiving and a Life of Gratitude — Rev. Mark Worthington • Luke 17:11-19",
        "11:00 am Sunday morning 8/11/2024 •  Attitude of Thanksgiving and a Life of Gratitude — Rev. Mark Worthington • Luke 17:11-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-08-11 00:00:00",
    ),  # youtube:a9a71cb0bb08
    (
        "a20c0636-9c21-51e0-baf8-ef213b32953c",
        "Truth and Love — Bro. Sorin Filimon •   2 John 8",
        "5:00 pm Sunday evening 8/4/2024 • Truth and Love — Bro. Sorin Filimon •   2 John 8 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-08-05 00:00:00",
    ),  # youtube:ef213b32953c
    (
        "e828be1b-bb9a-5dd3-b2bd-c9d50e98ba37",
        "A Sincere Love One For Another — Rev. Pete Sferle • 1 Peter 1:22",
        "11:00 am Sunday 8/4/2024 • A Sincere Love One For Another — Rev. Pete Sferle • 1 Peter 1:22\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-08-04 00:00:00",
    ),  # youtube:c9d50e98ba37
    (
        "8029eec7-69e5-5a6b-be16-7d35caad70e0",
        "Be Strong, Do Not Fear — Bro. Sorin Filimon • Isaiah 35:1-7",
        "5:00 pm Sunday evening 7/28/2024 •   Be Strong, Do Not Fear — Bro. Sorin Filimon • Isaiah 35:1-7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-08-04 00:00:00",
    ),  # youtube:7d35caad70e0
    (
        "f26891dd-cbbb-546c-9ae1-4717f8e331e5",
        "I Bow My Knees — Rev.Mark Worthington • Ephesians 3:14-21",
        "11:00 am Sunday morning 7/28/2024 •  I Bow My Knees — Rev.Mark Worthington • Ephesians 3:14-21\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-07-28 00:00:00",
    ),  # youtube:4717f8e331e5
    (
        "1185e1dc-c9e4-5285-8c2d-b127f46bafd7",
        "Fishes of Men, Stay With Jesus  — Rev. Pierre Hancock, LA, CA — John 21:1-9",
        "11:00 am Sunday 7/21/2024 • Fishes of Men, Stay With Jesus  — Rev. Pierre Hancock, LA, CA — John 21:1-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-07-28 00:00:00",
    ),  # youtube:b127f46bafd7
    (
        "9fea01f4-55d4-55f4-b128-bd8f1d21a673",
        "Lay Aside Every Weight— Rev. Mark  Worthington • Hebrews 12:1-2",
        "11:00 am Sunday morning 6/23/2024 • Lay Aside Every Weight— Rev. Mark  Worthington • Hebrews 12:1-2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-06-27 00:00:00",
    ),  # youtube:bd8f1d21a673
    (
        "10467aed-9e8a-5233-9e91-64c4008015f7",
        "Finding Home — Rev.Mark Worthington • Hebrews 4:9-12",
        "5:00 pm Sunday evening 6/9/2024 •  Finding Home — Rev.Mark Worthington • Hebrews 4:9-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-06-15 00:00:00",
    ),  # youtube:64c4008015f7
    (
        "62371edb-ce3a-532c-8ea5-cec9c9500dcd",
        "We Are Called to be Holy in Times of Trial  — Rev. Pete Sferle • 1 Peter 1:13-16",
        "11:00 am Sunday morning 6/9/2024 • We Are Called to be Holy in Times of Trial  — Rev. Pete Sferle • 1 Peter 1:13-16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-06-09 00:00:00",
    ),  # youtube:cec9c9500dcd
    (
        "635218ab-04bd-5424-a4ad-8d646e3f33d5",
        "We''re Going to Make it, if we Keep Our Hand in His— Rev. Cliff Kasper • Jude 24",
        "5:00 pm Sunday evening 6/2/2024 •  We''re Going to Make it, if we Keep Our Hand in His— Rev. Cliff Kasper • Jude 24\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-06-07 00:00:00",
    ),  # youtube:8d646e3f33d5
    (
        "f763ee80-b18a-5f5f-ba53-9e531a4d48ef",
        "God Won''t Forget You — Rev. Cliff Kasper • Genesis 40:23",
        "11:00 am Sunday morning 6/2/2024 • God Won''t Forget You — Rev. Cliff Kasper • Genesis 40:23\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-06-02 00:00:00",
    ),  # youtube:9e531a4d48ef
    (
        "72915192-78e4-5445-b2fb-dab9b43ba8b6",
        "Be Strong and Courageous  — Rev. Mark Worthington • Psalm 18:30-32",
        "11:00 am Sunday morning 5/26/2024 • Be Strong and Courageous  — Rev. Mark Worthington •  Psalm 18:30-32 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-05-27 00:00:00",
    ),  # youtube:dab9b43ba8b6
    (
        "8f2390e8-1e8a-5235-bf1f-ba6260dcdd8d",
        "Pride Goeth Before Destruction, and an Haughty Spirit Before a Fall — Rev. Pete Sferle • Prov. 1...",
        "5:00 pm Sunday evening 5/19/2024 •  Pride Goeth Before Destruction, and an Haughty Spirit Before a Fall.— Rev. Pete Sferle • Prov. 16:18 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-05-26 00:00:00",
    ),  # youtube:ba6260dcdd8d
    (
        "73b7da1e-94cf-52f0-b760-8b21aa95f10d",
        "Pentecost Sunday: The Holy Ghost— Rev. Pete Sferle • Acts 1:4-8",
        "11:00 am Sunday morning 5/19/2024 • Pentecost Sunday: The Holy Ghost— Rev. Pete Sferle • Acts 1:4-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-05-26 00:00:00",
    ),  # youtube:8b21aa95f10d
    (
        "69738d9c-1354-5592-8c92-6e760a929961",
        "A Mother Named Hannah — Rev. Pete Sferle • 1 Samuel 1:26-28",
        "11:00 am Sunday 5/5/2024 • A Mother Named Hannah — Rev. Pete Sferle • 1 Samuel 1:26-28\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-05-25 00:00:00",
    ),  # youtube:6e760a929961
    (
        "fbe7cb14-8acf-5dff-93e7-aaab70b2753e",
        "Wait for the Promise of the Father — Rev. Mark Worthington • Acts 2:1-4",
        "5:00 pm Sunday evening 5/5/2024 • Wait for the Promise of the Father — Rev. Mark Worthington • Acts 2:1-4  —Rev. Mark Worthington • Acts 2:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-05-19 00:00:00",
    ),  # youtube:aaab70b2753e
    (
        "9ed703ea-a70b-5b5f-a02f-411622b97ee0",
        "This Is How We Should Live — Rev. Pete Sferle • 1 Peter:13",
        "11:00 am Sunday morning 5/5/2024 • This Is How We Should Live — Rev. Pete Sferle • 1 Peter:13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-05-06 00:00:00",
    ),  # youtube:411622b97ee0
    (
        "98e42568-acb3-5356-8564-261f2035bf48",
        "A Living Hope— Rev. Pete Sferle • 1 Peter 3",
        "11:00 am Sunday morning4/14/2024 •  A Living Hope— Rev. Pete Sferle • 1 Peter 3\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-04-14 00:00:00",
    ),  # youtube:261f2035bf48
    (
        "c40d4c56-830d-5f2b-a391-afd38c3af7a8",
        "Don''t Bow Down — Rev.Mark Worthington • Daniel 3:15-18",
        "Sunday Evening April 7 , 2024 5:00 pm. • Don''t Bow Down — Rev.Mark Worthington • Daniel 3:15-18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2024-04-14 00:00:00",
    ),  # youtube:afd38c3af7a8
    (
        "c4f8f1b8-9896-5358-9b74-b8481d9b4c9c",
        "Peter — Rev. Pete Sferle • 1 Peter 1:1",
        "11:00 am Sunday morning 4/7/2024 • Peter — Rev. Pete Sferle • 1 Peter 1:1\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-04-07 00:00:00",
    ),  # youtube:b8481d9b4c9c
    (
        "da0fe8c0-9415-548e-9647-b1522c0abe85",
        "Peter — Rev. Pete Sferle • 1 Peter 1:1",
        "11:00 am Sunday morning 4/7/2024 • Peter — Rev. Pete Sferle • 1 Peter 1:1\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-04-07 00:00:00",
    ),  # youtube:b1522c0abe85
    (
        "d14f52ef-9cac-586c-9847-7a848e3d3dda",
        "Almost Thou Persuadest Me to be a Christian. — Bro Sorin Filimon • Acts 26",
        "5:00 pm Sunday evening 3/31/2023 • Almost thou persuadest me to be a Christian. — Bro Sorin Filimon • Acts 26\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-04-07 00:00:00",
    ),  # youtube:7a848e3d3dda
    (
        "19a31848-b568-518e-ad1e-5153cfb93b9e",
        "Christ Arose! — Rev. Pete Sferle • 1 Corinthians 15:1-11",
        "11:00 am Sunday morning 3/31/2024 • Easter – Christ Arose! — Rev. Pete Sferle • 1 Corinthians 15:1-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-31 00:00:00",
    ),  # youtube:5153cfb93b9e
    (
        "33a65519-9497-511d-ba44-47079b680c54",
        "Launch Out Into The Deep — Bro. Sorin Filimon • Luke 5:1-11",
        "Sunday Evening March 24 , 2024 5:00 pm. Launch Out Into The Deep — Bro. Sorin Filimon • Luke 5:1-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-27 00:00:00",
    ),  # youtube:47079b680c54
    (
        "40ffe773-a2a1-526c-8f53-ce72f61d7bce",
        "All Honor, Glory , and Praise to our God — Rev. Pete Sferle • Luke 9:35-38",
        "11:00 am Sunday morning 3/24/2024 •All Honor, Glory , and Praise to our God — Rev. Pete Sferle • Luke 9:35-38  \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-24 00:00:00",
    ),  # youtube:ce72f61d7bce
    (
        "271f1649-1a0d-5c41-b8b9-35a94f9eaad6",
        "I Am The True Vine — Rev. Pete Sferle • John 15:1-11",
        "5:00 pm Sunday evening 3/17/2023 •  I Am The True Vine — Rev. Pete Sferle • John 15:1-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-24 00:00:00",
    ),  # youtube:35a94f9eaad6
    (
        "26ef271e-49f9-5232-8c31-91c78ed38283",
        "Set your affection on things above, not on things on the earth. • Bro. Noah Mocan — Colossians 3:2",
        "5:00 pm Sunday evening 3/17/2023 •  Set your affection on things above, not on things on the earth. • Bro. Noah Mocan — Colossians 3:2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-24 00:00:00",
    ),  # youtube:91c78ed38283
    (
        "5db99052-b18f-5b37-baf3-c519cea714fb",
        "Stir up the Gift of God — Bro. Tom Udo • 2 Timothy 1:6",
        "11:00 am Sunday morning 3/17/2024 • Stir up the Gift of God — Bro. Tom Udo • 2 Timothy 1:6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-17 00:00:00",
    ),  # youtube:c519cea714fb
    (
        "860805d9-4108-5956-ab52-29ecba5c5512",
        "Patience and Comfort of the Scriptures — Bro. Sorin Filimon • Romans 15:4",
        "5:00 pm Sunday evening 3/10/2023 • Patience and Comfort of the Scriptures — Bro. Sorin Filimon • Romans 15:4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-16 00:00:00",
    ),  # youtube:29ecba5c5512
    (
        "e2c66a40-eb41-573f-9ea2-ffe3c5ceae62",
        "God Does Not Change — Rev. Pete Sferle • Hebrews 13:8",
        "11:00 am Sunday morning 3/10/2024 • God Does Not Change — Rev. Pete Sferle • Hebrews 13:8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-10 00:00:00",
    ),  # youtube:ffe3c5ceae62
    (
        "586cccdd-9e4d-5f50-973e-661b6528e929",
        "Lazarus Come Forth  — Bro. Sorin Filimon • John 11",
        "Sunday Evening March 3 , 2024 5:00 pm.  Lazarus Come Forth  — Bro. Sorin Filimon • John 11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-10 00:00:00",
    ),  # youtube:661b6528e929
    (
        "dd3653ae-0059-5bf4-86e9-009f6b3eafb2",
        "And Enoch Walked with GOD, and He Was Not: For GOD Took Him — Rev. Pete Sferle •  John 14:1-4",
        "Sunday Morning March 3, 2024 11:00 AM — Rev. Pete Sferle •  John 14:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-04 00:00:00",
    ),  # youtube:009f6b3eafb2
    (
        "b9ab5789-8fba-5bc2-8cc6-fb3f28969e35",
        "Too Late — Rev. Mark Worthington • Luke 16:22-24",
        "Sunday Morning February 25, 2024 11:00 AM. Too Late — Rev. Mark Worthington • Luke 16:22-24\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2024-03-03 00:00:00",
    ),  # youtube:fb3f28969e35
    (
        "6db2f099-07df-5e52-8b53-c0617cb3d42d",
        "Everyone Will Receive According to What They''ve Done — Bro. Sorin Filimon",
        "Sunday Morning February 11, 2024 11:00 AM. Everyone Will Receive According to What They''ve Done — Bro. Sorin Filimon • \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2024-02-12 00:00:00",
    ),  # youtube:c0617cb3d42d
    (
        "59b115f9-7aad-5104-b5d1-4c2165dfbc32",
        "Be Watchful — Bro. Sorin Filimon • Luke 12:35-48",
        "Sunday Evening January 28, 2024 5:00 pm. Be Watchful — Bro. Sorin Filimon • Luke 12:35-48 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2024-01-31 00:00:00",
    ),  # youtube:4c2165dfbc32
    (
        "b28de2d3-2ecc-5ae9-be7b-ac10dbc2be7e",
        "What Is That In Thine Hand? — Rev. Pete Sferle • Exodus 4:1-5",
        "11:00 am Sunday morning 1/28/2024 What is that in thine hand? — Rev. Pete Sferle • Exodus 4:1-5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-01-28 00:00:00",
    ),  # youtube:ac10dbc2be7e
    (
        "80843384-64fb-5797-83a7-d81a46f45381",
        "We Are in a Victory Parade — Bro. Sorin Filimon • 2 Corinthians 2:12-17",
        "5:00 pm Sunday Evening 1/21/2024 • Youth service • We Are in a Victory Parade — Bro. Sorin Filimon • 2 Corinthians 2:12-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-01-27 00:00:00",
    ),  # youtube:d81a46f45381
    (
        "4879f9ad-411e-5156-aeda-4da452490e31",
        "Set Your Heart to Serve the Lord In the Coming Year • Luke 9:62 — Rev. Pete Sferle",
        "11:00 am Sunday morning 1/21/2024 - Set Your Heart to Serve the Lord In the Coming Year • Luke 9:62 — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-01-21 00:00:00",
    ),  # youtube:4da452490e31
    (
        "af60777e-08c4-5d79-8985-0699307806ff",
        "Don''t Look Back • Philippians 3:7-14 — Rev. Mark Worthington",
        "11:00 am Sunday morning 1/14/2024 - Don''t Look Back • Philippians 3:7-14 — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-01-21 00:00:00",
    ),  # youtube:0699307806ff
    (
        "34592b1f-aa22-5836-b5c4-74d5a00df36c",
        "Ecclesiastes 3:1-8 — Life Lessons For The New Year • Rev. Pete Sferle",
        "11:00 am Sunday morning 1/7/2024 - Ecclesiastes 3:1-8 — Life Lessons For The New Year • Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-01-11 00:00:00",
    ),  # youtube:74d5a00df36c
    (
        "c63cc211-a171-513f-b77e-f6d07367b358",
        "Spiritual Blessings - Bro. Sorin — Ephesians 1:1-14",
        "11:00 am New Years Eve morning 12/31/2023 • Spiritual Blessings - Bro. Sorin — Ephesians 1:1-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2024-01-07 00:00:00",
    ),  # youtube:f6d07367b358
    (
        "c4916960-264b-574b-9c35-36caa0b0eb80",
        "In the beginning was the Word, and the Word was with God, and the Word was God — Rev. Pete Sferl...",
        "11:00 am Sunday morning 12/24/2023 • In the beginning was the Word, and the Word was with God, and the Word was God — Rev. Pete Sferle • John 1:1 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2023-12-27 00:00:00",
    ),  # youtube:36caa0b0eb80
    (
        "5c882822-ab2d-51a9-a107-97f4fcdbd6bb",
        "Fullness Of The Gospel — Bro. Sorin Filimon • Galatians 4:4-7",
        "11:00 am Sunday Morning 12/17/2023 The Fullness Of The Gospel — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2023-12-24 00:00:00",
    ),  # youtube:97f4fcdbd6bb
    (
        "1946fb76-a370-593b-8693-6616a49ed751",
        "Joseph the Earthly Father of Jesus — Rev. Pete Sferle",
        "11:00 am Sunday Morning 12/10/2023 • Joseph the Earthly Father of Jesus  — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2023-12-11 00:00:00",
    ),  # youtube:6616a49ed751
    (
        "7350a0f7-8d25-55ee-8c4c-ac75156b394c",
        "The Lord is with thee, thou mighty man of valour. —  Rev. Pete Sferle • Judges 6:11-16",
        "12.3.2023 – Sunday December 3, 2023 • Youth Service • The Lord is with thee, thou mighty man of valour. —  Rev. Pete Sferle • Judges 6:11-16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-12-10 00:00:00",
    ),  # youtube:ac75156b394c
    (
        "c632f1da-02f3-5547-a524-f70702052d31",
        "Keeping Christ in Christmas — Rev. Mark Worthington • Philippians 2:8",
        "Sunday December 3, 2023, 11:00 am  • Keeping Christ in Christmas — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-12-10 00:00:00",
    ),  # youtube:f70702052d31
    (
        "4192b601-0bc9-5cd5-b5cb-9ca226b84e59",
        "The Gifts of the Wisemen for Today — Bro. Sorin Filimon • Matthew 2:1-12",
        "Sunday November 26, 2023, 5:00 pm  • The Gifts of the Wisemen for Today  — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-12-01 00:00:00",
    ),  # youtube:9ca226b84e59
    (
        "06cc09db-fe04-510e-8bda-b114d4faac56",
        "Add Godliness — Rev. John Baros • 2 Peter 1:5-7",
        "Sunday November 26, 2023, 11:00 am • Add Godliness — Rev. John Baros\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-11-30 00:00:00",
    ),  # youtube:b114d4faac56
    (
        "e8e3c783-dd04-5b23-abf5-c46ba1008be2",
        "Thanksgiving — Rev. Mark Worthington",
        "Sunday November 19, 2023, 11:00 am  • Thanksgiving — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-11-26 00:00:00",
    ),  # youtube:c46ba1008be2
    (
        "b91fb0c2-e656-5519-9514-b55e894d2a6a",
        "Your Greatest Treasure: Christ Within — Bro. Sorin Filimon",
        "11.12.2023 – Sunday November 12, 2023 • Youth Service — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-11-16 00:00:00",
    ),  # youtube:b55e894d2a6a
    (
        "9ebd9436-5dc6-5d49-b19f-250e3671b8db",
        "Do Not Forget The God That Has Delivered You! — Rev. Pete Sferle",
        "Sunday November 12, 2023, 11:00 am  • Do Not Forget The God That Has Delivered You! — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-11-13 00:00:00",
    ),  # youtube:250e3671b8db
    (
        "80aa0c92-9064-5990-9e45-1939863c4a77",
        "Ordinance Service •  Rev. Pete Sferle &  Bro. Sorin Filimon",
        "11.5.2023 – 5:00 Ordinance Service •  Rev. Pete Sferle &  Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-11-11 00:00:00",
    ),  # youtube:1939863c4a77
    (
        "c4328f61-f59a-504b-875c-4d68558973a9",
        "I Will Bless The Lord— Rev. Mark Worthington",
        "11.5.2023 – 11:00 am Sunday morning  service • I Will Bless The Lord— Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-11-11 00:00:00",
    ),  # youtube:4d68558973a9
    (
        "830d1f20-f75f-5920-8897-8b61b93d55db",
        "I Have Called You Friends — Rev. Pete Sferle",
        "Sunday October 29, 2023, 11:00 am  • But I Have Called You Friends — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-11-05 00:00:00",
    ),  # youtube:8b61b93d55db
    (
        "4e7295c8-a868-5cb9-9157-0da281a10bbd",
        "Humble yourselves in the sight of the Lord, and he shall lift you up. — Bro. Sorin Filimon",
        "Sunday October 22, 2023, 5:00 pm  • Humble yourselves in the sight of the Lord, and he shall lift you up. — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-11-03 00:00:00",
    ),  # youtube:0da281a10bbd
    (
        "912e9486-8d9b-5772-bf9a-934882ccd853",
        "Whatever Your Need Is, God Is Faithful — Rev.  Pete Sferle",
        "10.22.2023 – Sunday October 22, 2023 • Whatever Your Need Is, God Is Faithful — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-10-29 00:00:00",
    ),  # youtube:934882ccd853
    (
        "b87d937c-1ecf-5d85-9004-8413afce8d02",
        "Be Ready, Be Aware, Be Encouraged — Rev. Pete Sferle",
        "10.15.2023 – 11:00 am Sunday morning  service • Be Ready, Be Aware, Be Encouraged — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-10-28 00:00:00",
    ),  # youtube:8413afce8d02
    (
        "c6db56ac-61aa-5d3e-aefa-ea12618c24e6",
        "Is Church Boring? — Bro. Sorin Filimon",
        "10.15.2023 – 5:00 pm Sunday evening  service • Is Church Boring? — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-10-18 00:00:00",
    ),  # youtube:ea12618c24e6
    (
        "022b06d0-020d-5067-95cb-01c953e7f2c3",
        "Blessed are they which do hunger and thirst after righteousness for they shall be filled.  D Lam...",
        "Sunday October 1, 2023, 5:00 pm  • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Rev.  David Lambert\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-10-11 00:00:00",
    ),  # youtube:01c953e7f2c3
    (
        "869bd0c8-d995-57fb-8666-9cd413e1b5b6",
        "Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthe...",
        "Sunday October 1, 2023, 11:00 am  • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Rev.  David Lambert\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-10-08 00:00:00",
    ),  # youtube:9cd413e1b5b6
    (
        "0d6a4603-324f-5b8a-9065-47eefd4b6559",
        "... And he said, Hast thou not reserved a blessing for me? — Bro. Randy Lee",
        "Saturday September 30, 2023 6:00 pm • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Youth Service Bro. Randy Lee\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-10-08 00:00:00",
    ),  # youtube:47eefd4b6559
    (
        "04f6f377-dac9-5dec-9266-4163b8d6c758",
        "Marriage — Rev. Howard Wilson",
        "Saturday September 30, 2023, 10:30 am  • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Marriage • Rev.  Howard Wilson\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-10-07 00:00:00",
    ),  # youtube:4163b8d6c758
    (
        "0e41dcfa-02dc-59fd-8f1a-c5df2d4b1ac0",
        "Blessed are they which do hunger and thirst after righteousness for they shall be filled.  — Rev...",
        "Friday September 29, 2023 8:00 pm • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Rev.  David Lambert\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nI Will Sing The Wondrous Story (Wondrous Story), Peter Philip Bilhorn, public domain\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-09-30 00:00:00",
    ),  # youtube:c5df2d4b1ac0
    (
        "566ffe6a-907e-5089-97ab-a7e289b51a35",
        "See the Glory of God   — Bro. Sorin Filimon",
        "9.24.2023 – Sunday September 24, 2023, 5:00 pm • See the Glory of God   — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-09-30 00:00:00",
    ),  # youtube:a7e289b51a35
    (
        "1738f87b-650b-51e3-8d0d-f478b82e4b16",
        "The God of Peace — Rev.  Pete Sferle",
        "9.24.2023 – Sunday September 24, 2023 • The God of Peace — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-09-29 00:00:00",
    ),  # youtube:f478b82e4b16
    (
        "ae54a13d-1a86-509b-b474-09b4f7351660",
        "Prayer, Communication — Rev.  Pete Sferle",
        "9.17.2023 – Sunday September 17, 2023 • Prayer, Communication — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-09-29 00:00:00",
    ),  # youtube:09b4f7351660
    (
        "844a61ac-2236-5817-a3ac-5c12a491f353",
        "Keep Thine Heart With All Diligence  — Rev. Pete Sferle",
        "9.10.2023 – Sunday September 10, 2023 • Keep Thine Heart With All Diligence  — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-09-24 00:00:00",
    ),  # youtube:5c12a491f353
    (
        "862082d0-0fa6-5bbc-bc56-d6712fec0a9a",
        "What Is Your Name  — Rev. Mark Worthington",
        "9.10.2023 – Sunday September, 10 2023 • What Is Your Name  — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-09-24 00:00:00",
    ),  # youtube:d6712fec0a9a
    (
        "da1b71d5-7177-5911-89b1-bbd4df959025",
        "Continually Offering Our Spiritual Sacrifice to God — Rev.  Pete Sferle",
        "9.3.2023 – Sunday September 3, 2023 • Continually Offering Our Spiritual Sacrifice to God — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-09-04 00:00:00",
    ),  # youtube:bbd4df959025
    (
        "a020e7a7-46f0-5065-a0cd-59303fdce191",
        "... And There Was Joy — Bro. Sorin Filimon",
        "8.27.2023 – 5:00 pm Sunday evening  service • ... And There Was Joy — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-08-28 00:00:00",
    ),  # youtube:59303fdce191
    (
        "872c09af-ac62-5423-aee5-06526999eafa",
        "How to Have Victory in the Battle of Life — Rev.  Mark Worthington",
        "8.27.2023 – Sunday August, 27 2023 • How to Have Victory in the Battle of Life  — Rev. Mark Worthington 2 Chronicles 20:1-4, 12-18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-08-28 00:00:00",
    ),  # youtube:06526999eafa
    (
        "6f199542-67f2-5165-b5ea-a848e6652681",
        "Jesus Suffered and Died Outside the Gate — Privilege Bearing Jesus Reproach • Rev. Pete Sferle",
        "11:00 am – Sunday August, 20 2023 • Jesus Suffered and Died Outside the Gate — Privilege Bearing Jesus Reproach   — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-08-20 00:00:00",
    ),  # youtube:a848e6652681
    (
        "c11085a3-b8c9-5992-b726-ca4ba46c309e",
        "God is No Respecter of Persons — Bro. Sorin Filimon",
        "8.13.2023 – 5:00 pm Sunday evening  service • God is No Respecter of Persons — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-08-15 00:00:00",
    ),  # youtube:ca4ba46c309e
    (
        "00903e43-5f12-5169-9b59-62029ff9158f",
        "Step Out of the Boat — Bro. Sorin Filimon",
        "8.6.2023 – 5:00 pm Sunday evening  service •.Step Out of the Boat — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-08-10 00:00:00",
    ),  # youtube:62029ff9158f
    (
        "a9758d56-9457-589c-beed-5282c361111e",
        "For a Man''s Life Consisteth Not in the Abundance of the Things Which He Possesseth — Rev Pete Sf...",
        "Sunday August 6, 2023 11:00 am morning service • Take heed, and beware of covetousness: for a man''s life consisteth not in the abundance of the things which he possesseth. — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-08-06 00:00:00",
    ),  # youtube:5282c361111e
    (
        "556fae49-5aa4-5717-bdbc-74fe50643602",
        "Don''t Just Stand There — Rev. Mark Worthington",
        "7.30.2023 – 5:00 pm Sunday evening  service • Don''t Just Stand There — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-08-05 00:00:00",
    ),  # youtube:74fe50643602
    (
        "ae96c494-46f1-5d91-ac4b-612812826a10",
        "Be Content With Such Things As You Have — Rev. Pete Sferle",
        "7.30.2023 – Sunday July 30, 2023 morning service • Be Content With Such Things As You Have — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-07-30 00:00:00",
    ),  # youtube:612812826a10
    (
        "0a060f6c-1918-529b-919c-6ec87a02c36b",
        "Come unto me, all ye that labour and are heavy laden, and I will give you rest. — Rev. Pete Sferle",
        "7.23.2023 – 5:00 pm Sunday evening  service • Come unto me, all ye that labour and are heavy laden, and I will give you rest. — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-07-29 00:00:00",
    ),  # youtube:6ec87a02c36b
    (
        "b594a5d9-5b5a-5891-b270-ea7aa6bdafcc",
        "A little Faith in a Big God  — Rev.  Pete Sferle",
        "7.23.2023 – Sunday July, 23 2023 • A little Faith in a Big God  — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-07-23 00:00:00",
    ),  # youtube:ea7aa6bdafcc
    (
        "ce41dc1c-fba4-5690-9a01-2b26fa942b4f",
        "What Is My Purpose For Living? — Rev. Mark Worthington",
        "7.16.2023 – Sunday July 16, 2023 morning service • What Is My Purpose For Living? — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-07-23 00:00:00",
    ),  # youtube:2b26fa942b4f
    (
        "9cc11912-105d-5e9e-b5c0-655fb0c89d88",
        "Speak, Lord, Your Servant is Listening — Bro. Sorin Filimon",
        "6.18.2023 – 3:00 pm Sunday evening  service • Speak, Lord, Your Servant is Listening — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-07-23 00:00:00",
    ),  # youtube:655fb0c89d88
    (
        "7d18e937-53b1-573f-989f-407819eebb39",
        "Tools — Bro. Noah Mocan",
        "6.18.2023 – 3:00 pm Sunday youth evening  service • Tools — Bro. Noah Mocan\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-07-23 00:00:00",
    ),  # youtube:407819eebb39
    (
        "116b5714-f81c-594d-ac28-9c90fbc9a68f",
        "Our Heavenly Father Day — Rev.  Pete Sferle",
        "6.18.2023 – Sunday June 18, 2023 morning service •  Our Heavenly Father Day — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-06-18 00:00:00",
    ),  # youtube:9c90fbc9a68f
    (
        "012d4998-b35d-5f51-878c-4b6cd21bc5dc",
        "A Special Treasure — Bro. Sorin Filimon",
        "6.11.2023 – 5:00 pm Sunday evening  service • A Special Treasure — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-06-17 00:00:00",
    ),  # youtube:4b6cd21bc5dc
    (
        "53361f63-0f74-5451-a384-40337b48b1c7",
        "We Are A Family — Rev.  Pete Sferle",
        "6.11.2023 – Sunday June 11, 2023 morning service • We Are A Family — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-06-11 00:00:00",
    ),  # youtube:40337b48b1c7
    (
        "cf200aa2-1148-5e2b-8986-3573ebf6c674",
        "A Time of Preparation  — Bro. Sorin Filimon",
        "6.4.2023 – 5:00 pm Sunday evening  service • A Time of Preparation — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-06-05 00:00:00",
    ),  # youtube:3573ebf6c674
    (
        "75f30902-d73e-5312-a14c-5843ae6cda0f",
        "God''s Unshakable Kingdom — Rev.  Pete Sferle",
        "6.4.2023 – Sunday June, 4 2023 morning service •  God''s Unshakable Kingdom  — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-06-04 00:00:00",
    ),  # youtube:5843ae6cda0f
    (
        "303d22bf-6663-59ed-bd0f-3ad9782c89f5",
        "Pentecost — Rev.  Pete Sferle",
        "5.28.2023 – Sunday morning service •  Pentecost — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-06-03 00:00:00",
    ),  # youtube:3ad9782c89f5
    (
        "1b7d07a5-e5bc-5c1a-bc7d-93d41cde6b95",
        "Loving and Celebrating Your Mom Jesus''s Way  — Rev.  Mark Worthington",
        "5.14.2023 – Sunday May, 14 2023 morning service • Loving and Celebrating Your Mom Jesus''s Way  — Rev.  Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-05-14 00:00:00",
    ),  # youtube:93d41cde6b95
    (
        "27903a77-b851-502c-ba9a-3fea538adff5",
        "Thirsting For Deeper Experiences — Bro. Sorin Filimon",
        "5.7.2023 – 5:00 pm Sunday evening service • Thirsting For Deeper Experiences — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-05-09 00:00:00",
    ),  # youtube:3fea538adff5
    (
        "13baef8b-6ef9-5c2a-a7a1-66c5b251ee74",
        "Mt. Sinai? Mt Zion?  — Rev.  Pete Sferle",
        "5.7.2023 – Sunday May, 7 2023 morning service • Mt. Sinai? Mt Zion?  — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-05-07 00:00:00",
    ),  # youtube:66c5b251ee74
    (
        "3fed629b-f91b-59ac-b9e2-a14c33350cac",
        "Fear of God — Rev. Mark Worthington",
        "4.30.2023 – 5:00 pm Sunday evening service • Fear of God — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-05-02 00:00:00",
    ),  # youtube:a14c33350cac
    (
        "3b1df1ee-3abe-5c8e-99b6-676b3cbf7566",
        "Faithful Is He That Calleth You Who Also Will Do It  — Rev.  Pete Sferle",
        "4.30.2023 – Sunday April 30, 2023 morning service •  Faithful Is He That Calleth You Who Also Will Do It  — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-04-30 00:00:00",
    ),  # youtube:676b3cbf7566
    (
        "3a8f5c8e-bc2a-5d09-98a8-09010fa3c25c",
        "God''s Greatness - Be Humble — Bro. Sorin Filimon",
        "4.23.2023 – 5:00 pm Sunday evening service • God''s Greatness - Be Humble — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-04-29 00:00:00",
    ),  # youtube:09010fa3c25c
    (
        "79c49598-7827-55a1-b3b4-41a5f06a6139",
        "For Whom the Lord Loves, He Chastens  Rev. Pete Sferle",
        "Sunday morning 4.23.2023 11:00 am • For Whom the Lord Loves, He Chastens  Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2023-04-23 00:00:00",
    ),  # youtube:41a5f06a6139
    (
        "e721bcf1-1fab-56e6-af2e-2fc823072872",
        "What Would God do With Your Lunch — Rev. Pete Sferle",
        "Sunday morning 4.16.2023 11:00 am • What Would God do With Your Lunch — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2023-04-22 00:00:00",
    ),  # youtube:2fc823072872
    (
        "8979e573-5ded-5275-9eb0-187cc0d38a0b",
        "Live for Jesus — Bro. Sorin Filimon",
        "4.9.2023 – 5:00 pm Sunday evening service • Live for Jesus — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-04-12 00:00:00",
    ),  # youtube:187cc0d38a0b
    (
        "0d29c30e-ab13-5912-9d8e-3500da17a72a",
        "Resurrection Day  — Rev.  Pete Sferle",
        "4.9.2023 – Sunday April 9, 2023 morning service • Resurrection Day  — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-04-10 00:00:00",
    ),  # youtube:3500da17a72a
    (
        "641cbbb6-396e-564d-a6b5-4660356a7d03",
        "Passover — Rev. Mark Worthington",
        "4.7.2023 – 7:00 pm Friday evening service • Passover — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-04-08 00:00:00",
    ),  # youtube:4660356a7d03
    (
        "591fd06e-0ea2-5b76-b30b-5eec3e5da38d",
        "The House of Prayer — Bro. Sorin Filimon",
        "4.2.2023 – 5:00 pm Sunday evening service • The House of Prayer — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-04-08 00:00:00",
    ),  # youtube:5eec3e5da38d
    (
        "e0ae9c8e-1854-5e26-aa28-cfa73722d313",
        "The Coronation of a King  — Rev.  Pete Sferle",
        "4.2.2023 – Sunday April 2, 2023 morning service • The Coronation of a King  — Rev.  Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-04-02 00:00:00",
    ),  # youtube:cfa73722d313
    (
        "af224179-f2ce-5931-ac60-1ebe74a847ae",
        "Keep Yourselves in the Love of God  — Bro. Sorin Filimon",
        "4.2.2023 – 5:00 pm Sunday evening service • Keep Yourselves in the Love of God — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-03-31 00:00:00",
    ),  # youtube:1ebe74a847ae
    (
        "9f6f5c6e-4329-5e1c-a43b-dc03ae0b630b",
        "Answering The Call Of God — Rev. Mark Worthington",
        "3.26.2023 – 11:00 am Sunday Morning Service • Answering The Call Of God — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-03-26 00:00:00",
    ),  # youtube:dc03ae0b630b
    (
        "fc59b6b2-b448-575c-84c9-96651ee3ff3f",
        "Why do Christians Suffer Persecution?  — Rev. Mark Worthington",
        "3.19.2023 – Sunday January 22, 2023 morning service • Why do Christians Suffer Persecution?  — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-03-25 00:00:00",
    ),  # youtube:96651ee3ff3f
    (
        "6033b9ab-0a54-5552-a793-7ff9fe8152b5",
        "Giving All to Jesus — Bro. Sola Omolayo",
        "3.12.2023 – 5:00 pm Sunday evening youth service • Giving All to Jesus — Bro. Sola Omolayo\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-03-18 00:00:00",
    ),  # youtube:7ff9fe8152b5
    (
        "ec886fdd-c8fb-5a5d-bfb8-f74418837481",
        "Consider Jesus — Rev. Pete Sferle",
        "3.12.2023 – 11:00 am Sunday Morning Service • Consider Jesus — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-03-12 00:00:00",
    ),  # youtube:f74418837481
    (
        "b0d1315a-f3a6-5b96-bd40-942ce5051254",
        "God Loves You — Bro. Sorin Filimon",
        "3.5.2023 – 11:00 am Sunday Morning Service •  —  God Loves You — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-03-08 00:00:00",
    ),  # youtube:942ce5051254
    (
        "536668f9-1daa-5d4e-a192-ed1776c15437",
        "Dry Bones • Hear the Word of the Lord — Rev. Mark Worthington",
        "2.26.2023 – Sunday evening service • Dry Bones • Hear the Word of the Lord — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-03-05 00:00:00",
    ),  # youtube:ed1776c15437
    (
        "7997fa83-c6b9-5ddf-bc22-9339680c3c8d",
        "God''s Grace — Bro. Sorin Filimon",
        "2.26.2023 – Sunday Morning Service •  God''s Grace — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-02-26 00:00:00",
    ),  # youtube:9339680c3c8d
    (
        "e214da6e-0c58-5df5-a2b9-a4300e3a7d02",
        "God is Light",
        "2.12.2023 – Sunday evening service • God is Light — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-02-17 00:00:00",
    ),  # youtube:a4300e3a7d02
    (
        "819f33cc-146b-5631-ac01-0c245ac8287f",
        "Run the Race Set  Before Us Laying Down Every Weight and the Sin Which so Easily Beset Us — Rev....",
        "2.12.2023 – Sunday Morning Service • Run the Race Set  Before Us Laying Down Every Weight and the Sin Which so Easily Beset Us — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-02-12 00:00:00",
    ),  # youtube:0c245ac8287f
    (
        "3a3992f4-3e1e-5c2a-9a37-82342fbd478e",
        "That Your Joy May be Full — Bro. Sorin Filimon",
        "2.5.2023 – Sunday evening service • That Your Joy May be Full — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-02-09 00:00:00",
    ),  # youtube:82342fbd478e
    (
        "568700d7-db4f-599a-b31f-2ea898ea754f",
        "The Testimony of the Great Cloud of Witnesses — Rev. Pete Sferle",
        "2.5.2023 – Sunday Morning Service • The Testimony of the Great Cloud of Witnesses — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-02-06 00:00:00",
    ),  # youtube:2ea898ea754f
    (
        "a18dfe88-54b0-5faf-a890-cb0c0c91991f",
        "Influencers — Rev. Mark Worthington",
        "1.29.2023 – Sunday Morning Service • Influencers — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-02-02 00:00:00",
    ),  # youtube:cb0c0c91991f
    (
        "7cf38fe8-26d1-52e6-93e4-734b2cb70324",
        "The Name of the Lord is a Strong Tower — Bro Sorin Filimon",
        "1.22.2023 – Sunday January 22, 2023 evening service • The Name of the Lord is a Strong Tower — Bro Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-01-26 00:00:00",
    ),  # youtube:734b2cb70324
    (
        "ead4d889-609e-53bd-975b-6dd0296b31ce",
        "Observing Faith — Rev. Pete Sferle",
        "1.22.2023 – Sunday Morning Service • Observing Faith — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-01-22 00:00:00",
    ),  # youtube:6dd0296b31ce
    (
        "fc3819a7-18c6-5ee2-a760-7d6b03a86270",
        "A Fruitless Fig Tree — Bro. Sorin Filimon",
        "1.8.2023 – Sunday January 8, 2023 Youth service • A Fruitless Fig Tree — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-01-16 00:00:00",
    ),  # youtube:7d6b03a86270
    (
        "6448d213-d80d-5969-a4d0-34444262a9c7",
        "Faith is the Substance of Things Hoped For, the Evidence of Things Not Seen — Rev. Pete Sferle",
        "1.8.2023 – Sunday Morning Service • Faith is the Substance of Things Hoped For, the Evidence of Things Not Seen — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2023-01-08 00:00:00",
    ),  # youtube:34444262a9c7
    (
        "c0988677-394c-51e2-beea-fd08c3dd9e88",
        "The Message Came to Them — Bro. Florin Baros",
        "12.25.2022 – Sunday Morning Service • The Message Came To Them — Bro. Florin Baros\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-12-31 00:00:00",
    ),  # youtube:fd08c3dd9e88
    (
        "a8cbfd9a-39ec-59be-97fd-8fc365e498d5",
        "The Shepherds Said One to Another, Let Us Now Go Even Unto Bethlehem —  Rev. Pete Sferle",
        "12.18.2022 – Sunday Morning Service • The Shepherds Said One to Another, Let Us Now Go Even Unto Bethlehem —  Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org \n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-12-25 00:00:00",
    ),  # youtube:8fc365e498d5
    (
        "3f1a35a4-a2ea-5098-919a-2a9c426a30dd",
        "Rev. Pete Sferle • Do Not Abandon what you Have Started",
        "11:00 am sunday morning December 11,2022 — Rev. Pete Sferle • Do Not Abandon what you Have Started\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-12-17 00:00:00",
    ),  # youtube:2a9c426a30dd
    (
        "7c6fd886-63af-59bc-b028-c851674e0241",
        "Provoke One Another to Love — Rev. Pete Sferle",
        "12.4.220– Sunday Morning Service •  Provoke One Another to Love — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-12-05 00:00:00",
    ),  # youtube:c851674e0241
    (
        "59a67730-8bf4-51d3-8ce2-e42ba063d48a",
        "Unconditional Love — Rev. Mark Worthington",
        "11.20.2022 – Sunday Morning Service • Unconditional Love — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-11-24 00:00:00",
    ),  # youtube:e42ba063d48a
    (
        "071ff662-bb51-5846-9b3f-89b534dc4963",
        "Christ Died Once, For All — Rev. Pete Sferle",
        "11.6.2022 – Sunday Morning Service • Christ Died Once, For All — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-11-13 00:00:00",
    ),  # youtube:89b534dc4963
    (
        "ea5757fd-99a3-51d3-8c22-e2e386c51972",
        "Rejoice Evermore — Rev. Mark Worthington",
        "Rejoice Evermore — 11:00 am 10.30.2022 – Sunday Morning Service •  — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-11-03 00:00:00",
    ),  # youtube:e2e386c51972
    (
        "bd655bf4-9817-5ac4-80b7-42162736cbf5",
        "A Cleansed Conscience — Rev. Pete Sferle",
        "A Cleaned Conscience — Rev. Pete Sferle • Hebrews 9:1-15 – 11:00 am Sunday Morning Service 10.23.2022\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-10-23 00:00:00",
    ),  # youtube:42162736cbf5
    (
        "4bb37eb8-d4d0-566f-abbd-a6b825a42735",
        "The Beggar at The Pool • Bro. Sorin Filimon",
        "The Beggar at The Pool • Bro. Sorin Filimon — 10.16.2022 –5:00 pm Sunday Evening Service \n\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-10-19 00:00:00",
    ),  # youtube:a6b825a42735
    (
        "825ae6f6-3493-59ed-a106-f4b0ed57a81c",
        "The Covenant of Grace is Better — Rev. Pete Sferle",
        "The Covenant of Grace is Better — Rev. Pete Sferle • 10.16.2022 – 11:00 am Sunday Morning Service \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-10-16 00:00:00",
    ),  # youtube:f4b0ed57a81c
    (
        "8a03f5d3-e4fc-5abf-b5d8-44b122e39c93",
        "A New Thing — Bro. Sorin Filimon",
        "A New Thing — Bro. Sorin Filimon - Isaiah 43:18-21 (KJV) • 10.9.2022 – Sunday Evening Service \n\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-10-15 00:00:00",
    ),  # youtube:44b122e39c93
    (
        "2c49a1a0-2ce4-59e6-aa6c-25aa39246b1b",
        "Jesus King and Priest For Ever, After the Order of Melchizedek — Rev. Pete Sferle",
        "10.9.2022 – Sunday Morning Service • Jesus King and Priest For Ever After the Order of Melchizedek — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-10-09 00:00:00",
    ),  # youtube:25aa39246b1b
    (
        "ed5c2356-d9cf-5dcb-ac5e-e3f64f015811",
        "I Press Toward the Mark for the Prize — Rev. Erik Calhoun",
        'California Combined Meetings — Sacramento\n10.02.2022 – Sunday Evening Service • "I Press Toward the Mark for the Prize of the High Calling of God in Christ Jesus" (Philippians 3:14) — Rev. Erik Calhoun\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org',
        "00000000-0000-0000-0000-000000000000",
        "2022-10-04 00:00:00",
    ),  # youtube:e3f64f015811
    (
        "3011ddb9-2692-5fd8-8588-0666d6a66198",
        "I Press Toward the Mark for the Prize of the High Calling of God in Christ Jesus — Rev Erik Calhoun",
        'California Combined Meetings — Sacramento\n10.02.2022 – Sunday morning Service • "I Press Toward the Mark for the Prize of the High Calling of God in Christ Jesus" (Philippians 3:14) — Rev. Erik Calhoun\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org',
        "00000000-0000-0000-0000-000000000000",
        "2022-10-02 00:00:00",
    ),  # youtube:0666d6a66198
    (
        "34e17891-b005-5cb1-9a9f-ef5e0c14b5ba",
        "I Press Toward the Mark for the Prize of the High Calling of God in Christ Jesus — Bro. Randy Lee",
        'California Combined Meetings — Sacramento\n10.01.2022 – Saturday Evening Service • "I Press Toward the Mark for the Prize of the High Calling of God in Christ Jesus" (Philippians 3:14) — Bro. Randy Lee\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org',
        "00000000-0000-0000-0000-000000000000",
        "2022-10-02 00:00:00",
    ),  # youtube:ef5e0c14b5ba
    (
        "efc8dcc4-e8fa-528e-9c2e-199c32b846fe",
        "Bro. Randy Lee — Saturday morning devotional",
        "Bro. Randy Lee\n10.1.2022 Saturday morning devotional\nCalifornia Combined Meetings — Sacramento\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\nInfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "2022-10-02 00:00:00",
    ),  # youtube:199c32b846fe
    (
        "d7fcae09-416f-538d-aa55-05c3699093da",
        "I Press Toward the Mark for the Prize of the High Calling of God in Christ Jesus — Rev. Erik Cal...",
        'California Combined Meetings — Sacramento\n9.30.2022 – Friday Evening Service • "I Press Toward the Mark for the Prize of the High Calling of God in Christ Jesus" (Philippians 3:14) — Rev. Erik Calhoun\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A',
        "00000000-0000-0000-0000-000000000000",
        "2022-10-01 00:00:00",
    ),  # youtube:05c3699093da
    (
        "0d2d0ef7-63b4-59cd-8ea7-c48097f98dd1",
        "Our World View — Rev. Mark Worthington",
        "9.25.2022 – Sunday Morning Service • Our World View — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2022-09-25 00:00:00",
    ),  # youtube:c48097f98dd1
    (
        "e434b1af-b6aa-5860-bcb8-3d9a9e598e0f",
        "Live Life in the Deep Water — Bro. Sorin Filimon",
        "5:00 pm Sunday evening September 18, 2022 • Live Life in the Deep Water — Bro. Sorin Filimon – Ezekiel 47:1-5",
        "00000000-0000-0000-0000-000000000000",
        "2022-09-22 00:00:00",
    ),  # youtube:3d9a9e598e0f
    (
        "1b624062-2b05-59ae-9798-15506f832d77",
        "Be Secure in Your Salvation — Rev. Pete Sferle",
        "Sunday morning, September 18, 2022 Be Secure in Your Salvation Hebrews 6:11 — Rev. Pete Sferle",
        "00000000-0000-0000-0000-000000000000",
        "2022-09-18 00:00:00",
    ),  # youtube:15506f832d77
    (
        "6113655d-c848-5504-96da-0ed6b8d5385b",
        "Shoes of the Gospel – Rev. Mark Worthington",
        "5:00 pm Sunday evening September 11, 2022 • Shoes of the Gospel Ephesians 6:13-15 – Rev. Mark Worthington",
        "00000000-0000-0000-0000-000000000000",
        "2022-09-17 00:00:00",
    ),  # youtube:0ed6b8d5385b
    (
        "ad84ac7b-7605-5a3d-b30a-d6f88ee2cbda",
        "The Holy Spirit Works in Wonderful Ways in Our Lives — Bro. Sorin Filimon",
        "11:00 Sunday morning, September 11, 2022 • The Holy Spirit Works in Wonderful Ways in Our Lives — Bro. Sorin Filimon Romans 8:15-17",
        "00000000-0000-0000-0000-000000000000",
        "2022-09-17 00:00:00",
    ),  # youtube:d6f88ee2cbda
    (
        "89aa1d08-f52b-56c0-b434-5f932bbda873",
        "True Salvation — Rev. Pete Sferle",
        "9.04.2022 – Sunday morning service • True Salvation — Rev. Pete Sferle – Hebrews 6:4-6",
        "00000000-0000-0000-0000-000000000000",
        "2022-09-04 00:00:00",
    ),  # youtube:5f932bbda873
    (
        "2dc95106-1e07-51e4-b5f3-2abf22697ba0",
        "I Heard You The First Time — Rev. Mark Worthington",
        "8.28.2022 - Sunday evening service • I Heard You The First Time — Rev. Mark Worthington - Daniel 10:12-24",
        "00000000-0000-0000-0000-000000000000",
        "2022-08-29 00:00:00",
    ),  # youtube:2abf22697ba0
    (
        "88f38b45-fb7f-5da0-969e-751c71f91914",
        "Are you Dull of Hearing? — Rev. Pete Sferle",
        "11:00 am Sunday morning service – Are you Dull of Hearing? — Rev. Pete Sferle • Hebrews 5:11",
        "00000000-0000-0000-0000-000000000000",
        "2022-08-28 00:00:00",
    ),  # youtube:751c71f91914
    (
        "8d9a349d-8df7-5216-bdfc-17913f842edc",
        "Give Me Jesus",
        "Give Me Jesus, David Budean\nPublic domain\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2022-08-18 00:00:00",
    ),  # youtube:17913f842edc
    (
        "ddd0f2bf-ea22-5fdd-bbae-c2fb7c1745e0",
        "An 8 Year Old Turns Nation to God — Rev. Mark Mark Worthington – Trinity Apostolic Faith Church",
        "11:00 am Sunday morning August 7, 2022\nAn 8 Year Old Turns Nation to God — 2 Kings 22:2\nRev. Mark Mark Worthington\n\nTrinity Apostolic Faith Church • Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "2022-08-09 00:00:00",
    ),  # youtube:c2fb7c1745e0
]


def _insert_sql(row: tuple) -> str:
    media_id, name, description, owner_id, ts = row
    desc_literal = "NULL" if description is None else f"'{description}'"
    return (
        "INSERT INTO media (id, name, description, owner_id, uploaded_on, created_on, updated_on) "
        f"VALUES ('{media_id}', '{name}', {desc_literal}, '{owner_id}', '{ts}', '{ts}', '{ts}') "
        "ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description), "
        "updated_on = VALUES(updated_on)"
    )


def upgrade() -> None:
    for row in MEDIA_ROWS:
        op.execute(_insert_sql(row))


def downgrade() -> None:
    ids = ", ".join(f"'{row[0]}'" for row in MEDIA_ROWS)
    op.execute(f"DELETE FROM media WHERE id IN ({ids})")
