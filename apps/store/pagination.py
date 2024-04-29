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


# Common Pagination
class ListQuerySetPagination(PageNumberPagination):
    def __init__(self, page_size=20) -> None:
        self.page_size = page_size
        super().__init__()

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
