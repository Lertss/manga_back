def data_acquisition_and_serialization(proposed_set_queries, proposed_class_serializer):
    """Executes a query to the database and returns the resulting data set and serializer class"""
    queryset = proposed_set_queries.objects.all()
    serializer_class = proposed_class_serializer
    return queryset, serializer_class
