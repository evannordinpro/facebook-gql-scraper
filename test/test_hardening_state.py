"""The state file holds the fb_dtsg session token: only the owner may read it."""

import os
import stat
import unittest

from hardening_fixtures import make_context


class StateFileModeTest(unittest.TestCase):
    def test_state_file_is_owner_only(self):
        ctx = make_context()
        ctx.csrf_token = "token"
        ctx._save_state()
        mode = stat.S_IMODE(os.stat(ctx._state_file).st_mode)
        self.assertEqual(mode, 0o600)

    def test_existing_state_file_is_tightened(self):
        ctx = make_context()
        with open(ctx._state_file, "w") as f:
            f.write("{}")
        os.chmod(ctx._state_file, 0o644)
        ctx._save_state()
        self.assertEqual(stat.S_IMODE(os.stat(ctx._state_file).st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
