from healthchecks_io.schemas.badges import Badges


def test_badge_from_api_result():
    badges_dict = {
        "svg": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M-2/backup.svg",
        "svg3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M/backup.svg",
        "json": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M-2/backup.json",
        "json3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M/backup.json",
        "shields": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M-2/backup.shields",
        "shields3": "https://healthchecks.io/badge/67541b37-8b9c-4d17-b952-690eae/LOegDs5M/backup.shields",
    }
    this_badge = Badges.from_api_result(badges_dict)
    assert this_badge.svg == badges_dict["svg"]
    assert this_badge.json_url == badges_dict["json"]
