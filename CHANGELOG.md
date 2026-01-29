# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]
- fix: handle missing topics in `get_topic_details` and `get_quiz` (returns 404)
- feat: semester-filtered recommendations in `/api/recommendations`
- feat: include `recommended_videos` in recommendations response
- test: add `tests/test_api_endpoints.py` (pytest integration tests)
- chore: add `test_api.py` smoke script for manual API verification
- chore: add `requests` and `pytest` to `requirements.txt`

