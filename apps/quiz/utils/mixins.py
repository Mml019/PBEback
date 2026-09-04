'''class to make a limit of a paginator total numpages
    To split up numpages into a maximum numpages per block
    To limit block size and not create in each list view one data_get_context'''
class PaginationBlockMixin:
    block_page_size = 5
    default_page_size = 20
    default_pages_size = 1000
    allowed_pages_size = [20, 50, 100, 1000]
    
    def get_paginate_by(self, queryset):
        pages = self.request.GET.get("pages")

        if pages == "" or None:
            return None
        
        # transform pages to type int
        try:
            pages = int(pages)
        except (TypeError, ValueError):
            pages = self.default_page_size

        if pages in self.allowed_pages_size:
            return pages
        # else only returns default pages
        return self.default_page_size

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # block_page_size = 5
        page_obj = context['page_obj']
        current_page = page_obj.number
        num_pages = page_obj.paginator.num_pages

        current_block = (current_page - 1)//self.block_page_size

        start = (current_block * self.block_page_size) + 1
        end = min(start + self.block_page_size-1, num_pages) 

        page_range = list(range(start,end+1))
        context['num_pages']=num_pages
        context['start_page'] =start
        context['end_page'] =end
        context['page_range'] = page_range

        # if de pagination have other filters:
        query = self.request.GET.copy()
        query.pop('page', None)
        context['query_params'] = query.urlencode()

        # context for what page was selected:
        context["select_pages"] = self.request.GET.get("pages") or ""             

        return context
    
    def queryset_paginated(request):
        page = request.GET.get("page", 1)
        pages = request.GET.get("pages", 1000)

        if page:
            page = int(page)
        else:
            page = 1

        if pages:
            pages = int(pages)
        else:
            pages =1000

        if pages not in [20, 50, 100, 1000]:
            pages = 1000

        return page, pages