"""seed video_uploads table from AFC Sacramento YouTube channel

Revision ID: 336acd53a355
Revises: ef463f5a4ac5
Create Date: 2026-08-24 03:43:00.212905

Data migration: one row per YouTube video that carries a scripture reference
(extracted via scripts/extract_youtube_services.py, parsed from the description's
first line ``[title - speaker • reference_text]``). Rows are idempotent — ids are
UUID5 of the YouTube video id (same value as the matching media row) and inserts
use ON DUPLICATE KEY UPDATE, so re-running after a fresh extraction only updates
changed values.
"""

from typing import Sequence, Union


from alembic import op

revision: str = "336acd53a355"
down_revision: Union[str, Sequence[str], None] = "ef463f5a4ac5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (id, upload_location, upload_name, description, owner_id, speaker_name, reference_text, media_association_date)
VIDEO_UPLOAD_ROWS = [
    (
        "5147a444-eb67-5e9f-ba74-2bb9181fd873",
        "https://www.youtube.com/watch?v=v5adSuMsdkc",
        "Two Worldviews Of Freedom",
        "8/16/2026 — 5:00 pm Sunday evening service - Two Worldviews Of Freedom — Bro. Noah Mocan • Romans 8:1-2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Romans 8:1-2",
        "2026-08-18 00:00:00",
    ),  # youtube:2bb9181fd873
    (
        "13f7674b-b503-5ca7-9525-474588cc3a01",
        "https://www.youtube.com/watch?v=0rkUQ3Zsces",
        "Walk In Humility",
        "8/16/2026 — 11:00 am Sunday morning service - Walk In Humility — Brother Sorin Filimon • Ephesians 4:1-16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Brother Sorin Filimon",
        "Ephesians 4:1-16",
        "2026-08-16 00:00:00",
    ),  # youtube:474588cc3a01
    (
        "0b0353c3-1c23-52cd-9b41-e7b89b52ec79",
        "https://www.youtube.com/watch?v=pHPdt4jD08E",
        "The Standard For Spiritual Success",
        "8/9/2026 — 5:00 pm Sunday evening youth service - The Standard For Spiritual Success — Bro. Noah Mocan • Joshua 1:7-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Joshua 1:7-9",
        "2026-08-10 00:00:00",
    ),  # youtube:e7b89b52ec79
    (
        "62ad7c88-00d3-5ad6-a85e-1c645965d934",
        "https://www.youtube.com/watch?v=kf1BAQ-tnx4",
        "What Would Ye That I Should Do For You?",
        "8/9/2026 — 11:00 am Sunday morning service - What Would Ye That I Should Do For You? — Rev. Mark Worthington • Mark 10:35-45\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Mark 10:35-45",
        "2026-08-09 00:00:00",
    ),  # youtube:1c645965d934
    (
        "b342cf67-767b-51df-8222-d2c74372e9cd",
        "https://www.youtube.com/watch?v=kSJ-rQEd4D8",
        "God Is My Salvation",
        "8/2/2026 — 5:00 pm Sunday evening service - God Is My Salvation — Brother Sorin Filimon • Isaiah 12:1-6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Brother Sorin Filimon",
        "Isaiah 12:1-6",
        "2026-08-03 00:00:00",
    ),  # youtube:d2c74372e9cd
    (
        "c8703250-867b-550e-a7af-c53b4d6fc5fd",
        "https://www.youtube.com/watch?v=imldqjjlTFo",
        "Living In The Light Of That Day",
        "8/2/2026 — 11:00 am Sunday morning service - Living In The Light Of That Day — Rev. Pete Sferle • 2 Peter 3:10-14 Trinity Apostolic Faith Church, Sacramento County, California For more information, please visit us at www.afcsacramento.org, email: pete@sferle.com CCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Peter 3:10-14",
        "2026-08-02 00:00:00",
    ),  # youtube:c53b4d6fc5fd
    (
        "42baaada-924c-5cbf-a592-ac9ce005e4e6",
        "https://www.youtube.com/watch?v=XANqGv6ZMU4",
        "Confidence In God",
        "7/26/2026 — 5:00 pm Sunday evening service - Confidence In God — Bro. Sorin Filimon • 1 Samuel 17:32-36\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "1 Samuel 17:32-36",
        "2026-07-27 00:00:00",
    ),  # youtube:ac9ce005e4e6
    (
        "47975d83-eef7-5bc5-a778-dd13e181594f",
        "https://www.youtube.com/watch?v=L_5_UCsYEf0",
        "Do Not Conform — But Be Transformed",
        "7/26/2026 — 11:00 am Sunday morning service - Do Not Conform - But Be Transformed — Rev. Pete Sferle • Romans 12-2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Romans 12-2",
        "2026-07-26 00:00:00",
    ),  # youtube:dd13e181594f
    (
        "a4a5a17a-ac3c-5c38-a552-dbe553f4b1a8",
        "https://www.youtube.com/watch?v=yWwDbgwEyJM",
        "Dead and Alive",
        "7/19/2026 — 11:00 am Sunday morning service - Dead and Alive — Rev. Pete Sferle • Romans 12:1\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Romans 12:1",
        "2026-07-22 00:00:00",
    ),  # youtube:dbe553f4b1a8
    (
        "cac9d85a-667f-5f9c-b27c-51de56fc22f3",
        "https://www.youtube.com/watch?v=gsrn8Hldv_c",
        "A Nameless Father That Had Great Influence Upon His Child",
        "6/21/2026 — 11:00 am Sunday morning service - A Nameless Father That Had Great Influence Upon His Child — Rev. Pete Sferle • Daniel 1:17-21\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Daniel 1:17-21",
        "2026-07-17 00:00:00",
    ),  # youtube:51de56fc22f3
    (
        "76b048f1-193c-5e45-b392-f142849a8550",
        "https://www.youtube.com/watch?v=BuZV_ywVnZA",
        "God''s Means and Methods",
        "6/14/2026 —  2:00 pm Sunday youth service  - God''s Means and Methods — Bro. Noah Mocan • Isiah 55:8-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com  ♪♫\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Isiah 55:8-11",
        "2026-07-05 00:00:00",
    ),  # youtube:f142849a8550
    (
        "74c8c03f-5688-56e5-bc6a-9b2f8aa00afc",
        "https://www.youtube.com/watch?v=YbiCqWTqBEE",
        "God''s Answer To The Scoffers",
        "6/14/2026 — 11:00 am Sunday morning service - God''s Answer To The Scoffers — Rev. Pete Sferle • 2 Peter 3:1-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Peter 3:1-9",
        "2026-06-24 00:00:00",
    ),  # youtube:9b2f8aa00afc
    (
        "b11d52d5-b771-578e-886c-3c5ef993b63d",
        "https://www.youtube.com/watch?v=lY-02RctneQ",
        "The Call",
        "6/7/2026 — 11:00 am Sunday morning service - The Call — Rev. John Musgrave • 2 Kings 2:9-15 › Scripture 1 Kings 19:13-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. John Musgrave",
        "2 Kings 2:9-15; 1 Kings 19:13-19",
        "2026-06-08 00:00:00",
    ),  # youtube:3c5ef993b63d
    (
        "7df88cf7-364e-5187-a1b3-5fe59c3270af",
        "https://www.youtube.com/watch?v=p8-Idsh0kt0",
        "Bartimaeus Healed",
        "5/31/2026 —  5:00 pm Sunday evening service  -  Bartimaeus Healed — Bro. Sorin Filimon •  Mark 10:46-53\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Mark 10:46-53",
        "2026-06-01 00:00:00",
    ),  # youtube:5fe59c3270af
    (
        "6c2b8ba3-b77e-56dc-ad59-77609137cf09",
        "https://www.youtube.com/watch?v=TAZ3xjKRvIU",
        "Walking On Water",
        "5/31/2026 — 11:00 am Sunday morning service - Walking On Water — Rev. Mark Worthington • Matthew 14:25-32\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Matthew 14:25-32",
        "2026-05-31 00:00:00",
    ),  # youtube:77609137cf09
    (
        "35b42b71-8c9a-554a-b2cd-c4182feb541d",
        "https://www.youtube.com/watch?v=YkHs67VYMao",
        "Memorials",
        "5/24/2026 — 11:00 am Sunday morning service - Memorials - Bro. Noah Mocan • Psalm 77:1-12 Trinity Apostolic Faith Church, Sacramento County, California For more information, please visit us at www.afcsacramento.org, email: pete@sferle.com CCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Psalm 77:1-12",
        "2026-05-24 00:00:00",
    ),  # youtube:c4182feb541d
    (
        "29d068e5-7427-5e92-8769-c61cc153a562",
        "https://www.youtube.com/watch?v=cwswwdpEhTk",
        "Enduring",
        "5/17/2026 — 11:00 am Sunday morning service - Enduring — Rev. Mark Worthington • Haggai 2:1-9 Trinity Apostolic Faith Church, Sacramento County, California \nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com \nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Haggai 2:1-9",
        "2026-05-22 00:00:00",
    ),  # youtube:c61cc153a562
    (
        "058e0f23-5109-55d3-bc31-1b682ef62a2e",
        "https://www.youtube.com/watch?v=QLtIpwXz8FI",
        "Mother''s Day A Mother''s Influence",
        "5/10/2026 — 11:00 am Sunday morning service - Mother''s Day › A Mother''s Influence — Rev. Pete  Sferle • 2 Timothy  1:5; 3:14-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Timothy 1:5; 3:14-17",
        "2026-05-21 00:00:00",
    ),  # youtube:1b682ef62a2e
    (
        "2f4805f0-a895-5a3f-b268-ba1b68b46a29",
        "https://www.youtube.com/watch?v=z0aaRSOcjFg",
        "Youth/Children''s service — An Encounter with Jesus",
        "5/3/2026 —  5:00 pm Sunday evening Youth/Children''s service  - An Encounter with Jesus — Rev. Pete Sferle • Luke  19:1-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com  ♪♫\nCCLI Streaming Plus License #20833650",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Luke 19:1-10",
        "2026-05-21 00:00:00",
    ),  # youtube:ba1b68b46a29
    (
        "72290648-32ce-5569-bf63-f4994fe99ac6",
        "https://www.youtube.com/watch?v=Mi0iowwMlU4",
        "Beauty For Ashes",
        "5/3/2026 —  11:00 am Sunday morning service -  Beauty For Ashes — Bro. Sorin Filimon • Luke 4:14-22\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Luke 4:14-22",
        "2026-05-04 00:00:00",
    ),  # youtube:f4994fe99ac6
    (
        "fddeec44-5747-571d-9835-8af000068649",
        "https://www.youtube.com/watch?v=m6EsYcaQbkg",
        "O Lord Revive Us Again",
        "4/26/2026 — 11:00 am Sunday morning service - O Lord Revive Us Again — Rev. Pete Sferle • Psalm 85:6 › Scripture Jonah 3:1-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Psalm 85:6; Jonah 3:1-10",
        "2026-04-30 00:00:00",
    ),  # youtube:8af000068649
    (
        "1eb198a4-1a3b-51d0-9b97-08a9c6fc7019",
        "https://www.youtube.com/watch?v=AdvZAlz1ON8",
        "Abide in the Vine",
        "4/19/2026 —  5:00 pm Sunday evening service  -  Abide in the Vine — Bro. Sorin Filimon • John 15:1-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "John 15:1-8",
        "2026-04-21 00:00:00",
    ),  # youtube:08a9c6fc7019
    (
        "adcd5d18-dc2d-501e-9b98-a98c28d8ded0",
        "https://www.youtube.com/watch?v=InCeFI2pbS4",
        "The Rise of the Antichrist",
        "4/19/2026 —  11:00 am Sunday morning service - The Rise of the Antichrist — Rev. Pete Sferle • Revelation 2 Thessalonians 2:1-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Revelation 2 Thessalonians 2:1-12",
        "2026-04-19 00:00:00",
    ),  # youtube:a98c28d8ded0
    (
        "b6d7b026-043d-5a8d-b579-445e70e16433",
        "https://www.youtube.com/watch?v=vrKrsdSyaqs",
        "Only Jesus",
        "4/12/2026 —  5:00 pm Sunday evening youth service  -  Only Jesus — Bro. Noah Mocan • Acts 4:12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Acts 4:12",
        "2026-04-14 00:00:00",
    ),  # youtube:445e70e16433
    (
        "e70e50e0-c36b-5573-b25f-2c8d1b2d9d2a",
        "https://www.youtube.com/watch?v=pcxTQmvRR-E",
        "Evangelism",
        "4/12/2026 —  11:00 am Sunday morning service - Evangelism — Rev. Mark Worthington • John 9:24-34\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "John 9:24-34",
        "2026-04-12 00:00:00",
    ),  # youtube:2c8d1b2d9d2a
    (
        "baa3357c-9eb6-53c0-9eed-147add163496",
        "https://www.youtube.com/watch?v=9yXDIMzCh_g",
        "Easter Sunday morning service — Jesus, The Only One Who Conquered Death",
        "4/5/2026 —  11:00 am Easter Sunday morning service - Jesus, The Only One Who Conquered Death — Rev. Pete Sferle • 2 Timothy 2:8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Timothy 2:8",
        "2026-04-06 00:00:00",
    ),  # youtube:147add163496
    (
        "21033936-6015-5f4f-8de5-1c8f99c15845",
        "https://www.youtube.com/watch?v=bNLcP4nFp4o",
        "Good Friday evening service — Jesus The Lamb Of God",
        "4/3/2026 — 7:00 pm Good Friday evening service - Jesus The Lamb Of God — Rev. Pete Sferle • Revelation 5:6 Trinity Apostolic Faith Church, Sacramento County, California For more information, please visit us at www.afcsacramento.org, email: pete@sferle.com CCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Revelation 5:6",
        "2026-04-05 00:00:00",
    ),  # youtube:1c8f99c15845
    (
        "cc910286-2cb8-5611-93c0-794912dad4ca",
        "https://www.youtube.com/watch?v=FpCxNiXNNns",
        "Parable Of The Sower",
        "3/29/2026 —  5:00 pm Sunday evening service  -  Parable  Of The Sower — Bro. Sorin Filimon • Mark 4:1-20\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Mark 4:1-20",
        "2026-03-31 00:00:00",
    ),  # youtube:794912dad4ca
    (
        "7bb221b7-350d-5db1-b6b3-19545a164ad3",
        "https://www.youtube.com/watch?v=y8luUw1ONaA",
        "Palm Sunday — Seeing The Glory Of Jesus",
        "3/29/2026 — 11:00 am Sunday morning service - Palm Sunday - Seeing The Glory Of Jesus — Rev. Mark Worthington • Luke 19:28-38\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Luke 19:28-38",
        "2026-03-29 00:00:00",
    ),  # youtube:19545a164ad3
    (
        "585005a8-5234-5d0b-b437-acbbcfd0e91e",
        "https://www.youtube.com/watch?v=aco1rUHnE5Y",
        "Let Your Gentleness Be Known To All Men",
        "3/22/2026 —  11:00 am Sunday morning service - Let Your Gentleness Be Known To All Men — Rev. Pete Sferle • Philippians 4:5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Philippians 4:5",
        "2026-03-25 00:00:00",
    ),  # youtube:acbbcfd0e91e
    (
        "6323525e-a6a4-53b4-ace8-0d20f995c124",
        "https://www.youtube.com/watch?v=PgCn57nrwWU",
        "Be a Berean",
        "3/15/2026 —  2:15 pm Sunday youth afternoon service  -  Be a Berean — 1 Thessalonians 5:21 • Bro. Noah Mocan\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "1 Thessalonians 5:21",
        "2026-03-22 00:00:00",
    ),  # youtube:0d20f995c124
    (
        "fa8cbe95-8042-53b8-b0dc-1453ad1b26be",
        "https://www.youtube.com/watch?v=QdYSZ0FIuL0",
        "God''s Certain Judgement",
        "3/15/2026 — 11:00 am Sunday morning service - God''s Certain Judgement — Rev. Pete Sferle • 2 Peter 2:4-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Peter 2:4-9",
        "2026-03-17 00:00:00",
    ),  # youtube:1453ad1b26be
    (
        "b1f773e1-ddb2-5dbc-b90c-e01d53c658b3",
        "https://www.youtube.com/watch?v=NJMnfZa1uuk",
        "When You Can''t, God Can",
        "3/8/2026 —  11:00 am Sunday morning service - When You Can''t, God Can — Bro Sorin Filimon •  Isaiah 40:27:31\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro Sorin Filimon",
        "Isaiah 40:27:31",
        "2026-03-12 00:00:00",
    ),  # youtube:e01d53c658b3
    (
        "9ac31ef2-fea7-550e-93f4-bdea78bbc304",
        "https://www.youtube.com/watch?v=61ATmttbvV8",
        "Are You Ready?",
        "3/1/2026 —  5:00 pm Sunday morning service  -  Are You Ready? — Rev. Mark Worthington • Matthew 25:1-13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Matthew 25:1-13",
        "2026-03-02 00:00:00",
    ),  # youtube:bdea78bbc304
    (
        "cb471ff2-806f-5b37-a43d-26aaad0c3cf1",
        "https://www.youtube.com/watch?v=QPhi5DCvi_w",
        "No Man Can Serve Two Masters — Be on Alert of False Teachers",
        "3/1/2026 —  5:00 pm Sunday morning service - No Man Can Serve Two Masters — Be on Alert of False Teachers - 2 Peter 2:1-3\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        None,
        "2 Peter 2:1-3",
        "2026-03-02 00:00:00",
    ),  # youtube:26aaad0c3cf1
    (
        "9aa99f65-53cf-5ceb-9df0-bed44f5a4e6a",
        "https://www.youtube.com/watch?v=PrP1ihx53R8",
        "No Man Can Serve Two Masters",
        "2/22/2026 —  5:00 pm Sunday evening  service - No Man Can Serve Two Masters — Bro. Sorin Filimon • Matthew  6:24\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Matthew 6:24",
        "2026-02-23 00:00:00",
    ),  # youtube:bed44f5a4e6a
    (
        "38bc3242-3103-5073-acec-7e5227bb1351",
        "https://www.youtube.com/watch?v=dSBuuT1MpB0",
        "Why Not To Worry",
        "2/22/2026 — 11:00 am Sunday morning service - Why Not To Worry — Rev. Pete Sferle • St Matthew 6:25-34\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "St Matthew 6:25-34",
        "2026-02-23 00:00:00",
    ),  # youtube:7e5227bb1351
    (
        "1c4bbd66-2ef2-508c-a6a7-04aa2097fcbe",
        "https://www.youtube.com/watch?v=Lik9Kd4fjSI",
        "Where Is Wisdom Found?",
        "2/8/2026 —  5:00 pm Sunday evening youth service - Where Is Wisdom Found? — Bro. Noah Mocan • Job 28 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A ♪♫",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Job 28",
        "2026-02-15 00:00:00",
    ),  # youtube:04aa2097fcbe
    (
        "8af5c80d-ab44-54ef-b477-3f58f53a9e34",
        "https://www.youtube.com/watch?v=nlpVGBxZnbQ",
        "How Is Your Memory? The Importance Of Reminders",
        "2/1/26 —  11:00 am Sunday morning service - How Is Your Memory? The Importance Of Reminders — Rev. Pete Sferle • 2 Peter 1:12-15; Reading:  Joshua 4:19-24\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Peter 1:12-15; Joshua 4:19-24",
        "2026-02-02 00:00:00",
    ),  # youtube:3f58f53a9e34
    (
        "366d1b23-6998-5433-b0de-1d62d5099b34",
        "https://www.youtube.com/watch?v=qVZdLvqOUfc",
        "Dare To Be A Daniel",
        "1/25/26 — 11:00 am Sunday morning service -  Dare To Be A Daniel  — Rev. Mark Worthington • Daniel 1:8-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Daniel 1:8-17",
        "2026-01-25 00:00:00",
    ),  # youtube:1d62d5099b34
    (
        "ba506406-58ae-5adc-8fc7-13797681ea7e",
        "https://www.youtube.com/watch?v=z1MGUFAfyms",
        "Continue To Grow",
        "1/18/26 — 11:00 am Sunday morning service - Continue To Grow — Rev. Pete Sferle • 2 Peter 1: 5-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Peter 1: 5-11",
        "2026-01-19 00:00:00",
    ),  # youtube:13797681ea7e
    (
        "040a6d75-8bfb-5618-a7fe-6eaa8aa0d680",
        "https://www.youtube.com/watch?v=kLYEiA9aiPc",
        "The Greatest Of These",
        "1/11/26 —  5:00 pm Sunday evening youth service - The Greatest Of These — Bro. Noah Mocan • 1 Corinthians 13:13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "1 Corinthians 13:13",
        "2026-01-12 00:00:00",
    ),  # youtube:6eaa8aa0d680
    (
        "9db19091-aa8e-5f5a-99f6-5aeb54270f19",
        "https://www.youtube.com/watch?v=xaeV79qTwvY",
        "God Gives Us Everything To Live A Godly Life",
        "1/11/26 —  11:00 am Sunday morning service - God Gives Us Everything To Live A Godly Life — Rev. Pete Sferle • 2 Peter 1:3-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Peter 1:3-4",
        "2026-01-12 00:00:00",
    ),  # youtube:5aeb54270f19
    (
        "4b0e6635-0eb5-58e1-bb52-14edfdcf8f3b",
        "https://www.youtube.com/watch?v=GYHGHR11e-4",
        "God Gives Us Everything To Live A Godly Life",
        "1/11/26 —  11:00 am Sunday morning service - God Gives Us Everything To Live A Godly Life — Rev. Pete Sferle • 2 Peter 1:3-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Peter 1:3-4",
        "2026-01-12 00:00:00",
    ),  # youtube:14edfdcf8f3b
    (
        "c4ce6334-0ab7-5824-a523-cbd4e8fb396e",
        "https://www.youtube.com/watch?v=eOMTswZwpTw",
        "Grace and Peace be Multiplied to You!",
        "1/4/26 — 11:00 am Sunday morning service - Grace and Peace be Multiplied to You! — Rev. Pete Sferle • 2 Peter 1:1-2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Peter 1:1-2",
        "2026-01-10 00:00:00",
    ),  # youtube:cbd4e8fb396e
    (
        "964ebb54-b6f4-5a4c-ad60-f760a0406562",
        "https://www.youtube.com/watch?v=f0FPPR0LAWs",
        "The Wise Men",
        "12/28/25 — 11:00 am Sunday morning service - The Wise Men — Bro. Sorin Filimon • Matthew 2:1-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Matthew 2:1-12",
        "2026-01-03 00:00:00",
    ),  # youtube:f760a0406562
    (
        "a65bb901-7af9-5ace-aa48-a04d420275ad",
        "https://www.youtube.com/watch?v=TK3BV_wdd7k",
        "Anticipating Our Lord''s Soon Return",
        "Sunday Morning 11:00 am December 21, 2025 • Anticipating Our Lord''s Soon Return — Rev. Jeffery Downey • Acts 1:9-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\n\nCCLI Streaming license #20833650 A+",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Jeffery Downey",
        "Acts 1:9-11",
        "2025-12-22 00:00:00",
    ),  # youtube:a04d420275ad
    (
        "5e101b94-99a8-56de-9a48-ce3d2afdd632",
        "https://www.youtube.com/watch?v=bXTxiZv0KCY",
        "Joseph — An Example Of Obedience",
        "Chanukah begins • 12/14/25 —  11:00 am Sunday morning service - Joseph - An Example Of Obedience — Bro. Sorin Filimon • Matthew 1:24; 2:12, Luke 1:38; 2:15 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Matthew 1:24; 2:12, Luke 1:38; 2:15",
        "2025-12-15 00:00:00",
    ),  # youtube:ce3d2afdd632
    (
        "976ca1e3-791b-5cc6-91c9-622139f7c5e8",
        "https://www.youtube.com/watch?v=ZQNeyxT_42s",
        "The Lord Is My Shepherd",
        "12/7/25 —  5:00 pm Sunday evening service - The Lord Is My Shepherd — Bro. Noah Mocan • Psalm 23\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Psalm 23",
        "2025-12-10 00:00:00",
    ),  # youtube:622139f7c5e8
    (
        "ccf40be1-b1a7-5553-bcc3-5ebdd6701dcb",
        "https://www.youtube.com/watch?v=Lmz5OYTiaJk",
        "Godliness with Contentment is Great Gain — (Medford, OR)",
        "11/30/25 —  11:00 am Sunday morning service - Godliness with Contentment is Great Gain — Rev. John Baros (Medford, OR)• 1 Timothy 6:1-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. John Baros",
        "1 Timothy 6:1-12",
        "2025-12-03 00:00:00",
    ),  # youtube:5ebdd6701dcb
    (
        "1ce93c74-7b6f-5681-b181-2b390a314266",
        "https://www.youtube.com/watch?v=SbAxS3U2NoA",
        "Thanksgiving",
        "11/23/25 —  11:00 am Sunday morning service - Thanksgiving — Bro Sorin Filimon • Colossians 3:15-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro Sorin Filimon",
        "Colossians 3:15-17",
        "2025-11-27 00:00:00",
    ),  # youtube:2b390a314266
    (
        "96d48277-0ae2-5347-992b-eb034b3ad86f",
        "https://www.youtube.com/watch?v=uOYSXj39KJY",
        "Who Is God",
        "11/16/25 —  5:00 pm Sunday evening youth service - Who Is God — Bro. Noah Mocan • Exodus 3:13-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Exodus 3:13-14",
        "2025-11-23 00:00:00",
    ),  # youtube:eb034b3ad86f
    (
        "6d82f437-640f-5085-93eb-50b7f26c2e64",
        "https://www.youtube.com/watch?v=DfAE20yEd1U",
        "Daniel — Conceal Until The End — When Travel And Knowledge Shall Be Increased",
        "11/16/25 —  11:00 am Sunday morning service - Daniel - Conceal Until The End - When Travel And Knowledge Shall Be Increased — Rev. Pete Sferle • Daniel 12:4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or email pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Daniel 12:4",
        "2025-11-17 00:00:00",
    ),  # youtube:50b7f26c2e64
    (
        "34ac0e08-c60c-5e26-8b9e-50afab95e61b",
        "https://www.youtube.com/watch?v=kMzHnLQ-660",
        "Three More Signs That Point To Jesus'' Soon Return: Deceivers, Scoffers, And Lawlessness",
        "11/9/25 —  11:00 am Sunday morning service - Three More Signs That Point To Jesus'' Soon Return: Deceivers, Scoffers, And Lawlessness — Rev . Pete Sferle • Matthew 24: 4-5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev . Pete Sferle",
        "Matthew 24: 4-5",
        "2025-11-10 00:00:00",
    ),  # youtube:50afab95e61b
    (
        "7918779e-516e-5a7d-8578-6308a5389bc5",
        "https://www.youtube.com/watch?v=3_qCrrYHFvo",
        "The First Rain And The Latter Rain",
        "11/2/25 —  5:00 pm Sunday evening service -The First Rain And The Latter Rain — Rev. Pete Sferle • Deuteronomy 11:10-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org, email: pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Deuteronomy 11:10-14",
        "2025-11-08 00:00:00",
    ),  # youtube:6308a5389bc5
    (
        "63086f51-be20-54d5-b582-e0487371886e",
        "https://www.youtube.com/watch?v=PVlFhj8S_L4",
        "Spiritual Warfare",
        "11/2/25 —  11:00 am Sunday morning service - Spiritual Warfare — Rev. Mark Worthington •  Ephesians 6:10-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Ephesians 6:10-19",
        "2025-11-08 00:00:00",
    ),  # youtube:e0487371886e
    (
        "3f1e075e-c7f1-5097-985f-4219ba211e5b",
        "https://www.youtube.com/watch?v=0iWj_L8iS-Q",
        "Baby Dedication Except the Lord Build a House",
        "10/26/25 —  11:00 am Sunday morning service - Baby Dedication › Mark 10:13-16 • Except the Lord Build a House — Rev. Pete Sferle • Psalm 127: 1-5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Mark 10:13-16; Psalm 127: 1-5",
        "2025-10-26 00:00:00",
    ),  # youtube:4219ba211e5b
    (
        "6a931e7b-7e4a-51ae-84a6-74a63e697c8e",
        "https://www.youtube.com/watch?v=xRrkHeW_U00",
        "Called & Enabled",
        "10/19/25 —  5:00 pm Sunday evening Youth Service • Called & Enabled — Bro. Noah Mocan — Isaiah 6:5-8 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org  email: pete@sferle.com \nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Isaiah 6:5-8",
        "2025-10-20 00:00:00",
    ),  # youtube:74a63e697c8e
    (
        "380146f9-d00a-5fdf-bcae-3ef4171f10e5",
        "https://www.youtube.com/watch?v=wEFgYkklPcI",
        "\"Israel\" The Sign Of Jesus''s Soon Return — Scripture Reading",
        "10/19/25 —  11:00 am Sunday morning service - \"Israel\" The Sign Of Jesus''s Soon Return — Rev. Pete Sferle • Matthew 24:1-2 » Scripture Reading – Matthew 24:33-39 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Matthew 24:1-2; Matthew 24:33-39",
        "2025-10-19 00:00:00",
    ),  # youtube:3ef4171f10e5
    (
        "75a0eecb-a574-5252-a0d5-24e1ce7deeed",
        "https://www.youtube.com/watch?v=2Ksn2ueLivk",
        "The Armor Of God",
        "10/12/25 —  5:00 pm Sunday evening service  The Armor Of God — Bro. Noah Mocan • Ephesians 6:10-20\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Ephesians 6:10-20",
        "2025-10-18 00:00:00",
    ),  # youtube:24e1ce7deeed
    (
        "0165369d-d609-5e57-b6c9-3fb6f5c7c355",
        "https://www.youtube.com/watch?v=HYGUJyirt98",
        "Understanding The Real Battle",
        "10/12/25 —  11:00 am Sunday morning service - Understanding The Real Battle — Rev. Mark Worthington • 1 Samuel 17:1-50\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "1 Samuel 17:1-50",
        "2025-10-13 00:00:00",
    ),  # youtube:3fb6f5c7c355
    (
        "1b131820-22bb-5bf3-a944-523bbd6fca3b",
        "https://www.youtube.com/watch?v=tIbqLOQ9pnE",
        "Marvelous are thy works",
        "10/5/25 —  5:00 pm Sunday evening service - Marvelous are thy works — Bro. Sorin Filimon  • Rev 15:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Rev 15:1-4",
        "2025-10-12 00:00:00",
    ),  # youtube:523bbd6fca3b
    (
        "c7e70775-cd20-556a-a6c1-6d2b979b552b",
        "https://www.youtube.com/watch?v=aX6_RaIsAL8",
        "God''s Grace Is More Than Enough",
        "10/5/25 —  11:00 am Sunday morning service - God''s Grace Is More Than Enough — Rev. Pete Sferle • 2 Corinthians 12:9-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org or\nemail pete@sferle.com\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Corinthians 12:9-11",
        "2025-10-11 00:00:00",
    ),  # youtube:6d2b979b552b
    (
        "8b711cc9-95b2-515d-b575-13579700632a",
        "https://www.youtube.com/watch?v=YgaURMaRQzk",
        "Rooted And Grounded In Love",
        "9/28/25 —  5:00 pm Sunday evening service -  Rooted And Grounded In Love — Rev. Nick Segres Jr. • Ephesians 3:14-21 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Nick Segres Jr.",
        "Ephesians 3:14-21",
        "2025-10-05 00:00:00",
    ),  # youtube:13579700632a
    (
        "5276b50c-3506-51cc-8c61-b7f4327ded1d",
        "https://www.youtube.com/watch?v=mOi52Gze8eM",
        "Rooted And Grounded In Love",
        "9/28/25 —  11:00 am Sunday morning service -  Rooted And Grounded In Love — Rev. Nick Segres Jr. • Ephesians 3:14-21 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Nick Segres Jr.",
        "Ephesians 3:14-21",
        "2025-10-05 00:00:00",
    ),  # youtube:b7f4327ded1d
    (
        "29908f03-67cd-52b3-80a7-94709a09a522",
        "https://www.youtube.com/watch?v=5GbY9bYxkck",
        "Rooted And Grounded In Love",
        "9/26/2025 —  8:00 pm Friday evening service - Rooted And Grounded In Love — Rev. Nick Segres Jr. • Ephesians 3:14-21 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Nick Segres Jr.",
        "Ephesians 3:14-21",
        "2025-09-27 00:00:00",
    ),  # youtube:94709a09a522
    (
        "05e91e0d-90c2-5c1e-9b44-1587b322dea2",
        "https://www.youtube.com/watch?v=xHg8aIzEpQI",
        "Christ''s Supremacy And Sufficiency",
        "9/21/25 —  11:00 am Sunday morning youth service - Christ''s Supremacy And Sufficiency — Bro. Noah Mocan • Colossians 1:14-16, 2:9-10, 3:17 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Colossians 1:14-16, 2:9-10, 3:17",
        "2025-09-26 00:00:00",
    ),  # youtube:1587b322dea2
    (
        "d32f48fb-f43f-5c31-8b94-fae595855899",
        "https://www.youtube.com/watch?v=AWIfIRYnW40",
        "Fight the Good Fight of Faith",
        "9/14/2025 5:00 pm Sunday  evening - Fight the Good Fight of Faith — Bro.  Sorin Filimon •  1 Timothy 6:11-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "1 Timothy 6:11-12",
        "2025-09-16 00:00:00",
    ),  # youtube:fae595855899
    (
        "6504983a-1156-5ddf-8988-a8177db3b420",
        "https://www.youtube.com/watch?v=SObVSpcyxNs",
        "A Sermon To Die For",
        "9/14/25 —  11:00 am Sunday morning service -  A Sermon To Die For — Rev. Mark Worthington • Acts 20:6-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Acts 20:6-12",
        "2025-09-14 00:00:00",
    ),  # youtube:a8177db3b420
    (
        "9c88da49-b554-5aea-a69e-43307a411857",
        "https://www.youtube.com/watch?v=A7KF7fic5ZQ",
        "A Tree Planted By The River",
        "9/7/2025 5:00 pm Sunday  evening A Tree Planted By The River — Bro. Sorin Filimon • Psalm 1:3\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Psalm 1:3",
        "2025-09-08 00:00:00",
    ),  # youtube:43307a411857
    (
        "34b4f310-09e3-5698-aa89-375c619e62d0",
        "https://www.youtube.com/watch?v=wx3QR-4Xy_E",
        "The Pretribulation Rapture",
        "9/7/25 —  11:00 am Sunday morning service -  The Pretribulation Rapture — Rev. Pete Sferle • 2 Thessalonians 2:1-17 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Thessalonians 2:1-17",
        "2025-09-07 00:00:00",
    ),  # youtube:375c619e62d0
    (
        "2a7f3b7f-9140-5eca-8051-98959a25fbf0",
        "https://www.youtube.com/watch?v=gk-2vgHvuHY",
        "Bringing Our Children To Jesus",
        "8/31/25 —  11:00 am Sunday morning service - Bringing Our Children To Jesus — Rev. Pete Sferle • Mark 10:13-16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Mark 10:13-16",
        "2025-09-03 00:00:00",
    ),  # youtube:98959a25fbf0
    (
        "2f2425a8-1e35-55eb-ac82-4e7c5a0c6b23",
        "https://www.youtube.com/watch?v=XQCg2NYgpFA",
        "What Have You Come to See?",
        "8/24/25 —  5:00 pm Sunday evening service - What Have You Come to See? — Bro. Sorin Filimon • Matthew 11:7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Matthew 11:7",
        "2025-08-29 00:00:00",
    ),  # youtube:4e7c5a0c6b23
    (
        "0bdfb492-fcb9-5b26-bd22-31d7348e0a54",
        "https://www.youtube.com/watch?v=Of0KXn-DyGs",
        "A Courageous Heart",
        "8/24/25 —  11:00 am Sunday morning service - A Courageous Heart — Rev.  Mark Worthington • Joshua 1:1-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Joshua 1:1-9",
        "2025-08-24 00:00:00",
    ),  # youtube:31d7348e0a54
    (
        "599132eb-6be8-58a0-a90d-e65bf19a8e2a",
        "https://www.youtube.com/watch?v=Peq6pwSof70",
        "Be Ye Ready",
        "8/17/25 11:00 am Sunday morning service Be Ye Ready — Rev. Pete Sferle • 1 Thessalonians 4:13-18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Thessalonians 4:13-18",
        "2025-08-18 00:00:00",
    ),  # youtube:e65bf19a8e2a
    (
        "29ea2900-aa5f-5b5a-aec7-7a46519ed02a",
        "https://www.youtube.com/watch?v=3bm1rWz20Wk",
        "Follow The Instructions",
        "8/17/2025 2:00 pm Sunday afternoon youth service Follow The Instructions — Bro. Noah Mocan • 2 Timothy 3:14-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "2 Timothy 3:14-17",
        "2025-08-18 00:00:00",
    ),  # youtube:7a46519ed02a
    (
        "41ba2edc-644b-5e37-8958-313e183d8bcb",
        "https://www.youtube.com/watch?v=LC4chVnrJvw",
        "Where Are The Spiritual Potholes? Know Your Enemy",
        "8/10/25 —  5:00 pm Sunday evening service - Where Are The Spiritual Potholes? Know Your Enemy\xa0- Rev. Mark Worthington • Luke 10:20\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Luke 10:20",
        "2025-08-15 00:00:00",
    ),  # youtube:313e183d8bcb
    (
        "5a45a2ab-572c-5855-950f-da81fe1fa875",
        "https://www.youtube.com/watch?v=R6RijzD6Duc",
        "You Are Fearfully and Wonderfully Made",
        "8/10/25 —  11:00 am Sunday morning service - You Are Fearfully and Wonderfully Made — Rev. Pete Sferle • Psalms 139:14-18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Psalms 139:14-18",
        "2025-08-10 00:00:00",
    ),  # youtube:da81fe1fa875
    (
        "7cb4dfe8-e95d-5959-9226-85a7238fc16d",
        "https://www.youtube.com/watch?v=7YWYt5UnSPc",
        "Biblical Prayer",
        "8/03/2025 5:00 pm Sunday evening  —  Biblical Prayer — Bro. Noah Mocan • Matthew 6:5-13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Matthew 6:5-13",
        "2025-08-07 00:00:00",
    ),  # youtube:85a7238fc16d
    (
        "067e8738-30fd-5d23-a81c-2547471d6a4a",
        "https://www.youtube.com/watch?v=Dkjb_Jqp-YU",
        "How Do We seek God",
        "8/3/25 —  11:00 am Sunday morning service - How Do We seek God — Bro. Sorin Filimon • Deuteronomy 4:29-30\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Deuteronomy 4:29-30",
        "2025-08-03 00:00:00",
    ),  # youtube:2547471d6a4a
    (
        "9a4a1a11-2ca7-5d72-be1d-f4517074b6b9",
        "https://www.youtube.com/watch?v=b0hknzlbQUs",
        "Palm Branches & Willow Branches",
        "7/27/2025 11:00 am Sunday morning  —  Palm Branches & Willow Branches — Rev. Mark Worthington • Leviticus 23:40\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Leviticus 23:40",
        "2025-08-02 00:00:00",
    ),  # youtube:f4517074b6b9
    (
        "43be8242-1a2b-539e-a3e5-9cab740babbf",
        "https://www.youtube.com/watch?v=PA3IKiioo7c",
        "Seeking The Lord Is Like Seeking For the Monalisa",
        "7/20/2025 11:00 am Sunday morning — Seeking The Lord Is Like Seeking For the Monalisa —  Bro. Sorin Filimon • Matthew 7:7-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Matthew 7:7-11",
        "2025-07-23 00:00:00",
    ),  # youtube:9cab740babbf
    (
        "f38ec1a2-56a7-522d-946b-c60226993941",
        "https://www.youtube.com/watch?v=NXmAN64kf0k",
        "Seek The Lord In Righteousness",
        "6/22/2025 11:00 am Sunday morning  —  Seek The Lord In Righteousness — Rev. Mark Worthington • 2 Chronicles 7:1-3\n\nTrinity Apostolic Faith Church, Sacramento County, California\n\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "2 Chronicles 7:1-3",
        "2025-06-27 00:00:00",
    ),  # youtube:c60226993941
    (
        "d114d4d2-a1eb-564e-8613-4f8579dc2491",
        "https://www.youtube.com/watch?v=J0MH3Lid-qo",
        "What Is Truth",
        "6/15/2025 —  11:00 am Sunday morning service - What Is Truth — Bro. Sola Omolayo • Daniel 2: 47\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sola Omolayo",
        "Daniel 2: 47",
        "2025-06-15 00:00:00",
    ),  # youtube:4f8579dc2491
    (
        "c4391bff-ba0c-5644-8a95-e34b61a93a9c",
        "https://www.youtube.com/watch?v=ezrNjeGbsxY",
        "Stand In God''s Grace",
        "6/8/2025 11:00 am Sunday morning — Stand In God''s Grace — Rev. Pete Sferle • 1 Peter 5:12-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 5:12-14",
        "2025-06-09 00:00:00",
    ),  # youtube:e34b61a93a9c
    (
        "5696b4a2-ceba-5ad1-aef3-453593163b38",
        "https://www.youtube.com/watch?v=81ydXwlXwNU",
        "From Good To Better",
        "6/1/25 —  5:00 pm Sunday evening service - From Good To Better  — Bro. Noah Mocan • 2 Corinthians 3:6-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "2 Corinthians 3:6-9",
        "2025-06-04 00:00:00",
    ),  # youtube:453593163b38
    (
        "653aed0f-406c-5f2b-8d72-424524e1dcfe",
        "https://www.youtube.com/watch?v=YOoDBFMSz8M",
        "Resisting The Devil! Successfully Like Jesus Did",
        "6/1/2025 11:00 am Sunday morning Resisting The Devil! Successfully Like Jesus Did —  Bro. Pete Sferle • 1 Peter 5:8-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Pete Sferle",
        "1 Peter 5:8-11",
        "2025-06-01 00:00:00",
    ),  # youtube:424524e1dcfe
    (
        "0e601663-7192-5a5a-91d8-3dc2c9a3b04d",
        "https://www.youtube.com/watch?v=cIjfKimlwAQ",
        "A Caring God To Cast Your Cares Upon",
        "5/25/2025 11:00 am Sunday morning — A Caring God To Cast Your Cares Upon — Rev. Pete Sferle • 1 Peter 5:7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 5:7",
        "2025-05-25 00:00:00",
    ),  # youtube:3dc2c9a3b04d
    (
        "dd539277-0b01-569e-a72d-b8e39986ac49",
        "https://www.youtube.com/watch?v=L3P7_4MXJPk",
        "Who Can Find A Virtues Woman?",
        "5/11/2025 11:00 am Sunday morning —  Who Can Find A Virtues Woman? — Rev. Pete Sferle • Proverbs 31:10-31\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Proverbs 31:10-31",
        "2025-05-11 00:00:00",
    ),  # youtube:b8e39986ac49
    (
        "3862c21b-8b7e-5f58-a46a-5e1dcb1133de",
        "https://www.youtube.com/watch?v=4UiWD9zIw90",
        "Divine Direction",
        "5/4/2025 —  5:00 pm Sunday evening service - Divine Direction — Rev. Mark Worthington • Proverbs 3:3-5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Proverbs 3:3-5",
        "2025-05-10 00:00:00",
    ),  # youtube:5e1dcb1133de
    (
        "0d781c6f-d575-5cbb-b3b4-1f2e2910c8f0",
        "https://www.youtube.com/watch?v=KiN7xyHHyUs",
        "Be Clothed with Humility",
        "5/4/2025 11:00 am Sunday morning service - Be Clothed with Humility — Rev. Pete Sferle • 2 Peter 5:5-6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "2 Peter 5:5-6",
        "2025-05-06 00:00:00",
    ),  # youtube:1f2e2910c8f0
    (
        "c6a45986-4583-5aed-9642-beaf07782d55",
        "https://www.youtube.com/watch?v=auIFHitVPqU",
        "Making Decisions Gods Way",
        "04/27/2025 — 5:00 pm Sunday evening service - Making Decisions Gods Way — Rev. Mark Worthington • Mark 16:15\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Mark 16:15",
        "2025-05-02 00:00:00",
    ),  # youtube:beaf07782d55
    (
        "e461ec89-2407-5ffa-a1f1-9cd0fb30317d",
        "https://www.youtube.com/watch?v=gUqLjMl8Cjk",
        "Exhortation and Encouragement from . Pete Sferle",
        "4/27/2025 11:00 am Sunday morning — Exhortation and Encouragement from 1 Peter 5:1-4 — Rev. Pete Sferle \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 5:1-4 — Rev",
        "2025-04-27 00:00:00",
    ),  # youtube:9cd0fb30317d
    (
        "6e5da48c-92bb-5fa2-b7de-34c22608a541",
        "https://www.youtube.com/watch?v=T5ZLh8UQmJc",
        "Remember The Truth: God Cares",
        "04/20/2025 — Sunday evening service - Remember The Truth: God Cares  — Bro. Noah Mocan • Psalm 22\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming Plus License #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Psalm 22",
        "2025-04-27 00:00:00",
    ),  # youtube:34c22608a541
    (
        "5fcdf5e3-b504-539e-98ff-536a4d646dd1",
        "https://www.youtube.com/watch?v=CeELU6iv0R4",
        "Easter Sunday",
        "4/20/2025 11:00 am morning service - Easter Sunday — Rev. Pete Sferle • Luke 24:1-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Luke 24:1-12",
        "2025-04-20 00:00:00",
    ),  # youtube:536a4d646dd1
    (
        "d07e57a5-0494-5692-8668-88e8ecbcbd55",
        "https://www.youtube.com/watch?v=Q5DB7YHRz_0",
        "Good Friday",
        "04/18/2025 7:00 pm\xa0— Good Friday — Rev. Mark Worthington • Hebrews 12:2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Hebrews 12:2",
        "2025-04-19 00:00:00",
    ),  # youtube:88e8ecbcbd55
    (
        "f4552ac8-cb86-5206-bb54-154cf83c2d97",
        "https://www.youtube.com/watch?v=GdkRv5mOxQg",
        "God Deeply Cares",
        "04/13/2025 — Sunday evening youth service -  God Deeply Cares — Bro. Noah Mocan • John 3:16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "John 3:16",
        "2025-04-14 00:00:00",
    ),  # youtube:154cf83c2d97
    (
        "0894e970-a5c8-5d5e-aa12-fe17579856ef",
        "https://www.youtube.com/watch?v=TVCB6cfBUo8",
        "Palm Sunday morning",
        "4/13/2025 11:00 am Palm Sunday morning — Rev. Pete Sferle • Luke 19:28-40 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Luke 19:28-40",
        "2025-04-13 00:00:00",
    ),  # youtube:fe17579856ef
    (
        "2fc20ec0-35d5-51dd-b902-20522c2a8f78",
        "https://www.youtube.com/watch?v=Dpk1sAGq08w",
        "Meekness",
        "4/6/2025 11:00 am Sunday morning service • Meekness — Rev. Mark Worthington • Galatians 5:16-25\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Galatians 5:16-25",
        "2025-04-07 00:00:00",
    ),  # youtube:20522c2a8f78
    (
        "835e7aee-3e19-52bb-8e71-049b52eaa4e6",
        "https://www.youtube.com/watch?v=HEVE97IVn7A",
        "Think It Not Strange",
        "3/30/2025 11:00 am Sunday morning service - Think It Not Strange — Rev. Pete Sferle • 1 Peter 4:12-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 4:12-19",
        "2025-03-31 00:00:00",
    ),  # youtube:049b52eaa4e6
    (
        "f470c249-7307-5af0-8a7a-e9f5d856181d",
        "https://www.youtube.com/watch?v=hBnqnr5Aq9E",
        "The End Of All Things Is At Hand So Serve God And Others With The Gift He Has Given You",
        "3/23/2025 11:00 am Sunday morning service • The End Of All Things Is At Hand So Serve God And Others With The Gift He Has Given You — Rev Pete Sferle - 1 Peter 4:7-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev Pete Sferle",
        "1 Peter 4:7-11",
        "2025-03-29 00:00:00",
    ),  # youtube:e9f5d856181d
    (
        "f263632e-a870-5892-82a9-d2e6d1f596ca",
        "https://www.youtube.com/watch?v=swKewCNhjSs",
        "Bringing Our Questions Before God",
        "Bringing Our Questions Before God — Bro. Noah Mocan • Matthew 7:7-11\n 03/16/2025 — Sunday evening Youth service \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Matthew 7:7-11",
        "2025-03-22 00:00:00",
    ),  # youtube:d2e6d1f596ca
    (
        "61091ade-c201-5899-8986-181ae0f24b46",
        "https://www.youtube.com/watch?v=s84CQlSi8Gk",
        "The End Is At Hand, So Fervently Love One Another",
        "3/16/2025 11:00 am Sunday morning service - The End Is At Hand, So Fervently Love One Another — Rev. Pete Sferle • 1 Peter 4:7-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 4:7-8",
        "2025-03-17 00:00:00",
    ),  # youtube:181ae0f24b46
    (
        "9705e94b-d061-5b49-b5a4-072be889366c",
        "https://www.youtube.com/watch?v=rX0P55jQem4",
        "Reading The Signs Of The Times",
        "3/9/2025 11:00 am Sunday morning service Reading The Signs Of The Times — Rev. Mark Worthington • Matthew 16: 1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Matthew 16: 1-4",
        "2025-03-10 00:00:00",
    ),  # youtube:072be889366c
    (
        "72a0e5e0-d79a-503e-8ef2-47be1fa4e47b",
        "https://www.youtube.com/watch?v=oASWK6_yhds",
        "The End is Near, Be Ready, Watching and Praying",
        "3/2/2025 11:00 am Sunday morning — The End is Near, Be Ready, Watching and Praying — Rev. Pete Sferle • 1 Peter 4:7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 4:7",
        "2025-03-03 00:00:00",
    ),  # youtube:47be1fa4e47b
    (
        "12fae71f-5c75-5911-9e1d-c6649925a2c3",
        "https://www.youtube.com/watch?v=4Jrs_iS1_yY",
        "Are we a Thermometer or Thermostat?",
        "Are we a Thermometer or Thermostat? • Bro. Mark Worthington — Revelation 3:14-22\n2/23/2025 11:00 am Sunday morning service\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Mark Worthington",
        "Revelation 3:14-22",
        "2025-02-23 00:00:00",
    ),  # youtube:c6649925a2c3
    (
        "a1d1bb18-b47f-5f5a-b31c-1dbca3425bdb",
        "https://www.youtube.com/watch?v=vBzYBKo6UuA",
        "Victory In Jesus — — Youth Service",
        "Victory In Jesus — Bro. Noah Mocan • 1 Corinthians 15:50 - 57 — Youth Service\n 02/09/2025 — Sunday afternoon Youth service • • • after the potluck\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "1 Corinthians 15:50 - 57",
        "2025-02-17 00:00:00",
    ),  # youtube:1dbca3425bdb
    (
        "e9c249e6-c0d8-5d9b-a5e0-4d04058ac977",
        "https://www.youtube.com/watch?v=emQodedIdUE",
        "Deny Yourself and Follow Jesus",
        "11:00 am Sunday 2/9/2025 • Deny Yourself and Follow Jesus — Bro. Sorin Filimon • Matthew 16:24-28\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Matthew 16:24-28",
        "2025-02-16 00:00:00",
    ),  # youtube:4d04058ac977
    (
        "ada6f2e2-5a69-53a7-be07-c59f8f60389b",
        "https://www.youtube.com/watch?v=dBg0YR3-0bA",
        "The Good Sheep",
        "11:00 am Sunday 2/2/2025 - The Good Sheep — Bro. Sorin Filimon • John 10:22-29\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "John 10:22-29",
        "2025-02-03 00:00:00",
    ),  # youtube:c59f8f60389b
    (
        "e5afa805-e004-5bed-a385-c0f123198dcc",
        "https://www.youtube.com/watch?v=_mSyPhQ06Nc",
        "From Glory To Glory",
        "11:00 am Sunday 1/26/2025 • From Glory To Glory • Bro. Sorin Filimon — 2 Corinthians 3:18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "2 Corinthians 3:18",
        "2025-01-31 00:00:00",
    ),  # youtube:c0f123198dcc
    (
        "74247510-2f58-591c-aaa9-2a923ea6c7f7",
        "https://www.youtube.com/watch?v=1ktdWS7JbvA",
        "The Object Of Our Faith — , 6 — 8",
        "1/26/2025 Sunday evening youth service 5:00 pm - The Object Of Our Faith — Bro. Noah Mocan • Hebrews 11:1, 6-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Hebrews 11:1",
        "2025-01-28 00:00:00",
    ),  # youtube:2a923ea6c7f7
    (
        "d3990322-c1b0-5403-b7cb-f37f88570db8",
        "https://www.youtube.com/watch?v=IjwFANETdME",
        "They Think It Strange That Ye Run Not With Them",
        "11:00 am Sunday 1/19/2025 • They Think It Strange That Ye Run Not With Them — Rev. Pete Sferle • 1 Peter 4:1-6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 4:1-6",
        "2025-01-20 00:00:00",
    ),  # youtube:f37f88570db8
    (
        "b2f1effa-5db8-5394-8598-f7bc638a7d58",
        "https://www.youtube.com/watch?v=B9F879nkxQg",
        "An Old Challenge For A New Year",
        "1/12/2025 Sunday evening service 5:00 pm - An Old Challenge For A New Year • Rev. Mark Worthington — Colossians 3:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Colossians 3:1-4",
        "2025-01-13 00:00:00",
    ),  # youtube:f7bc638a7d58
    (
        "a29c1996-af31-5452-a453-6b864695fe52",
        "https://www.youtube.com/watch?v=_59WxofkwfU",
        "When You Suffer For Christ''s Sake",
        "Sunday Morning 11:00 am January 12, 2025  -  • Rev. Pete Sferle — 1 Peter 3:13-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 3:13-17",
        "2025-01-12 00:00:00",
    ),  # youtube:6b864695fe52
    (
        "cc0670b3-45bc-5ec5-8ecf-b3f9911950eb",
        "https://www.youtube.com/watch?v=Dnpj0b3KjZ0",
        "Be Connected To The Vine This Coming Year",
        "11:00 am Sunday 1/5/2025 • Be Connected To The Vine This Coming Year — Bro. Toinda Gono • John 15:1-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Toinda Gono",
        "John 15:1-8",
        "2025-01-06 00:00:00",
    ),  # youtube:b3f9911950eb
    (
        "9cf4c71e-b9a8-5705-98fd-1612d16bbf52",
        "https://www.youtube.com/watch?v=0M-9A88CVPo",
        "Living Our Lives With Trust in God and Honoring Him in Humility and Obedience",
        "Sunday Morning 11:00 am December 29, 2024  - Living Our Lives With Trust in God and Honoring Him in Humility and Obedience.  •  Rev. Pete Sferle — Proverbs 3:1-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Proverbs 3:1-10",
        "2024-12-30 00:00:00",
    ),  # youtube:1612d16bbf52
    (
        "18521ab1-cc6b-5c24-bdd8-bfd0ab91fe86",
        "https://www.youtube.com/watch?v=82eF0C5n30k",
        "Gabriel''s Conversation With Mary",
        "Sunday Morning 11:00 am December 15, 2024 • Gabriel''s Conversation With Mary — Rev. Pete Sferle • Luke 1: 26:38\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Luke 1: 26:38",
        "2024-12-16 00:00:00",
    ),  # youtube:bfd0ab91fe86
    (
        "7e90791e-f7db-546e-9456-6755c85210be",
        "https://www.youtube.com/watch?v=zsptMViyDpY",
        "Christmas Is For Thanks — Giving",
        "Sunday evening service 5:00 pm - Christmas Is For Thanks-Giving — Rev. Mark Worthington • Philippians 4:6-7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Philippians 4:6-7",
        "2024-12-14 00:00:00",
    ),  # youtube:6755c85210be
    (
        "9af0ac0c-901c-5a7b-a662-749e9229825b",
        "https://www.youtube.com/watch?v=oE2-SlQLeKw",
        "Treatment of Our Christian Brother and Sisters",
        "11:00 am Sunday 12/8/2024 • Treatment of Our Christian Brother and Sisters — Rev. Pete Sferle • 1 Peter 3:8-13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 3:8-13",
        "2024-12-09 00:00:00",
    ),  # youtube:749e9229825b
    (
        "f35440d8-4de0-5719-a3db-cddc750f5045",
        "https://www.youtube.com/watch?v=Xf1v-Q2wKVk",
        "Unto Us a Son Is Given",
        "Sunday Morning 11:00 am December 17, 2024 • Unto Us a Son Is Given — Bro. Sorin Filimon • Isaiah 9:1-7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Isaiah 9:1-7",
        "2024-12-01 00:00:00",
    ),  # youtube:cddc750f5045
    (
        "a8a65f20-e88f-57f3-a44a-11c04cba5e22",
        "https://www.youtube.com/watch?v=mTjOgxjkUhA",
        "Thanksgiving",
        "11:00 am Sunday 11/24/2024 • Thanksgiving • Rev. Pete Sferle — Psalms 34:1-3\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Psalms 34:1-3",
        "2024-11-25 00:00:00",
    ),  # youtube:11c04cba5e22
    (
        "c11653ad-ec42-5c88-a847-2130598d734c",
        "https://www.youtube.com/watch?v=yhvODe_3HyM",
        "Husbands",
        "Sunday Morning 11:00 am November 17, 2024 • Husbands - Rev.Pete Sferle — Ephesians 5:22-33\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev.Pete Sferle",
        "Ephesians 5:22-33",
        "2024-11-18 00:00:00",
    ),  # youtube:2130598d734c
    (
        "8f76ae30-79ba-50d1-8817-7e6f222f4bfb",
        "https://www.youtube.com/watch?v=adH-9ITWXrs",
        "Lord, if thou wilt, thou canst make me clean",
        "Sunday Morning 11:00 am November 10, 2024 •  Lord, if thou wilt, thou canst make me clean. - Rev. Pete Sferle — Luke 5:12-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Luke 5:12-14",
        "2024-11-10 00:00:00",
    ),  # youtube:7e6f222f4bfb
    (
        "04388d24-80d7-54cf-92d1-4c3793efb18c",
        "https://www.youtube.com/watch?v=TMyFqQNQpes",
        "This World Is Not My Home",
        "Sunday evening 11/3/2024 5:00 pm - This World Is Not My Home - Bro. Sorin Filimon — Hebrews 13:14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Hebrews 13:14",
        "2024-11-08 00:00:00",
    ),  # youtube:4c3793efb18c
    (
        "a3bfed05-de17-5307-944a-e64c758e243a",
        "https://www.youtube.com/watch?v=mrf4UBTSLR4",
        "Fear Not",
        "11:00 am Sunday 11/3/2024 • Fear Not - Rev. Mark Worthington— Isaiah 41:10-13\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Isaiah 41:10-13",
        "2024-11-04 00:00:00",
    ),  # youtube:e64c758e243a
    (
        "84969447-c615-5860-be09-91bc792bfb40",
        "https://www.youtube.com/watch?v=VevxA-doW5U",
        "Nothing Is Too Hard For The Lord",
        "Youth Service 5:00 pm Sunday evening 10/20/2024 • Nothing Is Too Hard For The Lord - Bro. Sorin Filimon — Jeremiah 32:16-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Jeremiah 32:16-19",
        "2024-10-28 00:00:00",
    ),  # youtube:91bc792bfb40
    (
        "56465e5e-b1e6-5219-89e7-26e5443f4cd0",
        "https://www.youtube.com/watch?v=UQC-fzRhmTU",
        "Be Not Ashamed",
        "Sunday Morning 11:00 am October 20, 2024 • Be Not Ashamed - Rev. Mark Worthington— 2 Timothy 1:8-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "2 Timothy 1:8-17",
        "2024-10-21 00:00:00",
    ),  # youtube:26e5443f4cd0
    (
        "df470d85-7ec1-5abf-a07f-9e73a3dd7911",
        "https://www.youtube.com/watch?v=KZWP-1SS0WU",
        "Salvation is by Faith, Not by Works",
        "Sunday evening 10/13/2024 5:00 pm - Salvation is by Faith, Not by Works — Bro. Sorin Filimon - Galatians 2:15-21\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Galatians 2:15-21",
        "2024-10-16 00:00:00",
    ),  # youtube:9e73a3dd7911
    (
        "46219058-6cc7-5838-b805-a5de0e2a3bfe",
        "https://www.youtube.com/watch?v=FGPS9pVSdJk",
        "Instructions For Wives",
        "11:00 am Sunday 10/13/2024 • Instructions For Wives - Rev. Pete Sferle — 1 Peter 3:1-6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 3:1-6",
        "2024-10-13 00:00:00",
    ),  # youtube:a5de0e2a3bfe
    (
        "5677aaa9-4c66-551c-9157-a4892130d096",
        "https://www.youtube.com/watch?v=cMWYanyTx-k",
        "Pray Without Ceasing",
        "Sunday evening 10/6/2024 5:00 pm -  Pray Without Ceasing  — Rev. Mark Worthington - 1 Thessalonians 5:17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "1 Thessalonians 5:17",
        "2024-10-10 00:00:00",
    ),  # youtube:a4892130d096
    (
        "7d4fb33c-2d15-58eb-a032-e97eac619bf5",
        "https://www.youtube.com/watch?v=c1_0-rT2T9I",
        "The Goodness Of God",
        "Sunday Morning 11:00 am  The Goodness Of God — Bro. Sorin Filimon - Romans 2:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Romans 2:1-4",
        "2024-10-10 00:00:00",
    ),  # youtube:e97eac619bf5
    (
        "968560cd-b39e-5392-aba4-c557eaef71e0",
        "https://www.youtube.com/watch?v=_r1ap5LOy7U",
        "Facing The Giants In Your Life",
        "September 2024 Special Meetings: Sunday Evening 5:00 pm\nFacing The Giants In Your Life — Rev. John Baros - 1 Samuel 17:37\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. John Baros",
        "1 Samuel 17:37",
        "2024-10-06 00:00:00",
    ),  # youtube:c557eaef71e0
    (
        "1ecd303a-0c6b-5fda-99ed-e9635a16f3de",
        "https://www.youtube.com/watch?v=KE4GATa9A7k",
        "Facing The Giants In Your Life",
        "September 2024 Special Meetings: Sunday Morning 11:00 am\nFacing The Giants In Your Life — Rev. John Baros - 1 Samuel 17:37\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. John Baros",
        "1 Samuel 17:37",
        "2024-10-02 00:00:00",
    ),  # youtube:e9635a16f3de
    (
        "b4943f7f-36f9-5239-9d0d-f02d6513893b",
        "https://www.youtube.com/watch?v=IKz3qxxYlgg",
        "Facing The Giants In Your Life",
        "September 2024 Special Meetings Friday Evening 8:00 pm\nFacing The Giants In Your Life — Rev. John Baros - 1 Samuel 17:37\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. John Baros",
        "1 Samuel 17:37",
        "2024-09-28 00:00:00",
    ),  # youtube:f02d6513893b
    (
        "574c219b-073d-56c0-9cca-cd24cb4495f1",
        "https://www.youtube.com/watch?v=A98hNXiFiiE",
        "Be The Best Influencer For God In Your Workplace",
        "11:00 am Sunday 9/22/2024 •  Be The Best Influencer For God In Your Workplace — Rev. Pete Sferle • 1 Peter 2:18-25\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 2:18-25",
        "2024-09-22 00:00:00",
    ),  # youtube:cd24cb4495f1
    (
        "90902186-4db8-5954-9dfb-a63db3c3fc3a",
        "https://www.youtube.com/watch?v=5OJL_3Uqu0w",
        "The Lord God is a Sun and Shield",
        "Sunday evening 9/15/2024 5:00 pm - The Lord God is a Sun and Shield  — Bro. Sorin Filimon • Psalm 84:11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Psalm 84:11",
        "2024-09-22 00:00:00",
    ),  # youtube:a63db3c3fc3a
    (
        "ab652e26-d8d3-5865-82ab-49b84216dbff",
        "https://www.youtube.com/watch?v=ox4y7DUNJuE",
        "Called To Be Model Citizens",
        "11:00 am Sunday 9/15/2024 • Called To Be  Model Citizens  — Rev. Pete Sferle • 1 Peter 2:13-17 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 2:13-17",
        "2024-09-21 00:00:00",
    ),  # youtube:49b84216dbff
    (
        "51e81765-b734-582d-a82a-2d4d15d52047",
        "https://www.youtube.com/watch?v=-HiwlThtsV8",
        "Forgiveness Sets You Free",
        "11:00 am Sunday 9/8/2024 •  Forgiveness Sets You Free — Bro. Sorin Filimon • Genesis 50:15-21, Ephesians 4:31-32\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Genesis 50:15-21, Ephesians 4:31-32",
        "2024-09-09 00:00:00",
    ),  # youtube:2d4d15d52047
    (
        "1a51b62d-875f-511a-96e7-93805cc6a3b9",
        "https://www.youtube.com/watch?v=WgNG3T1LTRc",
        "Our Labor For The Lord",
        "11:00 am Sunday 9/1/2024 • Our Labor For The Lord — Rev. Pete Sferle • 1 Corinthians 5:58\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Corinthians 5:58",
        "2024-09-06 00:00:00",
    ),  # youtube:93805cc6a3b9
    (
        "371e2c3b-66d1-557f-ad57-1f4d85889eaa",
        "https://www.youtube.com/watch?v=7qHSxZ3CoZk",
        "Touch The Lord; But, Not Just Any Way",
        "5:00 pm Sunday evening 8/25/2024 •   Touch The Lord; But, Not Just Any Way • Bro. Sorin Filimon — Mark 5:21-34\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Mark 5:21-34",
        "2024-09-05 00:00:00",
    ),  # youtube:1f4d85889eaa
    (
        "6e858033-215c-56e3-a98d-309a834fddb7",
        "https://www.youtube.com/watch?v=eeO9j9BbtEY",
        "God''s Blessing To A Privileged People",
        "11:00 am Sunday 8/25/2024 • God''s Blessing To A Privileged People — Rev. Pete Sferle • 1 Peter 2:9-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 2:9-10",
        "2024-08-25 00:00:00",
    ),  # youtube:309a834fddb7
    (
        "5feb5bda-0675-535e-8f57-641d72de47b0",
        "https://www.youtube.com/watch?v=y8YH4JbxvL4",
        "Jesus Our Cornerstone — 1 — 10",
        "11:00 am Sunday 8/18/2024 •  Jesus Our Cornerstone — Rev. Pete Sferle • 1 Peter 2 1-10\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 2",
        "2024-08-18 00:00:00",
    ),  # youtube:641d72de47b0
    (
        "d3a55b0b-4ad0-59f2-8f10-663662088cc9",
        "https://www.youtube.com/watch?v=9h8gZjNTkLY",
        "The Word of God",
        "5:00 pm Sunday evening 8/11/2024 •   Youth Service  — The Word of God •  Bro. Sorin Filimon — Jeremiah 15:16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Jeremiah 15:16",
        "2024-08-15 00:00:00",
    ),  # youtube:663662088cc9
    (
        "09b5dbb9-9902-52a5-b6ba-a9a71cb0bb08",
        "https://www.youtube.com/watch?v=ne_02YMgrQo",
        "Attitude of Thanksgiving and a Life of Gratitude",
        "11:00 am Sunday morning 8/11/2024 •  Attitude of Thanksgiving and a Life of Gratitude — Rev. Mark Worthington • Luke 17:11-19\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Luke 17:11-19",
        "2024-08-11 00:00:00",
    ),  # youtube:a9a71cb0bb08
    (
        "a20c0636-9c21-51e0-baf8-ef213b32953c",
        "https://www.youtube.com/watch?v=VhKuupXf7l4",
        "Truth and Love",
        "5:00 pm Sunday evening 8/4/2024 • Truth and Love — Bro. Sorin Filimon •   2 John 8 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "2 John 8",
        "2024-08-05 00:00:00",
    ),  # youtube:ef213b32953c
    (
        "e828be1b-bb9a-5dd3-b2bd-c9d50e98ba37",
        "https://www.youtube.com/watch?v=Ahs158KltZI",
        "A Sincere Love One For Another",
        "11:00 am Sunday 8/4/2024 • A Sincere Love One For Another — Rev. Pete Sferle • 1 Peter 1:22\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 1:22",
        "2024-08-04 00:00:00",
    ),  # youtube:c9d50e98ba37
    (
        "8029eec7-69e5-5a6b-be16-7d35caad70e0",
        "https://www.youtube.com/watch?v=ciBXuJ9i0ck",
        "Be Strong, Do Not Fear",
        "5:00 pm Sunday evening 7/28/2024 •   Be Strong, Do Not Fear — Bro. Sorin Filimon • Isaiah 35:1-7\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Isaiah 35:1-7",
        "2024-08-04 00:00:00",
    ),  # youtube:7d35caad70e0
    (
        "f26891dd-cbbb-546c-9ae1-4717f8e331e5",
        "https://www.youtube.com/watch?v=HdKYd8EbyJU",
        "I Bow My Knees",
        "11:00 am Sunday morning 7/28/2024 •  I Bow My Knees — Rev.Mark Worthington • Ephesians 3:14-21\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev.Mark Worthington",
        "Ephesians 3:14-21",
        "2024-07-28 00:00:00",
    ),  # youtube:4717f8e331e5
    (
        "1185e1dc-c9e4-5285-8c2d-b127f46bafd7",
        "https://www.youtube.com/watch?v=0sMclWMjE2w",
        "Fishes of Men, Stay With Jesus — , LA, CA",
        "11:00 am Sunday 7/21/2024 • Fishes of Men, Stay With Jesus  — Rev. Pierre Hancock, LA, CA — John 21:1-9\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pierre Hancock",
        "John 21:1-9",
        "2024-07-28 00:00:00",
    ),  # youtube:b127f46bafd7
    (
        "9fea01f4-55d4-55f4-b128-bd8f1d21a673",
        "https://www.youtube.com/watch?v=JOxTq7CS-bY",
        "Lay Aside Every Weight",
        "11:00 am Sunday morning 6/23/2024 • Lay Aside Every Weight— Rev. Mark  Worthington • Hebrews 12:1-2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Hebrews 12:1-2",
        "2024-06-27 00:00:00",
    ),  # youtube:bd8f1d21a673
    (
        "10467aed-9e8a-5233-9e91-64c4008015f7",
        "https://www.youtube.com/watch?v=aIjrMhRIAgs",
        "Finding Home",
        "5:00 pm Sunday evening 6/9/2024 •  Finding Home — Rev.Mark Worthington • Hebrews 4:9-12\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev.Mark Worthington",
        "Hebrews 4:9-12",
        "2024-06-15 00:00:00",
    ),  # youtube:64c4008015f7
    (
        "62371edb-ce3a-532c-8ea5-cec9c9500dcd",
        "https://www.youtube.com/watch?v=Eqt2pFnlBDU",
        "We Are Called to be Holy in Times of Trial",
        "11:00 am Sunday morning 6/9/2024 • We Are Called to be Holy in Times of Trial  — Rev. Pete Sferle • 1 Peter 1:13-16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 1:13-16",
        "2024-06-09 00:00:00",
    ),  # youtube:cec9c9500dcd
    (
        "635218ab-04bd-5424-a4ad-8d646e3f33d5",
        "https://www.youtube.com/watch?v=RPHzCefVQw8",
        "We''re Going to Make it, if we Keep Our Hand in His",
        "5:00 pm Sunday evening 6/2/2024 •  We''re Going to Make it, if we Keep Our Hand in His— Rev. Cliff Kasper • Jude 24\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Cliff Kasper",
        "Jude 24",
        "2024-06-07 00:00:00",
    ),  # youtube:8d646e3f33d5
    (
        "f763ee80-b18a-5f5f-ba53-9e531a4d48ef",
        "https://www.youtube.com/watch?v=SBFGAnAsJw8",
        "God Won''t Forget You",
        "11:00 am Sunday morning 6/2/2024 • God Won''t Forget You — Rev. Cliff Kasper • Genesis 40:23\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Cliff Kasper",
        "Genesis 40:23",
        "2024-06-02 00:00:00",
    ),  # youtube:9e531a4d48ef
    (
        "72915192-78e4-5445-b2fb-dab9b43ba8b6",
        "https://www.youtube.com/watch?v=x2kh0XScZhE",
        "Be Strong and Courageous",
        "11:00 am Sunday morning 5/26/2024 • Be Strong and Courageous  — Rev. Mark Worthington •  Psalm 18:30-32 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Psalm 18:30-32",
        "2024-05-27 00:00:00",
    ),  # youtube:dab9b43ba8b6
    (
        "8f2390e8-1e8a-5235-bf1f-ba6260dcdd8d",
        "https://www.youtube.com/watch?v=-YPcKMKpi0U",
        "Pride Goeth Before Destruction, and an Haughty Spirit Before a Fall",
        "5:00 pm Sunday evening 5/19/2024 •  Pride Goeth Before Destruction, and an Haughty Spirit Before a Fall.— Rev. Pete Sferle • Prov. 16:18 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Prov. 16:18",
        "2024-05-26 00:00:00",
    ),  # youtube:ba6260dcdd8d
    (
        "73b7da1e-94cf-52f0-b760-8b21aa95f10d",
        "https://www.youtube.com/watch?v=CnA68pDbUQI",
        "Pentecost Sunday: The Holy Ghost",
        "11:00 am Sunday morning 5/19/2024 • Pentecost Sunday: The Holy Ghost— Rev. Pete Sferle • Acts 1:4-8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Acts 1:4-8",
        "2024-05-26 00:00:00",
    ),  # youtube:8b21aa95f10d
    (
        "69738d9c-1354-5592-8c92-6e760a929961",
        "https://www.youtube.com/watch?v=iS_Qz4uWqo0",
        "A Mother Named Hannah",
        "11:00 am Sunday 5/5/2024 • A Mother Named Hannah — Rev. Pete Sferle • 1 Samuel 1:26-28\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Samuel 1:26-28",
        "2024-05-25 00:00:00",
    ),  # youtube:6e760a929961
    (
        "fbe7cb14-8acf-5dff-93e7-aaab70b2753e",
        "https://www.youtube.com/watch?v=1MvaylFMGUk",
        "Wait for the Promise of the Father — . Mark Worthington",
        "5:00 pm Sunday evening 5/5/2024 • Wait for the Promise of the Father — Rev. Mark Worthington • Acts 2:1-4  —Rev. Mark Worthington • Acts 2:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Acts 2:1-4 —Rev; Acts 2:1-4",
        "2024-05-19 00:00:00",
    ),  # youtube:aaab70b2753e
    (
        "98e42568-acb3-5356-8564-261f2035bf48",
        "https://www.youtube.com/watch?v=Norjn33nuSU",
        "A Living Hope",
        "11:00 am Sunday morning4/14/2024 •  A Living Hope— Rev. Pete Sferle • 1 Peter 3\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 3",
        "2024-04-14 00:00:00",
    ),  # youtube:261f2035bf48
    (
        "c40d4c56-830d-5f2b-a391-afd38c3af7a8",
        "https://www.youtube.com/watch?v=XUq8unazIIw",
        "Don''t Bow Down",
        "Sunday Evening April 7 , 2024 5:00 pm. • Don''t Bow Down — Rev.Mark Worthington • Daniel 3:15-18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev.Mark Worthington",
        "Daniel 3:15-18",
        "2024-04-14 00:00:00",
    ),  # youtube:afd38c3af7a8
    (
        "c4f8f1b8-9896-5358-9b74-b8481d9b4c9c",
        "https://www.youtube.com/watch?v=TinN4ypHLDo",
        "Peter",
        "11:00 am Sunday morning 4/7/2024 • Peter — Rev. Pete Sferle • 1 Peter 1:1\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 1:1",
        "2024-04-07 00:00:00",
    ),  # youtube:b8481d9b4c9c
    (
        "da0fe8c0-9415-548e-9647-b1522c0abe85",
        "https://www.youtube.com/watch?v=Y6hv9k1x1qQ",
        "Peter",
        "11:00 am Sunday morning 4/7/2024 • Peter — Rev. Pete Sferle • 1 Peter 1:1\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Peter 1:1",
        "2024-04-07 00:00:00",
    ),  # youtube:b1522c0abe85
    (
        "d14f52ef-9cac-586c-9847-7a848e3d3dda",
        "https://www.youtube.com/watch?v=GYrSDsf6Cg8",
        "Almost thou persuadest me to be a Christian",
        "5:00 pm Sunday evening 3/31/2023 • Almost thou persuadest me to be a Christian. — Bro Sorin Filimon • Acts 26\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro Sorin Filimon",
        "Acts 26",
        "2024-04-07 00:00:00",
    ),  # youtube:7a848e3d3dda
    (
        "19a31848-b568-518e-ad1e-5153cfb93b9e",
        "https://www.youtube.com/watch?v=Xd3YWvhPLBY",
        "Easter — Christ Arose!",
        "11:00 am Sunday morning 3/31/2024 • Easter – Christ Arose! — Rev. Pete Sferle • 1 Corinthians 15:1-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "1 Corinthians 15:1-11",
        "2024-03-31 00:00:00",
    ),  # youtube:5153cfb93b9e
    (
        "33a65519-9497-511d-ba44-47079b680c54",
        "https://www.youtube.com/watch?v=MvyFWkBT2Yo",
        "Launch Out Into The Deep",
        "Sunday Evening March 24 , 2024 5:00 pm. Launch Out Into The Deep — Bro. Sorin Filimon • Luke 5:1-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Luke 5:1-11",
        "2024-03-27 00:00:00",
    ),  # youtube:47079b680c54
    (
        "40ffe773-a2a1-526c-8f53-ce72f61d7bce",
        "https://www.youtube.com/watch?v=K74yV8loWys",
        "All Honor, Glory , and Praise to our God",
        "11:00 am Sunday morning 3/24/2024 •All Honor, Glory , and Praise to our God — Rev. Pete Sferle • Luke 9:35-38  \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Luke 9:35-38",
        "2024-03-24 00:00:00",
    ),  # youtube:ce72f61d7bce
    (
        "271f1649-1a0d-5c41-b8b9-35a94f9eaad6",
        "https://www.youtube.com/watch?v=UUD9rtqRgdE",
        "I Am The True Vine",
        "5:00 pm Sunday evening 3/17/2023 •  I Am The True Vine — Rev. Pete Sferle • John 15:1-11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "John 15:1-11",
        "2024-03-24 00:00:00",
    ),  # youtube:35a94f9eaad6
    (
        "26ef271e-49f9-5232-8c31-91c78ed38283",
        "https://www.youtube.com/watch?v=2Ppcf3ZqTGo",
        "Set your affection on things above, not on things on the earth",
        "5:00 pm Sunday evening 3/17/2023 •  Set your affection on things above, not on things on the earth. • Bro. Noah Mocan — Colossians 3:2\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Noah Mocan",
        "Colossians 3:2",
        "2024-03-24 00:00:00",
    ),  # youtube:91c78ed38283
    (
        "5db99052-b18f-5b37-baf3-c519cea714fb",
        "https://www.youtube.com/watch?v=51HIFvBy-5Q",
        "Stir up the Gift of God",
        "11:00 am Sunday morning 3/17/2024 • Stir up the Gift of God — Bro. Tom Udo • 2 Timothy 1:6\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Tom Udo",
        "2 Timothy 1:6",
        "2024-03-17 00:00:00",
    ),  # youtube:c519cea714fb
    (
        "860805d9-4108-5956-ab52-29ecba5c5512",
        "https://www.youtube.com/watch?v=ZDfEUJmBqsQ",
        "Patience and Comfort of the Scriptures",
        "5:00 pm Sunday evening 3/10/2023 • Patience and Comfort of the Scriptures — Bro. Sorin Filimon • Romans 15:4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Romans 15:4",
        "2024-03-16 00:00:00",
    ),  # youtube:29ecba5c5512
    (
        "e2c66a40-eb41-573f-9ea2-ffe3c5ceae62",
        "https://www.youtube.com/watch?v=i1Rlgof_aWA",
        "God Does Not Change",
        "11:00 am Sunday morning 3/10/2024 • God Does Not Change — Rev. Pete Sferle • Hebrews 13:8\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Hebrews 13:8",
        "2024-03-10 00:00:00",
    ),  # youtube:ffe3c5ceae62
    (
        "586cccdd-9e4d-5f50-973e-661b6528e929",
        "https://www.youtube.com/watch?v=D2lptNVsZXM",
        "Lazarus Come Forth",
        "Sunday Evening March 3 , 2024 5:00 pm.  Lazarus Come Forth  — Bro. Sorin Filimon • John 11\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "John 11",
        "2024-03-10 00:00:00",
    ),  # youtube:661b6528e929
    (
        "dd3653ae-0059-5bf4-86e9-009f6b3eafb2",
        "https://www.youtube.com/watch?v=QWWNjUECsr8",
        "And Enoch Walked with GOD, and He Was Not: For GOD Took Him",
        "Sunday Morning March 3, 2024 11:00 AM — Rev. Pete Sferle •  John 14:1-4\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "John 14:1-4",
        "2024-03-04 00:00:00",
    ),  # youtube:009f6b3eafb2
    (
        "b9ab5789-8fba-5bc2-8cc6-fb3f28969e35",
        "https://www.youtube.com/watch?v=AU1bQMZ8xZM",
        "Too Late",
        "Sunday Morning February 25, 2024 11:00 AM. Too Late — Rev. Mark Worthington • Luke 16:22-24\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Luke 16:22-24",
        "2024-03-03 00:00:00",
    ),  # youtube:fb3f28969e35
    (
        "59b115f9-7aad-5104-b5d1-4c2165dfbc32",
        "https://www.youtube.com/watch?v=mVaa_sNbESE",
        "Be Watchful",
        "Sunday Evening January 28, 2024 5:00 pm. Be Watchful — Bro. Sorin Filimon • Luke 12:35-48 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Luke 12:35-48",
        "2024-01-31 00:00:00",
    ),  # youtube:4c2165dfbc32
    (
        "b28de2d3-2ecc-5ae9-be7b-ac10dbc2be7e",
        "https://www.youtube.com/watch?v=VMa_FYYFBCU",
        "What is that in thine hand?",
        "11:00 am Sunday morning 1/28/2024 What is that in thine hand? — Rev. Pete Sferle • Exodus 4:1-5\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Exodus 4:1-5",
        "2024-01-28 00:00:00",
    ),  # youtube:ac10dbc2be7e
    (
        "80843384-64fb-5797-83a7-d81a46f45381",
        "https://www.youtube.com/watch?v=Sfu0QJYupNA",
        "We Are in a Victory Parade",
        "5:00 pm Sunday Evening 1/21/2024 • Youth service • We Are in a Victory Parade — Bro. Sorin Filimon • 2 Corinthians 2:12-17\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "2 Corinthians 2:12-17",
        "2024-01-27 00:00:00",
    ),  # youtube:d81a46f45381
    (
        "4879f9ad-411e-5156-aeda-4da452490e31",
        "https://www.youtube.com/watch?v=S2sXcbEApSA",
        "Set Your Heart to Serve the Lord In the Coming Year . Pete Sferle",
        "11:00 am Sunday morning 1/21/2024 - Set Your Heart to Serve the Lord In the Coming Year • Luke 9:62 — Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Luke 9:62 — Rev",
        "2024-01-21 00:00:00",
    ),  # youtube:4da452490e31
    (
        "af60777e-08c4-5d79-8985-0699307806ff",
        "https://www.youtube.com/watch?v=VYivjduYBQQ",
        "Don''t Look Back . Mark Worthington",
        "11:00 am Sunday morning 1/14/2024 - Don''t Look Back • Philippians 3:7-14 — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Philippians 3:7-14 — Rev",
        "2024-01-21 00:00:00",
    ),  # youtube:0699307806ff
    (
        "34592b1f-aa22-5836-b5c4-74d5a00df36c",
        "https://www.youtube.com/watch?v=gjV7p-W0BfE",
        "Life Lessons For The New Year",
        "11:00 am Sunday morning 1/7/2024 - Ecclesiastes 3:1-8 — Life Lessons For The New Year • Rev. Pete Sferle\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Ecclesiastes 3:1-8",
        "2024-01-11 00:00:00",
    ),  # youtube:74d5a00df36c
    (
        "c63cc211-a171-513f-b77e-f6d07367b358",
        "https://www.youtube.com/watch?v=TV-6wEyxnJc",
        "Spiritual Blessings",
        "11:00 am New Years Eve morning 12/31/2023 • Spiritual Blessings - Bro. Sorin — Ephesians 1:1-14\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin",
        "Ephesians 1:1-14",
        "2024-01-07 00:00:00",
    ),  # youtube:f6d07367b358
    (
        "c4916960-264b-574b-9c35-36caa0b0eb80",
        "https://www.youtube.com/watch?v=gg91mjSKGRE",
        "In the beginning was the Word, and the Word was with God, and the Word was God",
        "11:00 am Sunday morning 12/24/2023 • In the beginning was the Word, and the Word was with God, and the Word was God — Rev. Pete Sferle • John 1:1 \nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "John 1:1",
        "2023-12-27 00:00:00",
    ),  # youtube:36caa0b0eb80
    (
        "5c882822-ab2d-51a9-a107-97f4fcdbd6bb",
        "https://www.youtube.com/watch?v=tSdZovCM7NU",
        "Fullness Of The Gospel",
        "11:00 am Sunday Morning 12/17/2023 The Fullness Of The Gospel — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming licence #20833650 A",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Galatians 4:4-7",
        "2023-12-24 00:00:00",
    ),  # youtube:97f4fcdbd6bb
    (
        "7350a0f7-8d25-55ee-8c4c-ac75156b394c",
        "https://www.youtube.com/watch?v=ka65Sx4-LtM",
        "The Lord is with thee, thou mighty man of valour",
        "12.3.2023 – Sunday December 3, 2023 • Youth Service • The Lord is with thee, thou mighty man of valour. —  Rev. Pete Sferle • Judges 6:11-16\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Judges 6:11-16",
        "2023-12-10 00:00:00",
    ),  # youtube:ac75156b394c
    (
        "c632f1da-02f3-5547-a524-f70702052d31",
        "https://www.youtube.com/watch?v=ufZn4z1bRJQ",
        "Keeping Christ in Christmas",
        "Sunday December 3, 2023, 11:00 am  • Keeping Christ in Christmas — Rev. Mark Worthington\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Philippians 2:8",
        "2023-12-10 00:00:00",
    ),  # youtube:f70702052d31
    (
        "4192b601-0bc9-5cd5-b5cb-9ca226b84e59",
        "https://www.youtube.com/watch?v=mYhfdWP6Nps",
        "The Gifts of the Wisemen for Today",
        "Sunday November 26, 2023, 5:00 pm  • The Gifts of the Wisemen for Today  — Bro. Sorin Filimon\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Matthew 2:1-12",
        "2023-12-01 00:00:00",
    ),  # youtube:9ca226b84e59
    (
        "06cc09db-fe04-510e-8bda-b114d4faac56",
        "https://www.youtube.com/watch?v=M2nC4HOIV10",
        "Add Godliness",
        "Sunday November 26, 2023, 11:00 am • Add Godliness — Rev. John Baros\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. John Baros",
        "2 Peter 1:5-7",
        "2023-11-30 00:00:00",
    ),  # youtube:b114d4faac56
    (
        "022b06d0-020d-5067-95cb-01c953e7f2c3",
        "https://www.youtube.com/watch?v=JwsyZ6KfeEw",
        "Blessed are they which do hunger and thirst after righteousness for they shall be filled. . David Lambert",
        "Sunday October 1, 2023, 5:00 pm  • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Rev.  David Lambert\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. David Lambert",
        "Matthew 5:6 — Rev",
        "2023-10-11 00:00:00",
    ),  # youtube:01c953e7f2c3
    (
        "869bd0c8-d995-57fb-8666-9cd413e1b5b6",
        "https://www.youtube.com/watch?v=d8bzJztjNQk",
        "Blessed are they which do hunger and thirst after righteousness for they shall be filled. . David Lambert",
        "Sunday October 1, 2023, 11:00 am  • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Rev.  David Lambert\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. David Lambert",
        "Matthew 5:6 — Rev",
        "2023-10-08 00:00:00",
    ),  # youtube:9cd413e1b5b6
    (
        "0d6a4603-324f-5b8a-9065-47eefd4b6559",
        "https://www.youtube.com/watch?v=vZ37UlKF2ww",
        "Blessed are they which do hunger and thirst after righteousness for they shall be filled. — Youth Service",
        "Saturday September 30, 2023 6:00 pm • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Youth Service Bro. Randy Lee\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Randy Lee",
        "Matthew 5:6",
        "2023-10-08 00:00:00",
    ),  # youtube:47eefd4b6559
    (
        "04f6f377-dac9-5dec-9266-4163b8d6c758",
        "https://www.youtube.com/watch?v=NAbL7fbGxM8",
        "Blessed are they which do hunger and thirst after righteousness for they shall be filled. — Marriage",
        "Saturday September 30, 2023, 10:30 am  • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Marriage • Rev.  Howard Wilson\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Howard Wilson",
        "Matthew 5:6",
        "2023-10-07 00:00:00",
    ),  # youtube:4163b8d6c758
    (
        "0e41dcfa-02dc-59fd-8f1a-c5df2d4b1ac0",
        "https://www.youtube.com/watch?v=wLFftUnOciU",
        "Blessed are they which do hunger and thirst after righteousness for they shall be filled. . David Lambert",
        "Friday September 29, 2023 8:00 pm • Blessed are they which do hunger and thirst after righteousness for they shall be filled. Matthew 5:6 — Rev.  David Lambert\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nI Will Sing The Wondrous Story (Wondrous Story), Peter Philip Bilhorn, public domain\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. David Lambert",
        "Matthew 5:6 — Rev",
        "2023-09-30 00:00:00",
    ),  # youtube:c5df2d4b1ac0
    (
        "872c09af-ac62-5423-aee5-06526999eafa",
        "https://www.youtube.com/watch?v=lEJ10bE-jWA",
        "How to Have Victory in the Battle of Life — , 12 — 18",
        "8.27.2023 – Sunday August, 27 2023 • How to Have Victory in the Battle of Life  — Rev. Mark Worthington 2 Chronicles 20:1-4, 12-18\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "2 Chronicles 20:1-4",
        "2023-08-28 00:00:00",
    ),  # youtube:06526999eafa
    (
        "bd655bf4-9817-5ac4-80b7-42162736cbf5",
        "https://www.youtube.com/watch?v=IWcOtnY5xvg",
        "A Cleansed Conscience",
        "A Cleaned Conscience — Rev. Pete Sferle • Hebrews 9:1-15 – 11:00 am Sunday Morning Service 10.23.2022\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Hebrews 9:1-15",
        "2022-10-23 00:00:00",
    ),  # youtube:42162736cbf5
    (
        "8a03f5d3-e4fc-5abf-b5d8-44b122e39c93",
        "https://www.youtube.com/watch?v=8qhTp4jxaSg",
        "A New Thing",
        "A New Thing — Bro. Sorin Filimon - Isaiah 43:18-21 (KJV) • 10.9.2022 – Sunday Evening Service \n\nTrinity Apostolic Faith Church, Sacramento County, California\nFor more information, please visit us at www.afcsacramento.org\n\nCCLI Streaming license #20833650 A\ninfo@afcsacramento.org",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Isaiah 43:18-21",
        "2022-10-15 00:00:00",
    ),  # youtube:44b122e39c93
    (
        "e434b1af-b6aa-5860-bcb8-3d9a9e598e0f",
        "https://www.youtube.com/watch?v=BtUA5OwBV6A",
        "Live Life in the Deep Water",
        "5:00 pm Sunday evening September 18, 2022 • Live Life in the Deep Water — Bro. Sorin Filimon – Ezekiel 47:1-5",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Ezekiel 47:1-5",
        "2022-09-22 00:00:00",
    ),  # youtube:3d9a9e598e0f
    (
        "1b624062-2b05-59ae-9798-15506f832d77",
        "https://www.youtube.com/watch?v=Xz8THGg_Sn8",
        "Be Secure in Your Salvation . Pete Sferle",
        "Sunday morning, September 18, 2022 Be Secure in Your Salvation Hebrews 6:11 — Rev. Pete Sferle",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Hebrews 6:11 — Rev",
        "2022-09-18 00:00:00",
    ),  # youtube:15506f832d77
    (
        "6113655d-c848-5504-96da-0ed6b8d5385b",
        "https://www.youtube.com/watch?v=zD_W1c5m5w8",
        "Shoes of the Gospel . Mark Worthington",
        "5:00 pm Sunday evening September 11, 2022 • Shoes of the Gospel Ephesians 6:13-15 – Rev. Mark Worthington",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Ephesians 6:13-15 – Rev",
        "2022-09-17 00:00:00",
    ),  # youtube:0ed6b8d5385b
    (
        "ad84ac7b-7605-5a3d-b30a-d6f88ee2cbda",
        "https://www.youtube.com/watch?v=--9_EvtswqA",
        "The Holy Spirit Works in Wonderful Ways in Our Lives",
        "11:00 Sunday morning, September 11, 2022 • The Holy Spirit Works in Wonderful Ways in Our Lives — Bro. Sorin Filimon Romans 8:15-17",
        "00000000-0000-0000-0000-000000000000",
        "Bro. Sorin Filimon",
        "Romans 8:15-17",
        "2022-09-17 00:00:00",
    ),  # youtube:d6f88ee2cbda
    (
        "89aa1d08-f52b-56c0-b434-5f932bbda873",
        "https://www.youtube.com/watch?v=SY2paup_aTE",
        "True Salvation",
        "9.04.2022 – Sunday morning service • True Salvation — Rev. Pete Sferle – Hebrews 6:4-6",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Hebrews 6:4-6",
        "2022-09-04 00:00:00",
    ),  # youtube:5f932bbda873
    (
        "2dc95106-1e07-51e4-b5f3-2abf22697ba0",
        "https://www.youtube.com/watch?v=I68TH23NpRg",
        "I Heard You The First Time",
        "8.28.2022 - Sunday evening service • I Heard You The First Time — Rev. Mark Worthington - Daniel 10:12-24",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Mark Worthington",
        "Daniel 10:12-24",
        "2022-08-29 00:00:00",
    ),  # youtube:2abf22697ba0
    (
        "88f38b45-fb7f-5da0-969e-751c71f91914",
        "https://www.youtube.com/watch?v=YvqRmMvX5FI",
        "Are you Dull of Hearing?",
        "11:00 am Sunday morning service – Are you Dull of Hearing? — Rev. Pete Sferle • Hebrews 5:11",
        "00000000-0000-0000-0000-000000000000",
        "Rev. Pete Sferle",
        "Hebrews 5:11",
        "2022-08-28 00:00:00",
    ),  # youtube:751c71f91914
]


def _insert_sql(row: tuple) -> str:
    vid, loc, name, desc, owner_id, speaker, ref, ts = row
    desc_literal = "NULL" if desc is None else f"'{desc}'"
    speaker_literal = "NULL" if speaker is None else f"'{speaker}'"
    ref_literal = "NULL" if ref is None else f"'{ref}'"
    return (
        "INSERT INTO video_uploads "
        "(id, upload_location, upload_name, description, owner_id, speaker_name, "
        f"reference_text, media_association_date, created_on, updated_on) "
        f"VALUES ('{vid}', '{loc}', '{name}', {desc_literal}, '{owner_id}', "
        f"{speaker_literal}, {ref_literal}, '{ts}', '{ts}', '{ts}') "
        "ON DUPLICATE KEY UPDATE upload_location = VALUES(upload_location), "
        "upload_name = VALUES(upload_name), description = VALUES(description), "
        "speaker_name = VALUES(speaker_name), reference_text = VALUES(reference_text), "
        "media_association_date = VALUES(media_association_date), updated_on = VALUES(updated_on)"
    )


def upgrade() -> None:
    for row in VIDEO_UPLOAD_ROWS:
        op.execute(_insert_sql(row))


def downgrade() -> None:
    ids = ", ".join(f"'{row[0]}'" for row in VIDEO_UPLOAD_ROWS)
    op.execute(f"DELETE FROM video_uploads WHERE id IN ({ids})")
