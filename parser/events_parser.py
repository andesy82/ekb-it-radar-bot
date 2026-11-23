
import json
import re
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent
FALLBACK_FILE = BASE_DIR / "sample_events.json"

SOURCES = [
    "https://timepad.ru/ekaterinburg/",
]


class EkbEventsParser:
    """Парсер IT-мероприятий Екатеринбурга."""

    def fetch_online_events(self) -> list[dict]:
        """Получает мероприятия из открытых источников."""
        events = []

        for url in SOURCES:
            try:
                response = httpx.get(
                    url,
                    timeout=5.0,
                    follow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                # Ищем структурированные данные JSON-LD.
                for script in soup.find_all(
                    "script",
                    type="application/ld+json"
                ):
                    try:
                        data = json.loads(script.string or script.get_text())

                        if isinstance(data, dict):
                            data = data.get("@graph", [data])

                        if not isinstance(data, list):
                            continue

                        for item in data:
                            if item.get("@type") not in (
                                "Event",
                                "EducationEvent",
                            ):
                                continue

                            title = item.get("name", "").strip()
                            if not title:
                                continue

                            location_data = item.get("location", {})
                            if isinstance(location_data, dict):
                                location = location_data.get("name", "")
                            else:
                                location = str(location_data)

                            description = item.get("description", "")
                            event_url = item.get("url", url)
                            date = item.get("startDate", "Дата уточняется")

                            events.append({
                                "id": str(item.get("@id", event_url)),
                                "title": title,
                                "date": str(date)[:10],
                                "location": location or "Екатеринбург",
                                "tags": self._extract_tags(
                                    title + " " + description
                                ),
                                "description": description,
                                "url": event_url,
                            })

                    except (json.JSONDecodeError, AttributeError, TypeError):
                        continue

            except httpx.HTTPError as error:
                print(f"Ошибка загрузки {url}: {error}")

        return events

    def load_fallback_events(self) -> list[dict]:
        """Загружает демонстрационные мероприятия из JSON."""
        try:
            with FALLBACK_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                return []

            required_fields = {
                "id",
                "title",
                "date",
                "location",
                "tags",
                "description",
                "url",
            }

            valid_events = []

            for event in data:
                if not isinstance(event, dict):
                    continue

                if not required_fields.issubset(event):
                    continue

                if not isinstance(event["tags"], list):
                    continue

                valid_events.append(event)

            return valid_events

        except (OSError, json.JSONDecodeError) as error:
            print(f"Ошибка чтения fallback-файла: {error}")
            return []

    @staticmethod
    def _extract_tags(text: str) -> list[str]:
        """Определяет теги по названию и описанию."""
        text = text.lower()

        keywords = {
            "python": ["python"],
            "csharp": ["c#", ".net", "csharp"],
            "web": ["web", "frontend", "backend", "javascript"],
            "ml": ["machine learning", "машинное обучение", "ai", "ml"],
        }

        tags = []

        for tag, words in keywords.items():
            if any(word in text for word in words):
                tags.append(tag)

        return tags

    def get_events(self, tag: str = "all") -> list[dict]:
        """Получает мероприятия и фильтрует их по тегу."""
        events = self.fetch_online_events()

        if not events:
            events = self.load_fallback_events()

        tag = tag.lower().strip()

        allowed_tags = {"all", "python", "csharp", "web", "ml"}

        if tag not in allowed_tags:
            raise ValueError(
                f"Неизвестный тег: {tag}. "
                f"Допустимые значения: {', '.join(sorted(allowed_tags))}"
            )

        if tag == "all":
            return events

        result = []

        for event in events:
            searchable_text = " ".join([
                event.get("title", ""),
                event.get("description", ""),
                " ".join(event.get("tags", [])),
            ]).lower()

            if tag == "python" and (
                "python" in searchable_text
            ):
                result.append(event)

            elif tag == "csharp" and re.search(
                r"c#|csharp|\.net", searchable_text
            ):
                result.append(event)

            elif tag in searchable_text:
                result.append(event)

        return result

    @staticmethod
    def format_event_card(event: dict[str, Any]) -> str:
        """Форматирует мероприятие для Telegram."""
        title = event.get("title", "Без названия")
        date = event.get("date", "Дата уточняется")
        location = event.get("location", "Место уточняется")
        description = event.get("description", "")
        url = event.get("url", "")
        tags = event.get("tags", [])

        tags_text = ", ".join(f"#{tag}" for tag in tags)

        return (
            f"*{title}*\n\n"
            f"📅 Дата: {date}\n"
            f"📍 Место: {location}\n"
            f"🏷 Теги: {tags_text}\n\n"
            f"{description}\n\n"
            f"🔗 {url}"
        )


if __name__ == "__main__":
    parser = EkbEventsParser()

    print("Мероприятия по Python:\n")

    for event in parser.get_events("python"):
        print(parser.format_event_card(event))
        print("-" * 50)
