def intent(func):
    """
    This is used inside the intent parser in `lessons.base.plugin._intent_dictionary()`
    :param func:
    :return:
    """
    func.decorator = intent
    return func
