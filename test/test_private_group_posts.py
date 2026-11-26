"""A private group's feed post is a post, not only its photos.

Private groups send shareable_from_perspective_of_feed_ufi as null where public groups send
{"__typename": "Story"}. Only a feed item that is itself a Photo, Video or Album is returned as its
media alone; anything else, null included, is a post with its text, time, link and author.
"""

import unittest

from facebook_gql_scraper.unifiedFacebookParser import ParserPost, _parse_feed_post


def photo_attachment(photo_id):
    return {"styles": {"__typename": "StoryAttachmentPhotoStyleRenderer", "attachment": {"media": {
        "__typename": "Photo", "id": photo_id, "photo_image": {"uri": "https://example.invalid/p.jpg"}}}}}


def feed_edge(shareable, attachments=()):
    return {"node": {
        "post_id": "100", "creation_time": 1764000000, "attachments": list(attachments),
        "actors": [{"id": "55", "name": "Member"}],
        "comet_sections": {
            "content": {"story": {"wwwURL": "https://www.facebook.com/groups/1/posts/100/",
                                  "message": {"text": "WTS 151 ETB $60, pickup only"}}},
            "feedback": {"story": {"story_ufi_container": {"story": {
                "shareable_from_perspective_of_feed_ufi": shareable}}}},
        },
    }}


class PrivateGroupFeedPostTest(unittest.TestCase):
    def assert_post(self, posts):
        [post] = posts
        self.assertIsInstance(post, ParserPost)
        self.assertEqual(post.id, "100")
        self.assertEqual(post.text, "WTS 151 ETB $60, pickup only")
        self.assertEqual(post.creation_time, 1764000000)
        self.assertEqual(post.url, "https://www.facebook.com/groups/1/posts/100/")
        self.assertEqual(post.author.id, "55")

    def test_null_shareable_text_only_post_is_kept(self):
        self.assert_post(_parse_feed_post(feed_edge(None)))

    def test_null_shareable_post_with_a_photo_is_the_post_not_the_photo(self):
        self.assert_post(_parse_feed_post(feed_edge(None, [photo_attachment("3000")])))

    def test_story_is_still_a_post(self):
        self.assert_post(_parse_feed_post(feed_edge({"__typename": "Story"})))

    def test_photo_item_is_still_its_media(self):
        posts = _parse_feed_post(feed_edge({"__typename": "Photo"}, [photo_attachment("3000")]))
        self.assertTrue(posts)
        self.assertFalse(any(isinstance(p, ParserPost) for p in posts))


if __name__ == "__main__":
    unittest.main()
