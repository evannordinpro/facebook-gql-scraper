"""The About parser keeps the places a group's admins set (XFBLocationGroupsAboutInfoItem)."""

import unittest

from facebook_gql_scraper.unifiedFacebookParser import parse_group_about_info


def about_payload(*items):
    return {"data": {"group": {"id": "100", "about_feed_units": [{
        "__typename": "GroupsAboutFeedAboutCardUnit",
        "group": {"id": "100", "description_with_entities": {"text": "Buy, sell, trade"},
                  "about_info_items": list(items)},
    }]}}}


def location_item(*locations):
    return {"__typename": "XFBLocationGroupsAboutInfoItem", "group": {"group_locations": list(locations)}}


class GroupAboutLocationsTest(unittest.TestCase):
    def test_locations_are_kept_in_order(self):
        about = parse_group_about_info(about_payload(location_item(
            {"id": "1", "name": "Springfield, Illinois"}, {"id": "2", "name": "Shelbyville, Illinois"})))
        self.assertEqual([(l.id, l.name) for l in about.locations],
                         [("1", "Springfield, Illinois"), ("2", "Shelbyville, Illinois")])
        self.assertEqual(about.description, "Buy, sell, trade")

    def test_no_location_item_gives_an_empty_list(self):
        self.assertEqual(parse_group_about_info(about_payload()).locations, [])

    def test_malformed_entries_are_dropped(self):
        about = parse_group_about_info(about_payload(location_item(
            None, "Springfield", {"id": "3"}, {"id": "4", "name": "Ogdenville, Illinois"})))
        self.assertEqual([l.name for l in about.locations], ["Ogdenville, Illinois"])

    def test_null_location_list_gives_an_empty_list(self):
        item = {"__typename": "XFBLocationGroupsAboutInfoItem", "group": {"group_locations": None}}
        self.assertEqual(parse_group_about_info(about_payload(item)).locations, [])


if __name__ == "__main__":
    unittest.main()
