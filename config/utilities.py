# This file contains common functions for apps 

def get_model_field(model, model_field, search_field, return_field):
    """
    Returns the a field given the a field
    """

    try:
        model = model.objects.get(model_field=search_field)
        return model.return_field
    except model.DoesNotExist:
        return None

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

def get_form_errors(form):
    errors = []
    for error in form.errors:
        errors.append(error)
    return errors



