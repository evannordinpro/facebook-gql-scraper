"""A shared post keeps the post it shares (attached_story): its text, author, link and media count.

A share with no words of its own has a null message and no attachments: everything is in the
shared post, so without it the post reads as empty.
"""

import unittest

from facebook_gql_scraper.unifiedFacebookParser import _parse_feed_post, parse_post


def album(count):
    return {"styles": {"__typename": "StoryAttachmentAlbumStyleRenderer",
                       "attachment": {"all_subattachments": {"count": count, "nodes": []}}}}


SHARED = {
    "post_id": "900", "wwwURL": "https://www.facebook.com/groups/5/permalink/900/",
    "actors": [{"id": "77", "name": "Original Seller", "url": "https://www.facebook.com/seller"}],
    "message": {"text": "Selling my binder, $40 each, offers welcome"},
    "attachments": [album(2)],
}


def story(message=None, attached=None):
    s = {"wwwURL": "https://www.facebook.com/groups/1/permalink/100/", "message": message}
    if attached is not None:
        s["attached_story"] = attached
    return s


def feed_edge(content_story):
    return {"node": {
        "post_id": "100", "creation_time": 1764000000, "attachments": [],
        "actors": [{"id": "55", "name": "Sharer"}],
        "comet_sections": {
            "content": {"story": content_story},
            "feedback": {"story": {"story_ufi_container": {"story": {
                "shareable_from_perspective_of_feed_ufi": {"__typename": "Story"}}}}},
        },
    }}


def single_post_payload(content_story):
    return {"data": {"node_v2": {
        "post_id": "100", "attachments": [], "feedback": {"id": "fb1"},
        "comet_sections": {"content": {"story": {**content_story, "actors": [{"id": "55", "name": "Sharer"}]}}},
    }}}


class FeedSharedPostTest(unittest.TestCase):
    def test_share_with_no_words_keeps_the_shared_post(self):
        [post] = _parse_feed_post(feed_edge(story(attached=SHARED)))
        self.assertIsNone(post.text)
        shared = post.shared_post
        self.assertEqual(shared.id, "900")
        self.assertEqual(shared.url, SHARED["wwwURL"])
        self.assertEqual(shared.text, "Selling my binder, $40 each, offers welcome")
        self.assertEqual((shared.author.id, shared.author.name), ("77", "Original Seller"))
        self.assertEqual(shared.media_posts_count, 2)

    def test_share_keeps_the_sharers_own_words_apart(self):
        [post] = _parse_feed_post(feed_edge(story(message={"text": "My friend is selling"}, attached=SHARED)))
        self.assertEqual(post.text, "My friend is selling")
        self.assertEqual(post.shared_post.text, SHARED["message"]["text"])

    def test_ordinary_post_has_no_shared_post(self):
        [post] = _parse_feed_post(feed_edge(story(message={"text": "WTB 151 bundle"})))
        self.assertIsNone(post.shared_post)

    def test_null_attached_story_is_no_shared_post(self):
        s = story(message={"text": "hi"})
        s["attached_story"] = None
        [post] = _parse_feed_post(feed_edge(s))
        self.assertIsNone(post.shared_post)


class SinglePostSharedPostTest(unittest.TestCase):
    def test_single_post_keeps_the_shared_post(self):
        post = parse_post(single_post_payload(story(attached=SHARED)))
        self.assertEqual(post.shared_post.id, "900")
        self.assertEqual(post.shared_post.text, SHARED["message"]["text"])


if __name__ == "__main__":
    unittest.main()
