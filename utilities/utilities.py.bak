def handle_uploaded_file(f, dest):

    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
            
# increments numbering in docs ex: Invoice, Receipt, and so on
def increment_document_number(model):
    # Returns the first object matched by the queryset, or None if there is no matching object. 
    i = model.objects.order_by('-id').first()
    if i is not None:
        document_number = i.number + 1
    else:
        document_number = 1

    return document_number