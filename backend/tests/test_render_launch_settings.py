"""Reviewable proposed Render settings; no cloud actions or app imports."""
import json
from pathlib import Path
import unittest


class RenderLaunchSettingsTests(unittest.TestCase):
    def test_ordered_same_origin_route_preserves_original_spa_and_security(self):
        root = Path(__file__).resolve().parents[2]
        config = json.loads((root / 'docs' / 'RENDER_LAUNCH_SETTINGS.json').read_text())
        self.assertFalse(config['production_change_approved'])
        self.assertFalse(config['frontend']['platform_edge_verified'])
        self.assertEqual(config['frontend']['build_environment_changes'], {'VITE_API_URL': '/api'})
        self.assertEqual(config['frontend']['ordered_rewrites'], [
            {'source': '/api/*', 'destination': 'https://priceyard-api.onrender.com/*', 'action': 'Rewrite'},
            {'source': '/*', 'destination': '/index.html', 'action': 'Rewrite'},
        ])
        self.assertEqual(config['backend']['required_allowed_browser_origin'], 'https://priceyard.onrender.com')
        self.assertEqual(config['backend']['cookie_policy_unchanged'], 'host-only Secure HttpOnly SameSite=Lax Path=/')
        self.assertTrue(config['backend']['direct_API_and_webhook_routes_preserved'])
        self.assertEqual((config['new_services'], config['new_dependencies'], config['paid_resources']), (0, 0, 0))
