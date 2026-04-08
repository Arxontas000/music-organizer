from unittest.mock import patch

from django.test import TestCase


class ApiViewTests(TestCase):
    def test_health_returns_ok(self):
        response = self.client.get('/health/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_scan_requires_path(self):
        response = self.client.get('/scan/')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "path is required"})

    @patch('organizer.views.scan_folder')
    def test_scan_returns_grouped_tracks(self, mock_scan_folder):
        mock_scan_folder.return_value = [
            {
                "path": r"C:\Music\artist - song.mp3",
                "artist": "Artist",
                "title": "Tech Song",
                "genre": "Tech House",
            }
        ]

        response = self.client.get('/scan/', {"path": r"C:\Music"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "grouped": {
                    "Tech House": [
                        {
                            "path": r"C:\Music\artist - song.mp3",
                            "artist": "Artist",
                            "title": "Tech Song",
                            "genre": "Tech House",
                        }
                    ]
                }
            },
        )

    def test_preview_requires_path(self):
        response = self.client.get('/preview/')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "path is required"})

    @patch('organizer.views.preview_by_genre')
    @patch('organizer.views.scan_folder')
    def test_preview_returns_generated_paths(self, mock_scan_folder, mock_preview):
        mock_scan_folder.return_value = [
            {
                "path": r"C:\Music\artist - song.mp3",
                "artist": "Artist",
                "title": "Song",
                "genre": "House",
            }
        ]
        mock_preview.return_value = [
            {
                "from": r"C:\Music\artist - song.mp3",
                "to": r"C:\All Music\House\Artist\Song.mp3",
            }
        ]

        response = self.client.get('/preview/', {"path": r"C:\Music"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "preview": [
                    {
                        "from": r"C:\Music\artist - song.mp3",
                        "to": r"C:\All Music\House\Artist\Song.mp3",
                    }
                ]
            },
        )
