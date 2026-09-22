import hashlib
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from readback import check, resolve_url


class Tests(unittest.TestCase):
    def test_resolve_fixed_host(self):
        url=resolve_url("https://example.com/base/","apps/demo",["apps","projects"])
        self.assertEqual(url,"https://example.com/base/apps/demo/")

    def test_http_base_rejected(self):
        with self.assertRaises(ValueError):
            resolve_url("http://example.com/","apps/demo",["apps"])

    def test_userinfo_rejected(self):
        with self.assertRaises(ValueError):
            resolve_url("https://user:pass@example.com/","apps/demo",["apps"])

    def test_unknown_root_rejected(self):
        with self.assertRaises(ValueError):
            resolve_url("https://example.com/","other/demo",["apps"])

    def test_traversal_shape_rejected(self):
        with self.assertRaises(ValueError):
            resolve_url("https://example.com/","apps/../demo",["apps"])

    @patch("readback.fetch",return_value=(200,b"hello"))
    def test_present_pass(self,_):
        ev=check("https://example.com/","apps/demo","present",["apps"])
        self.assertTrue(ev.passed)
        self.assertEqual(ev.body_sha256,hashlib.sha256(b"hello").hexdigest())
        self.assertEqual(ev.body_bytes,5)

    @patch("readback.fetch",return_value=(404,b"missing"))
    def test_absent_pass(self,_):
        ev=check("https://example.com/","apps/demo","absent",["apps"])
        self.assertTrue(ev.passed)

    @patch("readback.fetch",return_value=(200,b"x"))
    def test_absent_fails_on_200(self,_):
        ev=check("https://example.com/","apps/demo","absent",["apps"])
        self.assertFalse(ev.passed)


if __name__=="__main__":
    unittest.main()
