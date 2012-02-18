def tablefy( objects ):
    """Given a list of objects, build a matrix that is can be printed as a table. Also return
    the headers for that table. Populate the given url with the pk of the object. Return all
    headers, field array, and urls in a seperate lists.

    :param  objects: A list of objects to make the matrix out of.
    :type   objects: AddressRecords
    """
    matrix = []
    urls   = []
    headers = []
    if not objects:
        return (None, None, None)
    # Build the headers
    for title, value in objects[0].details():
        headers.append( title )

    # Build the matrix and urls
    for obj in objects:
        row = []
        urls.append( obj.get_absolute_url() )
        for title, value in obj.details():
            row.append( value )
        matrix.append(row)

    return (headers, matrix, urls)
