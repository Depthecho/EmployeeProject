from typing import List, Callable, Any


class Pagination:
    """Класс для работы с пагинацией"""

    def __init__(self, total: int, per_page: int, current_page: int):
        self.total = total
        self.per_page = per_page
        self.current_page = current_page
        self.total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    def get_page_range(self) -> List:
        """Получить диапазон страниц для отображения"""
        total_pages = self.total_pages
        current_page = self.current_page

        if total_pages <= 7:
            return list(range(1, total_pages + 1))

        page_range = [1]
        if current_page > 4:
            page_range.append('...')

        start_page = max(2, current_page - 2)
        end_page = min(total_pages - 1, current_page + 2)

        for p in range(start_page, end_page + 1):
            page_range.append(p)

        if current_page < total_pages - 3:
            page_range.append('...')

        if total_pages > 1:
            page_range.append(total_pages)

        return page_range

    def to_dict(self, url_for_page: Callable) -> dict:
        """Преобразовать в словарь для шаблона"""
        return {
            "total": self.total,
            "per_page": self.per_page,
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "from": (self.current_page - 1) * self.per_page + 1 if self.total > 0 else 0,
            "to": min(self.current_page * self.per_page, self.total),
            "page_range": self.get_page_range(),
            "url_for_page": url_for_page
        }