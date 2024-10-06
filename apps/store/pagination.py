from rest_framework.pagination import PageNumberPagination
from rest_framework.views import Response


class ProductsListPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"

    def get_paginated_response(self, data, options={}):
        response_dict = {
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "results": data,
            "page_size": self.page_size,
            "current_page": self.page.number,
        }

        if options:
            response_dict.update(options)
        return Response(response_dict)


class ListQuerySetPagination(PageNumberPagination):
    def __init__(self, page_size=10) -> None:
        self.page_size = page_size
        super().__init__()

    def get_pagination_details(self):
        return {
            "page_links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "total_records_count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "page_size": self.page_size,
            "current_page": self.page.number,
        }

    def get_paginated_response(
        self,
        data,
        options={},
    ):
        response_dict = {
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "results": data,
            "page_size": self.page_size,
            "current_page": self.page.number,
        }

        if options:
            response_dict.update(options)

        return Response(response_dict)
