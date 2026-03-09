from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
'''
i don't put page_size_param and max_page_size because by default
is None and users can't make request to decide page_size
'''
class SmallPageNumberPagination(PageNumberPagination):
    page_query_param = 'p'
    page_size = 3
    max_page_size = 3
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'previous_page':self.page.previous_page_number() if self.page.has_previous() else None,
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'previous': self.get_previous_link(),
            'next':self.get_next_link(),
            'results': {'data': data},
            'total_pages':self.page.paginator.num_pages,
            'total_range': range(1, self.page.paginator.num_pages + 1),
            'current_page':self.page.number
        })
        

class MediumQuestionNumberPagination(PageNumberPagination):
    page_query_param = 'p'
    page_size = 50
    max_page_size = 50
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'previous_page':self.page.previous_page_number() if self.page.has_previous() else None,
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'previous': self.get_previous_link(),
            'next':self.get_next_link(),
            'results': {'data': data},
            'total_pages':self.page.paginator.num_pages,
            'current_page':self.page.number
        })
    
class LargeQuestionNumberPagination(PageNumberPagination):
    page_query_param = 'p'
    page_size = 100
    max_page_size = 100
    page_size_query_param = 'page_size'
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'previous_page':self.page.previous_page_number() if self.page.has_previous() else None,
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'previous': self.get_previous_link(),
            'next':self.get_next_link(),
            'results': {'data': data},
            'total_pages':self.page.paginator.num_pages,
            'current_page':self.page.number
        })