from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class DefaultPaginator(Paginator):

    def __init__(self, request, object_list, per_page=8):
        super().__init__(object_list, per_page)
        self.request = request

    def get_paginated_response(self):
        page_num = self.request.GET.get('page', 1)
        try:
            objects = self.page(page_num)  # self.page() методидан фойдаланиш
        except PageNotAnInteger:
            objects = self.page(1)
        except EmptyPage:
            objects = self.page(self.num_pages)

        return objects