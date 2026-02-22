try:
    import lxml.etree as LET

    print("lxml available", LET.LXML_VERSION)
except Exception as e:
    print("lxml not available", type(e), e)
